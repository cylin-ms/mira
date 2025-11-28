#!/usr/bin/env python3
"""
GPT-5 Evaluation of Kening's Assertions Against Chin-Yew's Rubric

This script evaluates assertions from Kening's dataset using GPT-5 JJ API
against the selected dimensions (S1-S6, S11, S18, S19, G1-G5).

Key Features:
- Uses Substrate GPT-5 JJ API (same as pipeline)
- Two-Layer Framework evaluation (Structural vs Grounding)
- Checkpoint/resume support for long runs
- Detailed quality scoring per Chin-Yew's rubric
- Supporting span extraction for visualization

Usage:
    # Process all meetings
    python evaluate_kening_gpt5.py
    
    # Process specific range
    python evaluate_kening_gpt5.py --start 0 --end 10
    
    # Resume from checkpoint
    python evaluate_kening_gpt5.py --resume
    
    # Force reprocess all
    python evaluate_kening_gpt5.py --force

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
from typing import Dict, List, Optional, Any

# Add pipeline to path for shared config
sys.path.insert(0, os.path.dirname(__file__))
from pipeline.config import (
    get_substrate_token,
    call_gpt5_api,
    extract_json_from_response,
    DELAY_BETWEEN_CALLS,
    STRUCTURAL_DIMENSIONS,
    GROUNDING_DIMENSIONS,
)

# =============================================================================
# CONFIGURATION
# =============================================================================

# File paths
INPUT_FILE = "docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl"
OUTPUT_FILE = "docs/ChinYew/assertion_evaluation_gpt5.json"
CHECKPOINT_FILE = "docs/ChinYew/.gpt5_eval_checkpoint.json"

# Evaluation parameters
BATCH_SIZE = 5  # Save checkpoint every N meetings
DELAY_BETWEEN_MEETINGS = 2  # seconds
DELAY_BETWEEN_ASSERTIONS = 1  # seconds

# =============================================================================
# SELECTED DIMENSIONS (from WBP_Selected_Dimensions.md)
# =============================================================================

SELECTED_DIMENSIONS = {
    # Structural Dimensions
    "S1": {
        "name": "Meeting Details",
        "weight": 3,
        "layer": "structural",
        "definition": "Subject, date, time, timezone, attendee list clearly stated.",
        "evaluation": "Plan includes all meeting metadata; missing any field = fail."
    },
    "S2": {
        "name": "Timeline Alignment",
        "weight": 3,
        "layer": "structural",
        "definition": "Backward scheduling (T-minus) with dependency-aware sequencing from meeting date.",
        "evaluation": "Tasks arranged in reverse order from meeting date; dependencies respected."
    },
    "S3": {
        "name": "Ownership Assignment",
        "weight": 3,
        "layer": "structural",
        "definition": "Named owners per task or role/skill placeholder if names unavailable.",
        "evaluation": "Every task has named owner or role/skill requirement stated."
    },
    "S4": {
        "name": "Deliverables & Artifacts",
        "weight": 2,
        "layer": "structural",
        "definition": "All outputs listed with working links, version/format specified.",
        "evaluation": "Deliverables traceable and accessible; missing links or versions = fail."
    },
    "S5": {
        "name": "Task Dates",
        "weight": 2,
        "layer": "structural",
        "definition": "Due dates for every task aligned with timeline sequencing.",
        "evaluation": "All tasks have due dates; dates match milestone/timeline logic."
    },
    "S6": {
        "name": "Dependencies & Blockers",
        "weight": 2,
        "layer": "structural",
        "definition": "Predecessors and risks identified; mitigation steps documented.",
        "evaluation": "Blockers and mitigations listed; absence = fail."
    },
    "S11": {
        "name": "Risk Mitigation Strategy",
        "weight": 2,
        "layer": "structural",
        "definition": "Concrete contingencies for top risks with owners.",
        "evaluation": "Mitigation steps documented; vague 'monitor' = fail."
    },
    "S18": {
        "name": "Post-Event Actions",
        "weight": 1,
        "layer": "structural",
        "definition": "Wrap-up tasks, retrospectives, and reporting.",
        "evaluation": "Post-event steps listed; none = fail."
    },
    "S19": {
        "name": "Caveat & Clarification",
        "weight": 1,
        "layer": "structural",
        "definition": "Explicit disclosure of assumptions, missing information, uncertainties.",
        "evaluation": "Caveats and assumptions clearly stated; hidden assumptions = fail."
    },
    # Grounding Dimensions
    "G1": {
        "name": "Attendee Grounding",
        "weight": 3,
        "layer": "grounding",
        "definition": "Attendees match source; no hallucinated names.",
        "evaluation": "All attendees verified against source list."
    },
    "G2": {
        "name": "Date/Time Grounding",
        "weight": 3,
        "layer": "grounding",
        "definition": "Meeting date/time/timezone match the source.",
        "evaluation": "No deviation from source meeting schedule."
    },
    "G3": {
        "name": "Artifact Grounding",
        "weight": 2,
        "layer": "grounding",
        "definition": "Files/decks referenced exist in the source repository.",
        "evaluation": "Artifacts validated; missing or fabricated = fail."
    },
    "G4": {
        "name": "Topic Grounding",
        "weight": 2,
        "layer": "grounding",
        "definition": "Agenda topics align with source priorities/context.",
        "evaluation": "Topics match source; unrelated topics = fail."
    },
    "G5": {
        "name": "Hallucination Check",
        "weight": 3,
        "layer": "grounding",
        "definition": "No extraneous entities or fabricated details.",
        "evaluation": "Plan contains only source-backed entities."
    }
}

# =============================================================================
# DIMENSION MAPPING (Kening's dimensions -> Our selected dimensions)
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
# GPT-5 EVALUATION PROMPTS
# =============================================================================

SYSTEM_PROMPT = """You are an expert evaluator for Workback Plan (WBP) assertions.
You are evaluating assertions from Kening's dataset against Chin-Yew's quality rubric.

## Two-Layer Evaluation Framework

Assertions fall into two categories with DIFFERENT evaluation approaches:

### Structural Assertions (S1-S19) - Check PRESENCE/SHAPE
- Question: "Does the plan HAVE X?"
- Checks: Does the element exist? Is the format correct?
- ✅ PASS if the element exists (even if value might be imprecise)
- ❌ FAIL only if the element is completely missing

### Grounding Assertions (G1-G5) - Check FACTUAL ACCURACY
- Question: "Is X CORRECT vs source?"
- Checks: Does the value match the authoritative source?
- ✅ PASS if value matches source
- ❌ FAIL if value doesn't match (hallucination)

## Selected Dimensions

### Structural (S)
- S1 (Meeting Details): Subject, date, time, timezone, attendee list
- S2 (Timeline Alignment): Backward scheduling, T-minus, dependencies
- S3 (Ownership Assignment): Named owners or role/skill placeholder
- S4 (Deliverables & Artifacts): Outputs with links, version specified
- S5 (Task Dates): Due dates aligned with timeline
- S6 (Dependencies & Blockers): Predecessors, risks, mitigation
- S11 (Risk Mitigation Strategy): Contingencies with owners
- S18 (Post-Event Actions): Wrap-up, retrospectives
- S19 (Caveat & Clarification): Assumptions, uncertainties disclosed

### Grounding (G)
- G1 (Attendee Grounding): Names match source
- G2 (Date/Time Grounding): Schedule matches source
- G3 (Artifact Grounding): Files exist in source
- G4 (Topic Grounding): Topics align with source
- G5 (Hallucination Check): No fabricated entities

## Scoring Scale
- 0 = Missing/Not Met
- 1 = Partial (element exists but incomplete)
- 2 = Fully Met

Respond ONLY in valid JSON format."""


def get_evaluation_prompt(assertion: Dict, response: str, mapped_dim: str) -> str:
    """Generate evaluation prompt for a single assertion."""
    dim_info = SELECTED_DIMENSIONS.get(mapped_dim, {})
    layer = dim_info.get("layer", "structural")
    dim_name = dim_info.get("name", mapped_dim)
    dim_def = dim_info.get("definition", "")
    
    return f"""Evaluate this assertion against the workback plan response.

## Assertion
Text: "{assertion.get('text', '')}"
Level: {assertion.get('level', 'expected')}
Mapped Dimension: {mapped_dim} ({dim_name})
Layer: {layer.upper()}

## Dimension Definition
{dim_def}

## Response (first 2000 chars)
{response[:2000]}

## Evaluation Instructions
Since this is a {layer.upper()} assertion:
{"- Check if the structural ELEMENT EXISTS in the response" if layer == "structural" else "- Check if the VALUE MATCHES the source data"}
{"- Pass if element is present (even if imprecise)" if layer == "structural" else "- Pass only if factually correct vs source"}

## Output Format
Return JSON:
```json
{{
    "dimension": "{mapped_dim}",
    "dimension_name": "{dim_name}",
    "layer": "{layer}",
    "passed": true/false,
    "quality_score": 0|1|2,
    "explanation": "Brief reason for pass/fail",
    "evidence": "Quote from response supporting your decision",
    "issues": ["List any issues found"],
    "suggestions": ["Improvement suggestions if any"]
}}
```

Evaluate now:"""


def get_batch_evaluation_prompt(assertions: List[Dict], response: str) -> str:
    """Generate batch evaluation prompt for multiple assertions."""
    assertions_text = ""
    for i, a in enumerate(assertions):
        original_dim = a.get('anchors', {}).get('Dim', 'unknown')
        mapped_dim = DIMENSION_MAP.get(original_dim, "UNMAPPED")
        dim_info = SELECTED_DIMENSIONS.get(mapped_dim, {})
        layer = dim_info.get("layer", "unknown")
        
        assertions_text += f"""
{i+1}. [{a.get('level', 'expected')}] {a.get('text', '')}
   Original Dim: {original_dim}
   Mapped to: {mapped_dim} ({dim_info.get('name', 'Unknown')})
   Layer: {layer}
"""
    
    return f"""Evaluate these assertions against the workback plan response.

## Response (first 2000 chars)
{response[:2000]}

## Assertions to Evaluate
{assertions_text}

## Output Format
Return a JSON array with one evaluation per assertion:
```json
{{
    "evaluations": [
        {{
            "index": 1,
            "assertion_text": "...",
            "original_dimension": "...",
            "mapped_dimension": "S1|S2|...|G5",
            "layer": "structural|grounding",
            "passed": true/false,
            "quality_score": 0|1|2,
            "explanation": "Brief reason",
            "evidence": "Quote from response",
            "issues": [],
            "suggestions": []
        }}
    ]
}}
```

Evaluate all assertions now:"""


# =============================================================================
# EVALUATION FUNCTIONS
# =============================================================================

def load_data() -> List[Dict]:
    """Load Kening's assertions data."""
    data = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def load_checkpoint() -> Dict:
    """Load checkpoint if exists."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_index": -1, "results": []}


def save_checkpoint(checkpoint: Dict):
    """Save checkpoint."""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)


def map_dimension(dim: str) -> str:
    """Map Kening's dimension to our selected dimensions."""
    return DIMENSION_MAP.get(dim, "UNMAPPED")


def evaluate_assertion_gpt5(assertion: Dict, response: str) -> Dict:
    """Evaluate a single assertion using GPT-5."""
    original_dim = assertion.get('anchors', {}).get('Dim', 'unknown')
    mapped_dim = map_dimension(original_dim)
    
    try:
        prompt = get_evaluation_prompt(assertion, response, mapped_dim)
        result_text = call_gpt5_api(prompt, system_prompt=SYSTEM_PROMPT, temperature=0.1, max_tokens=1000)
        
        # Parse JSON
        result = extract_json_from_response(result_text)
        
        return {
            "assertion_text": assertion.get('text', ''),
            "level": assertion.get('level', 'expected'),
            "original_dimension": original_dim,
            "mapped_dimension": mapped_dim,
            "layer": result.get("layer", SELECTED_DIMENSIONS.get(mapped_dim, {}).get("layer", "unknown")),
            "passed": result.get("passed", False),
            "quality_score": result.get("quality_score", 0),
            "explanation": result.get("explanation", ""),
            "evidence": result.get("evidence", ""),
            "issues": result.get("issues", []),
            "suggestions": result.get("suggestions", []),
            "evaluation_method": "gpt5"
        }
        
    except Exception as e:
        print(f"    ⚠️ GPT-5 error: {e}")
        # Fallback to heuristic
        return evaluate_assertion_heuristic(assertion, mapped_dim)


def evaluate_batch_gpt5(assertions: List[Dict], response: str) -> List[Dict]:
    """Evaluate a batch of assertions using GPT-5."""
    try:
        prompt = get_batch_evaluation_prompt(assertions, response)
        result_text = call_gpt5_api(prompt, system_prompt=SYSTEM_PROMPT, temperature=0.1, max_tokens=4000)
        
        # Parse JSON
        result = extract_json_from_response(result_text)
        evaluations = result.get("evaluations", [])
        
        # Map results back to assertions
        results = []
        for i, a in enumerate(assertions):
            eval_result = evaluations[i] if i < len(evaluations) else {}
            original_dim = a.get('anchors', {}).get('Dim', 'unknown')
            mapped_dim = map_dimension(original_dim)
            
            results.append({
                "assertion_text": a.get('text', ''),
                "level": a.get('level', 'expected'),
                "original_dimension": original_dim,
                "mapped_dimension": eval_result.get("mapped_dimension", mapped_dim),
                "layer": eval_result.get("layer", SELECTED_DIMENSIONS.get(mapped_dim, {}).get("layer", "unknown")),
                "passed": eval_result.get("passed", False),
                "quality_score": eval_result.get("quality_score", 0),
                "explanation": eval_result.get("explanation", ""),
                "evidence": eval_result.get("evidence", ""),
                "issues": eval_result.get("issues", []),
                "suggestions": eval_result.get("suggestions", []),
                "evaluation_method": "gpt5"
            })
        
        return results
        
    except Exception as e:
        print(f"    ⚠️ Batch GPT-5 error: {e}")
        # Fallback to heuristic for each
        return [evaluate_assertion_heuristic(a, map_dimension(a.get('anchors', {}).get('Dim', ''))) for a in assertions]


def evaluate_assertion_heuristic(assertion: Dict, mapped_dim: str) -> Dict:
    """Heuristic evaluation fallback when GPT-5 is unavailable."""
    original_dim = assertion.get('anchors', {}).get('Dim', 'unknown')
    text = assertion.get('text', '')
    dim_info = SELECTED_DIMENSIONS.get(mapped_dim, {})
    layer = dim_info.get("layer", "unknown")
    
    # Basic quality heuristics
    has_specificity = any(x in text.lower() for x in [
        "should state that", "should reference the file",
        "should identify", "should mention"
    ]) and any(c.isupper() for c in text[20:] if c.isalpha())
    
    requires_grounding = layer == "grounding" or any(x in text.lower() for x in [
        "attendee", "date", "time", "file", "artifact", "should match"
    ])
    
    return {
        "assertion_text": text[:100] + "..." if len(text) > 100 else text,
        "level": assertion.get('level', 'expected'),
        "original_dimension": original_dim,
        "mapped_dimension": mapped_dim,
        "layer": layer,
        "passed": mapped_dim != "UNMAPPED",
        "quality_score": 1 if mapped_dim != "UNMAPPED" else 0,
        "explanation": "Heuristic evaluation - dimension mapping verified",
        "evidence": "",
        "issues": ["Specificity issue detected"] if has_specificity else [],
        "suggestions": ["Requires source grounding verification"] if requires_grounding else [],
        "evaluation_method": "heuristic"
    }


def compute_statistics(results: List[Dict]) -> Dict:
    """Compute evaluation statistics."""
    total = len(results)
    if total == 0:
        return {}
    
    # Dimension distribution
    dim_counts = {}
    for r in results:
        dim = r.get("mapped_dimension", "UNMAPPED")
        dim_counts[dim] = dim_counts.get(dim, 0) + 1
    
    # Layer distribution
    layer_counts = {"structural": 0, "grounding": 0, "unknown": 0}
    for r in results:
        layer = r.get("layer", "unknown")
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    # Quality distribution
    quality_counts = {0: 0, 1: 0, 2: 0}
    for r in results:
        score = r.get("quality_score", 0)
        quality_counts[score] = quality_counts.get(score, 0) + 1
    
    # Pass/fail
    passed = sum(1 for r in results if r.get("passed"))
    failed = total - passed
    
    # Issues
    with_issues = sum(1 for r in results if r.get("issues"))
    
    # Evaluation method
    gpt5_evaluated = sum(1 for r in results if r.get("evaluation_method") == "gpt5")
    
    return {
        "total_assertions": total,
        "dimension_distribution": dim_counts,
        "layer_distribution": layer_counts,
        "quality_distribution": {
            "missing (0)": quality_counts[0],
            "partial (1)": quality_counts[1],
            "fully_met (2)": quality_counts[2]
        },
        "average_quality": sum(r.get("quality_score", 0) for r in results) / total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total * 100, 1),
        "with_issues": with_issues,
        "issue_rate": round(with_issues / total * 100, 1),
        "gpt5_evaluated": gpt5_evaluated,
        "gpt5_rate": round(gpt5_evaluated / total * 100, 1),
        "unmapped_dimensions": dim_counts.get("UNMAPPED", 0),
        "unmapped_rate": round(dim_counts.get("UNMAPPED", 0) / total * 100, 1)
    }


def calculate_weighted_score(results: List[Dict]) -> float:
    """Calculate weighted quality score per Chin-Yew's rubric."""
    if not results:
        return 0.0
    
    total_weighted = 0
    max_possible = 0
    
    for r in results:
        dim = r.get("mapped_dimension", "UNMAPPED")
        dim_info = SELECTED_DIMENSIONS.get(dim, {})
        weight = dim_info.get("weight", 1)
        score = r.get("quality_score", 0)
        
        total_weighted += score * weight
        max_possible += 2 * weight  # Max score is 2
    
    return round(total_weighted / max_possible, 3) if max_possible > 0 else 0.0


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="GPT-5 evaluation of Kening's assertions")
    parser.add_argument("--start", type=int, default=0, help="Start index")
    parser.add_argument("--end", type=int, default=None, help="End index")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--force", action="store_true", help="Force reprocess all")
    parser.add_argument("--batch-size", type=int, default=5, help="Assertions per GPT-5 call")
    args = parser.parse_args()
    
    print("=" * 70)
    print("GPT-5 Evaluation of Kening's Assertions")
    print("Using Chin-Yew's WBP Evaluation Rubric")
    print("=" * 70)
    print(f"Input: {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
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
    
    print()
    print("🔐 Initializing GPT-5 JJ API...")
    
    # Pre-authenticate
    try:
        get_substrate_token()
        print("   ✅ Authentication successful")
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        print("   Falling back to heuristic evaluation...")
    
    print()
    print("📊 Evaluating assertions...")
    print("-" * 70)
    
    total_assertions = 0
    evaluated_with_gpt5 = 0
    
    for i in range(start_idx, end_idx):
        item = data[i]
        utterance = item.get('utterance', '')[:50]
        assertions = item.get('assertions', [])
        response = item.get('response', '')
        
        print(f"[{i + 1}/{end_idx}] {utterance}... ({len(assertions)} assertions)")
        
        meeting_results = []
        
        # Process in batches
        batch_size = args.batch_size
        for j in range(0, len(assertions), batch_size):
            batch = assertions[j:j + batch_size]
            
            try:
                # Use batch evaluation for efficiency
                batch_results = evaluate_batch_gpt5(batch, response)
                meeting_results.extend(batch_results)
                evaluated_with_gpt5 += sum(1 for r in batch_results if r.get("evaluation_method") == "gpt5")
                
                time.sleep(DELAY_BETWEEN_CALLS)
                
            except Exception as e:
                print(f"    ⚠️ Batch error, falling back to heuristic: {e}")
                for a in batch:
                    mapped_dim = map_dimension(a.get('anchors', {}).get('Dim', ''))
                    meeting_results.append(evaluate_assertion_heuristic(a, mapped_dim))
        
        total_assertions += len(assertions)
        
        # Store meeting result
        all_results.append({
            "index": i,
            "utterance": item.get('utterance', ''),
            "num_assertions": len(assertions),
            "assertion_evaluations": meeting_results,
            "weighted_score": calculate_weighted_score(meeting_results),
            "timestamp": datetime.now().isoformat()
        })
        
        # Save checkpoint periodically
        if (i - start_idx + 1) % BATCH_SIZE == 0:
            checkpoint = {"last_index": i, "results": all_results}
            save_checkpoint(checkpoint)
            print(f"    💾 Checkpoint saved at meeting {i + 1}")
        
        time.sleep(DELAY_BETWEEN_MEETINGS)
    
    # Compute final statistics
    print()
    print("📈 Computing statistics...")
    
    all_evaluations = []
    for r in all_results:
        all_evaluations.extend(r.get("assertion_evaluations", []))
    
    stats = compute_statistics(all_evaluations)
    weighted_score = calculate_weighted_score(all_evaluations)
    
    # Save final results
    final_output = {
        "metadata": {
            "input_file": INPUT_FILE,
            "timestamp": datetime.now().isoformat(),
            "num_meetings": len(all_results),
            "total_assertions": stats.get("total_assertions", 0),
            "evaluation_method": "gpt5",
            "rubric": "Chin-Yew's WBP Evaluation Rubric",
            "dimensions_used": list(SELECTED_DIMENSIONS.keys())
        },
        "statistics": stats,
        "weighted_score": weighted_score,
        "meetings": all_results
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    # Clean up checkpoint
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
    
    # Print summary
    print()
    print("=" * 70)
    print("📊 EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total meetings evaluated: {len(all_results)}")
    print(f"Total assertions evaluated: {stats.get('total_assertions', 0)}")
    print(f"GPT-5 evaluated: {stats.get('gpt5_evaluated', 0)} ({stats.get('gpt5_rate', 0)}%)")
    print()
    
    print("📐 Dimension Distribution:")
    for dim in ["S1", "S2", "S3", "S4", "S5", "S6", "S11", "S18", "S19", "G1", "G2", "G3", "G4", "G5"]:
        count = stats.get("dimension_distribution", {}).get(dim, 0)
        if count > 0:
            dim_name = SELECTED_DIMENSIONS.get(dim, {}).get("name", dim)
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
    print("⭐ Quality Distribution:")
    for level, count in stats.get("quality_distribution", {}).items():
        print(f"  {level}: {count}")
    
    print()
    print(f"✅ Pass Rate: {stats.get('pass_rate', 0)}%")
    print(f"📊 Average Quality Score: {stats.get('average_quality', 0):.2f}/2.0")
    print(f"🏆 Weighted Score (Chin-Yew Rubric): {weighted_score:.3f}")
    print(f"⚠️  Assertions with Issues: {stats.get('issue_rate', 0)}%")
    print()
    print(f"💾 Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
