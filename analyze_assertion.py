#!/usr/bin/env python3
"""
Analyze and convert a single assertion using GPT-5 and the WBP framework.

Usage:
    python analyze_assertion.py "Your assertion text here"
    python analyze_assertion.py  # Uses default example assertion

Output:
    - GPT-5 classification (dimension, layer, level)
    - Generated assertion_id
    - Grounding assertions with parent_assertion_id linkage
"""

import sys
import json
import argparse

sys.path.insert(0, '.')
from pipeline.config import call_gpt5_api, extract_json_from_response

# =============================================================================
# S → G MAPPING (which grounding dimensions apply to each structural dimension)
# =============================================================================
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

# =============================================================================
# G RATIONALE FOR S - Why each G dimension applies to its parent S dimension
# =============================================================================
G_RATIONALE_FOR_S = {
    # S1: Meeting Details
    ("S1", "G2"): "Meeting details must reference actual attendees from the meeting context to verify participant accuracy",
    ("S1", "G3"): "Meeting details must match the actual meeting date/time to ensure schedule accuracy",
    ("S1", "G5"): "Meeting subject/agenda must align with actual topics from the meeting context",
    
    # S2: Timeline Alignment
    ("S2", "G3"): "Timeline sequencing requires verifying that scheduled dates are consistent with the actual meeting date and don't conflict",
    ("S2", "G6"): "Task ordering in the timeline must be traceable to actual action items discussed in the meeting",
    
    # S3: Ownership Assignment
    ("S3", "G2"): "Task owners must be actual attendees who can be held accountable for the work",
    ("S3", "G6"): "Ownership assignments must correspond to action items that were actually agreed upon",
    
    # S4: Deliverables & Artifacts
    ("S4", "G4"): "Referenced deliverables/documents must actually exist or be creatable from available artifacts",
    ("S4", "G5"): "Deliverables must align with topics actually discussed, not fabricated requirements",
    
    # S5: Task Dates
    ("S5", "G3"): "Task start/end dates must be consistent with the meeting date and realistic timeframes",
    
    # S6: Dependencies & Blockers
    ("S6", "G5"): "Dependencies must relate to topics actually discussed, not assumed or hallucinated blockers",
    ("S6", "G6"): "Blockers should be traceable to action items or issues raised in the discussion",
    
    # S7: Meeting Outcomes
    ("S7", "G5"): "Expected outcomes must align with actual meeting topics and agenda items",
    ("S7", "G7"): "Outcomes should preserve the context of what was actually requested or discussed",
    
    # S8: Parallel Workstreams
    ("S8", "G6"): "Parallel tasks must be traceable to distinct action items that can proceed independently",
    
    # S9: Checkpoints
    ("S9", "G3"): "Checkpoint dates must be realistic and consistent with the project timeline",
    ("S9", "G6"): "Checkpoints should align with key action items that need review",
    
    # S10: Resource Allocation
    ("S10", "G2"): "Resource assignments must reference actual attendees or known team members",
    
    # S11: Risk Mitigation
    ("S11", "G5"): "Identified risks must relate to topics actually discussed, not hypothetical concerns",
    ("S11", "G6"): "Mitigation actions must be traceable to commitments made during the meeting",
    
    # S12: Communication Plan
    ("S12", "G2"): "Communication recipients must be actual stakeholders from the attendee list",
    ("S12", "G5"): "Communication topics must align with what was actually discussed",
    
    # S13: Escalation Protocol
    ("S13", "G2"): "Escalation contacts must be actual attendees with authority to resolve issues",
    
    # S14: Feedback Integration
    ("S14", "G5"): "Feedback mechanisms must relate to actual topics that need refinement",
    ("S14", "G7"): "Feedback integration must preserve the original context and intent",
    
    # S15: Progress Tracking
    ("S15", "G6"): "Progress metrics must track actual action items that were committed to",
    
    # S16: Assumptions & Prerequisites
    ("S16", "G5"): "Listed assumptions must relate to topics actually discussed or implied",
    ("S16", "G7"): "Prerequisites should preserve context from the original discussion",
    
    # S17: Cross-team Coordination
    ("S17", "G2"): "Cross-team contacts must be actual people mentioned or implied in the meeting",
    ("S17", "G5"): "Coordination needs must relate to actual cross-team topics discussed",
    
    # S18: Post-Event Actions
    ("S18", "G2"): "Post-event action owners must be actual attendees who can execute them",
    ("S18", "G3"): "Post-event deadlines must be realistic relative to the meeting date",
    ("S18", "G6"): "Post-event actions must be traceable to decisions made during the meeting",
    
    # S19: Caveat & Clarification
    ("S19", "G5"): "Caveats must relate to actual topics discussed, not fabricated limitations",
    ("S19", "G7"): "Clarifications must preserve the original context and not distort meaning",
    ("S19", "G8"): "Clarifications must adhere to any specific user instructions about format or scope",
}

# =============================================================================
# DIMENSION SPECIFICATIONS
# =============================================================================
DIMENSION_SPEC = {
    # Structural Dimensions
    "S1": {"name": "Meeting Details", "layer": "structural", "weight": 3,
           "template": "The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES]"},
    "S2": {"name": "Timeline Alignment", "layer": "structural", "weight": 3,
           "template": "The response should include a backward timeline from T₀ with dependency-aware sequencing"},
    "S3": {"name": "Ownership Assignment", "layer": "structural", "weight": 3,
           "template": "The response should assign an owner for each [TASK] or specify role/skill placeholder"},
    "S4": {"name": "Deliverables & Artifacts", "layer": "structural", "weight": 2,
           "template": "The response should list [DELIVERABLES] with working links, version/format specified"},
    "S5": {"name": "Task Dates", "layer": "structural", "weight": 2,
           "template": "The response should specify [START_DATE] and [END_DATE] for each task"},
    "S6": {"name": "Dependencies & Blockers", "layer": "structural", "weight": 3,
           "template": "The response should identify [DEPENDENCIES/BLOCKERS] with mitigation steps documented"},
    "S7": {"name": "Meeting Outcomes", "layer": "structural", "weight": 2,
           "template": "The response should specify expected [OUTCOMES] for the meeting"},
    "S8": {"name": "Parallel Workstreams", "layer": "structural", "weight": 2,
           "template": "The response should identify [PARALLEL_TASKS] that can proceed concurrently"},
    "S9": {"name": "Checkpoints", "layer": "structural", "weight": 2,
           "template": "The response should include [CHECKPOINT_DATES] for progress review"},
    "S10": {"name": "Resource Allocation", "layer": "structural", "weight": 2,
            "template": "The response should specify [RESOURCES] required for each task"},
    "S11": {"name": "Risk Mitigation Strategy", "layer": "structural", "weight": 2,
            "template": "The response should include concrete [RISK_MITIGATION] strategies with owners"},
    "S12": {"name": "Communication Plan", "layer": "structural", "weight": 1,
            "template": "The response should specify [COMMUNICATION_CHANNELS] and [UPDATE_FREQUENCY]"},
    "S13": {"name": "Escalation Protocol", "layer": "structural", "weight": 1,
            "template": "The response should define [ESCALATION_PATH] for blockers"},
    "S14": {"name": "Feedback Integration", "layer": "structural", "weight": 1,
            "template": "The response should specify how [FEEDBACK] will be incorporated"},
    "S15": {"name": "Progress Tracking", "layer": "structural", "weight": 2,
            "template": "The response should include [TRACKING_METHOD] for progress monitoring"},
    "S16": {"name": "Assumptions & Prerequisites", "layer": "structural", "weight": 2,
            "template": "The response should list [ASSUMPTIONS] and [PREREQUISITES]"},
    "S17": {"name": "Cross-team Coordination", "layer": "structural", "weight": 2,
            "template": "The response should identify [CROSS_TEAM_DEPENDENCIES] and coordination points"},
    "S18": {"name": "Post-Event Actions", "layer": "structural", "weight": 2,
            "template": "The response should list [POST_EVENT_ACTIONS] with owners and deadlines"},
    "S19": {"name": "Caveat & Clarification", "layer": "structural", "weight": 2,
            "template": "The response should disclose [CAVEATS], [ASSUMPTIONS], and [OPEN_QUESTIONS]"},
    # Grounding Dimensions
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

# =============================================================================
# SYSTEM PROMPT
# =============================================================================
SYSTEM_PROMPT = '''You are an expert at classifying assertions according to the Mira 2.0 WBP (Workback Plan) framework.

The framework has 27 dimensions:

STRUCTURAL (S1-S19) - Verify plan structure and completeness:
- S1: Meeting Details (forward-looking, actionable)
- S2: Timeline Alignment (sequencing, buffer time, contingency)
- S3: Ownership Assignment
- S4: Deliverables & Artifacts
- S5: Task Dates (date ranges, flexibility)
- S6: Dependencies & Blockers
- S7: Meeting Outcomes
- S8: Parallel Workstreams
- S9: Checkpoints
- S10: Resource Allocation
- S11: Risk Mitigation Strategy
- S12: Communication Plan
- S13: Escalation Protocol
- S14: Feedback Integration
- S15: Progress Tracking
- S16: Assumptions & Prerequisites
- S17: Cross-team Coordination
- S18: Post-Event Actions (with owners and deadlines)
- S19: Caveat & Clarification (open questions, decision points)

GROUNDING (G1-G8) - Verify factual accuracy against source data:
- G1: Hallucination Check
- G2: Attendee Grounding
- G3: Date/Time Grounding
- G4: Artifact Grounding
- G5: Topic Grounding
- G6: Action Item Grounding
- G7: Context Preservation
- G8: Instruction Adherence

Classification guidelines:
- Choose the MOST SPECIFIC dimension that fits
- Use "critical" for must-have requirements, "expected" for should-have, "aspirational" for nice-to-have
- Structural (S) dimensions verify plan structure; Grounding (G) dimensions verify factual accuracy
'''


def analyze_assertion(assertion_text: str, context: str = None) -> dict:
    """
    Analyze an assertion using GPT-5 and return classification with S+G linkage.
    
    Args:
        assertion_text: The assertion to analyze
        context: Optional context about the meeting/response
        
    Returns:
        dict with primary assertion and generated grounding assertions
    """
    
    context_str = f"\nContext: {context}" if context else ""
    
    prompt = f'''Analyze this assertion and classify it according to the WBP framework.

Assertion: "{assertion_text}"{context_str}

Provide your analysis as JSON with these fields:
- dimension_id: The best matching dimension (e.g., "S2", "G3")
- dimension_name: Full name of the dimension
- layer: "structural" or "grounding"
- level: "critical", "expected", or "aspirational"
- rationale: Why this dimension is the best fit
- converted_text: The assertion text converted to match the dimension template style

Return ONLY valid JSON, no other text.
'''

    print("🔐 Calling GPT-5 for analysis...")
    result_text = call_gpt5_api(prompt, system_prompt=SYSTEM_PROMPT, temperature=0.2)
    
    try:
        result = extract_json_from_response(result_text)
    except:
        # Try to parse directly
        import re
        json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"error": "Failed to parse GPT-5 response", "raw": result_text}
    
    return result


def generate_sg_assertions(gpt5_result: dict, assertion_text: str, assertion_index: int = 0) -> list:
    """
    Generate the full S+G assertion set with proper linkage.
    
    Args:
        gpt5_result: Classification result from GPT-5
        assertion_text: Original assertion text
        assertion_index: Index for generating unique IDs
        
    Returns:
        List of assertions: [primary S/G assertion, generated G assertions...]
    """
    results = []
    
    dimension_id = gpt5_result.get('dimension_id', 'UNMAPPED')
    dimension_name = gpt5_result.get('dimension_name', DIMENSION_SPEC.get(dimension_id, {}).get('name', 'Unknown'))
    layer = gpt5_result.get('layer', DIMENSION_SPEC.get(dimension_id, {}).get('layer', 'unknown'))
    level = gpt5_result.get('level', 'expected')
    converted_text = gpt5_result.get('converted_text', assertion_text)
    rationale = gpt5_result.get('rationale', '')
    
    # Generate primary assertion ID
    primary_assertion_id = f"A{assertion_index:04d}_{dimension_id}"
    
    # Create primary assertion
    primary = {
        "assertion_id": primary_assertion_id,
        "parent_assertion_id": None,
        "text": converted_text,
        "original_text": assertion_text,
        "dimension_id": dimension_id,
        "dimension_name": dimension_name,
        "layer": layer,
        "level": level,
        "weight": DIMENSION_SPEC.get(dimension_id, {}).get('weight', 2),
        "rationale": {
            "mapping_reason": rationale,
            "conversion_method": "gpt5"
        },
        "quality_assessment": {
            "is_well_formed": True,
            "is_testable": True
        }
    }
    results.append(primary)
    
    # Generate grounding assertions if primary is structural
    if dimension_id.startswith("S") and dimension_id in S_TO_G_MAP:
        g_dims = S_TO_G_MAP[dimension_id]
        
        for g_idx, g_dim in enumerate(g_dims):
            g_spec = DIMENSION_SPEC.get(g_dim, {})
            if not g_spec:
                continue
            
            g_assertion_id = f"A{assertion_index:04d}_{g_dim}_{g_idx}"
            
            # Get specific rationale for why this G applies to this S
            g_rationale = G_RATIONALE_FOR_S.get(
                (dimension_id, g_dim),
                f"Generated from {dimension_id}: {g_spec.get('name', '')} grounds {dimension_name}"
            )
            
            g_assertion = {
                "assertion_id": g_assertion_id,
                "parent_assertion_id": primary_assertion_id,
                "text": g_spec.get('template', ''),
                "original_text": assertion_text,
                "dimension_id": g_dim,
                "dimension_name": g_spec.get('name', 'Unknown'),
                "layer": "grounding",
                "level": "critical",
                "weight": g_spec.get('weight', 3),
                "rationale": {
                    "mapping_reason": g_rationale,
                    "parent_dimension": dimension_id,
                    "parent_dimension_name": dimension_name,
                    "conversion_method": "s_to_g_mapping"
                },
                "quality_assessment": {
                    "is_well_formed": True,
                    "is_testable": True
                }
            }
            results.append(g_assertion)
    
    return results


def print_results(assertions: list):
    """Pretty print the assertion results."""
    print("\n" + "=" * 70)
    print("CONVERSION RESULTS")
    print("=" * 70)
    
    for i, a in enumerate(assertions):
        is_primary = a.get('parent_assertion_id') is None
        prefix = "📌" if is_primary else "  └─"
        dim = a.get('dimension_id', 'UNMAPPED')
        layer = a.get('layer', 'unknown')
        level = a.get('level', 'unknown')
        
        print(f"\n{prefix} [{a.get('assertion_id')}] {dim} ({layer}/{level})")
        print(f"   {a.get('dimension_name')}")
        print(f"   Text: {a.get('text', '')[:80]}...")
        
        if is_primary:
            rationale = a.get('rationale', {}).get('mapping_reason', '')
            if rationale:
                print(f"   Rationale: {rationale[:80]}...")
    
    print("\n" + "-" * 70)
    s_count = sum(1 for a in assertions if a.get('dimension_id', '').startswith('S'))
    g_count = sum(1 for a in assertions if a.get('dimension_id', '').startswith('G'))
    print(f"Total: {len(assertions)} assertions ({s_count} S + {g_count} G)")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and convert a single assertion using GPT-5 and WBP framework"
    )
    parser.add_argument(
        "assertion",
        nargs="?",
        default="The response arranges the draft slides task before review slides task in the plan",
        help="The assertion text to analyze"
    )
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="Optional context about the meeting/response"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text"
    )
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Assertion index for ID generation (default: 0)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("WBP Assertion Analyzer (GPT-5)")
    print("=" * 70)
    print(f"Input: \"{args.assertion}\"")
    if args.context:
        print(f"Context: {args.context}")
    print()
    
    # Step 1: GPT-5 classification
    gpt5_result = analyze_assertion(args.assertion, args.context)
    
    if "error" in gpt5_result:
        print(f"❌ Error: {gpt5_result.get('error')}")
        print(f"Raw response: {gpt5_result.get('raw', 'N/A')}")
        return 1
    
    print(f"\n✅ GPT-5 Classification:")
    print(f"   Dimension: {gpt5_result.get('dimension_id')} - {gpt5_result.get('dimension_name')}")
    print(f"   Layer: {gpt5_result.get('layer')}")
    print(f"   Level: {gpt5_result.get('level')}")
    
    # Step 2: Generate S+G assertions with linkage
    assertions = generate_sg_assertions(gpt5_result, args.assertion, args.index)
    
    # Step 3: Output results
    if args.json:
        print(json.dumps(assertions, indent=2, ensure_ascii=False))
    else:
        print_results(assertions)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
