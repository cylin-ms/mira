#!/usr/bin/env python3
"""
Convert Kening's Assertions to Chin-Yew's WBP Format

This script:
1. Reads Kening's assertions JSONL
2. Evaluates each assertion using GPT-5 JJ
3. Maps and converts to Chin-Yew's WBP_Selected_Dimensions.md format
4. Generates templated assertions conforming to our spec
5. Adds rationale explaining each conversion

Target Format (from WBP_Selected_Dimensions.md):
- 9 Structural Dimensions: S1, S2, S3, S4, S5, S6, S11, S18, S19
- 5 Grounding Dimensions: G1, G2, G3, G4, G5
- Each assertion follows the template pattern for its dimension

Usage:
    python convert_kening_assertions.py                  # Convert all
    python convert_kening_assertions.py --start 0 --end 10
    python convert_kening_assertions.py --resume
    python convert_kening_assertions.py --dry-run       # Preview without GPT-5

Author: Chin-Yew Lin
Date: November 28, 2025
"""

import os
import sys
import json
import time
import argparse
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Add pipeline to path for shared config
sys.path.insert(0, os.path.dirname(__file__))
from pipeline.config import (
    get_substrate_token,
    call_gpt5_api,
    extract_json_from_response,
    DELAY_BETWEEN_CALLS,
)

# =============================================================================
# CONFIGURATION
# =============================================================================

INPUT_FILE = "docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl"
WEIWEI_FILE = "docs/Weiwei/UseUserEntity_Part1.WithUserUrl.jsonl"  # For USER info

# Output 1: Kening's schema with minimal enhancements (compatible format)
OUTPUT_KENING_ENHANCED = "docs/ChinYew/assertions_kening_enhanced.jsonl"

# Output 2: Full conversion with comprehensive details
OUTPUT_CONVERTED_FULL = "docs/ChinYew/assertions_converted_full.jsonl"

# Conversion report
REPORT_FILE = "docs/ChinYew/conversion_report.json"
CHECKPOINT_FILE = "docs/ChinYew/.conversion_checkpoint.json"

BATCH_SIZE = 5
DELAY_BETWEEN_MEETINGS = 2

# Self-throttling configuration
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # seconds
MAX_BACKOFF = 60  # seconds
RATES_PER_MINUTE = 10  # conservative rate limit
DELAY_BETWEEN_BATCHES = 6  # 10 requests per minute = 1 per 6 seconds

# =============================================================================
# TARGET DIMENSION SPEC (from WBP_Selected_Dimensions.md)
# =============================================================================

DIMENSION_SPEC = {
    # Structural Dimensions
    "S1": {
        "name": "Meeting Details",
        "weight": 3,
        "layer": "structural",
        "level": "event/meeting",
        "template": 'The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES] accurately',
        "definition": "Subject, date, time, timezone, attendee list clearly stated.",
        "evaluation": "Plan includes all meeting metadata; missing any field = fail.",
        "success_example": "Board Review — Dec 15, 2025, 10:00 AM CST; Attendees: Alice Chen, Bob Li; TZ: CST.",
        "fail_example": "Board Review next month (no date/time/timezone or attendee list)."
    },
    "S2": {
        "name": "Timeline Alignment",
        "weight": 3,
        "layer": "structural",
        "level": "overall",
        "template": 'The response should include a backward timeline from T₀ with dependency-aware sequencing',
        "definition": "Backward scheduling (T-minus) with dependency-aware sequencing from meeting date.",
        "evaluation": "Tasks arranged in reverse order from meeting date; dependencies respected.",
        "success_example": "T–30: Draft deck → T–15: Review → T–1: Dry run → Meeting Day.",
        "fail_example": "Tasks listed randomly; e.g., Review deck after meeting."
    },
    "S3": {
        "name": "Ownership Assignment",
        "weight": 3,
        "layer": "structural",
        "level": "task",
        "template": 'The response should assign an owner for each [TASK] or specify role/skill placeholder if name unavailable',
        "definition": "Named owners per task or role/skill placeholder if names unavailable.",
        "evaluation": "Every task has named owner or role/skill requirement stated.",
        "success_example": "Draft deck — Owner: Alice Chen; If name pending: Role: Staff PM; Skills: exec storytelling.",
        "fail_example": "Draft deck — Owner: TBD."
    },
    "S4": {
        "name": "Deliverables & Artifacts",
        "weight": 2,
        "layer": "structural",
        "level": "task",
        "template": 'The response should list [DELIVERABLES] with working links, version/format specified',
        "definition": "All outputs listed with working links, version/format specified.",
        "evaluation": "Deliverables traceable and accessible; missing links or versions = fail.",
        "success_example": "Final deck (link); Budget sheet (link); Risk log (link); v3.2 PDF.",
        "fail_example": "Prepare documents (no links or specifics)."
    },
    "S5": {
        "name": "Task Dates",
        "weight": 2,
        "layer": "structural",
        "level": "task",
        "template": 'The response should include due dates for every [TASK] aligned with timeline sequencing',
        "definition": "Due dates for every task aligned with S2 sequencing.",
        "evaluation": "All tasks have due dates; dates match milestone/timeline logic.",
        "success_example": "Draft deck due Dec 1; Review Dec 10; Dry run Dec 14.",
        "fail_example": "No dates provided for any task."
    },
    "S6": {
        "name": "Dependencies & Blockers",
        "weight": 2,
        "layer": "structural",
        "level": "task",
        "template": 'The response should identify [DEPENDENCIES/BLOCKERS] with mitigation steps documented',
        "definition": "Predecessors and risks identified; mitigation steps documented.",
        "evaluation": "Blockers and mitigations listed; absence = fail.",
        "success_example": "Dependency: Finance approval; Mitigation: escalate to CFO by Dec 5; Owner: Ops PM.",
        "fail_example": "No mention of blockers or mitigation."
    },
    "S11": {
        "name": "Risk Mitigation Strategy",
        "weight": 2,
        "layer": "structural",
        "level": "risk",
        "template": 'The response should include concrete [RISK MITIGATION] strategies with owners',
        "definition": "Concrete contingencies for top risks with owners.",
        "evaluation": "Mitigation steps documented; vague 'monitor' = fail.",
        "success_example": "Risk: Vendor delay; Mitigation: backup vendor PO in place; Owner: Procurement Lead.",
        "fail_example": "Risks listed with 'monitor' and no mitigation."
    },
    "S18": {
        "name": "Post-Event Actions",
        "weight": 1,
        "layer": "structural",
        "level": "post-event",
        "template": 'The response should list [POST-EVENT ACTIONS] (wrap-up, retrospectives, reporting)',
        "definition": "Wrap-up tasks, retrospectives, and reporting.",
        "evaluation": "Post-event steps listed; none = fail.",
        "success_example": "Post-meeting: send summary; archive deck; retrospective; publish decisions.",
        "fail_example": "No post-event tasks listed."
    },
    "S19": {
        "name": "Caveat & Clarification",
        "weight": 1,
        "layer": "structural",
        "level": "transparency",
        "template": 'The response should disclose [CAVEATS], [ASSUMPTIONS], and [CLARIFICATIONS] about information gaps or uncertainties',
        "definition": "Explicit disclosure of assumptions, missing information, uncertainties.",
        "evaluation": "Caveats and assumptions clearly stated; hidden assumptions = fail.",
        "success_example": "Caveat: Budget figures pending CFO approval; Assumption: All attendees confirmed.",
        "fail_example": "Plan presents uncertain items as facts; no disclosure of assumptions."
    },
    # Grounding Dimensions
    # G1 is the overall recall check - should pass if all other G dimensions pass
    "G1": {
        "name": "Hallucination Check",
        "weight": 3,
        "layer": "grounding",
        "level": "grounding",
        "template": 'No entities introduced that don\'t exist in source',
        "definition": "No extraneous entities or fabricated details. Overall grounding recall check.",
        "evaluation": "Plan contains only source-backed entities. If G2-G6 all pass, G1 passes.",
        "success_example": "No extra tasks or entities beyond source-backed items.",
        "fail_example": "Includes 'Prepare marketing video' not in source."
    },
    "G2": {
        "name": "Attendee Grounding",
        "weight": 3,
        "layer": "grounding",
        "level": "grounding",
        "template": 'All people mentioned must exist in {source.ATTENDEES}',
        "definition": "Attendees match source; no hallucinated names.",
        "evaluation": "All attendees verified against source list.",
        "success_example": "Attendees exactly match the invite roster.",
        "fail_example": "Adds 'John Doe' not in source."
    },
    "G3": {
        "name": "Date/Time Grounding",
        "weight": 3,
        "layer": "grounding",
        "level": "grounding",
        "template": 'Meeting date must match {source.MEETING.StartTime}',
        "definition": "Meeting date/time/timezone match the source.",
        "evaluation": "No deviation from source meeting schedule.",
        "success_example": "Date/time/timezone exactly match the invite.",
        "fail_example": "Uses Dec 16 instead of Dec 15."
    },
    "G4": {
        "name": "Artifact Grounding",
        "weight": 2,
        "layer": "grounding",
        "level": "grounding",
        "template": 'All files must exist in {source.ENTITIES where type=File}',
        "definition": "Files/decks referenced exist in the source repository.",
        "evaluation": "Artifacts validated; missing or fabricated = fail.",
        "success_example": "Deck link points to real file in repo.",
        "fail_example": "Links to non-existent or fabricated file."
    },
    "G5": {
        "name": "Topic Grounding",
        "weight": 2,
        "layer": "grounding",
        "level": "grounding",
        "template": 'Topics must align with {source.UTTERANCE} or {source.MEETING.Subject}',
        "definition": "Agenda topics align with source priorities/context.",
        "evaluation": "Topics match source; unrelated topics = fail.",
        "success_example": "Agenda topics match the source agenda.",
        "fail_example": "Adds 'New product launch' not in source."
    },
    "G6": {
        "name": "Task Grounding",
        "weight": 3,
        "layer": "grounding",
        "level": "grounding",
        "template": 'All tasks/action items must exist in {source.ENTITIES} (Email, Chat, CalendarEvent, or File)',
        "definition": "Tasks and action items derived from source material, not fabricated.",
        "evaluation": "All tasks traceable to source entities; fabricated tasks = fail.",
        "success_example": "Action items match those mentioned in source emails/chats.",
        "fail_example": "Adds 'Review Q4 budget' task not mentioned in any source."
    },
    "G7": {
        "name": "Role Grounding",
        "weight": 2,
        "layer": "grounding",
        "level": "grounding",
        "template": 'All role/responsibility assignments must match {source.ENTITIES} or be derivable from context',
        "definition": "Roles and responsibilities assigned to people must be accurate to source or reasonably inferred.",
        "evaluation": "All role assignments traceable to source; fabricated roles = fail.",
        "success_example": "Owner assignments match organizer/attendee roles from source.",
        "fail_example": "Assigns 'Project Lead' role to someone who is just an attendee."
    },
    "G8": {
        "name": "Constraint Grounding",
        "weight": 2,
        "layer": "grounding",
        "level": "grounding",
        "template": 'All constraints/limits must be derivable from {source.ENTITIES} or {source.UTTERANCE}',
        "definition": "Constraints, limitations, and requirements mentioned must exist in or be derivable from source.",
        "evaluation": "All constraints traceable to source; fabricated constraints = fail.",
        "success_example": "Timeline constraint matches meeting date from source.",
        "fail_example": "Claims 'budget cap of $50K' not mentioned in any source."
    }
}

# =============================================================================
# S-TO-G MAPPING: Which grounding checks apply to each structural dimension
# =============================================================================
# Each S dimension should have corresponding G checks to verify accuracy
# This enables generating both S (structure) and G (grounding) assertions

S_TO_G_MAP = {
    # S1 (Meeting Details) → Check attendees and dates are correct
    "S1": ["G2", "G3"],  # G2: Attendee Grounding, G3: Date/Time Grounding
    
    # S2 (Timeline) → Check dates, tasks, and constraints
    "S2": ["G3", "G6", "G8"],  # G3: Date/Time, G6: Task, G8: Constraint
    
    # S3 (Ownership) → Check people, tasks, and roles are real
    "S3": ["G2", "G6", "G7"],  # G2: Attendee, G6: Task, G7: Role
    
    # S4 (Deliverables) → Check artifacts exist in source
    "S4": ["G4"],  # G4: Artifact Grounding
    
    # S5 (Task Dates) → Check dates and tasks
    "S5": ["G3", "G6"],  # G3: Date/Time Grounding, G6: Task Grounding
    
    # S6 (Dependencies) → Check tasks/blockers and constraints
    "S6": ["G6", "G8"],  # G6: Task, G8: Constraint
    
    # S11 (Risk) → Check topics, tasks, and constraints
    "S11": ["G5", "G6", "G8"],  # G5: Topic, G6: Task, G8: Constraint
    
    # S18 (Post-Event) → Check tasks
    "S18": ["G6"],  # G6: Task Grounding
    
    # S19 (Caveat) → Check topics/assumptions and constraints
    "S19": ["G5", "G8"],  # G5: Topic, G8: Constraint
}

# Grounding assertions that map from original grounding dimensions
G_DIRECT_MAP = {
    "G1": "G1",  # Hallucination Check (overall)
    "G2": "G2",  # Attendee Grounding (was G1 in old mapping)
    "G3": "G3",  # Date/Time Grounding (was G2)
    "G4": "G4",  # Artifact Grounding (was G3)
    "G5": "G5",  # Topic Grounding (was G4)
    "G6": "G6",  # Task Grounding (new)
}

# =============================================================================
# KENING'S DIMENSION MAPPING
# =============================================================================

DIMENSION_MAP = {
    # S1: Meeting Details
    "Meeting Objective": "S1",
    "Meeting Objective & Scope": "S1",
    "Meeting Objective & Schedule": "S1",
    "Meeting Objective & Timing": "S1",
    "Meeting Objective Alignment": "S1",
    "Meeting Scope": "S1",
    "Meeting Logistics": "S1",
    "Meeting logistics": "S1",
    "Meeting Readiness": "S1",
    "MeetingObjective": "S1",
    "Objective": "S1",
    "Objective & Scope": "S1",
    "Objectives & Scope": "S1",
    "ObjectivesAndTasks": "S1",
    "Timeline & Meeting Details": "S1",
    "Timeline & Meeting Scope": "S1",
    "Logistics": "S1",
    "Logistics & Setup": "S1",
    "Logistics & Tech Setup": "S1",
    "Logistics & Tooling": "S1",
    "Logistics confirmation": "S1",
    
    # S2: Timeline Alignment
    "Timeline": "S2",
    "Timeline & Buffer": "S2",
    "Timeline & Buffers": "S2",
    "Timeline & buffers": "S2",
    "Timeline & Dependencies": "S2",
    "Timeline & dependencies": "S2",
    "Timeline & Milestones": "S2",
    "Timeline & T₀": "S2",
    "Timeline & Scope": "S2",
    "Timeline Buffer": "S2",
    "TimelineBuffer": "S2",
    "Timeline Visualization": "S2",
    "Timeline feasibility": "S2",
    "Sequencing": "S2",
    "Workback Structure": "S2",
    "Workflow sequencing": "S2",
    "Timeline & Agenda Prep": "S2",
    "Timeline & Event Confirmation": "S2",
    "Timeline & Ownership": "S2",
    "Timeline & Pre-Read": "S2",
    "Timeline & Prep": "S2",
    "Timeline & Review Quality": "S2",
    
    # S3: Ownership Assignment
    "Ownership": "S3",
    "Ownership & Action Plan": "S3",
    "Ownership & Attendees": "S3",
    "Ownership & Dependencies": "S3",
    "Ownership & RACI": "S3",
    "Ownership & Roles": "S3",
    "Ownership Accuracy": "S3",
    "Ownership Clarity": "S3",
    "Ownership clarity": "S3",
    "Participant accuracy": "S3",
    "Accuracy of Participants": "S3",
    "Stakeholder Alignment": "S3",
    "Stakeholder alignment": "S3",
    "StakeholderAlignment": "S3",
    "Stakeholders": "S3",
    "Stakeholder Communication": "S3",
    "Stakeholder communication": "S3",
    "Stakeholder coordination": "S3",
    "Stakeholder Alignment & Communication": "S3",
    
    # S4: Deliverables & Artifacts
    "Artifact": "S4",
    "Artifact Inclusion": "S4",
    "Artifact Readiness": "S4",
    "Artifact readiness": "S4",
    "ArtifactReadiness": "S4",
    "Artifact Readiness & Dependencies": "S4",
    "Artifact readiness & Timeline": "S4",
    "Artifact readiness & timeline": "S4",
    "Artifact Reference": "S4",
    "Artifact integration": "S4",
    "Artifacts": "S4",
    "Agenda & Preparation Quality": "S4",
    "Agenda Preparation": "S4",
    "Agenda & Scope alignment": "S4",
    "Pre-Meeting Readiness": "S4",
    "Meeting Preparation": "S4",
    "Preparation": "S4",
    
    # S5: Task Dates
    "Tasks": "S5",
    "Action Initiation": "S5",
    "Early Actions": "S5",
    "Immediate Action": "S5",
    "Critical steps": "S5",
    "Execution Readiness": "S5",
    "Execution readiness": "S5",
    "ExecutionReadiness": "S5",
    "Operational readiness": "S5",
    "Readiness": "S5",
    "Readiness & Logistics": "S5",
    "Final Readiness": "S5",
    "Final Review": "S5",
    
    # S6: Dependencies & Blockers
    "Dependencies": "S6",
    "Dependencies & Context": "S6",
    "Dependencies & Contingencies": "S6",
    "Dependencies & Quality Check": "S6",
    "Dependencies & Risk Notes": "S6",
    "Dependencies & Risks": "S6",
    "Dependencies & Sequencing": "S6",
    "Dependencies & sequencing": "S6",
    "Dependencies and Sequencing": "S6",
    "Dependency": "S6",
    "Dependency & Sequencing": "S6",
    "Sequencing & Dependencies": "S6",
    "Logistics & Dependencies": "S6",
    "Logistics & Contingency": "S6",
    "Logistics & Readiness": "S6",
    "Logistics & Risk Mitigation": "S6",
    "Logistics & Sequencing": "S6",
    "ComplianceDependency": "S6",
    
    # S11: Risk Mitigation Strategy
    "Risk & Buffer": "S11",
    "Risk & Timeline": "S11",
    "Risk & Transparency": "S11",
    "Risk & contingency": "S11",
    "Risk Disclosure": "S11",
    "Risk Management": "S11",
    "Risk Management & Tech Readiness": "S11",
    "Risk Mitigation": "S11",
    "Risk Planning": "S11",
    "Risk buffer": "S11",
    "Risk handling": "S11",
    "Risk management": "S11",
    "Risks & Mitigation": "S11",
    "Risks & Mitigations": "S11",
    "Key Risks & Mitigations": "S11",
    "Buffer & Risk Management": "S11",
    "Buffer Transparency": "S11",
    "Meeting Risks": "S11",
    "Readiness & risk mitigation": "S11",
    "Communication & Risk Mitigation": "S11",
    
    # S18: Post-Event Actions
    "Follow-up": "S18",
    "Follow-up actions": "S18",
    "Follow-up enablement": "S18",
    "Post-Meeting Action Hooks": "S18",
    
    # S19: Caveat & Clarification
    "Assumption Disclosure": "S19",
    "Assumption Transparency": "S19",
    "Assumption disclosure": "S19",
    "AssumptionTransparency": "S19",
    "Assumptions": "S19",
    "Assumptions & Disclosure": "S19",
    "Assumptions & Disclosures": "S19",
    "Assumptions & Gaps": "S19",
    "Assumptions & Info Gaps": "S19",
    "Assumptions & Missing Info": "S19",
    "Assumptions & Risk": "S19",
    "Assumptions & Risks": "S19",
    "Assumptions & Transparency": "S19",
    "Assumptions & disclosures": "S19",
    "Assumptions & transparency": "S19",
    "Assumptions Disclosure": "S19",
    "Assumptions Transparency": "S19",
    "Assumptions and transparency": "S19",
    "Assumptions disclosure": "S19",
    "AssumptionsDisclosure": "S19",
    "Disclosure": "S19",
    "Disclosure & Assumptions": "S19",
    "Disclosure / Assumptions": "S19",
    "Disclosure of Assumptions": "S19",
    "Disclosure of Missing Info": "S19",
    "Disclosure of Missing Info & Assumptions": "S19",
    "Disclosure of Missing Info / Assumptions": "S19",
    "Disclosure of Missing Info Assumptions": "S19",
    "Disclosure of Missing Info and Assumptions": "S19",
    "Disclosure of Missing Info/Assumptions": "S19",
    "Disclosure of Missing Information": "S19",
    "Disclosure of Missing Information & Assumptions": "S19",
    "Disclosure of Missing Information and Assumptions": "S19",
    "Disclosure of Missing/Assumptions": "S19",
    "Disclosure of assumptions": "S19",
    "Disclosure of missing info": "S19",
    "Disclosure of missing info & assumptions": "S19",
    "Disclosure of missing info / assumptions": "S19",
    "Disclosure of missing info and assumptions": "S19",
    "Disclosure of missing info/assumptions": "S19",
    "Disclosure of missing information": "S19",
    "Disclosures of assumptions": "S19",
    "Missing Info & Assumptions": "S19",
    "Missing Info Disclosure": "S19",
    "Missing info disclosure": "S19",
    "Transparency": "S19",
    "Transparency & Assumptions": "S19",
    "Transparency & Missing Info": "S19",
    "Transparency & Structure": "S19",
    "Transparency & Traceability": "S19",
    "Transparency of assumptions": "S19",
    "Transparency on Assumptions": "S19",
    
    # G1-G5: Grounding
    "Accuracy": "G5",
    "Accuracy & Scope": "G5",
    "Accuracy & no contradictions": "G5",
    "Anti-hallucination": "G5",
    "Grounding & Consistency": "G5",
    "Grounding & Relevance": "G5",
    "Grounding & Scope": "G5",
    "Grounding & Scope Integrity": "G5",
    "Grounding & Traceability": "G5",
    "Grounding & Transparency": "G5",
    "Grounding & consistency": "G5",
    "Grounding & contextual linkage": "G5",
    "Grounding & sequencing": "G5",
    "Grounding & traceability": "G5",
    "Grounding Consistency": "G5",
    "Grounding Integrity": "G5",
    "Scope & Accuracy": "G5",
    "Scope & Integrity": "G5",
    "Scope Adherence": "G5",
    "Scope Alignment": "G5",
    "Scope Control": "G5",
    "Scope alignment": "G5",
    "Content Alignment": "G4",
    "Context Alignment": "G4",
    "Context Linkage": "G4",
    "Consistency": "G5",
    
    # Others map to closest
    "Actionability": "S5",
    "Actionability & Clarity": "S5",
    "Aspirational enhancements": "S18",
    "Clarity & Readability": "S19",
    "Collaboration": "S3",
    "Collaboration Enhancement": "S3",
    "Collaboration Prompt": "S3",
    "Communication": "S3",
    "Communication Aids": "S3",
    "Enhancement": "S18",
    "Enhancements & Communication": "S18",
    "Proactive Guidance": "S11",
    "Proactive Quality": "S11",
    "Quality": "S4",
    "Quality Enhancement": "S4",
    "Quality Review": "S4",
    "Quality assurance": "S4",
    "Technical Readiness": "S4",
    "Value-add": "S18",
    "Workflow enhancement": "S2",
}

# =============================================================================
# GPT-5 CONVERSION PROMPT
# =============================================================================
# Full prompt documentation: prompts/convert_assertions_prompt.md
# =============================================================================

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "convert_assertions_prompt.md")

def load_system_prompt():
    """Load system prompt from markdown file, extracting the code block."""
    try:
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract system prompt from markdown code block
        import re
        match = re.search(r'## System Prompt\s+```\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            print(f"Warning: Could not extract system prompt from {PROMPT_FILE}, using fallback")
            return get_fallback_system_prompt()
    except FileNotFoundError:
        print(f"Warning: Prompt file not found: {PROMPT_FILE}, using fallback")
        return get_fallback_system_prompt()

def get_fallback_system_prompt():
    """Fallback system prompt if file not found."""
    return """You are an expert at converting assertions to a standardized format.

Your task is to:
1. Analyze the original assertion from Kening's dataset
2. Map it to the correct dimension (S1-S19 or G1-G8)
3. Rewrite the assertion using the standardized template
4. Provide rationale for the conversion

## Target Dimensions (from WBP_Selected_Dimensions.md)

### Structural (S) - Check PRESENCE ("Does the plan HAVE X?")
- S1: Meeting Details - "The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES]"
- S2: Timeline Alignment - "The response should include a backward timeline from T₀ with dependency-aware sequencing"
- S3: Ownership Assignment - "The response should assign an owner for each [TASK] or specify role/skill placeholder"
- S4: Deliverables & Artifacts - "The response should list [DELIVERABLES] with working links, version/format specified"
- S5: Task Dates - "The response should include due dates for every [TASK] aligned with timeline sequencing"
- S6: Dependencies & Blockers - "The response should identify [DEPENDENCIES/BLOCKERS] with mitigation steps documented"
- S11: Risk Mitigation Strategy - "The response should include concrete [RISK MITIGATION] strategies with owners"
- S18: Post-Event Actions - "The response should list [POST-EVENT ACTIONS] (wrap-up, retrospectives, reporting)"
- S19: Caveat & Clarification - "The response should disclose [CAVEATS], [ASSUMPTIONS], and [CLARIFICATIONS]"

### Grounding (G) - Check ACCURACY ("Is X CORRECT vs source?")
- G1: Hallucination Check - "No entities introduced that don't exist in source"
- G2: Attendee Grounding - "All people mentioned must exist in {source.ATTENDEES}"
- G3: Date/Time Grounding - "Meeting date must match {source.MEETING.StartTime}"
- G4: Artifact Grounding - "All files must exist in {source.ENTITIES where type=File}"
- G5: Topic Grounding - "Topics must align with {source.UTTERANCE} or {source.MEETING.Subject}"
- G6: Task Grounding - "All tasks/action items must exist in {source.ENTITIES}"
- G7: Role Grounding - "All role/responsibility assignments must match {source.ENTITIES} or context"
- G8: Constraint Grounding - "All constraints/limits must be derivable from {source.ENTITIES} or {source.UTTERANCE}"

## Key Conversion Rules

1. **Remove hardcoded values** - Replace specific names/dates with placeholders or source references
2. **Use template pattern** - Follow the dimension's template structure
3. **Structural vs Grounding** - Structural checks PRESENCE, Grounding checks ACCURACY
4. **Level assignment** - critical (weight 3), expected (weight 2), aspirational (weight 1)

Respond ONLY in valid JSON format."""

# Load system prompt at module initialization
SYSTEM_PROMPT = load_system_prompt()


def get_conversion_prompt(assertion: Dict, response: str, mapped_dim: str) -> str:
    """Generate conversion prompt for GPT-5."""
    dim_spec = DIMENSION_SPEC.get(mapped_dim, {})
    
    return f"""Convert this assertion to the standardized WBP format.

## Original Assertion (Kening's)
Text: "{assertion.get('text', '')}"
Level: {assertion.get('level', 'expected')}
Original Dimension: {assertion.get('anchors', {}).get('Dim', 'unknown')}
Source ID: {assertion.get('anchors', {}).get('sourceID', '')}

## Target Dimension: {mapped_dim} - {dim_spec.get('name', '')}
Layer: {dim_spec.get('layer', '').upper()}
Weight: {dim_spec.get('weight', 1)}
Template: "{dim_spec.get('template', '')}"
Definition: {dim_spec.get('definition', '')}
Evaluation: {dim_spec.get('evaluation', '')}

## Response Context (first 1500 chars)
{response[:1500]}

## Conversion Task
1. Rewrite the assertion using the template pattern for {mapped_dim}
2. Remove hardcoded values (replace with placeholders or source references)
3. Ensure it checks for PRESENCE (structural) or ACCURACY (grounding)
4. Assign appropriate level: critical/expected/aspirational

## Output Format
Return JSON:
```json
{{
    "original_text": "...",
    "converted_text": "Rewritten assertion following {mapped_dim} template",
    "dimension_id": "{mapped_dim}",
    "dimension_name": "{dim_spec.get('name', '')}",
    "layer": "{dim_spec.get('layer', '')}",
    "level": "critical|expected|aspirational",
    "weight": {dim_spec.get('weight', 1)},
    "sourceID": "{{source.FIELD}} if grounding, null if structural",
    "placeholders_used": ["[PLACEHOLDER1]", "[PLACEHOLDER2]"],
    "rationale": {{
        "mapping_reason": "Why this maps to {mapped_dim}",
        "conversion_changes": ["Change 1", "Change 2"],
        "template_alignment": "How it follows the template",
        "value_removed": "What hardcoded values were replaced"
    }},
    "quality_assessment": {{
        "is_well_formed": true|false,
        "is_testable": true|false,
        "issues": []
    }}
}}
```

Convert now:"""


def get_batch_conversion_prompt(assertions: List[Dict], response: str) -> str:
    """Generate batch conversion prompt."""
    items = []
    for i, a in enumerate(assertions):
        original_dim = a.get('anchors', {}).get('Dim', 'unknown')
        mapped_dim = DIMENSION_MAP.get(original_dim, "UNMAPPED")
        dim_spec = DIMENSION_SPEC.get(mapped_dim, {})
        
        items.append(f"""
{i+1}. Original: "{a.get('text', '')[:150]}..."
   Level: {a.get('level', 'expected')}
   Original Dim: {original_dim}
   → Target: {mapped_dim} ({dim_spec.get('name', 'Unknown')})
   Template: "{dim_spec.get('template', 'N/A')}"
""")
    
    return f"""Convert these assertions to the standardized WBP format.

## Response Context (first 1500 chars)
{response[:1500]}

## Assertions to Convert
{''.join(items)}

## Output Format
Return JSON with array of conversions:
```json
{{
    "conversions": [
        {{
            "index": 1,
            "original_text": "...",
            "converted_text": "Rewritten assertion following template",
            "dimension_id": "S1|S2|...|G5",
            "dimension_name": "...",
            "layer": "structural|grounding",
            "level": "critical|expected|aspirational",
            "weight": 1|2|3,
            "sourceID": "{{source.FIELD}} or null",
            "placeholders_used": [],
            "rationale": {{
                "mapping_reason": "...",
                "conversion_changes": [],
                "template_alignment": "...",
                "value_removed": "..."
            }},
            "quality_assessment": {{
                "is_well_formed": true,
                "is_testable": true,
                "issues": []
            }}
        }}
    ]
}}
```

Convert all assertions now:"""


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================

def load_data() -> List[Dict]:
    """Load Kening's assertions."""
    data = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def load_checkpoint() -> Dict:
    """Load checkpoint."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_index": -1, "results": []}


def save_checkpoint(checkpoint: Dict):
    """Save checkpoint."""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)


def convert_assertion_heuristic(assertion: Dict) -> Dict:
    """Heuristic conversion without GPT-5 - returns single assertion."""
    original_dim = assertion.get('anchors', {}).get('Dim', 'unknown')
    mapped_dim = DIMENSION_MAP.get(original_dim, "UNMAPPED")
    dim_spec = DIMENSION_SPEC.get(mapped_dim, {})
    original_text = assertion.get('text', '')
    level = assertion.get('level', 'expected')
    
    # Simple template-based conversion
    if mapped_dim != "UNMAPPED":
        template = dim_spec.get('template', '')
        # Use the template as converted text (simplified)
        converted_text = template
    else:
        converted_text = original_text
    
    return {
        "original_text": original_text,
        "converted_text": converted_text,
        "dimension_id": mapped_dim,
        "dimension_name": dim_spec.get('name', 'Unknown'),
        "layer": dim_spec.get('layer', 'unknown'),
        "level": level,
        "weight": dim_spec.get('weight', 1),
        "sourceID": None,
        "placeholders_used": [],
        "rationale": {
            "mapping_reason": f"Kening's '{original_dim}' maps to {mapped_dim} based on keyword matching",
            "conversion_changes": ["Applied template pattern"],
            "template_alignment": "Uses dimension template as base",
            "value_removed": "N/A (heuristic conversion)"
        },
        "quality_assessment": {
            "is_well_formed": mapped_dim != "UNMAPPED",
            "is_testable": mapped_dim != "UNMAPPED",
            "issues": ["Heuristic conversion - review recommended"] if mapped_dim == "UNMAPPED" else []
        },
        "conversion_method": "heuristic"
    }


def convert_assertion_with_grounding(assertion: Dict, assertion_index: int = 0) -> List[Dict]:
    """
    Convert assertion to S+G pair(s).
    
    For each original assertion:
    1. Generate the primary S (structural) assertion with unique assertion_id
    2. Generate corresponding G (grounding) assertions based on S_TO_G_MAP
    3. G assertions include parent_assertion_id linking back to their source S
    4. S and G assertions are returned adjacently in the list
    
    Returns: List of converted assertions (1 S + 0-N G assertions, kept adjacent)
    """
    import uuid
    
    results = []
    original_dim = assertion.get('anchors', {}).get('Dim', 'unknown')
    mapped_dim = DIMENSION_MAP.get(original_dim, "UNMAPPED")
    original_text = assertion.get('text', '')
    level = assertion.get('level', 'expected')
    
    # Generate unique ID for the primary assertion
    primary_assertion_id = f"A{assertion_index:04d}_{mapped_dim}"
    
    # Generate primary assertion (S or G)
    primary = convert_assertion_heuristic(assertion)
    primary["assertion_id"] = primary_assertion_id
    primary["parent_assertion_id"] = None  # Primary assertions have no parent
    results.append(primary)
    
    # If mapped to a structural dimension, add corresponding grounding assertions
    # These are kept adjacent to their parent S assertion
    if mapped_dim.startswith("S") and mapped_dim in S_TO_G_MAP:
        g_dims = S_TO_G_MAP[mapped_dim]
        
        for g_idx, g_dim in enumerate(g_dims):
            g_spec = DIMENSION_SPEC.get(g_dim, {})
            if not g_spec:
                continue
            
            # Generate unique ID for this G assertion
            g_assertion_id = f"A{assertion_index:04d}_{g_dim}_{g_idx}"
            
            # Create grounding assertion with parent linkage
            g_assertion = {
                "assertion_id": g_assertion_id,
                "parent_assertion_id": primary_assertion_id,  # Links to source S assertion
                "original_text": original_text,
                "converted_text": g_spec.get('template', ''),
                "dimension_id": g_dim,
                "dimension_name": g_spec.get('name', 'Unknown'),
                "layer": "grounding",
                "level": "critical",  # Grounding is always critical
                "weight": g_spec.get('weight', 3),
                "sourceID": None,
                "placeholders_used": [],
                "rationale": {
                    "mapping_reason": f"Generated from {mapped_dim} ({primary['dimension_name']}) via S_TO_G_MAP",
                    "conversion_changes": ["Applied grounding template for factual verification"],
                    "template_alignment": f"S→G mapping: {mapped_dim}→{g_dim}",
                    "value_removed": "N/A (grounding complement)",
                    "parent_dimension": mapped_dim,
                    "parent_dimension_name": primary['dimension_name']
                },
                "quality_assessment": {
                    "is_well_formed": True,
                    "is_testable": True,
                    "issues": []
                },
                "conversion_method": "heuristic_s_to_g",
                "derived_from": mapped_dim
            }
            results.append(g_assertion)
    
    return results


def convert_assertion_gpt5(assertion: Dict, response: str) -> Dict:
    """Convert assertion using GPT-5."""
    original_dim = assertion.get('anchors', {}).get('Dim', 'unknown')
    mapped_dim = DIMENSION_MAP.get(original_dim, "UNMAPPED")
    
    if mapped_dim == "UNMAPPED":
        return convert_assertion_heuristic(assertion)
    
    try:
        prompt = get_conversion_prompt(assertion, response, mapped_dim)
        result_text = call_gpt5_api(prompt, system_prompt=SYSTEM_PROMPT, temperature=0.2, max_tokens=1500)
        result = extract_json_from_response(result_text)
        result["conversion_method"] = "gpt5"
        return result
        
    except Exception as e:
        print(f"    ⚠️ GPT-5 error: {e}")
        return convert_assertion_heuristic(assertion)


def convert_batch_gpt5(assertions: List[Dict], response: str, retry_count: int = 0) -> List[Dict]:
    """Convert a batch of assertions using GPT-5 with self-throttling and retry logic."""
    try:
        prompt = get_batch_conversion_prompt(assertions, response)
        result_text = call_gpt5_api(prompt, system_prompt=SYSTEM_PROMPT, temperature=0.2, max_tokens=4000)
        result = extract_json_from_response(result_text)
        
        conversions = result.get("conversions", [])
        
        # Ensure we have results for all assertions
        results = []
        for i, a in enumerate(assertions):
            if i < len(conversions):
                conv = conversions[i]
                conv["conversion_method"] = "gpt5"
                results.append(conv)
            else:
                results.append(convert_assertion_heuristic(a))
        
        return results
        
    except Exception as e:
        error_str = str(e).lower()
        
        # Check for rate limit errors (429 or throttling messages)
        is_rate_limit = "429" in error_str or "rate" in error_str or "throttl" in error_str or "too many" in error_str
        
        if is_rate_limit and retry_count < MAX_RETRIES:
            # Exponential backoff
            backoff = min(INITIAL_BACKOFF * (2 ** retry_count), MAX_BACKOFF)
            print(f"    ⏳ Rate limited, backing off {backoff}s (retry {retry_count + 1}/{MAX_RETRIES})...")
            time.sleep(backoff)
            return convert_batch_gpt5(assertions, response, retry_count + 1)
        
        print(f"    ⚠️ Batch GPT-5 error: {e}")
        return [convert_assertion_heuristic(a) for a in assertions]


def compute_statistics(all_conversions: List[Dict]) -> Dict:
    """Compute conversion statistics."""
    total = len(all_conversions)
    if total == 0:
        return {}
    
    # Dimension distribution
    dim_counts = {}
    for c in all_conversions:
        dim = c.get("dimension_id", "UNMAPPED")
        dim_counts[dim] = dim_counts.get(dim, 0) + 1
    
    # Layer distribution
    layer_counts = {"structural": 0, "grounding": 0, "unknown": 0}
    for c in all_conversions:
        layer = c.get("layer", "unknown")
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    # Level distribution
    level_counts = {"critical": 0, "expected": 0, "aspirational": 0}
    for c in all_conversions:
        level = c.get("level", "expected")
        level_counts[level] = level_counts.get(level, 0) + 1
    
    # Quality assessment
    well_formed = sum(1 for c in all_conversions if c.get("quality_assessment", {}).get("is_well_formed"))
    testable = sum(1 for c in all_conversions if c.get("quality_assessment", {}).get("is_testable"))
    
    # Conversion method
    gpt5_converted = sum(1 for c in all_conversions if c.get("conversion_method") == "gpt5")
    heuristic_s_to_g = sum(1 for c in all_conversions if c.get("conversion_method") == "heuristic_s_to_g")
    
    # Count derived grounding assertions (from S_TO_G_MAP)
    derived_from_s = sum(1 for c in all_conversions if c.get("derived_from"))
    
    return {
        "total_assertions": total,
        "dimension_distribution": dim_counts,
        "layer_distribution": layer_counts,
        "level_distribution": level_counts,
        "well_formed_count": well_formed,
        "well_formed_rate": round(well_formed / total * 100, 1),
        "testable_count": testable,
        "testable_rate": round(testable / total * 100, 1),
        "gpt5_converted": gpt5_converted,
        "gpt5_rate": round(gpt5_converted / total * 100, 1),
        "unmapped_count": dim_counts.get("UNMAPPED", 0),
        "unmapped_rate": round(dim_counts.get("UNMAPPED", 0) / total * 100, 1),
        "s_to_g_derived": heuristic_s_to_g,
        "s_to_g_derived_rate": round(heuristic_s_to_g / total * 100, 1) if total > 0 else 0,
        "structural_count": layer_counts.get("structural", 0),
        "grounding_count": layer_counts.get("grounding", 0),
    }


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Convert Kening's assertions to Chin-Yew's format")
    parser.add_argument("--start", type=int, default=0, help="Start index")
    parser.add_argument("--end", type=int, default=None, help="End index")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--force", action="store_true", help="Force reprocess all")
    parser.add_argument("--dry-run", action="store_true", help="Use heuristic only (no GPT-5)")
    parser.add_argument("--batch-size", type=int, default=5, help="Assertions per GPT-5 call")
    parser.add_argument("--with-grounding", action="store_true", help="Generate S+G assertion pairs")
    args = parser.parse_args()
    
    print("=" * 70)
    print("Convert Kening's Assertions to Chin-Yew's WBP Format")
    print("=" * 70)
    print(f"Input: {INPUT_FILE}")
    print(f"Output 1 (Kening Enhanced): {OUTPUT_KENING_ENHANCED}")
    print(f"Output 2 (Full Conversion): {OUTPUT_CONVERTED_FULL}")
    print(f"Report: {REPORT_FILE}")
    print()
    
    # Load data
    print("📂 Loading data...")
    data = load_data()
    print(f"   Loaded {len(data)} meetings")
    
    # Determine range
    start_idx = args.start
    end_idx = args.end if args.end else len(data)
    end_idx = min(end_idx, len(data))
    print(f"   Processing meetings {start_idx + 1} to {end_idx}")
    
    # Load checkpoint
    if args.resume and not args.force:
        checkpoint = load_checkpoint()
        last_processed = checkpoint.get("last_index", -1)
        all_results = checkpoint.get("results", [])
        if last_processed >= start_idx:
            print(f"   Resuming from checkpoint (last processed: {last_processed + 1})")
            start_idx = last_processed + 1
    else:
        all_results = []
        if args.force and os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
            print("   Cleared previous checkpoint")
    
    # Initialize GPT-5
    if not args.dry_run:
        print()
        print("🔐 Initializing GPT-5 JJ API...")
        try:
            get_substrate_token()
            print("   ✅ Authentication successful")
            print(f"   🚦 Self-throttling: {DELAY_BETWEEN_BATCHES}s between batches, {MAX_RETRIES} retries with backoff")
            use_gpt5 = True
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            print("   Falling back to heuristic conversion...")
            use_gpt5 = False
    else:
        print()
        print("🔧 Dry-run mode: Using heuristic conversion only")
        use_gpt5 = False
    
    # S+G mode
    generate_grounding = args.with_grounding
    if generate_grounding:
        print()
        print("🔗 S+G Mode: Will generate grounding assertions for each structural assertion")
    
    print()
    print("🔄 Converting assertions...")
    print("-" * 70)
    
    # Process each meeting - store both original assertions and conversions
    for i in range(start_idx, end_idx):
        item = data[i]
        utterance = item.get('utterance', '')[:50]
        assertions = item.get('assertions', [])
        response = item.get('response', '')
        
        print(f"[{i + 1}/{end_idx}] {utterance}... ({len(assertions)} assertions)")
        
        meeting_conversions = []
        assertion_counter = 0  # Track assertion index for unique IDs
        
        # Process in batches
        batch_size = args.batch_size
        for j in range(0, len(assertions), batch_size):
            batch = assertions[j:j + batch_size]
            
            if use_gpt5:
                try:
                    batch_results = convert_batch_gpt5(batch, response)
                    meeting_conversions.extend(batch_results)
                    # Self-throttling: wait between batches to avoid rate limits
                    time.sleep(DELAY_BETWEEN_BATCHES)
                except Exception as e:
                    print(f"    ⚠️ Batch error: {e}")
                    for a in batch:
                        if generate_grounding:
                            meeting_conversions.extend(convert_assertion_with_grounding(a, assertion_counter))
                            assertion_counter += 1
                        else:
                            meeting_conversions.append(convert_assertion_heuristic(a))
            else:
                for a in batch:
                    if generate_grounding:
                        meeting_conversions.extend(convert_assertion_with_grounding(a, assertion_counter))
                        assertion_counter += 1
                    else:
                        meeting_conversions.append(convert_assertion_heuristic(a))        # Store meeting result with both original assertions and conversions
        all_results.append({
            "index": i,
            "utterance": item.get('utterance', ''),
            "response": item.get('response', ''),
            "original_assertions": assertions,  # Keep original for Kening-enhanced output
            "num_assertions": len(assertions),
            "conversions": meeting_conversions,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save checkpoint
        if (i - start_idx + 1) % BATCH_SIZE == 0:
            checkpoint = {"last_index": i, "results": all_results}
            save_checkpoint(checkpoint)
            print(f"    💾 Checkpoint saved")
        
        time.sleep(DELAY_BETWEEN_MEETINGS)
    
    # Compute statistics
    print()
    print("📈 Computing statistics...")
    
    all_conversions = []
    for r in all_results:
        all_conversions.extend(r.get("conversions", []))
    
    stats = compute_statistics(all_conversions)
    
    # =================================================================
    # OUTPUT 1: Kening's Schema with Minimal Enhancements
    # =================================================================
    print()
    print("💾 Saving Output 1: Kening-enhanced format...")
    
    with open(OUTPUT_KENING_ENHANCED, 'w', encoding='utf-8') as f:
        for result in all_results:
            # Preserve Kening's original schema, add metadata
            output_item = {
                "utterance": result["utterance"],
                "response": result["response"],
                "assertions": []
            }
            
            original_assertions = result.get("original_assertions", [])
            conversions = result.get("conversions", [])
            
            for idx, orig_assertion in enumerate(original_assertions):
                conv = conversions[idx] if idx < len(conversions) else {}
                
                # Keep Kening's original structure
                enhanced_assertion = {
                    # === Original Kening fields (preserved) ===
                    "text": orig_assertion.get("text", ""),
                    "level": orig_assertion.get("level", "expected"),
                    "anchors": orig_assertion.get("anchors", {}),
                    
                    # === New metadata for compatibility ===
                    "_mira_metadata": {
                        "dimension_id": conv.get("dimension_id", DIMENSION_MAP.get(
                            orig_assertion.get("anchors", {}).get("Dim", ""), "UNMAPPED")),
                        "dimension_name": conv.get("dimension_name", ""),
                        "layer": conv.get("layer", ""),
                        "weight": conv.get("weight", 1),
                        "sourceID": orig_assertion.get("anchors", {}).get("sourceID", ""),
                        "mapping_rationale": conv.get("rationale", {}).get("mapping_reason", "")
                    }
                }
                output_item["assertions"].append(enhanced_assertion)
            
            f.write(json.dumps(output_item, ensure_ascii=False) + "\n")
    
    print(f"   ✅ Saved to: {OUTPUT_KENING_ENHANCED}")
    
    # =================================================================
    # OUTPUT 2: Full Conversion with Comprehensive Details
    # =================================================================
    print()
    print("💾 Saving Output 2: Full conversion format...")
    
    # Build utterance -> USER map from Weiwei file
    utterance_to_user = {}
    if os.path.exists(WEIWEI_FILE):
        with open(WEIWEI_FILE, 'r', encoding='utf-8') as wf:
            for line in wf:
                item = json.loads(line)
                utt = item.get('UTTERANCE', {}).get('text', '')
                user = item.get('USER', {})
                if utt and utt not in utterance_to_user:
                    utterance_to_user[utt] = user
        print(f"   Loaded {len(utterance_to_user)} user mappings from Weiwei file")
    
    with open(OUTPUT_CONVERTED_FULL, 'w', encoding='utf-8') as f:
        for result in all_results:
            # Get USER from Weiwei file mapping
            user_data = utterance_to_user.get(result["utterance"], {})
            
            # Full conversion format with all details
            output_item = {
                "user": user_data,  # USER info from Weiwei file
                "utterance": result["utterance"],
                "response": result.get("response", ""),  # Include response from source
                "assertions": []
            }
            
            # Get original assertions for preserving sourceID
            original_assertions = result.get("original_assertions", [])
            
            # Track which original assertion index we're on for sourceID mapping
            orig_assertion_idx = 0
            
            for idx, conv in enumerate(result["conversions"]):
                # Get original sourceID - only for primary assertions (not derived G)
                orig_sourceID = ""
                is_derived = conv.get("conversion_method") == "heuristic_s_to_g"
                
                if not is_derived and orig_assertion_idx < len(original_assertions):
                    orig_sourceID = original_assertions[orig_assertion_idx].get("anchors", {}).get("sourceID", "")
                    orig_assertion_idx += 1
                elif is_derived:
                    # For derived G assertions, use the parent's sourceID from rationale
                    parent_id = conv.get("parent_assertion_id", "")
                    # sourceID for G assertions can be empty or inherited
                    orig_sourceID = ""
                
                # Build assertion output with S+G relationship fields
                assertion_output = {
                    "assertion_id": conv.get("assertion_id", ""),  # Unique ID for this assertion
                    "parent_assertion_id": conv.get("parent_assertion_id"),  # Link to source S (null for S assertions)
                    "text": conv.get("converted_text", ""),
                    "level": conv.get("level", "expected"),
                    "dimension": conv.get("dimension_id", "UNMAPPED"),
                    "dimension_name": conv.get("dimension_name", ""),
                    "layer": conv.get("layer", ""),
                    "weight": conv.get("weight", 1),
                    "sourceID": orig_sourceID,  # Use original sourceID for primary assertions
                    "original_text": conv.get("original_text", ""),
                    "rationale": conv.get("rationale", {}),
                    "quality_assessment": conv.get("quality_assessment", {}),
                    "conversion_method": conv.get("conversion_method", "unknown")
                }
                
                output_item["assertions"].append(assertion_output)
            f.write(json.dumps(output_item, ensure_ascii=False) + "\n")
    
    print(f"   ✅ Saved to: {OUTPUT_CONVERTED_FULL}")
    
    # =================================================================
    # Save Conversion Report
    # =================================================================
    print()
    print("💾 Saving conversion report...")
    
    report = {
        "metadata": {
            "input_file": INPUT_FILE,
            "output_kening_enhanced": OUTPUT_KENING_ENHANCED,
            "output_converted_full": OUTPUT_CONVERTED_FULL,
            "timestamp": datetime.now().isoformat(),
            "num_meetings": len(all_results),
            "total_assertions": stats.get("total_assertions", 0),
            "conversion_method": "gpt5" if use_gpt5 else "heuristic",
            "target_spec": "WBP_Selected_Dimensions.md"
        },
        "output_formats": {
            "kening_enhanced": {
                "description": "Kening's original schema with _mira_metadata added",
                "preserves": ["text", "level", "anchors"],
                "adds": ["_mira_metadata.dimension_id", "_mira_metadata.layer", "_mira_metadata.weight", "_mira_metadata.sourceID"]
            },
            "converted_full": {
                "description": "Full conversion to Chin-Yew's format with rationale",
                "includes": ["converted_text", "dimension", "layer", "weight", "original_text", "rationale", "quality_assessment"]
            }
        },
        "statistics": stats,
        "dimension_templates": {k: v.get("template", "") for k, v in DIMENSION_SPEC.items()},
        "dimension_mapping_used": {k: v for k, v in list(DIMENSION_MAP.items())[:20]},  # Sample of mappings
        "sample_conversions": all_results[:2] if all_results else []
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Report saved to: {REPORT_FILE}")
    
    # Clean up checkpoint
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
    
    # Print summary
    print()
    print("=" * 70)
    print("📊 CONVERSION SUMMARY")
    print("=" * 70)
    print(f"Total meetings: {len(all_results)}")
    print(f"Total assertions converted: {stats.get('total_assertions', 0)}")
    print(f"GPT-5 converted: {stats.get('gpt5_converted', 0)} ({stats.get('gpt5_rate', 0)}%)")
    print()
    
    print("📐 Dimension Distribution:")
    for dim in ["S1", "S2", "S3", "S4", "S5", "S6", "S11", "S18", "S19", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]:
        count = stats.get("dimension_distribution", {}).get(dim, 0)
        if count > 0:
            dim_name = DIMENSION_SPEC.get(dim, {}).get("name", dim)
            pct = round(count / stats.get("total_assertions", 1) * 100, 1)
            print(f"  {dim}: {count} ({pct}%) - {dim_name}")
    
    unmapped = stats.get("dimension_distribution", {}).get("UNMAPPED", 0)
    if unmapped > 0:
        print(f"  UNMAPPED: {unmapped} ({stats.get('unmapped_rate', 0)}%)")
    
    print()
    print("🎯 Layer Distribution:")
    for layer, count in stats.get("layer_distribution", {}).items():
        if count > 0:
            print(f"  {layer}: {count}")
    
    print()
    print("⚖️  Level Distribution:")
    for level, count in stats.get("level_distribution", {}).items():
        if count > 0:
            print(f"  {level}: {count}")
    
    print()
    print(f"✅ Well-formed: {stats.get('well_formed_rate', 0)}%")
    print(f"🧪 Testable: {stats.get('testable_rate', 0)}%")
    print()
    print(f"📄 Output files:")
    print(f"   - Kening Enhanced: {OUTPUT_KENING_ENHANCED}")
    print(f"   - Full Conversion: {OUTPUT_CONVERTED_FULL}")
    print(f"   - Conversion Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
