#!/usr/bin/env python3
"""
Convert Kening's Assertions to S+G Framework Format

This script uses the assertion_analyzer package to classify Kening's assertions
according to the new WBP S+G framework (29 dimensions: S1-S20 + G1-G9).

Features:
- GPT-5 classification using classify_assertion()
- Generates full S+G unit (S assertion + linked G assertions)
- JSONL output format (one assertion per line, S and G assertions adjacent)
- UNKNOWN dimension for unclassifiable assertions
- Progress tracking and resumable processing

Output Format:
- Each S assertion is followed by its linked G assertions
- G assertions have parent_assertion_id linking to their source S
- S assertions have linked_g_dims listing which G dimensions apply

Usage:
    python convert_kening_assertions_v2.py                    # Convert all
    python convert_kening_assertions_v2.py --start 0 --end 10 # Range
    python convert_kening_assertions_v2.py --resume           # Resume from checkpoint
    python convert_kening_assertions_v2.py --dry-run          # Preview without GPT-5

Author: Chin-Yew Lin
Date: November 30, 2025
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add assertion_analyzer to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "assertion_analyzer"))

from assertion_analyzer import classify_assertion, S_TO_G_MAP, DIMENSION_NAMES
from assertion_analyzer.config import get_substrate_token, call_gpt5_api, extract_json_from_response
from assertion_analyzer.dimensions import G_RATIONALE_FOR_S

# =============================================================================
# CONFIGURATION
# =============================================================================

INPUT_FILE = "docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl"
OUTPUT_FILE = "docs/ChinYew/assertions_sg_classified.jsonl"
CHECKPOINT_FILE = "docs/ChinYew/.sg_classification_checkpoint.json"
REPORT_FILE = "docs/ChinYew/sg_classification_report.json"

# Rate limiting
DELAY_BETWEEN_CALLS = 0.5  # seconds between GPT-5 calls
BATCH_SAVE_SIZE = 10       # Save checkpoint every N assertions

# G Dimension slot descriptions
G_SLOT_DESCRIPTIONS = {
    "G1": "hallucination_check - entities that must not be fabricated",
    "G2": "attendees - specific people/names mentioned",
    "G3": "dates_times - specific dates, times, deadlines mentioned",
    "G4": "artifacts - specific files, documents, links mentioned",
    "G5": "topics - meeting subject, agenda items mentioned",
    "G6": "action_items - specific tasks, action items, dependencies mentioned",
    "G7": "roles - role/responsibility assignments mentioned",
    "G8": "constraints - limits, requirements, conditions mentioned",
    "G9": "planner_generated - assumptions, blockers, mitigations mentioned",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_checkpoint() -> dict:
    """Load checkpoint if exists."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_count": 0, "last_meeting_idx": -1, "last_assertion_idx": -1}


def save_checkpoint(checkpoint: dict):
    """Save checkpoint for resumability."""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)


def load_input_data() -> List[dict]:
    """Load Kening's assertions from JSONL file."""
    data = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def generate_sg_unit(
    assertion_text: str,
    assertion_level: str,
    meeting_idx: int,
    assertion_idx: int,
    utterance: str,
    classification_result: dict,
    slot_values: dict = None
) -> List[dict]:
    """
    Generate the full S+G unit for a classified assertion.
    
    For S assertions: generates 1 S assertion + N linked G assertions with slot values
    For G assertions: generates just the G assertion
    
    Args:
        assertion_text: Original assertion text
        assertion_level: critical/expected/aspirational
        meeting_idx: Meeting index for ID generation
        assertion_idx: Assertion index for ID generation
        utterance: Original user utterance
        classification_result: Result from classify_assertion
        slot_values: Extracted slot values from GPT-5 (g_dim -> value)
    
    Returns list of assertions (S first, then linked Gs with populated slots)
    """
    results = []
    slot_values = slot_values or {}
    
    dimension = classification_result.get("dimension", "UNKNOWN")
    dimension_name = classification_result.get("dimension_name", "Unknown")
    layer = classification_result.get("layer", "unknown")
    rationale = classification_result.get("rationale", "")
    linked_g_dims = classification_result.get("linked_g_dims", [])
    
    # Generate primary assertion ID
    primary_id = f"M{meeting_idx:04d}_A{assertion_idx:03d}_{dimension}"
    
    # Create primary assertion
    primary = {
        "assertion_id": primary_id,
        "parent_assertion_id": None,
        "text": assertion_text,
        "dimension": dimension,
        "dimension_name": dimension_name,
        "layer": layer,
        "level": assertion_level,
        "linked_g_dims": linked_g_dims,
        "rationale": {
            "mapping_reason": rationale,
            "conversion_method": "gpt5_classify"
        },
        "quality_assessment": {
            "is_well_formed": dimension != "UNKNOWN",
            "is_testable": dimension != "UNKNOWN"
        },
        "utterance_preview": utterance[:100] + "..." if len(utterance) > 100 else utterance
    }
    results.append(primary)
    
    # For S assertions, generate linked G assertions with slot values
    if dimension.startswith("S") and linked_g_dims:
        for g_idx, g_dim in enumerate(linked_g_dims):
            g_id = f"M{meeting_idx:04d}_A{assertion_idx:03d}_{g_dim}_{g_idx}"
            g_name = DIMENSION_NAMES.get(g_dim, "Unknown")
            
            # Get slot value for this G dimension (extracted by GPT-5)
            slot_value = slot_values.get(g_dim, None)
            
            # Generate G assertion text with slot value
            if slot_value:
                g_text = f"The {g_name.lower()} must match: {slot_value}"
            else:
                g_text = f"Verify {g_name.lower()} against source data"
            
            # Get rationale for this S→G mapping
            g_rationale = G_RATIONALE_FOR_S.get((dimension, g_dim), 
                f"Generated from {dimension} via S_TO_G_MAP")
            
            g_assertion = {
                "assertion_id": g_id,
                "parent_assertion_id": primary_id,
                "text": g_text,
                "slot_value": slot_value,
                "original_s_text": assertion_text,
                "dimension": g_dim,
                "dimension_name": g_name,
                "layer": "grounding",
                "level": "critical",  # G assertions are always critical
                "linked_g_dims": [],
                "rationale": {
                    "mapping_reason": g_rationale,
                    "parent_dimension": dimension,
                    "parent_dimension_name": dimension_name,
                    "conversion_method": "s_to_g_mapping"
                },
                "quality_assessment": {
                    "is_well_formed": True,
                    "is_testable": slot_value is not None
                }
            }
            results.append(g_assertion)
    
    return results


def extract_slot_values(assertion_text: str, linked_g_dims: List[str]) -> dict:
    """
    Use GPT-5 to extract slot values from assertion text for each G dimension.
    Uses optimized IE prompt from prompts/ie_slot_extraction_prompt.json.
    
    Args:
        assertion_text: The original assertion text
        linked_g_dims: List of G dimensions to extract values for
        
    Returns:
        dict mapping g_dim -> extracted value (or None if not found)
    """
    if not linked_g_dims:
        return {}
    
    # Load optimized IE prompt from file
    prompt_file = os.path.join(
        os.path.dirname(__file__), 
        "assertion_analyzer", "prompts", "ie_slot_extraction_prompt.json"
    )
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_config = json.load(f)
        prompt_template = prompt_config.get("user_prompt_template", "")
        slot_descriptions = prompt_config.get("slot_descriptions", {})
        system_prompt = prompt_config.get("system_prompt", "")
        temperature = prompt_config.get("temperature", 0.1)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"      Warning: Could not load ie_slot_extraction_prompt.json: {e}, using fallback")
        # Fallback to inline descriptions
        slot_descriptions = G_SLOT_DESCRIPTIONS
        prompt_template = None
        system_prompt = "You extract specific values from assertions for grounding verification."
        temperature = 0.1
    
    # Build slot descriptions for this extraction
    slots_desc = []
    for g_dim in linked_g_dims:
        desc = slot_descriptions.get(g_dim, G_SLOT_DESCRIPTIONS.get(g_dim, g_dim))
        slots_desc.append(f"- {g_dim}: {desc}")
    
    if prompt_template:
        # Use loaded template
        prompt = prompt_template.replace("{assertion_text}", assertion_text)
        prompt = prompt.replace("{slot_descriptions}", chr(10).join(slots_desc))
    else:
        # Fallback prompt
        prompt = f'''Extract specific values from this assertion for grounding verification.

ASSERTION: "{assertion_text}"

SLOTS TO EXTRACT:
{chr(10).join(slots_desc)}

For each slot, extract the EXACT value mentioned in the assertion.
If a slot type is not mentioned, return null.

Return JSON:
{{
{chr(10).join([f'    "{g}": "<extracted value or null>"' for g in linked_g_dims])}
}}

Return ONLY valid JSON with extracted values.
'''

    try:
        result_text = call_gpt5_api(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        result = extract_json_from_response(result_text)
        
        # Clean up results - convert "null" strings to None, handle lists
        cleaned = {}
        for g_dim in linked_g_dims:
            val = result.get(g_dim)
            if val is None:
                continue
            if isinstance(val, str) and val.lower() in ["null", "none", "n/a", ""]:
                continue
            if isinstance(val, list):
                # Filter out null-like values from lists
                val = [v for v in val if v and str(v).lower() not in ["null", "none", "n/a", ""]]
                if val:
                    cleaned[g_dim] = val
            else:
                cleaned[g_dim] = val
        return cleaned
    except Exception as e:
        print(f"      Warning: slot extraction failed: {e}")
        return {}


def classify_and_expand(
    assertion_text: str,
    assertion_level: str,
    meeting_idx: int,
    assertion_idx: int,
    utterance: str,
    dry_run: bool = False
) -> List[dict]:
    """
    Classify assertion and expand to full S+G unit.
    
    Returns list of assertions (1 S/G + 0-N linked G assertions)
    """
    if dry_run:
        # Return placeholder for dry run
        return [{
            "assertion_id": f"M{meeting_idx:04d}_A{assertion_idx:03d}_DRY_RUN",
            "parent_assertion_id": None,
            "text": assertion_text,
            "dimension": "DRY_RUN",
            "dimension_name": "Dry Run Mode",
            "layer": "unknown",
            "level": assertion_level,
            "linked_g_dims": [],
            "rationale": {"mapping_reason": "Dry run - no GPT-5 call made"},
            "quality_assessment": {"is_well_formed": False, "is_testable": False},
            "utterance_preview": utterance[:100] + "..." if len(utterance) > 100 else utterance
        }]
    
    # Call classify_assertion from assertion_analyzer
    try:
        result = classify_assertion(assertion_text, verbose=False)
        
        # Extract slot values for G assertions if this is an S assertion
        slot_values = {}
        linked_g_dims = result.get("linked_g_dims", [])
        if result.get("dimension", "").startswith("S") and linked_g_dims:
            slot_values = extract_slot_values(assertion_text, linked_g_dims)
        
        return generate_sg_unit(
            assertion_text=assertion_text,
            assertion_level=assertion_level,
            meeting_idx=meeting_idx,
            assertion_idx=assertion_idx,
            utterance=utterance,
            classification_result=result,
            slot_values=slot_values
        )
    except Exception as e:
        # Return UNKNOWN on error
        return [{
            "assertion_id": f"M{meeting_idx:04d}_A{assertion_idx:03d}_UNKNOWN",
            "parent_assertion_id": None,
            "text": assertion_text,
            "dimension": "UNKNOWN",
            "dimension_name": "Classification Error",
            "layer": "unknown",
            "level": assertion_level,
            "linked_g_dims": [],
            "rationale": {"mapping_reason": f"Error: {str(e)}"},
            "quality_assessment": {"is_well_formed": False, "is_testable": False},
            "utterance_preview": utterance[:100] + "..." if len(utterance) > 100 else utterance
        }]


def process_assertions(
    start_meeting: int = 0,
    end_meeting: Optional[int] = None,
    resume: bool = False,
    dry_run: bool = False
) -> dict:
    """
    Process all assertions from Kening's data.
    
    Args:
        start_meeting: Starting meeting index
        end_meeting: Ending meeting index (exclusive), None for all
        resume: Whether to resume from checkpoint
        dry_run: If True, don't call GPT-5
        
    Returns:
        Summary statistics
    """
    print("=" * 70)
    print("Kening Assertions → S+G Framework Conversion")
    print("=" * 70)
    
    # Load data
    print(f"\nLoading input from: {INPUT_FILE}")
    data = load_input_data()
    total_meetings = len(data)
    print(f"Total meetings: {total_meetings}")
    
    # Handle resume
    checkpoint = load_checkpoint() if resume else {"processed_count": 0, "last_meeting_idx": -1, "last_assertion_idx": -1}
    
    if resume and checkpoint["processed_count"] > 0:
        print(f"Resuming from checkpoint: {checkpoint['processed_count']} assertions already processed")
        start_meeting = checkpoint["last_meeting_idx"]
    
    # Determine range
    if end_meeting is None:
        end_meeting = total_meetings
    
    print(f"Processing meetings {start_meeting} to {end_meeting - 1}")
    
    if not dry_run:
        print("\nAuthenticating with GPT-5...")
        get_substrate_token()  # Pre-authenticate
        print("Authentication successful")
    
    # Statistics
    stats = {
        "total_input_assertions": 0,
        "total_output_assertions": 0,  # Includes generated G assertions
        "s_assertions": 0,
        "g_assertions_generated": 0,
        "unknown": 0,
        "by_dimension": {},
        "by_layer": {"structural": 0, "grounding": 0, "unknown": 0},
        "by_level": {"critical": 0, "expected": 0, "aspirational": 0}
    }
    
    # Open output file in append mode if resuming, write mode otherwise
    mode = 'a' if resume and checkpoint["processed_count"] > 0 else 'w'
    output_file = open(OUTPUT_FILE, mode, encoding='utf-8')
    
    try:
        input_assertion_count = checkpoint["processed_count"]
        
        for meeting_idx in range(start_meeting, end_meeting):
            meeting = data[meeting_idx]
            utterance = meeting.get("utterance", "")
            assertions = meeting.get("assertions", [])
            
            print(f"\n[Meeting {meeting_idx + 1}/{end_meeting}] {len(assertions)} assertions")
            print(f"  Utterance: {utterance[:60]}...")
            
            # Determine starting assertion index for this meeting
            start_assertion_idx = 0
            if resume and meeting_idx == checkpoint["last_meeting_idx"]:
                start_assertion_idx = checkpoint["last_assertion_idx"] + 1
            
            for assertion_idx in range(start_assertion_idx, len(assertions)):
                assertion = assertions[assertion_idx]
                assertion_text = assertion.get("text", "")
                assertion_level = assertion.get("level", "expected")
                
                # Classify and expand to S+G unit
                sg_unit = classify_and_expand(
                    assertion_text=assertion_text,
                    assertion_level=assertion_level,
                    meeting_idx=meeting_idx,
                    assertion_idx=assertion_idx,
                    utterance=utterance,
                    dry_run=dry_run
                )
                
                # Write all assertions in the unit
                for a in sg_unit:
                    output_file.write(json.dumps(a, ensure_ascii=False) + "\n")
                output_file.flush()
                
                # Update statistics
                stats["total_input_assertions"] += 1
                stats["total_output_assertions"] += len(sg_unit)
                
                primary = sg_unit[0]
                dim = primary["dimension"]
                
                if dim == "UNKNOWN" or dim == "DRY_RUN":
                    stats["unknown"] += 1
                elif dim.startswith("S"):
                    stats["s_assertions"] += 1
                    stats["g_assertions_generated"] += len(sg_unit) - 1
                
                stats["by_dimension"][dim] = stats["by_dimension"].get(dim, 0) + 1
                stats["by_layer"][primary.get("layer", "unknown")] = stats["by_layer"].get(primary.get("layer", "unknown"), 0) + 1
                stats["by_level"][assertion_level] = stats["by_level"].get(assertion_level, 0) + 1
                
                input_assertion_count += 1
                
                # Progress
                g_count = len(sg_unit) - 1
                g_info = f" +{g_count}G" if g_count > 0 else ""
                print(f"    [{assertion_idx + 1}/{len(assertions)}] {dim}{g_info}: {assertion_text[:50]}...")
                
                # Save checkpoint periodically
                if input_assertion_count % BATCH_SAVE_SIZE == 0:
                    checkpoint = {
                        "processed_count": input_assertion_count,
                        "last_meeting_idx": meeting_idx,
                        "last_assertion_idx": assertion_idx
                    }
                    save_checkpoint(checkpoint)
                
                # Rate limiting
                if not dry_run:
                    time.sleep(DELAY_BETWEEN_CALLS)
    
    finally:
        output_file.close()
    
    # Final checkpoint
    checkpoint = {
        "processed_count": input_assertion_count,
        "last_meeting_idx": end_meeting - 1,
        "last_assertion_idx": -1,  # Completed
        "completed": True
    }
    save_checkpoint(checkpoint)
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "input_file": INPUT_FILE,
        "output_file": OUTPUT_FILE,
        "meetings_processed": end_meeting - start_meeting,
        "statistics": stats,
        "dry_run": dry_run
    }
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    return stats


def print_summary(stats: dict):
    """Print summary statistics."""
    print("\n" + "=" * 70)
    print("CONVERSION SUMMARY")
    print("=" * 70)
    print(f"Input assertions:     {stats['total_input_assertions']}")
    print(f"Output assertions:    {stats['total_output_assertions']} (S + generated G)")
    print(f"  - S assertions:     {stats['s_assertions']}")
    print(f"  - G generated:      {stats['g_assertions_generated']}")
    print(f"  - Unknown:          {stats['unknown']}")
    
    print("\nBy Dimension (input):")
    for dim, count in sorted(stats["by_dimension"].items(), key=lambda x: -x[1]):
        name = DIMENSION_NAMES.get(dim, dim)
        print(f"  {dim:8s} {name:30s} {count:4d}")
    
    print("\nBy Layer (input):")
    for layer, count in stats["by_layer"].items():
        print(f"  {layer:12s} {count:4d}")
    
    print("\nBy Level (input):")
    for level, count in stats["by_level"].items():
        print(f"  {level:12s} {count:4d}")
    
    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Convert Kening's assertions to S+G framework")
    parser.add_argument("--start", type=int, default=0, help="Starting meeting index")
    parser.add_argument("--end", type=int, default=None, help="Ending meeting index (exclusive)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--dry-run", action="store_true", help="Preview without GPT-5 calls")
    
    args = parser.parse_args()
    
    stats = process_assertions(
        start_meeting=args.start,
        end_meeting=args.end,
        resume=args.resume,
        dry_run=args.dry_run
    )
    
    print_summary(stats)


if __name__ == "__main__":
    main()
