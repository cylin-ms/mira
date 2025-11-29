#!/usr/bin/env python3
"""
Post-process existing GPT-5 conversion results to add:
1. assertion_id for each assertion
2. parent_assertion_id for S+G linkage
3. Generate grounding (G) assertions from structural (S) assertions

This avoids re-running expensive GPT-5 API calls.
"""

import json
import sys
from datetime import datetime

# S → G mapping (which grounding dimensions apply to each structural dimension)
S_TO_G_MAP = {
    "S1": ["G2", "G3", "G5"],      # Meeting Details → Attendee, Date/Time, Topic
    "S2": ["G3", "G6"],             # Timeline → Date/Time, Action Items
    "S3": ["G2", "G6"],             # Ownership → Attendee, Action Items
    "S4": ["G4", "G5"],             # Deliverables → Artifact, Topic
    "S5": ["G3"],                   # Task Dates → Date/Time
    "S6": ["G5", "G6"],             # Dependencies → Topic, Action Items
    "S7": ["G5", "G7"],             # Meeting Outcomes → Topic, Context
    "S8": ["G6"],                   # Parallel Workstreams → Action Items
    "S9": ["G3", "G6"],             # Checkpoints → Date/Time, Action Items
    "S10": ["G2"],                  # Resource Allocation → Attendee
    "S11": ["G5", "G6"],            # Risk Mitigation → Topic, Action Items
    "S12": ["G2", "G5"],            # Communication Plan → Attendee, Topic
    "S13": ["G2"],                  # Escalation Protocol → Attendee
    "S14": ["G5", "G7"],            # Feedback Integration → Topic, Context
    "S15": ["G6"],                  # Progress Tracking → Action Items
    "S16": ["G5", "G7"],            # Assumptions → Topic, Context
    "S17": ["G2", "G5"],            # Cross-team Coordination → Attendee, Topic
    "S18": ["G2", "G3", "G6"],      # Post-Event Actions → Attendee, Date/Time, Action Items
    "S19": ["G5", "G7", "G8"],      # Caveat & Clarification → Topic, Context, Instruction
}

# Dimension specs for grounding assertions
DIMENSION_SPEC = {
    "G1": {"name": "Hallucination Check", "layer": "grounding", "weight": 3,
           "template": "All facts in the response should be verifiable from [GROUNDING_SOURCES]"},
    "G2": {"name": "Attendee Grounding", "layer": "grounding", "weight": 3,
           "template": "Names mentioned should match [ATTENDEES] from meeting context"},
    "G3": {"name": "Date/Time Grounding", "layer": "grounding", "weight": 3,
           "template": "Dates and times should be consistent with [MEETING_DATE] and [CURRENT_TIME]"},
    "G4": {"name": "Artifact Grounding", "layer": "grounding", "weight": 3,
           "template": "Referenced documents should exist in [AVAILABLE_ARTIFACTS]"},
    "G5": {"name": "Topic Grounding", "layer": "grounding", "weight": 2,
           "template": "Topics discussed should align with [MEETING_AGENDA] or [EMAIL_CONTEXT]"},
    "G6": {"name": "Action Item Grounding", "layer": "grounding", "weight": 3,
           "template": "Action items should be traceable to [DISCUSSION_POINTS] or [PRIOR_COMMITMENTS]"},
    "G7": {"name": "Context Preservation", "layer": "grounding", "weight": 2,
           "template": "Response should preserve key context from [USER_QUERY] and [CONVERSATION_HISTORY]"},
    "G8": {"name": "Instruction Adherence", "layer": "grounding", "weight": 3,
           "template": "Response should follow [USER_INSTRUCTIONS] and [SPECIFIED_CONSTRAINTS]"},
}


def generate_grounding_assertions(primary_assertion: dict, assertion_index: int) -> list:
    """Generate grounding assertions for a structural assertion."""
    results = []
    
    # Check both 'dimension_id' and 'dimension' field names
    dimension_id = primary_assertion.get('dimension_id') or primary_assertion.get('dimension', 'UNMAPPED')
    primary_assertion_id = primary_assertion.get('assertion_id', f"A{assertion_index:04d}_{dimension_id}")
    original_text = primary_assertion.get('original_text') or primary_assertion.get('text', '')
    
    # Only generate G assertions for S dimensions
    if not dimension_id.startswith("S") or dimension_id not in S_TO_G_MAP:
        return results
    
    g_dims = S_TO_G_MAP[dimension_id]
    
    for g_idx, g_dim in enumerate(g_dims):
        g_spec = DIMENSION_SPEC.get(g_dim, {})
        if not g_spec:
            continue
        
        g_assertion_id = f"A{assertion_index:04d}_{g_dim}_{g_idx}"
        
        g_assertion = {
            "assertion_id": g_assertion_id,
            "parent_assertion_id": primary_assertion_id,
            "original_text": original_text,
            "converted_text": g_spec.get('template', ''),
            "dimension_id": g_dim,
            "dimension_name": g_spec.get('name', 'Unknown'),
            "layer": "grounding",
            "level": "critical",
            "weight": g_spec.get('weight', 3),
            "sourceID": primary_assertion.get('sourceID'),
            "placeholders_used": [],
            "rationale": {
                "mapping_reason": f"Generated from GPT-5 classified {dimension_id} via S_TO_G_MAP",
                "conversion_changes": ["Applied grounding template for factual verification"],
                "template_alignment": f"S→G mapping: {dimension_id}→{g_dim}",
                "value_removed": "N/A (grounding complement)",
                "parent_dimension": dimension_id,
                "parent_dimension_name": primary_assertion.get('dimension_name', 'Unknown')
            },
            "quality_assessment": {
                "is_well_formed": True,
                "is_testable": True,
                "issues": []
            },
            "conversion_method": "postprocess_s_to_g",
            "derived_from": dimension_id
        }
        results.append(g_assertion)
    
    return results


def postprocess_meeting(meeting: dict, meeting_index: int) -> dict:
    """Post-process a single meeting's assertions."""
    assertions = meeting.get('assertions', [])
    enhanced_assertions = []
    
    for idx, assertion in enumerate(assertions):
        # Get or generate dimension_id (check both field names)
        dimension_id = assertion.get('dimension_id') or assertion.get('dimension', 'UNMAPPED')
        
        # Normalize to dimension_id field
        if 'dimension_id' not in assertion and 'dimension' in assertion:
            assertion['dimension_id'] = assertion['dimension']
        
        # Add assertion_id if missing
        if not assertion.get('assertion_id'):
            assertion['assertion_id'] = f"A{idx:04d}_{dimension_id}"
        
        # Add parent_assertion_id if missing (primary assertions have None)
        if 'parent_assertion_id' not in assertion:
            assertion['parent_assertion_id'] = None
        
        # Add the primary assertion
        enhanced_assertions.append(assertion)
        
        # Generate and add grounding assertions
        g_assertions = generate_grounding_assertions(assertion, idx)
        enhanced_assertions.extend(g_assertions)
    
    meeting['assertions'] = enhanced_assertions
    return meeting


def main():
    input_file = "docs/ChinYew/assertions_converted_gpt5_combined.jsonl"  # Combined 218 + 6 = 224 meetings
    output_file = "docs/ChinYew/assertions_converted_gpt5_enhanced.jsonl"
    
    print("=" * 70)
    print("Post-process GPT-5 Results: Add assertion_id and S+G linkage")
    print("=" * 70)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()
    
    # Load existing results
    meetings = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            meetings.append(json.loads(line))
    
    print(f"Loaded {len(meetings)} meetings")
    
    # Process each meeting
    total_s = 0
    total_g = 0
    
    for i, meeting in enumerate(meetings):
        original_count = len(meeting.get('assertions', []))
        meeting = postprocess_meeting(meeting, i)
        new_count = len(meeting.get('assertions', []))
        
        # Count S and G
        for a in meeting.get('assertions', []):
            dim = a.get('dimension_id', '')
            if dim.startswith('S'):
                total_s += 1
            elif dim.startswith('G'):
                total_g += 1
        
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(meetings)} meetings...")
    
    # Save enhanced results
    with open(output_file, 'w', encoding='utf-8') as f:
        for meeting in meetings:
            f.write(json.dumps(meeting, ensure_ascii=False) + "\n")
    
    print()
    print("=" * 70)
    print("POST-PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Total meetings: {len(meetings)}")
    print(f"Structural (S) assertions: {total_s}")
    print(f"Grounding (G) assertions: {total_g}")
    print(f"Total assertions: {total_s + total_g}")
    print(f"S+G ratio: 1:{total_g/total_s:.1f}" if total_s > 0 else "")
    print(f"Output saved to: {output_file}")


if __name__ == "__main__":
    main()
