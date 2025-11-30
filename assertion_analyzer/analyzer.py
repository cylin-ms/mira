"""
Main analyzer module for WBP assertion analysis.

This module provides:
- GPT-5 based assertion classification
- Scenario generation for ground truth
- Workback Plan generation with S+G linkage
- WBP verification against scenario
"""

import os
import re
import json
import datetime
from typing import Dict, List, Optional, Any

from .config import call_gpt5_api, extract_json_from_response, save_json
from .dimensions import (
    S_TO_G_MAP, 
    G_RATIONALE_FOR_S, 
    DIMENSION_NAMES,
    STRUCTURAL_DIMENSIONS,
    GROUNDING_DIMENSIONS,
    get_dimension_name,
    get_rationale,
)

# ═══════════════════════════════════════════════════════════════════════════════
# LOAD PROMPTS FROM EXTERNAL FILE
# ═══════════════════════════════════════════════════════════════════════════════

PROMPTS_FILE = os.path.join(os.path.dirname(__file__), "prompts.json")

def _load_prompts() -> Dict[str, str]:
    """Load prompts from prompts.json file."""
    try:
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {PROMPTS_FILE} not found, using built-in prompts")
        return {}
    except json.JSONDecodeError as e:
        print(f"Warning: Error parsing {PROMPTS_FILE}: {e}")
        return {}

# Load prompts at module import time
_PROMPTS = _load_prompts()

def get_prompt(key: str, fallback: str = "") -> str:
    """Get a prompt from the loaded PROMPTS dict with fallback."""
    return _PROMPTS.get(key, fallback)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION SPECIFICATIONS (Templates for assertions)
# ═══════════════════════════════════════════════════════════════════════════════

DIMENSION_SPEC = {
    # Structural Dimensions
    "S1": {"name": "Meeting Details", "layer": "structural", "weight": 3,
           "template": "The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES]"},
    "S2": {"name": "Timeline Alignment", "layer": "structural", "weight": 3,
           "template": "The response should include a backward timeline from T0 with dependency-aware sequencing"},
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
    "G9": {"name": "Planner-Generated Consistency", "layer": "grounding", "weight": 3,
           "template": "Planner-generated content ([ASSUMPTION], [BLOCKER], [MITIGATION], [OPEN_QUESTION]) should not contradict [SCENARIO_FACTS]"},
    "G10": {"name": "Relation Grounding", "layer": "grounding", "weight": 3,
            "template": "Relations (DEPENDS_ON, OWNS, BLOCKS, PRODUCES, REQUIRES_INPUT) should be grounded in [SCENARIO_STATED_DEPENDENCIES]"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT PROMPTS (fallback if prompts.json missing)
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_SYSTEM_PROMPT = '''You are an expert at classifying assertions according to the Mira 2.0 WBP (Workback Plan) framework.

The framework has 30 dimensions:

STRUCTURAL (S1-S20) - Verify plan structure and completeness:
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

GROUNDING (G1-G10) - Verify factual accuracy against source data:
- G1: Hallucination Check
- G2: Attendee Grounding
- G3: Date/Time Grounding
- G4: Artifact Grounding
- G5: Topic Grounding
- G6: Action Item Grounding
- G7: Context Preservation
- G8: Instruction Adherence
- G9: Planner-Generated Consistency
- G10: Relation Grounding (DEPENDS_ON, OWNS, BLOCKS, PRODUCES, REQUIRES_INPUT)

Classification guidelines:
- Choose the MOST SPECIFIC dimension that fits
- Use "critical" for must-have requirements, "expected" for should-have, "aspirational" for nice-to-have
- Structural (S) dimensions verify plan structure; Grounding (G) dimensions verify factual accuracy
'''

DEFAULT_SCENARIO_PROMPT = '''You are generating a realistic meeting SCENARIO that provides context for an assertion to be meaningful.

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
Return ONLY valid JSON.
'''

DEFAULT_WBP_GENERATION_PROMPT = '''You are generating a Workback Plan (WBP) based on a meeting scenario.

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

## WBP FORMAT REQUIREMENTS
The WBP MUST include a Timeline Overview table with columns: T-n, Date, Task, Owner, Deliverable.

Return JSON with:
{{
  "workback_plan": "The complete workback plan in markdown format with the timeline table"
}}

Return ONLY valid JSON.
'''

DEFAULT_WBP_VERIFICATION_PROMPT = '''You are verifying a Workback Plan against a scenario and assertions.

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

DEFAULT_G_SELECTION_PROMPT = '''Given a structural assertion and its classification, determine which grounding dimensions are ACTUALLY RELEVANT based on what the assertion explicitly requests or implies.

**Original Assertion:** "{assertion_text}"
**Classified as:** {dimension_id} - {dimension_name}
**Classification Rationale:** {rationale}

**Available Grounding Dimensions for {dimension_id}:**
{available_g_dims}

**Instructions:**
1. Analyze what the original assertion ACTUALLY requests or checks
2. For each available G dimension, determine if it's RELEVANT to verifying this specific assertion
3. A G dimension is relevant ONLY if the assertion explicitly or implicitly requires checking that aspect
4. Do NOT include G dimensions just because they're in the mapping - they must be needed for THIS assertion

**Examples:**
- "Tasks are ordered correctly" → G6 (Action Items) is relevant, G3 (Dates) may NOT be relevant if no dates mentioned
- "Meeting is scheduled for next Tuesday" → G3 (Dates) is relevant
- "Alice is assigned to the task" → G2 (Attendees) is relevant

Return JSON:
{{
    "selected_g_dimensions": [
        {{
            "dimension_id": "G3",
            "dimension_name": "Date/Time Grounding",
            "relevance_reason": "The assertion mentions specific dates that need verification",
            "grounding_text": "The dates mentioned (Dec 5, Dec 10) must be consistent with the meeting context"
        }}
    ],
    "excluded_g_dimensions": [
        {{
            "dimension_id": "G6",
            "reason": "The assertion does not mention or imply any action items"
        }}
    ]
}}
'''

# Load prompts with fallbacks
SYSTEM_PROMPT = get_prompt("system_prompt", DEFAULT_SYSTEM_PROMPT)
SCENARIO_GENERATION_PROMPT = get_prompt("scenario_generation_prompt", DEFAULT_SCENARIO_PROMPT)
WBP_GENERATION_PROMPT = get_prompt("wbp_generation_prompt", DEFAULT_WBP_GENERATION_PROMPT)
WBP_VERIFICATION_PROMPT = get_prompt("wbp_verification_prompt", DEFAULT_WBP_VERIFICATION_PROMPT)
G_SELECTION_PROMPT = get_prompt("g_selection_prompt", DEFAULT_G_SELECTION_PROMPT)


# ═══════════════════════════════════════════════════════════════════════════════
# TABLE ALIGNMENT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def fix_markdown_table_alignment(text: str) -> str:
    """
    Post-process markdown tables to ensure proper column alignment.
    Finds markdown tables and fixes column widths so all pipes align.
    """
    lines = text.split('\n')
    result_lines = []
    table_lines = []
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        if '|' in stripped and (stripped.startswith('|') or re.match(r'^[\|\s\-]+$', stripped)):
            in_table = True
            table_lines.append(line)
        else:
            if in_table and table_lines:
                fixed_table = _align_table(table_lines)
                result_lines.extend(fixed_table)
                table_lines = []
                in_table = False
            result_lines.append(line)
    
    if table_lines:
        fixed_table = _align_table(table_lines)
        result_lines.extend(fixed_table)
    
    return '\n'.join(result_lines)


def _align_table(table_lines: list) -> list:
    """Align a markdown table so all columns have consistent widths."""
    if not table_lines:
        return table_lines
    
    rows = []
    leading_spaces = ""
    
    for i, line in enumerate(table_lines):
        if i == 0:
            leading_spaces = line[:len(line) - len(line.lstrip())]
        
        stripped = line.strip()
        if set(stripped.replace('|', '').replace('-', '').replace(':', '').replace(' ', '')) == set():
            rows.append(None)  # Placeholder for separator
        else:
            cells = [c.strip() for c in stripped.split('|')]
            if cells and cells[0] == '':
                cells = cells[1:]
            if cells and cells[-1] == '':
                cells = cells[:-1]
            rows.append(cells)
    
    if not rows:
        return table_lines
    
    num_cols = max(len(r) for r in rows if r is not None)
    col_widths = [0] * num_cols
    
    for row in rows:
        if row is None:
            continue
        for i, cell in enumerate(row):
            if i < num_cols:
                col_widths[i] = max(col_widths[i], len(cell))
    
    col_widths = [max(w, 3) for w in col_widths]
    
    result = []
    for row in rows:
        if row is None:
            sep_parts = ['|'] + ['-' * (w + 2) + '|' for w in col_widths]
            result.append(leading_spaces + ''.join(sep_parts))
        else:
            padded_cells = []
            for i in range(num_cols):
                cell = row[i] if i < len(row) else ''
                padded_cells.append(' ' + cell.ljust(col_widths[i]) + ' ')
            result.append(leading_spaces + '|' + '|'.join(padded_cells) + '|')
    
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def select_relevant_g_dimensions(
    assertion_text: str,
    dimension_id: str,
    dimension_name: str,
    rationale: str,
    verbose: bool = True
) -> list:
    """
    Use GPT-5 to select which G dimensions are actually relevant for this specific assertion.
    
    Args:
        assertion_text: The original assertion text
        dimension_id: The classified S dimension (e.g., "S2")
        dimension_name: The name of the S dimension
        rationale: The classification rationale
        verbose: Whether to print progress
        
    Returns:
        List of dicts with selected G dimensions and their grounding text
    """
    if dimension_id not in S_TO_G_MAP:
        return []
    
    available_g_dims = S_TO_G_MAP[dimension_id]
    
    # Build description of available G dimensions
    g_dims_text = []
    for g_dim in available_g_dims:
        g_spec = DIMENSION_SPEC.get(g_dim, {})
        g_rationale = G_RATIONALE_FOR_S.get((dimension_id, g_dim), "")
        g_dims_text.append(f"- {g_dim} ({g_spec.get('name', 'Unknown')}): {g_rationale}")
    
    prompt = G_SELECTION_PROMPT.format(
        assertion_text=assertion_text,
        dimension_id=dimension_id,
        dimension_name=dimension_name,
        rationale=rationale,
        available_g_dims="\n".join(g_dims_text)
    )
    
    if verbose:
        print(f"   Selecting relevant G dimensions for {dimension_id}...")
    
    result_text = call_gpt5_api(
        prompt,
        system_prompt="You analyze assertions to determine which grounding dimensions are relevant for verification.",
        temperature=0.2
    )
    
    try:
        result = extract_json_from_response(result_text)
        return result.get("selected_g_dimensions", [])
    except:
        # Fallback: return all available G dimensions with default rationales
        fallback = []
        for g_dim in available_g_dims:
            g_spec = DIMENSION_SPEC.get(g_dim, {})
            fallback.append({
                "dimension_id": g_dim,
                "dimension_name": g_spec.get('name', 'Unknown'),
                "relevance_reason": G_RATIONALE_FOR_S.get((dimension_id, g_dim), "Default mapping"),
                "grounding_text": g_spec.get('template', '')
            })
        return fallback


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
        system_prompt=get_prompt("scenario_generation_system", 
                                 "You generate realistic meeting scenarios for assertion testing."),
        temperature=0.5
    )
    
    try:
        result = extract_json_from_response(result_text)
        return result.get("scenario", {})
    except:
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


def generate_wbp_with_scenario(
    scenario: dict, 
    original_utterance: str, 
    s_assertion: dict, 
    g_assertions: list
) -> str:
    """
    Generate a WBP conditioned on the scenario and assertions.
    
    Args:
        scenario: The meeting scenario (ground truth)
        original_utterance: The original user input
        s_assertion: The structural assertion
        g_assertions: List of grounding assertions
        
    Returns:
        Workback plan content as markdown string
    """
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
        system_prompt=get_prompt("wbp_generation_system",
                                 "You generate workback plans based on meeting scenarios."),
        temperature=0.4
    )
    
    try:
        result = extract_json_from_response(result_text)
        wbp = result.get("workback_plan", result_text)
    except:
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                wbp = result.get("workback_plan", "")
            except:
                wbp = "Unable to generate WBP"
        else:
            wbp = "Unable to generate WBP"
    
    return fix_markdown_table_alignment(wbp)


def verify_wbp_against_scenario(
    scenario: dict, 
    wbp_content: str, 
    all_assertions: list
) -> dict:
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
        system_prompt=get_prompt("wbp_verification_system",
                                 "You verify workback plans against scenarios and assertions."),
        temperature=0.2
    )
    
    try:
        result = extract_json_from_response(result_text)
        return result
    except:
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        return {"overall_passes": False, "assertion_results": []}


def analyze_assertion(assertion_text: str, context: Optional[str] = None) -> dict:
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

    print("Calling GPT-5 for analysis...")
    result_text = call_gpt5_api(prompt, system_prompt=SYSTEM_PROMPT, temperature=0.2)
    
    try:
        result = extract_json_from_response(result_text)
    except:
        json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"error": "Failed to parse GPT-5 response", "raw": result_text}
    
    return result


def classify_assertion(assertion_text: str, verbose: bool = False) -> dict:
    """
    Lightweight classification of an assertion - classification only, no WBP generation.
    
    This is faster than analyze_assertion() as it only classifies the assertion
    into a dimension without generating scenarios, WBPs, or verification.
    
    Args:
        assertion_text: The assertion to classify
        verbose: Whether to print progress messages
        
    Returns:
        dict with:
        - dimension: The classified dimension ID (e.g., "S5", "G3", or "UNKNOWN")
        - dimension_name: Full name of the dimension
        - layer: "structural" or "grounding"  
        - level: "critical", "expected", or "aspirational"
        - rationale: Why this dimension was chosen
        - linked_g_dims: List of grounding dimensions that apply (for S dimensions)
    """
    # Load optimized prompt from file
    prompt_file = os.path.join(os.path.dirname(__file__), "prompts", "classification_prompt.json")
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_config = json.load(f)
        prompt_template = prompt_config.get("user_prompt_template", "")
        system_prompt = prompt_config.get("system_prompt", SYSTEM_PROMPT)
        temperature = prompt_config.get("temperature", 0.2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if verbose:
            print(f"Warning: Could not load classification_prompt.json: {e}, using fallback")
        # Fallback prompt
        prompt_template = '''Classify this assertion into WBP framework dimension (S1-S20 or G1-G9).
Assertion: "{assertion_text}"
Return JSON: {{"dimension_id": "S5", "dimension_name": "...", "layer": "structural", "level": "critical", "rationale": "..."}}'''
        system_prompt = SYSTEM_PROMPT
        temperature = 0.2
    
    prompt = prompt_template.replace("{assertion_text}", assertion_text)

    if verbose:
        print(f"Classifying: {assertion_text[:50]}...")
    
    result_text = call_gpt5_api(prompt, system_prompt=system_prompt, temperature=temperature)
    
    try:
        result = extract_json_from_response(result_text)
    except:
        json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
            except:
                result = {"dimension_id": "UNKNOWN", "error": "Failed to parse response"}
        else:
            result = {"dimension_id": "UNKNOWN", "error": "Failed to parse response"}
    
    # Normalize and add linked_g_dims
    dimension_id = result.get("dimension_id", "UNKNOWN")
    
    # Validate dimension exists
    if dimension_id not in DIMENSION_NAMES and dimension_id != "UNKNOWN":
        dimension_id = "UNKNOWN"
    
    return {
        "dimension": dimension_id,
        "dimension_name": result.get("dimension_name", DIMENSION_NAMES.get(dimension_id, "Unknown")),
        "layer": result.get("layer", "unknown"),
        "level": result.get("level", "expected"),
        "rationale": result.get("rationale", ""),
        "linked_g_dims": S_TO_G_MAP.get(dimension_id, []) if dimension_id.startswith("S") else []
    }


def generate_sg_assertions(
    gpt5_result: dict, 
    assertion_text: str, 
    assertion_index: int = 0, 
    generate_examples: bool = True,
    verbose: bool = True
) -> list:
    """
    Generate the full S+G assertion set with proper linkage.
    
    Args:
        gpt5_result: Classification result from GPT-5
        assertion_text: Original assertion text (user input)
        assertion_index: Index for generating unique IDs
        generate_examples: Whether to generate mock WBP via GPT-5
        verbose: Whether to print progress messages
        
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
    
    primary_assertion_id = f"A{assertion_index:04d}_{dimension_id}"
    
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
        "linked_g_dims": S_TO_G_MAP.get(dimension_id, []) if dimension_id.startswith("S") else [],
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
    # Use GPT-5 to select ONLY the G dimensions that are relevant to this specific assertion
    g_assertions = []
    if dimension_id.startswith("S") and dimension_id in S_TO_G_MAP:
        # Call GPT-5 to intelligently select relevant G dimensions
        selected_g_dims = select_relevant_g_dimensions(
            assertion_text=assertion_text,
            dimension_id=dimension_id,
            dimension_name=dimension_name,
            rationale=rationale,
            verbose=verbose
        )
        
        for g_idx, g_info in enumerate(selected_g_dims):
            g_dim = g_info.get("dimension_id", "")
            g_spec = DIMENSION_SPEC.get(g_dim, {})
            if not g_spec:
                continue
            
            g_assertion_id = f"A{assertion_index:04d}_{g_dim}_{g_idx}"
            
            # Use GPT-5's relevance reason if available, otherwise fall back to mapping
            g_rationale = g_info.get(
                "relevance_reason",
                G_RATIONALE_FOR_S.get(
                    (dimension_id, g_dim),
                    f"Generated from {dimension_id}: {g_spec.get('name', '')} grounds {dimension_name}"
                )
            )
            
            # Use GPT-5's grounding text if available, otherwise use template
            grounding_text = g_info.get("grounding_text", g_spec.get('template', ''))
            
            g_assertion = {
                "assertion_id": g_assertion_id,
                "parent_assertion_id": primary_assertion_id,
                "text": grounding_text,
                "original_text": assertion_text,
                "dimension_id": g_dim,
                "dimension_name": g_info.get("dimension_name", g_spec.get('name', 'Unknown')),
                "layer": "grounding",
                "level": "critical",
                "weight": g_spec.get('weight', 3),
                "rationale": {
                    "mapping_reason": g_rationale,
                    "parent_dimension": dimension_id,
                    "parent_dimension_name": dimension_name,
                    "conversion_method": "gpt5_g_selection"
                },
                "quality_assessment": {
                    "is_well_formed": True,
                    "is_testable": True
                }
            }
            g_assertions.append(g_assertion)
    
    # Generate scenario + WBP
    if generate_examples and dimension_id.startswith("S"):
        if verbose:
            print(f"   Generating scenario for assertion context...")
        scenario = generate_scenario_for_assertion(assertion_text)
        
        if verbose:
            print(f"   Generating WBP for {dimension_id} + {len(g_assertions)} grounding assertions...")
        wbp_content = generate_wbp_with_scenario(
            scenario=scenario,
            original_utterance=assertion_text,
            s_assertion=primary,
            g_assertions=g_assertions
        )
        
        if verbose:
            print(f"   Verifying WBP against scenario...")
        all_assertions = [primary] + g_assertions
        verification = verify_wbp_against_scenario(
            scenario=scenario,
            wbp_content=wbp_content,
            all_assertions=all_assertions
        )
        
        shared_success_example = {
            "scenario": scenario,
            "workback_plan": wbp_content,
            "overall_verified": verification.get("overall_passes", False),
            "assertion_results": verification.get("assertion_results", [])
        }
        
        primary["success_example"] = shared_success_example
        
        assertion_results_map = {
            r.get("assertion_id"): r 
            for r in verification.get("assertion_results", [])
        }
        
        for g_assertion in g_assertions:
            g_id = g_assertion["assertion_id"]
            g_verification = assertion_results_map.get(g_id, {})
            g_assertion["success_example"] = {
                "scenario": scenario,
                "workback_plan": wbp_content,
                "evidence": g_verification.get("evidence", ""),
                "ground_truth_check": g_verification.get("ground_truth_check", ""),
                "verification": g_verification.get("reasoning", ""),
                "verified": g_verification.get("passes", False)
            }
    elif generate_examples and dimension_id.startswith("G"):
        if verbose:
            print(f"   Generating scenario for standalone {dimension_id}...")
        scenario = generate_scenario_for_assertion(assertion_text)
        
        if verbose:
            print(f"   Generating WBP for standalone {dimension_id}...")
        wbp_content = generate_wbp_with_scenario(
            scenario=scenario,
            original_utterance=assertion_text,
            s_assertion=primary,
            g_assertions=[]
        )
        
        if verbose:
            print(f"   Verifying WBP against scenario...")
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
                "scenario": {}, "workback_plan": "", "evidence": "", 
                "ground_truth_check": "", "verification": "", "verified": False
            }
    
    results.append(primary)
    results.extend(g_assertions)
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_markdown_report(report: dict, original_utterance: str, assertions: list) -> str:
    """
    Generate a markdown mini-report for easy communication and discussion.
    Includes all 5 steps of the workflow.
    
    Args:
        report: The full report dictionary
        original_utterance: The original input text
        assertions: List of generated assertions
        
    Returns:
        Markdown formatted report string
    """
    lines = []
    metadata = report.get('metadata', {})
    scenario = report.get('scenario', {})
    wbp = report.get('workback_plan', '')
    vs = report.get('verification_summary', {})
    
    # Get primary assertion info
    primary = assertions[0] if assertions else {}
    s_assertions = [a for a in assertions if a.get('dimension_id', '').startswith('S')]
    g_assertions = [a for a in assertions if a.get('dimension_id', '').startswith('G')]
    
    # Header
    lines.append("# Assertion Analysis Report")
    lines.append("")
    lines.append("**Author**: TimeBerry Assertion Analyzer  ")
    lines.append(f"**Generated**: {metadata.get('timestamp', 'N/A')}  ")
    lines.append(f"**Assertion ID**: {primary.get('assertion_id', 'N/A')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 1: INPUT
    # ═══════════════════════════════════════════════════════════════════════════
    lines.append("## Step 1: Input Assertion")
    lines.append("")
    lines.append("The user provides a natural language assertion to analyze:")
    lines.append("")
    lines.append("```")
    lines.append(original_utterance)
    lines.append("```")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 2: SCENARIO GENERATION
    # ═══════════════════════════════════════════════════════════════════════════
    lines.append("## Step 2: Scenario Generation (GPT-5)")
    lines.append("")
    lines.append("GPT-5 generates a realistic meeting scenario as **ground truth** for verification.")
    lines.append("")
    
    if scenario and scenario.get('title'):
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        lines.append(f"| **Meeting** | {scenario.get('title', 'N/A')} |")
        lines.append(f"| **Date** | {scenario.get('date', 'N/A')} at {scenario.get('time', 'N/A')} |")
        lines.append(f"| **Organizer** | {scenario.get('organizer', 'N/A')} |")
        lines.append(f"| **Duration** | {scenario.get('duration_minutes', 'N/A')} minutes |")
        lines.append("")
        
        if scenario.get('attendees'):
            lines.append("**Attendees** (ground truth for G2 - Attendee Grounding):")
            for att in scenario.get('attendees', []):
                lines.append(f"- {att}")
            lines.append("")
        
        if scenario.get('artifacts'):
            lines.append("**Artifacts** (ground truth for G4 - Artifact Grounding):")
            for art in scenario.get('artifacts', []):
                lines.append(f"- `{art}`")
            lines.append("")
        
        if scenario.get('context'):
            lines.append("**Context:**")
            lines.append(f"> {scenario.get('context')}")
            lines.append("")
        
        if scenario.get('action_items_discussed'):
            lines.append("**Action Items Discussed** (ground truth for G6):")
            for item in scenario.get('action_items_discussed', []):
                lines.append(f"- {item}")
            lines.append("")
    else:
        lines.append("*Scenario generation skipped (use full mode without --no-examples)*")
        lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 3: CLASSIFICATION
    # ═══════════════════════════════════════════════════════════════════════════
    lines.append("## Step 3: Assertion Classification (GPT-5)")
    lines.append("")
    lines.append("GPT-5 classifies the assertion into one of 28 dimensions (S1-S20, G1-G8).")
    lines.append("")
    
    lines.append("| Property | Value |")
    lines.append("|----------|-------|")
    lines.append(f"| **Dimension** | {primary.get('dimension_id', 'N/A')} - {primary.get('dimension_name', 'N/A')} |")
    lines.append(f"| **Layer** | {primary.get('layer', 'N/A')} |")
    lines.append(f"| **Level** | {primary.get('level', 'N/A')} |")
    lines.append(f"| **Weight** | {primary.get('weight', 'N/A')} |")
    lines.append("")
    
    rationale = primary.get('rationale', {})
    if rationale.get('mapping_reason'):
        lines.append("**Classification Rationale:**")
        lines.append(f"> {rationale.get('mapping_reason', 'N/A')}")
        lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 4: S+G CONVERSION (Intelligent G Selection)
    # ═══════════════════════════════════════════════════════════════════════════
    lines.append("## Step 4: Intelligent G Selection (GPT-5)")
    lines.append("")
    lines.append("GPT-5 analyzes the assertion to select **only relevant** G dimensions,")
    lines.append("rather than blindly using all mapped Gs from the static table.")
    lines.append("")
    
    if g_assertions:
        # Show the S->G mapping result
        g_dims = [a.get('dimension_id') for a in g_assertions]
        lines.append(f"**S→G Selection Result**: `{primary.get('dimension_id')}` → `[{', '.join(g_dims)}]`")
        lines.append("")
        
        lines.append("### Selected G Dimensions")
        lines.append("")
        lines.append("| G Dimension | Name | Why Selected |")
        lines.append("|-------------|------|--------------|")
        for g in g_assertions:
            g_reason = g.get('rationale', {}).get('mapping_reason', 'N/A')
            # Truncate long reasons
            if len(g_reason) > 55:
                g_reason = g_reason[:52] + "..."
            lines.append(f"| **{g.get('dimension_id')}** | {g.get('dimension_name')} | {g_reason} |")
        lines.append("")
        
        lines.append("### GPT-5 Selection Reasoning")
        lines.append("")
        lines.append("The model analyzed the assertion text and determined which grounding")
        lines.append("dimensions are actually needed to verify this specific assertion:")
        lines.append("")
        lines.append(f"- **Input**: \"{original_utterance[:60]}{'...' if len(original_utterance) > 60 else ''}\"")
        lines.append(f"- **Selected**: {len(g_assertions)} G dimension(s)")
        lines.append("")
    else:
        if primary.get('dimension_id', '').startswith('G'):
            lines.append("*This is already a Grounding (G) assertion - no S→G conversion needed.*")
        else:
            lines.append("*No grounding dimensions were selected as relevant for this assertion.*")
        lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GENERATED ASSERTIONS SUMMARY
    # ═══════════════════════════════════════════════════════════════════════════
    lines.append("### Generated Assertions Summary")
    lines.append("")
    lines.append("| ID | Dimension | Layer | Level | Assertion Text |")
    lines.append("|----|-----------|-------|-------|----------------|")
    for a in assertions:
        text = a.get('text', '')[:45]
        if len(a.get('text', '')) > 45:
            text += "..."
        lines.append(f"| `{a.get('assertion_id')}` | {a.get('dimension_id')} | {a.get('layer')} | {a.get('level')} | {text} |")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 5: WBP GENERATION
    # ═══════════════════════════════════════════════════════════════════════════
    lines.append("## Step 5: WBP Generation (GPT-5)")
    lines.append("")
    lines.append("GPT-5 generates a Workback Plan (WBP) based on the scenario.")
    lines.append("The WBP is conditioned on the meeting context to ensure factual grounding.")
    lines.append("")
    
    if wbp:
        lines.append("### Generated Workback Plan")
        lines.append("")
        lines.append("```markdown")
        # Include full WBP content
        wbp_lines = wbp.split('\n')
        lines.extend(wbp_lines)
        lines.append("```")
        lines.append("")
    else:
        lines.append("*WBP generation skipped (use full mode without --no-examples)*")
        lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 6: VERIFICATION
    # ═══════════════════════════════════════════════════════════════════════════
    lines.append("## Step 6: Verification (GPT-5)")
    lines.append("")
    lines.append("GPT-5 verifies each assertion (S + G) against the generated WBP.")
    lines.append("Each assertion is checked for evidence in the WBP content.")
    lines.append("")
    
    total = vs.get('total_verified', 0) + vs.get('total_failed', 0)
    passed = vs.get('total_verified', 0)
    failed = vs.get('total_failed', 0)
    
    if total > 0:
        status_emoji = "✅" if vs.get('all_passed') else "⚠️"
        lines.append(f"**Overall Status**: {status_emoji} **{passed}/{total}** assertions passed")
        lines.append("")
        
        if vs.get('results'):
            lines.append("| Assertion ID | Status | Evidence |")
            lines.append("|--------------|--------|----------|")
            for r in vs.get('results', []):
                status = "✅ Pass" if r.get('passes') else "❌ Fail"
                evidence = r.get('evidence', '')[:35]
                if len(r.get('evidence', '')) > 35:
                    evidence += "..."
                lines.append(f"| `{r.get('assertion_id')}` | {status} | {evidence} |")
            lines.append("")
    else:
        lines.append("*Verification not performed (use full mode without --no-examples)*")
        lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════════
    lines.append("---")
    lines.append("")
    lines.append("## Workflow Summary")
    lines.append("")
    lines.append("```")
    lines.append("Step 1: INPUT          → User assertion received")
    lines.append(f"Step 2: SCENARIO       → {'Generated' if scenario and scenario.get('title') else 'Skipped'}")
    lines.append(f"Step 3: CLASSIFICATION → {primary.get('dimension_id', 'N/A')} ({primary.get('layer', 'N/A')})")
    lines.append(f"Step 4: G SELECTION    → {len(g_assertions)} grounding dimension(s)")
    lines.append(f"Step 5: WBP GENERATION → {'Generated' if wbp else 'Skipped'}")
    lines.append(f"Step 6: VERIFICATION   → {passed}/{total} passed")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by WBP Assertion Analyzer using GPT-5*")
    
    return "\n".join(lines)


def generate_report(
    assertions: list, 
    original_utterance: str, 
    output_dir: Optional[str] = None,
    assertion_id: Optional[str] = None
) -> dict:
    """
    Generate a final report with summary table and JSON file.
    
    Args:
        assertions: List of generated assertions
        original_utterance: The original input text
        output_dir: Directory to save JSON file (optional)
        assertion_id: Custom assertion ID for filename (e.g., "A0001")
        
    Returns:
        dict with summary_table, json_file_path, and full report
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Build filename with assertion_id if provided
    if assertion_id:
        filename = f"{assertion_id}_analysis.json"
    else:
        filename = f"assertion_analysis_{timestamp}.json"
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, filename)
    else:
        json_path = filename
    
    s_assertions = [a for a in assertions if a.get('dimension_id', '').startswith('S')]
    g_assertions = [a for a in assertions if a.get('dimension_id', '').startswith('G')]
    
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
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Generate markdown mini-report
    md_path = json_path.replace('.json', '.md')
    md_content = _generate_markdown_report(report, original_utterance, assertions)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    # Build summary table
    table_lines = _build_summary_table(report, original_utterance, json_path, assertions)
    summary_table = "\n".join(table_lines)
    
    return {
        "summary_table": summary_table,
        "json_file_path": json_path,
        "md_file_path": md_path,
        "report": report
    }


def _build_summary_table(
    report: dict, 
    original_utterance: str, 
    json_path: str, 
    assertions: list
) -> list:
    """Build the summary table lines for the report."""
    table_lines = []
    scenario = report.get('scenario')
    wbp = report.get('workback_plan')
    verification_results = report.get('verification_summary', {}).get('results', [])
    vs = report.get('verification_summary', {})
    
    table_lines.append("")
    table_lines.append("=" * 140)
    table_lines.append("ASSERTION ANALYSIS REPORT")
    table_lines.append("=" * 140)
    table_lines.append(f"Timestamp: {report['metadata']['timestamp']}")
    table_lines.append(f"Input: \"{original_utterance}\"")
    table_lines.append("")
    
    # Workflow steps
    table_lines.append("-" * 140)
    table_lines.append("WORKFLOW EXECUTED")
    table_lines.append("-" * 140)
    table_lines.append("  Step 1: INPUT ASSERTION")
    table_lines.append(f"          \"{original_utterance}\"")
    table_lines.append("")
    table_lines.append("  Step 2: SCENARIO GENERATION (GPT-5)")
    table_lines.append(f"          Generated meeting context as ground truth for grounding assertions")
    if scenario:
        table_lines.append(f"          -> Meeting: {scenario.get('title', 'N/A')}")
        table_lines.append(f"          -> Attendees: {len(scenario.get('attendees', []))} | Artifacts: {len(scenario.get('artifacts', []))}")
    table_lines.append("")
    table_lines.append("  Step 3: ASSERTION ANALYSIS (GPT-5)")
    if assertions:
        primary = assertions[0]
        table_lines.append(f"          Classified as: {primary.get('dimension_id')} - {primary.get('dimension_name')}")
        table_lines.append(f"          Layer: {primary.get('layer')} | Level: {primary.get('level')}")
    table_lines.append("")
    table_lines.append("  Step 4: S+G ASSERTION CONVERSION")
    s_count = sum(1 for a in assertions if a.get('dimension_id', '').startswith('S'))
    g_count = sum(1 for a in assertions if a.get('dimension_id', '').startswith('G'))
    table_lines.append(f"          Generated {s_count} Structural + {g_count} Grounding assertions with linkage")
    if g_count > 0:
        g_dims = [a.get('dimension_id') for a in assertions if a.get('dimension_id', '').startswith('G')]
        table_lines.append(f"          -> S->G mapping: {assertions[0].get('dimension_id')} -> {', '.join(g_dims)}")
    table_lines.append("")
    table_lines.append("  Step 5: WBP GENERATION & VERIFICATION (GPT-5)")
    table_lines.append(f"          Generated WBP conditioned on scenario, verified against all S+G assertions")
    table_lines.append(f"          -> Result: {vs.get('total_verified', 0)} passed, {vs.get('total_failed', 0)} failed")
    table_lines.append("")
    
    # Scenario summary
    if scenario:
        table_lines.append("-" * 140)
        table_lines.append("SCENARIO CONTEXT (Ground Truth)")
        table_lines.append("-" * 140)
        table_lines.append(f"  Meeting: {scenario.get('title', 'N/A')}")
        table_lines.append(f"  Date: {scenario.get('date', 'N/A')} at {scenario.get('time', 'N/A')}")
        table_lines.append(f"  Organizer: {scenario.get('organizer', 'N/A')}")
        table_lines.append(f"  Attendees: {', '.join(scenario.get('attendees', []))}")
        if scenario.get('artifacts'):
            table_lines.append(f"  Artifacts: {', '.join(scenario.get('artifacts', []))}")
        if scenario.get('action_items_discussed'):
            table_lines.append(f"  Action Items: {len(scenario.get('action_items_discussed', []))} items discussed")
        table_lines.append("")
    
    # Generated WBP
    if wbp:
        table_lines.append("-" * 140)
        table_lines.append("GENERATED WORKBACK PLAN (WBP)")
        table_lines.append("-" * 140)
        wbp_lines = wbp.split('\n')
        for line in wbp_lines[:50]:
            table_lines.append(f"  {line}")
        if len(wbp_lines) > 50:
            table_lines.append(f"  ... ({len(wbp_lines) - 50} more lines, see JSON for full WBP)")
        table_lines.append("")
    
    # Assertions table
    table_lines.append("-" * 140)
    table_lines.append("ASSERTIONS SUMMARY TABLE")
    table_lines.append("-" * 140)
    
    header = f"{'ID':<15} {'Dim':<5} {'Layer':<12} {'Level':<10} {'Mapping Reason':<45} {'Success Example':<50}"
    table_lines.append(header)
    table_lines.append("-" * 140)
    
    for a in assertions:
        aid = a.get('assertion_id', 'N/A')
        dim = a.get('dimension_id', 'N/A')
        layer = a.get('layer', 'N/A')
        level = a.get('level', 'N/A')
        
        reason = a.get('rationale', {}).get('mapping_reason', '')[:43]
        if len(a.get('rationale', {}).get('mapping_reason', '')) > 43:
            reason += ".."
        
        example_text = ""
        for v in verification_results:
            if v.get('assertion_id') == aid:
                example_text = v.get('evidence', '')[:48]
                if len(v.get('evidence', '')) > 48:
                    example_text += ".."
                break
        
        row = f"{aid:<15} {dim:<5} {layer:<12} {level:<10} {reason:<45} {example_text:<50}"
        table_lines.append(row)
    
    table_lines.append("-" * 140)
    
    # Verification summary
    table_lines.append("")
    table_lines.append("VERIFICATION SUMMARY")
    table_lines.append("-" * 140)
    all_passed = vs.get('all_passed', False)
    status = "ALL PASSED" if all_passed else f"{vs.get('total_failed', 0)} FAILED"
    table_lines.append(f"  Status: {status}")
    table_lines.append(f"  Passed: {vs.get('total_verified', 0)} / {vs.get('total_verified', 0) + vs.get('total_failed', 0)}")
    table_lines.append("")
    
    # File output
    md_path = json_path.replace('.json', '.md')
    table_lines.append("=" * 140)
    table_lines.append(f"JSON Report saved to: {json_path}")
    table_lines.append(f"Markdown Report saved to: {md_path}")
    table_lines.append("=" * 140)
    
    return table_lines


# ═══════════════════════════════════════════════════════════════════════════════
# HIGH-LEVEL CLASS INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class AssertionAnalyzer:
    """
    High-level interface for assertion analysis.
    
    Example:
        analyzer = AssertionAnalyzer()
        result = analyzer.analyze("The response should list tasks in chronological order")
        print(result.summary_table)
    """
    
    def __init__(self, output_dir: Optional[str] = None, verbose: bool = True):
        """
        Initialize the analyzer.
        
        Args:
            output_dir: Directory to save JSON reports
            verbose: Whether to print progress messages
        """
        self.output_dir = output_dir
        self.verbose = verbose
    
    def analyze(
        self, 
        assertion_text: str, 
        context: Optional[str] = None,
        generate_examples: bool = True
    ) -> dict:
        """
        Analyze an assertion and return full results.
        
        Args:
            assertion_text: The assertion to analyze
            context: Optional context about the meeting/response
            generate_examples: Whether to generate WBP examples
            
        Returns:
            dict with assertions, report, and summary_table
        """
        # Step 1: GPT-5 classification
        gpt5_result = analyze_assertion(assertion_text, context)
        
        if "error" in gpt5_result:
            return {"error": gpt5_result}
        
        # Step 2: Generate S+G assertions
        assertions = generate_sg_assertions(
            gpt5_result, 
            assertion_text,
            assertion_index=0,
            generate_examples=generate_examples,
            verbose=self.verbose
        )
        
        # Step 3: Generate report
        report_result = generate_report(assertions, assertion_text, self.output_dir)
        
        return {
            "assertions": assertions,
            "report": report_result['report'],
            "summary_table": report_result['summary_table'],
            "json_file_path": report_result['json_file_path']
        }
    
    def classify(self, assertion_text: str, context: Optional[str] = None) -> dict:
        """
        Classify an assertion without generating examples.
        
        Args:
            assertion_text: The assertion to classify
            context: Optional context
            
        Returns:
            dict with dimension_id, dimension_name, layer, level, rationale
        """
        return analyze_assertion(assertion_text, context)
    
    def get_grounding_dimensions(self, s_dimension: str) -> list:
        """Get the grounding dimensions that apply to a structural dimension."""
        return S_TO_G_MAP.get(s_dimension, [])
