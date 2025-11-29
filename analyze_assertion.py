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
import os
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
# SUCCESS EXAMPLES - What a successful evaluation looks like for each dimension
# =============================================================================
SUCCESS_EXAMPLES = {
    # Structural Dimensions
    "S1": "Plan includes 'Q4 Planning Review, Dec 5 2025 2pm PST, with Alice, Bob, Carol'",
    "S2": "Draft slides (Dec 1) → Review slides (Dec 3) → Final presentation (Dec 5)",
    "S3": "Each task shows owner: 'Alice: Draft slides', 'Bob: Review budget'",
    "S4": "Links to shared docs: 'Budget v2.xlsx', 'Slides_Draft.pptx'",
    "S5": "Task shows date range: 'Dec 1-3: Draft slides', 'Dec 4-5: Review'",
    "S6": "'Blocked by: Legal approval needed' with mitigation: 'Escalate to VP if not received by Dec 2'",
    "S7": "Expected outcome: 'Finalize Q4 budget allocation decisions'",
    "S8": "'While Alice drafts slides, Bob can prepare budget analysis in parallel'",
    "S9": "Checkpoint: 'Dec 3: Review draft progress with team'",
    "S10": "'Requires 2 engineers + 1 designer for UI work'",
    "S11": "'Risk: Vendor delay possible. Mitigation: Identify backup vendor by Dec 2'",
    "S12": "'Daily standup on Teams, weekly email summary to stakeholders'",
    "S13": "'If blocked >24hrs, escalate to Alice (PM), then to VP Bob'",
    "S14": "'Collect feedback in shared doc, review in Wed standup'",
    "S15": "'Track via Jira board, update status daily'",
    "S16": "'Assumes: Budget approved by Dec 1, Team at full capacity'",
    "S17": "'Sync with Marketing team on messaging by Dec 3'",
    "S18": "'Post-meeting: Alice sends summary within 24hrs, Bob files ticket by EOD'",
    "S19": "'Note: Timeline assumes no holiday delays; dates may shift if approvals delayed'",
    
    # Grounding Dimensions
    "G1": "All facts verified against meeting transcript/email thread",
    "G2": "'Alice' appears in attendee list: [Alice@company.com, Bob@company.com]",
    "G3": "'Dec 5' is after meeting date 'Nov 29' and within reasonable timeframe",
    "G4": "'Budget_v2.xlsx' exists in shared drive linked in meeting notes",
    "G5": "'Q4 budget' topic matches agenda item #2 from meeting invite",
    "G6": "'Draft slides' action traceable to discussion point at 14:23 in transcript",
    "G7": "Response preserves user's request: 'focus on high-priority items only'",
    "G8": "Output follows user instruction: 'use bullet points, max 5 items'",
}

# Success examples for specific S→G combinations (more contextual)
G_SUCCESS_FOR_S = {
    ("S2", "G3"): "'Dec 1 → Dec 3 → Dec 5' sequence is valid relative to meeting date Nov 29",
    ("S2", "G6"): "'Draft slides before review' matches action items from meeting discussion",
    ("S3", "G2"): "Owner 'Alice' is in attendee list [Alice, Bob, Carol]",
    ("S3", "G6"): "'Alice owns draft slides' matches her commitment in meeting",
    ("S1", "G2"): "Listed attendees [Alice, Bob] match actual meeting participants",
    ("S1", "G3"): "Meeting date 'Dec 5' matches calendar invite",
    ("S1", "G5"): "Subject 'Q4 Planning' matches meeting agenda",
    ("S4", "G4"): "'Budget_v2.xlsx' link resolves to actual document",
    ("S4", "G5"): "'Budget deliverable' relates to budget discussion topic",
    ("S5", "G3"): "Task dates 'Dec 1-3' are realistic given meeting on Nov 29",
    ("S6", "G5"): "'Legal approval blocker' was discussed in meeting",
    ("S6", "G6"): "'Escalate to VP' action was agreed upon as mitigation",
    ("S7", "G5"): "'Finalize budget' outcome aligns with agenda item",
    ("S7", "G7"): "Outcome preserves context: user wanted 'actionable decisions'",
    ("S8", "G6"): "Parallel tasks 'slides + budget' are distinct action items",
    ("S9", "G3"): "Checkpoint 'Dec 3' is realistic midpoint in timeline",
    ("S9", "G6"): "Checkpoint covers key action item 'draft review'",
    ("S10", "G2"): "Resource 'Alice (engineer)' is known team member",
    ("S11", "G5"): "'Vendor delay risk' was mentioned in discussion",
    ("S11", "G6"): "'Backup vendor' mitigation was agreed action",
    ("S12", "G2"): "Communication to 'stakeholders' matches attendee roles",
    ("S12", "G5"): "'Weekly summary' relates to discussed coordination needs",
    ("S13", "G2"): "Escalation contact 'VP Bob' is actual executive attendee",
    ("S14", "G5"): "'Feedback on draft' relates to draft review topic",
    ("S14", "G7"): "Feedback process preserves iterative intent from discussion",
    ("S15", "G6"): "'Jira tracking' for action items discussed",
    ("S16", "G5"): "'Budget approved' assumption relates to budget topic",
    ("S16", "G7"): "Prerequisites preserve context from planning discussion",
    ("S17", "G2"): "'Marketing team' mentioned as cross-team dependency",
    ("S17", "G5"): "'Messaging sync' relates to launch coordination topic",
    ("S18", "G2"): "'Alice sends summary' - Alice is actual attendee",
    ("S18", "G3"): "'Within 24hrs' deadline is realistic post-meeting",
    ("S18", "G6"): "'File ticket' action was agreed in meeting",
    ("S19", "G5"): "'Holiday delays' caveat relates to timeline discussion",
    ("S19", "G7"): "Caveat preserves uncertainty expressed in meeting",
    ("S19", "G8"): "Clarification follows user's 'be explicit about risks' instruction",
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

# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO GENERATION - Create context where the assertion makes sense
# ═══════════════════════════════════════════════════════════════════════════════

SCENARIO_GENERATION_PROMPT = '''You are generating a realistic meeting SCENARIO that provides context for an assertion to be meaningful.

## ASSERTION TO CONTEXTUALIZE
"{assertion_text}"

## TASK
Generate a realistic meeting scenario where this assertion would naturally apply.
The scenario should provide **ground truth** for grounding verification.

## REQUIREMENTS
1. Create a meeting that naturally involves the topics/tasks mentioned in the assertion
2. Include realistic attendees, dates, and artifacts
3. Include discussion points that justify the action items in the assertion
4. All details must be consistent and realistic

Return JSON with:
{{
  "scenario": {{
    "title": "Meeting title",
    "date": "Meeting date (e.g., 2025-12-05)",
    "time": "Meeting time (e.g., 2:00 PM PST)",
    "duration_minutes": 60,
    "organizer": "Name of organizer",
    "attendees": ["List of attendee names - these are the ONLY valid people"],
    "context": "Background context for the meeting (2-3 sentences)",
    "artifacts": ["List of available files/documents"],
    "discussion_points": ["Key topics discussed that relate to the assertion"],
    "action_items_discussed": ["Specific action items mentioned in the meeting"]
  }}
}}

IMPORTANT: The scenario must provide ground truth that makes the assertion verifiable.
For example, if the assertion mentions "draft slides before review slides", the discussion_points
should include something like "Team agreed to draft slides first, then schedule review".

Return ONLY valid JSON.
'''

# ═══════════════════════════════════════════════════════════════════════════════
# WBP GENERATION - Generate WBP conditioned on scenario + assertions
# ═══════════════════════════════════════════════════════════════════════════════

WBP_GENERATION_PROMPT = '''You are generating a Workback Plan (WBP) based on a meeting scenario.

## MEETING SCENARIO (Ground Truth)
```json
{scenario_json}
```

## ORIGINAL USER INPUT
"{original_utterance}"

## ASSERTIONS TO SATISFY
### Structural Assertion (S)
- {s_dimension_id} ({s_dimension_name}): {s_assertion_text}
- Reason: {s_mapping_reason}

### Grounding Assertions (G)
{g_assertions_text}

## TASK
Generate a Workback Plan that:
1. Is based on the meeting scenario above (use the exact attendees, dates, artifacts)
2. Addresses the original user input
3. Satisfies the structural assertion (correct structure/presence)
4. Satisfies ALL grounding assertions (factually accurate against the scenario)

## GROUNDING REQUIREMENTS
- ONLY use names from the attendees list: {attendees}
- ONLY reference dates consistent with meeting date: {meeting_date}
- ONLY reference artifacts from: {artifacts}
- Action items must trace to discussion_points: {discussion_points}

Return JSON with:
{{
  "workback_plan": "The complete workback plan in markdown format"
}}

Return ONLY valid JSON.
'''

WBP_VERIFICATION_PROMPT = '''You are verifying a Workback Plan against a scenario and assertions.

## MEETING SCENARIO (Ground Truth)
```json
{scenario_json}
```

## ASSERTIONS TO VERIFY
{assertions_to_verify}

## WORKBACK PLAN
```
{wbp_content}
```

## TASK
For EACH assertion, verify if the WBP passes using the scenario as ground truth.

For GROUNDING assertions, check:
- G2 (Attendee): Are all names in the WBP from the scenario's attendees list?
- G3 (Date/Time): Are all dates consistent with the scenario's meeting date?
- G4 (Artifact): Are all referenced files from the scenario's artifacts list?
- G5 (Topic): Are topics aligned with the scenario's discussion_points?
- G6 (Action Item): Are action items traceable to the scenario's action_items_discussed?

Return JSON with:
{{
  "overall_passes": true/false,
  "assertion_results": [
    {{
      "assertion_id": "ID",
      "dimension": "S2 or G3 etc",
      "passes": true/false,
      "evidence": "Specific evidence from WBP",
      "ground_truth_check": "What scenario element was checked",
      "reasoning": "Why it passes or fails"
    }}
  ]
}}

Return ONLY valid JSON.
'''


def generate_scenario_for_assertion(assertion_text: str) -> dict:
    """
    Generate a meeting scenario that provides context for the assertion.
    
    Args:
        assertion_text: The original assertion/utterance
        
    Returns:
        dict with scenario details (attendees, date, artifacts, etc.)
    """
    prompt = SCENARIO_GENERATION_PROMPT.format(assertion_text=assertion_text)
    
    result_text = call_gpt5_api(
        prompt,
        system_prompt="You generate realistic meeting scenarios for assertion testing.",
        temperature=0.5
    )
    
    try:
        result = extract_json_from_response(result_text)
        return result.get("scenario", {})
    except:
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return result.get("scenario", result)
            except:
                pass
        return {
            "title": "Default Meeting",
            "date": "2025-12-05",
            "time": "2:00 PM PST",
            "attendees": ["Alice", "Bob", "Carol"],
            "artifacts": [],
            "discussion_points": [],
            "action_items_discussed": []
        }


def generate_wbp_with_scenario(scenario: dict, original_utterance: str, 
                                s_assertion: dict, g_assertions: list) -> dict:
    """
    Generate a WBP conditioned on the scenario and assertions.
    
    Args:
        scenario: The meeting scenario (ground truth)
        original_utterance: The original user input
        s_assertion: The structural assertion
        g_assertions: List of grounding assertions
        
    Returns:
        dict with workback_plan content
    """
    # Build G assertions text
    if g_assertions:
        g_text_parts = []
        for i, g in enumerate(g_assertions):
            g_text_parts.append(f"{i+1}. {g['dimension_id']} ({g['dimension_name']}): {g['text']}")
            g_text_parts.append(f"   Why: {g['rationale']['mapping_reason']}")
        g_assertions_text = "\n".join(g_text_parts)
    else:
        g_assertions_text = "(No grounding assertions)"
    
    prompt = WBP_GENERATION_PROMPT.format(
        scenario_json=json.dumps(scenario, indent=2),
        original_utterance=original_utterance,
        s_dimension_id=s_assertion.get('dimension_id', ''),
        s_dimension_name=s_assertion.get('dimension_name', ''),
        s_assertion_text=s_assertion.get('text', ''),
        s_mapping_reason=s_assertion.get('rationale', {}).get('mapping_reason', ''),
        g_assertions_text=g_assertions_text,
        attendees=scenario.get('attendees', []),
        meeting_date=scenario.get('date', ''),
        artifacts=scenario.get('artifacts', []),
        discussion_points=scenario.get('discussion_points', [])
    )
    
    result_text = call_gpt5_api(
        prompt,
        system_prompt="You generate workback plans based on meeting scenarios.",
        temperature=0.4
    )
    
    try:
        result = extract_json_from_response(result_text)
        return result.get("workback_plan", result_text)
    except:
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return result.get("workback_plan", "")
            except:
                pass
        return "Unable to generate WBP"


def verify_wbp_against_scenario(scenario: dict, wbp_content: str, 
                                 all_assertions: list) -> dict:
    """
    Verify the WBP against the scenario (ground truth) for all assertions.
    
    Args:
        scenario: The meeting scenario (ground truth)
        wbp_content: The generated workback plan
        all_assertions: List of all assertions (S + G)
        
    Returns:
        dict with verification results for each assertion
    """
    assertions_to_verify = "\n".join([
        f"- [{a['assertion_id']}] {a['dimension_id']} ({a['layer']}): {a['text']}"
        for a in all_assertions
    ])
    
    prompt = WBP_VERIFICATION_PROMPT.format(
        scenario_json=json.dumps(scenario, indent=2),
        assertions_to_verify=assertions_to_verify,
        wbp_content=wbp_content
    )
    
    result_text = call_gpt5_api(
        prompt,
        system_prompt="You verify workback plans against scenarios and assertions.",
        temperature=0.2
    )
    
    try:
        result = extract_json_from_response(result_text)
        return result
    except:
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        return {"overall_passes": False, "assertion_results": []}


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


def generate_sg_assertions(gpt5_result: dict, assertion_text: str, assertion_index: int = 0, generate_examples: bool = True) -> list:
    """
    Generate the full S+G assertion set with proper linkage.
    Generates ONE mock WBP that satisfies both S and all related G assertions together.
    
    Args:
        gpt5_result: Classification result from GPT-5
        assertion_text: Original assertion text (user input)
        assertion_index: Index for generating unique IDs
        generate_examples: Whether to generate mock WBP via GPT-5
        
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
    
    # Create primary assertion (without success_example yet)
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
    
    # Build grounding assertions list (for S dimensions only)
    g_assertions = []
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
            g_assertions.append(g_assertion)
    
    # Generate scenario + WBP that satisfies S + all G assertions together
    if generate_examples and dimension_id.startswith("S"):
        # Step 1: Generate scenario (ground truth context)
        print(f"   🎭 Generating scenario for assertion context...")
        scenario = generate_scenario_for_assertion(assertion_text)
        
        # Step 2: Generate WBP conditioned on scenario
        print(f"   🔄 Generating WBP for {dimension_id} + {len(g_assertions)} grounding assertions...")
        wbp_content = generate_wbp_with_scenario(
            scenario=scenario,
            original_utterance=assertion_text,
            s_assertion=primary,
            g_assertions=g_assertions
        )
        
        # Step 3: Verify WBP against scenario for all assertions
        print(f"   ✅ Verifying WBP against scenario...")
        all_assertions = [primary] + g_assertions
        verification = verify_wbp_against_scenario(
            scenario=scenario,
            wbp_content=wbp_content,
            all_assertions=all_assertions
        )
        
        # Create shared success_example for all assertions
        shared_success_example = {
            "scenario": scenario,
            "workback_plan": wbp_content,
            "overall_verified": verification.get("overall_passes", False),
            "assertion_results": verification.get("assertion_results", [])
        }
        
        # Add success_example to primary assertion
        primary["success_example"] = shared_success_example
        
        # Find verification result for each G assertion and add to it
        assertion_results_map = {
            r.get("assertion_id"): r 
            for r in verification.get("assertion_results", [])
        }
        
        for g_assertion in g_assertions:
            g_id = g_assertion["assertion_id"]
            g_verification = assertion_results_map.get(g_id, {})
            g_assertion["success_example"] = {
                "scenario": scenario,  # Same scenario (ground truth)
                "workback_plan": wbp_content,  # Same WBP
                "evidence": g_verification.get("evidence", ""),
                "ground_truth_check": g_verification.get("ground_truth_check", ""),
                "verification": g_verification.get("reasoning", ""),
                "verified": g_verification.get("passes", False)
            }
    elif generate_examples and dimension_id.startswith("G"):
        # For standalone G assertions (not derived from S)
        print(f"   🎭 Generating scenario for standalone {dimension_id}...")
        scenario = generate_scenario_for_assertion(assertion_text)
        
        print(f"   🔄 Generating WBP for standalone {dimension_id}...")
        wbp_content = generate_wbp_with_scenario(
            scenario=scenario,
            original_utterance=assertion_text,
            s_assertion=primary,
            g_assertions=[]
        )
        
        print(f"   ✅ Verifying WBP against scenario...")
        verification = verify_wbp_against_scenario(
            scenario=scenario,
            wbp_content=wbp_content,
            all_assertions=[primary]
        )
        
        primary["success_example"] = {
            "scenario": scenario,
            "workback_plan": wbp_content,
            "overall_verified": verification.get("overall_passes", False),
            "assertion_results": verification.get("assertion_results", [])
        }
    else:
        primary["success_example"] = {
            "scenario": {}, "workback_plan": "", "overall_verified": False, "assertion_results": []
        }
        for g_assertion in g_assertions:
            g_assertion["success_example"] = {
                "scenario": {}, "workback_plan": "", "evidence": "", "ground_truth_check": "", "verification": "", "verified": False
            }
    
    # Build final results list
    results.append(primary)
    results.extend(g_assertions)
    
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


def generate_final_report(assertions: list, original_utterance: str, output_dir: str = None) -> dict:
    """
    Generate a final report with summary table and JSON file.
    
    Returns a dict with:
    - summary_table: formatted table string
    - json_file_path: path to saved JSON file
    - report: full report dict
    """
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, f"assertion_analysis_{timestamp}.json")
    else:
        json_path = f"assertion_analysis_{timestamp}.json"
    
    # Build the full report
    s_assertions = [a for a in assertions if a.get('dimension_id', '').startswith('S')]
    g_assertions = [a for a in assertions if a.get('dimension_id', '').startswith('G')]
    
    # Get scenario and WBP from the first assertion's success_example
    scenario = None
    wbp = None
    verification_results = []
    
    if assertions and 'success_example' in assertions[0]:
        example = assertions[0]['success_example']
        scenario = example.get('scenario')
        wbp = example.get('workback_plan')
        verification_results = example.get('assertion_results', [])
    
    report = {
        "metadata": {
            "timestamp": datetime.datetime.now().isoformat(),
            "original_utterance": original_utterance,
            "total_assertions": len(assertions),
            "structural_count": len(s_assertions),
            "grounding_count": len(g_assertions)
        },
        "scenario": scenario,
        "workback_plan": wbp,
        "assertions": assertions,
        "verification_summary": {
            "total_verified": sum(1 for v in verification_results if v.get('passes')),
            "total_failed": sum(1 for v in verification_results if not v.get('passes')),
            "all_passed": all(v.get('passes', False) for v in verification_results) if verification_results else False,
            "results": verification_results
        }
    }
    
    # Save JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Build summary table
    table_lines = []
    table_lines.append("")
    table_lines.append("=" * 120)
    table_lines.append("ASSERTION ANALYSIS REPORT")
    table_lines.append("=" * 120)
    table_lines.append(f"Timestamp: {report['metadata']['timestamp']}")
    table_lines.append(f"Input: \"{original_utterance}\"")
    table_lines.append("")
    
    # Scenario summary
    if scenario:
        table_lines.append("-" * 120)
        table_lines.append("SCENARIO CONTEXT (Ground Truth)")
        table_lines.append("-" * 120)
        table_lines.append(f"  Meeting: {scenario.get('title', 'N/A')}")
        table_lines.append(f"  Date: {scenario.get('date', 'N/A')} at {scenario.get('time', 'N/A')}")
        table_lines.append(f"  Organizer: {scenario.get('organizer', 'N/A')}")
        table_lines.append(f"  Attendees: {', '.join(scenario.get('attendees', []))}")
        if scenario.get('artifacts'):
            table_lines.append(f"  Artifacts: {', '.join(scenario.get('artifacts', []))}")
        table_lines.append("")
    
    # Assertions table
    table_lines.append("-" * 120)
    table_lines.append("ASSERTIONS SUMMARY TABLE")
    table_lines.append("-" * 120)
    
    # Header
    header = f"{'ID':<15} {'Dim':<5} {'Layer':<12} {'Level':<10} {'Verified':<10} {'Mapping Reason':<50}"
    table_lines.append(header)
    table_lines.append("-" * 120)
    
    # Rows
    for a in assertions:
        aid = a.get('assertion_id', 'N/A')
        dim = a.get('dimension_id', 'N/A')
        layer = a.get('layer', 'N/A')
        level = a.get('level', 'N/A')
        
        # Find verification status
        verified = "N/A"
        for v in verification_results:
            if v.get('assertion_id') == aid:
                verified = "✅ PASS" if v.get('passes') else "❌ FAIL"
                break
        
        # Get mapping reason (truncated)
        reason = a.get('rationale', {}).get('mapping_reason', '')[:48]
        if len(a.get('rationale', {}).get('mapping_reason', '')) > 48:
            reason += ".."
        
        row = f"{aid:<15} {dim:<5} {layer:<12} {level:<10} {verified:<10} {reason:<50}"
        table_lines.append(row)
    
    table_lines.append("-" * 120)
    
    # Verification summary
    table_lines.append("")
    table_lines.append("VERIFICATION SUMMARY")
    table_lines.append("-" * 120)
    vs = report['verification_summary']
    status = "✅ ALL PASSED" if vs['all_passed'] else f"⚠️ {vs['total_failed']} FAILED"
    table_lines.append(f"  Status: {status}")
    table_lines.append(f"  Passed: {vs['total_verified']} / {vs['total_verified'] + vs['total_failed']}")
    table_lines.append("")
    
    # Evidence details
    if verification_results:
        table_lines.append("VERIFICATION DETAILS")
        table_lines.append("-" * 120)
        for v in verification_results:
            status_icon = "✅" if v.get('passes') else "❌"
            table_lines.append(f"  {status_icon} [{v.get('assertion_id')}] {v.get('dimension')}")
            table_lines.append(f"     Evidence: {v.get('evidence', 'N/A')[:100]}...")
            table_lines.append(f"     Ground Truth: {v.get('ground_truth_check', 'N/A')[:100]}")
            table_lines.append("")
    
    # File output
    table_lines.append("=" * 120)
    table_lines.append(f"📄 JSON Report saved to: {json_path}")
    table_lines.append("=" * 120)
    
    summary_table = "\n".join(table_lines)
    
    return {
        "summary_table": summary_table,
        "json_file_path": json_path,
        "report": report
    }


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
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save the JSON report (default: current directory)"
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip final report generation"
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
    elif not args.no_report:
        # Generate final report
        report_result = generate_final_report(assertions, args.assertion, args.output_dir)
        print(report_result['summary_table'])
    else:
        print_results(assertions)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
