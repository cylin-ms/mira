#!/usr/bin/env python3
"""
GPT-5 Evaluation of Kening's Assertions Against Selected Dimensions

This script evaluates assertions from Kening's dataset against our selected
evaluation dimensions (S1-S6, S11, S18, S19, G1-G5).

Author: Chin-Yew Lin
Date: November 28, 2025
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Optional
from openai import AzureOpenAI

# =============================================================================
# CONFIGURATION
# =============================================================================

# File paths
INPUT_FILE = "docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl"
OUTPUT_FILE = "docs/ChinYew/assertion_evaluation_results.json"
CHECKPOINT_FILE = "docs/ChinYew/.evaluation_checkpoint.json"

# Evaluation parameters
START_INDEX = 0
NUM_SAMPLES = None  # None = all samples
BATCH_SIZE = 5  # Process N meetings before saving checkpoint

# Azure OpenAI Configuration
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://gpt-5.openai.azure.com/")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_API_VERSION = "2024-12-01-preview"
AZURE_DEPLOYMENT = "gpt-5-turbo"  # or your deployment name

# =============================================================================
# SELECTED DIMENSIONS (from WBP_Selected_Dimensions.md)
# =============================================================================

SELECTED_DIMENSIONS = {
    # Structural Dimensions
    "S1": {
        "name": "Meeting Details",
        "weight": 3,
        "level": "event/meeting",
        "definition": "Subject, date, time, timezone, attendee list clearly stated.",
        "evaluation": "Plan includes all meeting metadata; missing any field = fail."
    },
    "S2": {
        "name": "Timeline Alignment",
        "weight": 3,
        "level": "overall",
        "definition": "Backward scheduling (T-minus) with dependency-aware sequencing from meeting date.",
        "evaluation": "Tasks arranged in reverse order from meeting date; dependencies respected."
    },
    "S3": {
        "name": "Ownership Assignment",
        "weight": 3,
        "level": "task",
        "definition": "Named owners per task or role/skill placeholder if names unavailable.",
        "evaluation": "Every task has named owner or role/skill requirement stated."
    },
    "S4": {
        "name": "Deliverables & Artifacts",
        "weight": 2,
        "level": "task",
        "definition": "All outputs listed with working links, version/format specified.",
        "evaluation": "Deliverables traceable and accessible; missing links or versions = fail."
    },
    "S5": {
        "name": "Task Dates",
        "weight": 2,
        "level": "task",
        "definition": "Due dates for every task aligned with timeline sequencing.",
        "evaluation": "All tasks have due dates; dates match milestone/timeline logic."
    },
    "S6": {
        "name": "Dependencies & Blockers",
        "weight": 2,
        "level": "task",
        "definition": "Predecessors and risks identified; mitigation steps documented.",
        "evaluation": "Blockers and mitigations listed; absence = fail."
    },
    "S11": {
        "name": "Risk Mitigation Strategy",
        "weight": 2,
        "level": "risk",
        "definition": "Concrete contingencies for top risks with owners.",
        "evaluation": "Mitigation steps documented; vague 'monitor' = fail."
    },
    "S18": {
        "name": "Post-Event Actions",
        "weight": 1,
        "level": "post-event",
        "definition": "Wrap-up tasks, retrospectives, and reporting.",
        "evaluation": "Post-event steps listed; none = fail."
    },
    "S19": {
        "name": "Caveat & Clarification",
        "weight": 1,
        "level": "transparency",
        "definition": "Explicit disclosure of assumptions, missing information, uncertainties.",
        "evaluation": "Caveats and assumptions clearly stated; hidden assumptions = fail."
    },
    # Grounding Dimensions
    "G1": {
        "name": "Attendee Grounding",
        "weight": 3,
        "level": "grounding",
        "definition": "Attendees match source; no hallucinated names.",
        "evaluation": "All attendees verified against source list."
    },
    "G2": {
        "name": "Date/Time Grounding",
        "weight": 3,
        "level": "grounding",
        "definition": "Meeting date/time/timezone match the source.",
        "evaluation": "No deviation from source meeting schedule."
    },
    "G3": {
        "name": "Artifact Grounding",
        "weight": 2,
        "level": "grounding",
        "definition": "Files/decks referenced exist in the source repository.",
        "evaluation": "Artifacts validated; missing or fabricated = fail."
    },
    "G4": {
        "name": "Topic Grounding",
        "weight": 2,
        "level": "grounding",
        "definition": "Agenda topics align with source priorities/context.",
        "evaluation": "Topics match source; unrelated topics = fail."
    },
    "G5": {
        "name": "Hallucination Check",
        "weight": 3,
        "level": "grounding",
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
    
    # G1-G5: Grounding (map accuracy/grounding dimensions)
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
# GPT-5 EVALUATION PROMPT
# =============================================================================

EVALUATION_SYSTEM_PROMPT = """You are an expert evaluator for Workback Plan (WBP) assertions.

Your task is to evaluate whether each assertion correctly maps to the assigned dimension and assess its quality.

## Selected Dimensions

### Structural Dimensions (S)
- **S1 (Meeting Details)**: Subject, date, time, timezone, attendee list
- **S2 (Timeline Alignment)**: Backward scheduling, T-minus, dependency-aware sequencing
- **S3 (Ownership Assignment)**: Named owners per task or role/skill placeholder
- **S4 (Deliverables & Artifacts)**: Outputs with links, version/format specified
- **S5 (Task Dates)**: Due dates for every task aligned with timeline
- **S6 (Dependencies & Blockers)**: Predecessors, risks, mitigation steps
- **S11 (Risk Mitigation Strategy)**: Concrete contingencies with owners
- **S18 (Post-Event Actions)**: Wrap-up, retrospectives, reporting
- **S19 (Caveat & Clarification)**: Assumptions, missing info, uncertainties

### Grounding Dimensions (G)
- **G1 (Attendee Grounding)**: Attendees match source, no hallucinated names
- **G2 (Date/Time Grounding)**: Date/time/timezone match source
- **G3 (Artifact Grounding)**: Files exist in source repository
- **G4 (Topic Grounding)**: Topics align with source context
- **G5 (Hallucination Check)**: No fabricated entities

## Evaluation Criteria

For each assertion, evaluate:
1. **Dimension Mapping**: Is the assigned dimension correct? (correct/incorrect/partial)
2. **Assertion Quality**: Is the assertion well-formed and testable? (0=poor, 1=partial, 2=good)
3. **Specificity Issue**: Does the assertion have over-specificity problems? (true/false)
4. **Grounding Requirement**: Does this assertion require source verification? (true/false)

Respond in JSON format only."""

def get_evaluation_prompt(assertions: list, response: str) -> str:
    """Generate evaluation prompt for a batch of assertions."""
    assertions_text = "\n".join([
        f"{i+1}. [{a.get('level', 'unknown')}] {a.get('text', '')}\n   Original Dim: {a.get('anchors', {}).get('Dim', 'unknown')}\n   Mapped to: {DIMENSION_MAP.get(a.get('anchors', {}).get('Dim', ''), 'UNMAPPED')}"
        for i, a in enumerate(assertions)
    ])
    
    return f"""Evaluate the following assertions for a workback plan.

## Response Being Evaluated (first 500 chars):
{response[:500]}...

## Assertions to Evaluate:
{assertions_text}

## Output Format:
Return a JSON array with one object per assertion:
```json
[
  {{
    "index": 1,
    "assertion_text": "...",
    "original_dimension": "...",
    "mapped_dimension": "S1|S2|...|G5|UNMAPPED",
    "dimension_mapping_correct": "correct|incorrect|partial",
    "suggested_dimension": "S1|S2|...|G5|null",
    "quality_score": 0|1|2,
    "quality_reasoning": "...",
    "has_specificity_issue": true|false,
    "specificity_explanation": "...",
    "requires_grounding": true|false,
    "overall_assessment": "good|acceptable|needs_improvement|poor"
  }}
]
```

Evaluate each assertion now:"""

# =============================================================================
# MAIN EVALUATION FUNCTIONS
# =============================================================================

def load_checkpoint() -> dict:
    """Load checkpoint if exists."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_index": -1, "results": []}

def save_checkpoint(checkpoint: dict):
    """Save checkpoint."""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)

def load_data() -> list:
    """Load Kening's assertions data."""
    data = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def map_dimension(dim: str) -> str:
    """Map Kening's dimension to our selected dimensions."""
    return DIMENSION_MAP.get(dim, "UNMAPPED")

def create_client() -> AzureOpenAI:
    """Create Azure OpenAI client."""
    return AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION
    )

def evaluate_with_gpt5(client: AzureOpenAI, assertions: list, response: str) -> list:
    """Evaluate assertions using GPT-5."""
    try:
        completion = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
                {"role": "user", "content": get_evaluation_prompt(assertions, response)}
            ],
            temperature=0.1,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        result_text = completion.choices[0].message.content
        # Parse JSON response
        result = json.loads(result_text)
        if isinstance(result, dict) and "evaluations" in result:
            return result["evaluations"]
        elif isinstance(result, list):
            return result
        else:
            return [result]
    except Exception as e:
        print(f"  Error calling GPT-5: {e}")
        return []

def analyze_without_gpt5(assertions: list) -> list:
    """Analyze assertions without GPT-5 (dimension mapping only)."""
    results = []
    for i, a in enumerate(assertions):
        original_dim = a.get('anchors', {}).get('Dim', 'unknown')
        mapped_dim = map_dimension(original_dim)
        
        # Basic quality heuristics
        text = a.get('text', '')
        has_specificity = any(x in text.lower() for x in [
            "should state that", "should reference the file",
            "should identify", "should mention"
        ]) and any(c.isupper() for c in text[20:] if c.isalpha())  # Has proper nouns
        
        requires_grounding = mapped_dim.startswith('G') or any(x in text.lower() for x in [
            "attendee", "date", "time", "file", "artifact", "should match"
        ])
        
        results.append({
            "index": i + 1,
            "assertion_text": text[:100] + "..." if len(text) > 100 else text,
            "original_dimension": original_dim,
            "mapped_dimension": mapped_dim,
            "dimension_mapping_correct": "assumed_correct" if mapped_dim != "UNMAPPED" else "unmapped",
            "suggested_dimension": None,
            "quality_score": 1 if mapped_dim != "UNMAPPED" else 0,
            "quality_reasoning": "Automated mapping analysis",
            "has_specificity_issue": has_specificity,
            "specificity_explanation": "Contains specific names/values" if has_specificity else "",
            "requires_grounding": requires_grounding,
            "overall_assessment": "acceptable" if mapped_dim != "UNMAPPED" else "needs_improvement"
        })
    return results

def compute_statistics(results: list) -> dict:
    """Compute evaluation statistics."""
    total = len(results)
    if total == 0:
        return {}
    
    # Dimension distribution
    dim_counts = {}
    for r in results:
        dim = r.get("mapped_dimension", "UNMAPPED")
        dim_counts[dim] = dim_counts.get(dim, 0) + 1
    
    # Quality distribution
    quality_counts = {0: 0, 1: 0, 2: 0}
    for r in results:
        score = r.get("quality_score", 0)
        quality_counts[score] = quality_counts.get(score, 0) + 1
    
    # Issues
    specificity_issues = sum(1 for r in results if r.get("has_specificity_issue"))
    grounding_required = sum(1 for r in results if r.get("requires_grounding"))
    unmapped = dim_counts.get("UNMAPPED", 0)
    
    return {
        "total_assertions": total,
        "dimension_distribution": dim_counts,
        "quality_distribution": {
            "poor (0)": quality_counts[0],
            "partial (1)": quality_counts[1],
            "good (2)": quality_counts[2]
        },
        "average_quality": sum(r.get("quality_score", 0) for r in results) / total,
        "specificity_issues": specificity_issues,
        "specificity_rate": round(specificity_issues / total * 100, 1),
        "grounding_required": grounding_required,
        "grounding_rate": round(grounding_required / total * 100, 1),
        "unmapped_dimensions": unmapped,
        "unmapped_rate": round(unmapped / total * 100, 1)
    }

def main():
    """Main evaluation function."""
    print("=" * 70)
    print("GPT-5 Evaluation of Kening's Assertions")
    print("=" * 70)
    print(f"Input: {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print()
    
    # Load data
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} meetings")
    
    # Determine range
    end_index = len(data) if NUM_SAMPLES is None else min(START_INDEX + NUM_SAMPLES, len(data))
    data_to_process = data[START_INDEX:end_index]
    print(f"Processing meetings {START_INDEX + 1} to {end_index}")
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    last_processed = checkpoint.get("last_index", -1)
    all_results = checkpoint.get("results", [])
    
    if last_processed >= START_INDEX:
        print(f"Resuming from checkpoint (last processed: {last_processed + 1})")
    
    # Check if GPT-5 is available
    use_gpt5 = bool(AZURE_API_KEY)
    if use_gpt5:
        print("Using GPT-5 for evaluation")
        client = create_client()
    else:
        print("WARNING: No API key found. Using heuristic evaluation only.")
        client = None
    
    print()
    
    # Process each meeting
    for i, item in enumerate(data_to_process):
        global_idx = START_INDEX + i
        
        # Skip if already processed
        if global_idx <= last_processed:
            continue
        
        utterance = item.get('utterance', '')[:50]
        assertions = item.get('assertions', [])
        response = item.get('response', '')
        
        print(f"[{global_idx + 1}/{end_index}] {utterance}... ({len(assertions)} assertions)")
        
        # Evaluate assertions
        if use_gpt5 and client:
            eval_results = evaluate_with_gpt5(client, assertions, response)
        else:
            eval_results = analyze_without_gpt5(assertions)
        
        # Store results
        meeting_result = {
            "index": global_idx,
            "utterance": item.get('utterance', ''),
            "num_assertions": len(assertions),
            "assertion_evaluations": eval_results,
            "timestamp": datetime.now().isoformat()
        }
        all_results.append(meeting_result)
        
        # Save checkpoint periodically
        if (i + 1) % BATCH_SIZE == 0:
            checkpoint = {"last_index": global_idx, "results": all_results}
            save_checkpoint(checkpoint)
            print(f"  Checkpoint saved at index {global_idx + 1}")
    
    # Compute final statistics
    print()
    print("Computing statistics...")
    
    all_evaluations = []
    for r in all_results:
        all_evaluations.extend(r.get("assertion_evaluations", []))
    
    stats = compute_statistics(all_evaluations)
    
    # Save final results
    final_output = {
        "metadata": {
            "input_file": INPUT_FILE,
            "timestamp": datetime.now().isoformat(),
            "num_meetings": len(all_results),
            "total_assertions": stats.get("total_assertions", 0),
            "evaluation_method": "gpt5" if use_gpt5 else "heuristic"
        },
        "statistics": stats,
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
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total meetings evaluated: {len(all_results)}")
    print(f"Total assertions evaluated: {stats.get('total_assertions', 0)}")
    print()
    print("Dimension Distribution:")
    for dim, count in sorted(stats.get("dimension_distribution", {}).items()):
        dim_name = SELECTED_DIMENSIONS.get(dim, {}).get("name", dim)
        print(f"  {dim}: {count} ({dim_name})")
    print()
    print("Quality Distribution:")
    for level, count in stats.get("quality_distribution", {}).items():
        print(f"  {level}: {count}")
    print()
    print(f"Average Quality Score: {stats.get('average_quality', 0):.2f}/2.0")
    print(f"Specificity Issues: {stats.get('specificity_rate', 0)}%")
    print(f"Grounding Required: {stats.get('grounding_rate', 0)}%")
    print(f"Unmapped Dimensions: {stats.get('unmapped_rate', 0)}%")
    print()
    print(f"Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
