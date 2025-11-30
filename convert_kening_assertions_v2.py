#!/usr/bin/env python3
"""
Convert Kening's Assertions to S+G Framework Format (v2 - Atomic Decomposition)

This script uses the decomposition prompt to convert free-form assertions
into ATOMIC S+G units. Each free-form assertion can decompose into multiple
S dimensions, each with linked G dimensions and extracted slot values.

Key Insight: S+G dimensions are ATOMIC (test one thing), but free-form 
assertions can combine multiple requirements. This script decomposes them.

Features:
- GPT-5 decomposition using decomposition_prompt.json (v3.0)
- Decomposes free-form assertions into multiple atomic S+G units
- Extracts slot values for G assertions
- JSONL output format
- Progress tracking and resumable processing

Output Format:
- Each decomposed S unit is written as separate assertion
- G assertions follow their parent S assertion
- original_assertion field tracks the source

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

from assertion_analyzer import S_TO_G_MAP, DIMENSION_NAMES
from assertion_analyzer.config import get_substrate_token, call_gpt5_api, extract_json_from_response
from assertion_analyzer.dimensions import G_RATIONALE_FOR_S

# =============================================================================
# CONFIGURATION
# =============================================================================

INPUT_FILE = "docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl"
OUTPUT_FILE = "docs/ChinYew/assertions_sg_classified_v2.3.jsonl"
OUTPUT_DIR = "docs/ChinYew/sg_stages_v2.3"  # Directory for staged outputs
CHECKPOINT_FILE = "docs/ChinYew/.sg_classification_checkpoint_v2.3.json"
REPORT_FILE = "docs/ChinYew/sg_classification_report_v2.3.json"

# Rate limiting
DELAY_BETWEEN_CALLS = 0.5  # seconds between GPT-5 calls
BATCH_SAVE_SIZE = 10       # Save checkpoint every N assertions
STAGE_SIZE = 50            # Meetings per stage (refresh token between stages)

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
    "G10": "relations - DEPENDS_ON, OWNS, BLOCKS, PRODUCES relationships mentioned",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Load decomposition prompt once at module level
DECOMPOSITION_PROMPT_FILE = os.path.join(
    os.path.dirname(__file__), 
    "assertion_analyzer", "prompts", "decomposition_prompt.json"
)

def load_decomposition_prompt() -> dict:
    """Load the decomposition prompt configuration."""
    with open(DECOMPOSITION_PROMPT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Cache the prompt config
_DECOMPOSITION_CONFIG = None

def get_decomposition_config() -> dict:
    """Get cached decomposition prompt config."""
    global _DECOMPOSITION_CONFIG
    if _DECOMPOSITION_CONFIG is None:
        _DECOMPOSITION_CONFIG = load_decomposition_prompt()
    return _DECOMPOSITION_CONFIG


def decompose_assertion(assertion_text: str) -> List[dict]:
    """
    Decompose a free-form assertion into atomic S+G units using GPT-5.
    
    Args:
        assertion_text: The free-form assertion to decompose
        
    Returns:
        List of atomic units, each with:
        - s_dimension: S code (e.g., "S1") or null
        - s_name: S dimension name
        - s_assertion: Atomic structural requirement
        - linked_g: List of {g_dimension, slot_value} dicts
    """
    config = get_decomposition_config()
    prompt = config['user_prompt_template'].replace('{assertion_text}', assertion_text)
    
    result_text = call_gpt5_api(
        prompt,
        system_prompt=config['system_prompt'],
        temperature=config.get('temperature', 0.2)
    )
    
    return extract_json_from_response(result_text)


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


def decompose_and_expand(
    assertion_text: str,
    assertion_level: str,
    meeting_idx: int,
    assertion_idx: int,
    utterance: str,
    dry_run: bool = False
) -> List[dict]:
    """
    Decompose a free-form assertion into atomic S+G units and expand.
    
    Uses decomposition_prompt.json to break down assertions that may 
    contain multiple structural requirements into separate atomic units.
    
    Returns list of assertions (multiple S assertions, each with linked Gs)
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
    
    try:
        # Decompose into atomic units using GPT-5
        atomic_units = decompose_assertion(assertion_text)
        
        if not atomic_units or not isinstance(atomic_units, list):
            raise ValueError("Decomposition returned empty or invalid result")
        
        results = []
        s_unit_idx = 0
        
        for unit in atomic_units:
            s_dim = unit.get('s_dimension')
            s_name = unit.get('s_name', '')
            # Support both old (s_assertion) and new (s_template/s_literal) formats
            s_template = unit.get('s_template', '')
            s_literal = unit.get('s_literal', '')
            s_assertion = unit.get('s_assertion', '')  # Fallback for old format
            linked_g = unit.get('linked_g', [])
            
            # Handle pure G assertions (no S dimension)
            if not s_dim:
                # This is a pure grounding assertion
                for g_idx, g_info in enumerate(linked_g):
                    g_dim = g_info.get('g_dimension', 'G1')
                    slot_value = g_info.get('slot_value')
                    constraint = g_info.get('constraint', '')
                    
                    g_id = f"M{meeting_idx:04d}_A{assertion_idx:03d}_{g_dim}"
                    g_name = DIMENSION_NAMES.get(g_dim, g_dim)
                    
                    g_assertion = {
                        "assertion_id": g_id,
                        "parent_assertion_id": None,
                        "text": assertion_text,
                        "original_assertion": assertion_text,
                        "slot_value": slot_value,
                        "constraint": constraint if constraint else None,
                        "dimension": g_dim,
                        "dimension_name": g_name,
                        "layer": "grounding",
                        "level": assertion_level,
                        "linked_g_dims": [],
                        "rationale": {
                            "mapping_reason": "Pure grounding assertion (no structural requirement)",
                            "conversion_method": "decomposition"
                        },
                        "quality_assessment": {
                            "is_well_formed": True,
                            "is_testable": True
                        },
                        "utterance_preview": utterance[:100] + "..." if len(utterance) > 100 else utterance
                    }
                    results.append(g_assertion)
                continue
            
            # Generate S assertion ID
            s_id = f"M{meeting_idx:04d}_A{assertion_idx:03d}_S{s_unit_idx}_{s_dim}"
            s_unit_idx += 1
            
            # Build G slots as nested array inside S unit
            g_slots = []
            for g_idx, g_info in enumerate(linked_g):
                g_dim = g_info.get('g_dimension')
                if not g_dim:
                    continue
                    
                slot_name = g_info.get('slot_name', g_dim)
                slot_value = g_info.get('slot_value')
                g_name = DIMENSION_NAMES.get(g_dim, g_dim)
                
                # Get rationale for S→G mapping
                g_rationale = G_RATIONALE_FOR_S.get((s_dim, g_dim), 
                    f"Generated from {s_dim} decomposition")
                
                g_slot = {
                    "g_dimension": g_dim,
                    "g_dimension_name": g_name,
                    "slot_name": slot_name,
                    "slot_value": slot_value,
                    "rationale": g_rationale
                }
                g_slots.append(g_slot)
            
            # Create unified S+G unit
            # s_dimension_name: Canonical name from DIMENSION_NAMES (e.g., "Meeting Details")
            # sub_category: Specialized name from GPT-5 decomposition (e.g., "Meeting Title")
            canonical_name = DIMENSION_NAMES.get(s_dim, s_dim) if s_dim else None
            specialized_name = s_name if s_name and s_name != canonical_name else None
            
            sg_unit_obj = {
                "assertion_id": s_id,
                "original_assertion": assertion_text,
                "s_dimension": s_dim,
                "s_dimension_name": canonical_name,
                "sub_category": specialized_name,
                "s_template": s_template or None,
                "s_literal": s_literal or s_assertion or assertion_text,
                "level": assertion_level,
                "g_slots": g_slots,
                "rationale": {
                    "mapping_reason": f"Decomposed from: {assertion_text[:80]}...",
                    "conversion_method": "decomposition"
                },
                "utterance_preview": utterance[:100] + "..." if len(utterance) > 100 else utterance
            }
            results.append(sg_unit_obj)
        
        return results if results else [{
            "assertion_id": f"M{meeting_idx:04d}_A{assertion_idx:03d}_UNKNOWN",
            "original_assertion": assertion_text,
            "s_dimension": "UNKNOWN",
            "s_dimension_name": "Unknown",
            "sub_category": "Decomposition Empty",
            "s_template": None,
            "s_literal": assertion_text,
            "level": assertion_level,
            "g_slots": [],
            "rationale": {"mapping_reason": "Decomposition returned no units"},
            "utterance_preview": utterance[:100] + "..." if len(utterance) > 100 else utterance
        }]
        
    except Exception as e:
        # Return UNKNOWN on error
        return [{
            "assertion_id": f"M{meeting_idx:04d}_A{assertion_idx:03d}_UNKNOWN",
            "parent_assertion_id": None,
            "text": assertion_text,
            "dimension": "UNKNOWN",
            "dimension_name": "Decomposition Error",
            "layer": "unknown",
            "level": assertion_level,
            "linked_g_dims": [],
            "rationale": {"mapping_reason": f"Error: {str(e)}"},
            "quality_assessment": {"is_well_formed": False, "is_testable": False},
            "utterance_preview": utterance[:100] + "..." if len(utterance) > 100 else utterance
        }]


def refresh_gpt5_token():
    """Force refresh the GPT-5 token by clearing cached token."""
    from assertion_analyzer.config import clear_token_cache
    clear_token_cache()
    print("  [Token cleared, will re-authenticate on next call]")


def process_stage(
    data: List[dict],
    stage_start: int,
    stage_end: int,
    stage_num: int,
    dry_run: bool = False
) -> tuple:
    """
    Process a single stage of meetings and save to a stage-specific file.
    
    Returns:
        tuple: (stage_stats, output_file_path)
    """
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    stage_output = os.path.join(OUTPUT_DIR, f"stage_{stage_num:03d}.jsonl")
    
    stats = {
        "total_input_assertions": 0,
        "total_sg_units": 0,  # Number of S+G unit records
        "s_count": 0,         # Total S assertions (for structural success rate)
        "g_count": 0,         # Total G slots (for grounding success rate)
        "unknown": 0,
        "by_s_dimension": {},  # Count by S dimension
        "by_g_dimension": {},  # Count by G dimension
        "by_level": {"critical": 0, "expected": 0, "aspirational": 0}
    }
    
    with open(stage_output, 'w', encoding='utf-8') as output_file:
        for meeting_idx in range(stage_start, stage_end):
            meeting = data[meeting_idx]
            utterance = meeting.get("utterance", "")
            assertions = meeting.get("assertions", [])
            
            print(f"\n  [Meeting {meeting_idx + 1}] {len(assertions)} assertions")
            print(f"    Utterance: {utterance[:55]}...")
            
            for assertion_idx in range(len(assertions)):
                assertion = assertions[assertion_idx]
                assertion_text = assertion.get("text", "")
                assertion_level = assertion.get("level", "expected")
                
                # Decompose and expand to atomic S+G units
                sg_units = decompose_and_expand(
                    assertion_text=assertion_text,
                    assertion_level=assertion_level,
                    meeting_idx=meeting_idx,
                    assertion_idx=assertion_idx,
                    utterance=utterance,
                    dry_run=dry_run
                )
                
                # Write all S+G units
                for unit in sg_units:
                    output_file.write(json.dumps(unit, ensure_ascii=False) + "\n")
                output_file.flush()
                
                # Update statistics
                stats["total_input_assertions"] += 1
                stats["total_sg_units"] += len(sg_units)
                
                for unit in sg_units:
                    s_dim = unit.get("s_dimension", "UNKNOWN")
                    g_slots = unit.get("g_slots", [])
                    
                    if s_dim == "UNKNOWN" or s_dim == "DRY_RUN":
                        stats["unknown"] += 1
                    else:
                        # Count S assertion
                        stats["s_count"] += 1
                        stats["by_s_dimension"][s_dim] = stats["by_s_dimension"].get(s_dim, 0) + 1
                        
                        # Count each G slot
                        for g_slot in g_slots:
                            g_dim = g_slot.get("g_dimension", "UNKNOWN")
                            stats["g_count"] += 1
                            stats["by_g_dimension"][g_dim] = stats["by_g_dimension"].get(g_dim, 0) + 1
                    
                    stats["by_level"][assertion_level] = stats["by_level"].get(assertion_level, 0) + 1
                
                # Progress
                primary = sg_units[0]
                dim = primary.get("s_dimension", "UNKNOWN")
                g_count = len(primary.get("g_slots", []))
                g_info = f" +{g_count}G" if g_count > 0 else ""
                print(f"      [{assertion_idx + 1}/{len(assertions)}] {dim}{g_info}: {assertion_text[:45]}...")
                
                # Rate limiting
                if not dry_run:
                    time.sleep(DELAY_BETWEEN_CALLS)
    
    return stats, stage_output


def combine_stage_files(stage_files: List[str], output_path: str):
    """Combine all stage files into a single output file."""
    print(f"\nCombining {len(stage_files)} stage files into {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as out_f:
        for stage_file in stage_files:
            with open(stage_file, 'r', encoding='utf-8') as in_f:
                for line in in_f:
                    out_f.write(line)
    print(f"  Combined output saved to: {output_path}")


def merge_stats(total_stats: dict, stage_stats: dict) -> dict:
    """Merge stage statistics into total statistics."""
    total_stats["total_input_assertions"] += stage_stats["total_input_assertions"]
    total_stats["total_sg_units"] += stage_stats["total_sg_units"]
    total_stats["s_count"] += stage_stats["s_count"]
    total_stats["g_count"] += stage_stats["g_count"]
    total_stats["unknown"] += stage_stats["unknown"]
    
    for dim, count in stage_stats["by_s_dimension"].items():
        total_stats["by_s_dimension"][dim] = total_stats["by_s_dimension"].get(dim, 0) + count
    
    for dim, count in stage_stats["by_g_dimension"].items():
        total_stats["by_g_dimension"][dim] = total_stats["by_g_dimension"].get(dim, 0) + count
    
    for level, count in stage_stats["by_level"].items():
        total_stats["by_level"][level] = total_stats["by_level"].get(level, 0) + count
    
    return total_stats


def process_assertions(
    start_meeting: int = 0,
    end_meeting: Optional[int] = None,
    resume: bool = False,
    dry_run: bool = False,
    stage_size: int = STAGE_SIZE
) -> dict:
    """
    Process all assertions from Kening's data.
    
    Args:
        start_meeting: Starting meeting index
        end_meeting: Ending meeting index (exclusive), None for all
        resume: Whether to resume from checkpoint
        dry_run: If True, don't call GPT-5
        stage_size: Number of meetings per stage (default 50)
        
    Returns:
        Summary statistics
    """
    print("=" * 70)
    print("Kening Assertions → S+G Framework Conversion (Staged)")
    print("=" * 70)
    
    # Load data
    print(f"\nLoading input from: {INPUT_FILE}")
    data = load_input_data()
    total_meetings = len(data)
    print(f"Total meetings: {total_meetings}")
    
    # Handle resume
    checkpoint = load_checkpoint() if resume else {"processed_count": 0, "last_meeting_idx": -1, "last_assertion_idx": -1, "completed_stages": []}
    
    if resume and checkpoint.get("processed_count", 0) > 0:
        print(f"Resuming from checkpoint: {checkpoint['processed_count']} assertions already processed")
        start_meeting = checkpoint.get("last_meeting_idx", 0) + 1
    
    # Determine range
    if end_meeting is None:
        end_meeting = total_meetings
    
    print(f"Processing meetings {start_meeting} to {end_meeting - 1}")
    print(f"Stage size: {stage_size} meetings per stage")
    
    # Calculate stages
    num_stages = (end_meeting - start_meeting + stage_size - 1) // stage_size
    print(f"Total stages: {num_stages}")
    
    # Initialize total statistics
    total_stats = {
        "total_input_assertions": 0,
        "total_sg_units": 0,
        "s_count": 0,
        "g_count": 0,
        "unknown": 0,
        "by_s_dimension": {},
        "by_g_dimension": {},
        "by_level": {"critical": 0, "expected": 0, "aspirational": 0}
    }
    
    stage_files = checkpoint.get("completed_stages", [])
    
    # Process each stage
    current_start = start_meeting
    stage_num = len(stage_files) + 1
    
    while current_start < end_meeting:
        current_end = min(current_start + stage_size, end_meeting)
        
        print(f"\n{'=' * 70}")
        print(f"STAGE {stage_num}/{num_stages}: Meetings {current_start} to {current_end - 1}")
        print(f"{'=' * 70}")
        
        # Authenticate/re-authenticate for this stage
        if not dry_run:
            print("\nAuthenticating with GPT-5...")
            refresh_gpt5_token()  # Clear cached token
            get_substrate_token()  # Get fresh token
            print("Authentication successful (fresh token)")
        
        # Process the stage
        stage_stats, stage_file = process_stage(
            data=data,
            stage_start=current_start,
            stage_end=current_end,
            stage_num=stage_num,
            dry_run=dry_run
        )
        
        # Merge statistics
        total_stats = merge_stats(total_stats, stage_stats)
        stage_files.append(stage_file)
        
        # Save checkpoint after each stage
        checkpoint = {
            "processed_count": total_stats["total_input_assertions"],
            "last_meeting_idx": current_end - 1,
            "last_assertion_idx": -1,
            "completed_stages": stage_files,
            "stage_num": stage_num
        }
        save_checkpoint(checkpoint)
        
        # Print stage summary
        print(f"\n  Stage {stage_num} complete: {stage_stats['total_input_assertions']} input → {stage_stats['total_sg_units']} S+G units ({stage_stats['s_count']}S, {stage_stats['g_count']}G)")
        print(f"  Output saved to: {stage_file}")
        
        current_start = current_end
        stage_num += 1
    
    # Combine all stage files
    combine_stage_files(stage_files, OUTPUT_FILE)
    
    # Final checkpoint
    checkpoint = {
        "processed_count": total_stats["total_input_assertions"],
        "last_meeting_idx": end_meeting - 1,
        "last_assertion_idx": -1,
        "completed": True,
        "completed_stages": stage_files
    }
    save_checkpoint(checkpoint)
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "input_file": INPUT_FILE,
        "output_file": OUTPUT_FILE,
        "meetings_processed": end_meeting - start_meeting,
        "num_stages": num_stages,
        "stage_files": stage_files,
        "statistics": total_stats,
        "dry_run": dry_run
    }
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    return total_stats


def print_summary(stats: dict):
    """Print summary statistics."""
    print("\n" + "=" * 70)
    print("CONVERSION SUMMARY")
    print("=" * 70)
    print(f"Input assertions:     {stats['total_input_assertions']}")
    print(f"Output S+G units:     {stats['total_sg_units']}")
    print(f"  - S assertions:     {stats['s_count']} (for structural success rate)")
    print(f"  - G slots:          {stats['g_count']} (for grounding success rate)")
    print(f"  - Unknown:          {stats['unknown']}")
    
    print("\nBy S Dimension (structural):")
    for dim, count in sorted(stats["by_s_dimension"].items(), key=lambda x: -x[1]):
        name = DIMENSION_NAMES.get(dim, dim)
        print(f"  {dim:8s} {name:30s} {count:4d}")
    
    print("\nBy G Dimension (grounding):")
    for dim, count in sorted(stats["by_g_dimension"].items(), key=lambda x: -x[1]):
        name = DIMENSION_NAMES.get(dim, dim)
        print(f"  {dim:8s} {name:30s} {count:4d}")
    
    print("\nBy Level:")
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
    parser.add_argument("--stage-size", type=int, default=STAGE_SIZE, 
                        help=f"Meetings per stage (default: {STAGE_SIZE}). Token refreshed between stages.")
    
    args = parser.parse_args()
    
    stats = process_assertions(
        start_meeting=args.start,
        end_meeting=args.end,
        resume=args.resume,
        dry_run=args.dry_run,
        stage_size=args.stage_size
    )
    
    print_summary(stats)


if __name__ == "__main__":
    main()
