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
## STRUCTURAL ASSERTION PATTERNS (S1-S18)
Based on Chin-Yew's WBP Evaluation Rubric (docs/ChinYew/WBP_Evaluation_Rubric.md)

Purpose: Check if the plan HAS required elements (PRESENCE/SHAPE)
Question: "Does the plan HAVE X?"
Key Rule: Do NOT include specific values - only check if the element EXISTS

### Critical Priority (Weight 3)
| ID | Pattern Name | Checks For | Example |
|----|--------------|------------|---------|
| S1 | Meeting Details | Subject, date, time, timezone, attendee list clearly stated | "The plan includes meeting date, time, and attendees" |
| S2 | Timeline Alignment | Backward scheduling (T-minus) with dependency-aware sequencing | "Tasks are arranged in reverse order from meeting date" |
| S3 | Ownership Assignment | Named owners OR role/skill placeholders per task | "Each task has a named owner or role requirement" |

### Moderate Priority (Weight 2)
| ID | Pattern Name | Checks For | Example |
|----|--------------|------------|---------|
| S12 | Milestone Validation | Feasible, right-sized, coherent milestones with acceptance criteria | "Milestones are achievable and have clear criteria" |
| S4 | Deliverables & Artifacts | All outputs listed with links, version/format | "Deliverables have links and version info" |
| S5 | Task Dates | Due dates for every task aligned with timeline | "All tasks have due dates" |
| S6 | Dependencies & Blockers | Predecessors, risks, and mitigation steps | "Blockers and mitigations are documented" |
| S7 | Source Traceability | Tasks/artifacts link back to source | "Tasks map to source materials" |
| S9 | Grounding Meta-Check | All G1-G5 pass; no factual drift | "Content is grounded in source" |
| S10 | Priority Assignment | Tasks ranked by critical path/impact | "Tasks have priority tags (P1/P2/P3)" |
| S11 | Risk Mitigation Strategy | Concrete contingencies with owners | "Risks have mitigation steps and owners" |
| S13 | Goal & Success Criteria | Clear objectives and measurable indicators | "Goals and success metrics are stated" |
| S14 | Resource Allocation | People/time/tools/budget visibility | "Resources and constraints are listed" |

### Light Priority (Weight 1)
| ID | Pattern Name | Checks For | Example |
|----|--------------|------------|---------|
| S8 | Communication Channels | Teams, email, meeting cadence specified | "Communication methods are specified" |
| S15 | Compliance & Governance | Security, privacy, regulatory checks | "Compliance considerations are noted" |
| S16 | Review & Feedback Loops | Scheduled checkpoints for validation | "Review dates are included" |
| S17 | Escalation Path | Escalation owners and steps defined | "Escalation path is clear" |
| S18 | Post-Event Actions | Wrap-up tasks, retrospectives, reporting | "Post-event steps are listed" |

⚠️ ANTI-PATTERN: "The plan states the meeting date as January 15" ← This is GROUNDING, not structural!
✅ CORRECT: "The plan includes a meeting date" ← Checks presence only
"""

GROUNDING_PATTERNS = """
## GROUNDING ASSERTION PATTERNS (G1-G5)
Based on Chin-Yew's WBP Evaluation Rubric (docs/ChinYew/WBP_Evaluation_Rubric.md)

Purpose: Check if values are CORRECT vs source (FACTUAL ACCURACY)
Question: "Is X CORRECT?"
Key Rule: MUST reference a source field for comparison

### Critical Priority (Weight 3)
| ID | Pattern Name | Source Field | Verification |
|----|--------------|--------------|--------------|
| G1 | Attendee Grounding | source.attendees | Attendees match source; no hallucinated names |
| G2 | Date/Time Grounding | source.meeting_date, source.meeting_time | Meeting date/time/timezone match source |
| G5 | Hallucination Check | ALL source fields | No extraneous entities or fabricated details |

### Moderate Priority (Weight 2)
| ID | Pattern Name | Source Field | Verification |
|----|--------------|--------------|--------------|
| G3 | Artifact Grounding | source.files | Files/decks referenced exist in source repository |
| G4 | Topic Grounding | source.topics | Agenda topics align with source priorities/context |

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
            "checks_for": "Presence of meeting date, time, timezone, and attendee list",
            "weight": 3
        }},
        ...
    ]
}}

REQUIREMENTS:
1. Generate 15-18 structural assertions covering patterns S1-S18 (prioritize S1-S3, S12, S4-S7)
2. Do NOT include any specific values (no "January 15", no "Sarah Chen")
3. Use language: "includes", "has", "lists", "specifies", "identifies"
4. Assign levels based on weight: critical (weight 3), expected (weight 2), aspirational (weight 1)
5. Include weight field (3=Critical, 2=Moderate, 1=Light) per Chin-Yew's rubric
6. Each assertion must be testable by checking PRESENCE only

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
            "verification_method": "Check each person name against the attendee list",
            "weight": 3
        }},
        ...
    ]
}}

REQUIREMENTS:
1. Generate 5 grounding assertions covering patterns G1-G5
2. Each MUST reference a specific source field (source.attendees, source.meeting_date, etc.)
3. Specify the verification method (how to compare)
4. Assign levels based on weight: critical (weight 3 for G1, G2, G5), expected (weight 2 for G3, G4)
5. Include weight field (3=Critical, 2=Moderate) per Chin-Yew's rubric
6. G5 (hallucination check) must verify NO fabricated entities

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
    print(f"    → Structural (S1-S18, Chin-Yew's Rubric)...")
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
    print(f"  Framework: Chin-Yew's WBP Rubric (S1-S18 Structural + G1-G5 Grounding)")
    print(f"  Reference: docs/ChinYew/WBP_Evaluation_Rubric.md")
    
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
        "framework_version": "3.0",
        "framework": "Chin-Yew WBP Rubric (S1-S18 Structural + G1-G5 Grounding)",
        "rubric_reference": "docs/ChinYew/WBP_Evaluation_Rubric.md",
        "scoring_model": {
            "scale": "0=Missing, 1=Partial, 2=Fully Met",
            "weights": "Critical=3, Moderate=2, Light=1"
        },
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
    print(f"   Structural Assertions: {total_structural} (S1-S18)")
    print(f"   Grounding Assertions: {total_grounding} (G1-G5)")
    print(f"   Total: {total_structural + total_grounding}")
    print(f"   Output: {args.output}")
    
    return all_assertions


if __name__ == "__main__":
    main()
