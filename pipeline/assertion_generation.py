"""
Stage 2: Assertion Generation

Generates two-layer assertions following the framework:
- Structural Assertions (S1-S10): Check PRESENCE/SHAPE
- Grounding Assertions (G1-G5): Check FACTUAL ACCURACY

Key Rules:
1. Structural assertions should NOT contain hardcoded values
2. Grounding assertions MUST reference source fields
3. Never mix grounding logic into structural assertions

Usage:
    python -m pipeline.assertion_generation
    python -m pipeline.assertion_generation --scenarios docs/pipeline_output/scenarios.json
"""

import json
import argparse
import time
from datetime import datetime
from typing import List, Dict

from .config import (
    Scenario,
    StructuralAssertion,
    GroundingAssertion,
    AssertionSet,
    SCENARIOS_FILE,
    ASSERTIONS_FILE,
    save_json,
    load_json,
    call_gpt5_api,
    extract_json_from_response,
    DELAY_BETWEEN_CALLS
)


# ═══════════════════════════════════════════════════════════════════════════════
# Two-Layer Assertion Framework Definition
# ═══════════════════════════════════════════════════════════════════════════════

STRUCTURAL_PATTERNS = """
## STRUCTURAL ASSERTION PATTERNS (S1-S10)

Purpose: Check if the plan HAS required elements (PRESENCE/SHAPE)
Question: "Does the plan HAVE X?"
Key Rule: Do NOT include specific values - only check if the element EXISTS

| ID | Pattern Name | Checks For | Example |
|----|--------------|------------|---------|
| S1 | Explicit Meeting Details | Has date, time, timezone, attendees listed | "The plan includes a meeting date and time" |
| S2 | Timeline Alignment | Has timeline working back from meeting | "The plan has a timeline with dates before the meeting" |
| S3 | Ownership Assignment | Has named owners (not "someone", "team") | "Each task has a specifically named owner" |
| S4 | Artifact Specification | Lists specific files/documents | "The plan references specific artifacts" |
| S5 | Date Specification | States completion dates for tasks | "Tasks have specified due dates" |
| S6 | Blocker Identification | Identifies dependencies and blockers | "The plan identifies blockers or dependencies" |
| S7 | Source Traceability | Links tasks to specific source entities | "Tasks are linked to source materials" |
| S8 | Communication Channels | Mentions appropriate communication methods | "The plan specifies how to communicate updates" |
| S9 | Grounding Meta-Check | Passes when G1-G5 all pass | "Content is grounded in provided context" |
| S10 | Priority Assignment | Has priority levels for tasks | "Tasks have priority or importance indicators" |

⚠️ ANTI-PATTERN: "The plan states the meeting date as January 15" ← This is GROUNDING, not structural!
✅ CORRECT: "The plan includes a meeting date" ← Checks presence only
"""

GROUNDING_PATTERNS = """
## GROUNDING ASSERTION PATTERNS (G1-G5)

Purpose: Check if values are CORRECT vs source (FACTUAL ACCURACY)
Question: "Is X CORRECT?"
Key Rule: MUST reference a source field for comparison

| ID | Pattern Name | Source Field | Verification |
|----|--------------|--------------|--------------|
| G1 | People Grounding | source.attendees | All people mentioned must exist in attendee list |
| G2 | Temporal Grounding | source.meeting_date, source.meeting_time | Dates/times must match source |
| G3 | Artifact Grounding | source.files | All files referenced must exist in source |
| G4 | Topic Grounding | source.topics | Topics must align with meeting subject |
| G5 | Hallucination Check | ALL source fields | No fabricated entities (people, files, dates) |

⚠️ ANTI-PATTERN: "All attendees are correct" ← Vague, no source reference!
✅ CORRECT: "All people mentioned exist in source.attendees" ← Explicit source reference
"""

TWO_LAYER_FRAMEWORK = f"""
# TWO-LAYER ASSERTION FRAMEWORK

{STRUCTURAL_PATTERNS}

{GROUNDING_PATTERNS}

## CRITICAL DISTINCTION

| Layer | Question | Checks For | Pass If | Fail If |
|-------|----------|------------|---------|---------|
| Structural | "Does plan HAVE X?" | Presence/Shape | Element exists | Element missing |
| Grounding | "Is X CORRECT?" | Accuracy vs source | Value matches source | Hallucination |

## COMMON MISTAKES TO AVOID

1. ❌ Hardcoded values in structural: "Plan states date as January 15"
   ✅ Correct: "Plan includes a meeting date"

2. ❌ Missing source reference in grounding: "All dates are correct"
   ✅ Correct: "Meeting date matches source.meeting_date"

3. ❌ Mixing layers: "Plan has correct attendees"
   ✅ Correct: Split into S (has attendees) + G (match source.attendees)
"""


# ═══════════════════════════════════════════════════════════════════════════════
# Assertion Generation Prompts
# ═══════════════════════════════════════════════════════════════════════════════

def build_structural_assertion_prompt(scenario: Scenario) -> str:
    """Build prompt for generating structural assertions."""
    return f"""{TWO_LAYER_FRAMEWORK}

---

## TASK: Generate STRUCTURAL Assertions (S1-S10)

For the following scenario, generate 10 structural assertions that check for PRESENCE of required elements.

**Scenario:**
- Title: {scenario.title}
- Date: {scenario.date} at {scenario.time} {scenario.timezone}
- Attendees: {', '.join(scenario.attendees)}
- Organizer: {scenario.organizer}
- Context: {scenario.context}
- Artifacts: {', '.join(scenario.artifacts)}

**User Request:** "{scenario.user_prompt}"

Generate structural assertions in this JSON format:
{{
    "structural_assertions": [
        {{
            "id": "A1",
            "pattern_id": "S1",
            "text": "The workback plan includes explicit meeting details (date, time, and attendees)",
            "level": "critical",
            "checks_for": "Presence of meeting date, time, timezone, and attendee list"
        }},
        ...
    ]
}}

REQUIREMENTS:
1. Generate 8-10 structural assertions covering patterns S1-S10
2. Do NOT include any specific values (no "January 15", no "Sarah Chen")
3. Use language: "includes", "has", "lists", "specifies", "identifies"
4. Assign levels: critical (must have), expected (should have), aspirational (nice to have)
5. Each assertion must be testable by checking PRESENCE only

Return ONLY valid JSON."""


def build_grounding_assertion_prompt(scenario: Scenario) -> str:
    """Build prompt for generating grounding assertions."""
    source = scenario.source_entities
    
    return f"""{TWO_LAYER_FRAMEWORK}

---

## TASK: Generate GROUNDING Assertions (G1-G5)

For the following scenario, generate grounding assertions that verify FACTUAL ACCURACY against source data.

**Scenario:**
- Title: {scenario.title}
- Date: {scenario.date} at {scenario.time} {scenario.timezone}
- Attendees: {', '.join(scenario.attendees)}
- Organizer: {scenario.organizer}
- Artifacts: {', '.join(scenario.artifacts)}

**SOURCE DATA (Ground Truth):**
```json
{json.dumps(source, indent=2)}
```

Generate grounding assertions in this JSON format:
{{
    "grounding_assertions": [
        {{
            "id": "G1",
            "pattern_id": "G1",
            "text": "All people mentioned in the plan exist in source.attendees",
            "level": "critical",
            "source_field": "source.attendees",
            "verification_method": "Check each person name against the attendee list"
        }},
        ...
    ]
}}

REQUIREMENTS:
1. Generate 5 grounding assertions covering patterns G1-G5
2. Each MUST reference a specific source field (source.attendees, source.meeting_date, etc.)
3. Specify the verification method (how to compare)
4. Most grounding assertions should be "critical" level (hallucinations are serious)
5. G5 (hallucination check) must verify NO fabricated entities

Return ONLY valid JSON."""


# ═══════════════════════════════════════════════════════════════════════════════
# Assertion Generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_structural_assertions(scenario: Scenario) -> List[StructuralAssertion]:
    """Generate structural assertions for a scenario using GPT-5."""
    prompt = build_structural_assertion_prompt(scenario)
    
    try:
        response = call_gpt5_api(prompt, temperature=0.3, max_tokens=2000)
        data = extract_json_from_response(response)
        
        assertions = []
        for item in data.get("structural_assertions", []):
            assertions.append(StructuralAssertion(
                id=item.get("id", f"S{len(assertions)+1}"),
                pattern_id=item.get("pattern_id", "S1"),
                text=item.get("text", ""),
                level=item.get("level", "expected"),
                checks_for=item.get("checks_for", "")
            ))
        
        return assertions
    except Exception as e:
        print(f"  ⚠️ Structural assertion generation failed: {e}")
        return []


def generate_grounding_assertions(scenario: Scenario) -> List[GroundingAssertion]:
    """Generate grounding assertions for a scenario using GPT-5."""
    prompt = build_grounding_assertion_prompt(scenario)
    
    try:
        response = call_gpt5_api(prompt, temperature=0.3, max_tokens=1500)
        data = extract_json_from_response(response)
        
        assertions = []
        for item in data.get("grounding_assertions", []):
            assertions.append(GroundingAssertion(
                id=item.get("id", f"G{len(assertions)+1}"),
                pattern_id=item.get("pattern_id", "G1"),
                text=item.get("text", ""),
                level=item.get("level", "critical"),
                source_field=item.get("source_field", ""),
                verification_method=item.get("verification_method", "")
            ))
        
        return assertions
    except Exception as e:
        print(f"  ⚠️ Grounding assertion generation failed: {e}")
        return []


def generate_assertions_for_scenario(scenario: Scenario) -> AssertionSet:
    """Generate complete assertion set (structural + grounding) for a scenario."""
    print(f"  📝 Generating assertions for: {scenario.title[:40]}...")
    
    # Generate structural assertions
    print(f"    → Structural (S1-S10)...")
    structural = generate_structural_assertions(scenario)
    time.sleep(DELAY_BETWEEN_CALLS)
    
    # Generate grounding assertions
    print(f"    → Grounding (G1-G5)...")
    grounding = generate_grounding_assertions(scenario)
    
    assertion_set = AssertionSet(
        scenario_id=scenario.id,
        structural=structural,
        grounding=grounding
    )
    
    print(f"    ✅ Generated {len(structural)} structural + {len(grounding)} grounding assertions")
    
    return assertion_set


# ═══════════════════════════════════════════════════════════════════════════════
# Validation
# ═══════════════════════════════════════════════════════════════════════════════

def validate_assertion_set(assertion_set: AssertionSet) -> Dict:
    """Validate assertion set against framework rules."""
    issues = []
    
    # Check structural assertions
    for a in assertion_set.structural:
        # Check for hardcoded values (simple heuristic)
        text_lower = a.text.lower()
        if any(month in text_lower for month in ["january", "february", "march", "april", "may", "june", 
                                                   "july", "august", "september", "october", "november", "december"]):
            issues.append(f"S:{a.id} - May contain hardcoded date: {a.text[:60]}...")
        
        # Check for name patterns (capitalized words that might be names)
        if "correct" in text_lower or "matches" in text_lower:
            issues.append(f"S:{a.id} - May contain grounding language: {a.text[:60]}...")
    
    # Check grounding assertions
    for a in assertion_set.grounding:
        if not a.source_field or not a.source_field.startswith("source."):
            issues.append(f"G:{a.id} - Missing or invalid source_field: {a.source_field}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "structural_count": len(assertion_set.structural),
        "grounding_count": len(assertion_set.grounding)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point for assertion generation."""
    parser = argparse.ArgumentParser(description="Stage 2: Assertion Generation")
    parser.add_argument("--scenarios", type=str, default=SCENARIOS_FILE, help="Input scenarios file")
    parser.add_argument("--output", type=str, default=ASSERTIONS_FILE, help="Output assertions file")
    parser.add_argument("--validate", action="store_true", help="Validate generated assertions")
    args = parser.parse_args()
    
    print("\n📝 Stage 2: Assertion Generation")
    print("=" * 60)
    print(f"  Framework: Two-Layer (S1-S10 Structural + G1-G5 Grounding)")
    
    # Load scenarios
    scenarios_data = load_json(args.scenarios)
    scenarios = [Scenario.from_dict(s) for s in scenarios_data.get("scenarios", [])]
    print(f"  Loaded {len(scenarios)} scenarios from {args.scenarios}")
    
    # Generate assertions for each scenario
    all_assertions = []
    validation_results = []
    
    for scenario in scenarios:
        assertion_set = generate_assertions_for_scenario(scenario)
        all_assertions.append(assertion_set)
        
        # Validate if requested
        if args.validate:
            validation = validate_assertion_set(assertion_set)
            validation_results.append({
                "scenario_id": scenario.id,
                **validation
            })
            if not validation["valid"]:
                print(f"    ⚠️ Validation issues found:")
                for issue in validation["issues"]:
                    print(f"       - {issue}")
        
        time.sleep(DELAY_BETWEEN_CALLS)
    
    # Save assertions
    output = {
        "generated_at": datetime.now().isoformat(),
        "framework_version": "2.0",
        "framework": "Two-Layer (Structural S1-S10 + Grounding G1-G5)",
        "scenarios_source": args.scenarios,
        "count": len(all_assertions),
        "assertions": [a.to_dict() for a in all_assertions],
        "validation": validation_results if args.validate else None
    }
    
    save_json(output, args.output)
    
    # Summary
    total_structural = sum(len(a.structural) for a in all_assertions)
    total_grounding = sum(len(a.grounding) for a in all_assertions)
    
    print(f"\n✅ Stage 2 Complete")
    print(f"   Scenarios: {len(all_assertions)}")
    print(f"   Structural Assertions: {total_structural}")
    print(f"   Grounding Assertions: {total_grounding}")
    print(f"   Total: {total_structural + total_grounding}")
    print(f"   Output: {args.output}")
    
    return all_assertions


if __name__ == "__main__":
    main()
