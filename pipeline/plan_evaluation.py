"""
Stage 4: Plan Evaluation

Evaluates generated workback plans against two-layer assertions:
- Structural Evaluation (S1-S10): Check PRESENCE of required elements
- Grounding Evaluation (G1-G5): Check FACTUAL ACCURACY vs source

Key evaluation rules:
1. Structural: PASS if element exists, FAIL if missing (ignore correctness)
2. Grounding: PASS if value matches source, FAIL if hallucination

Usage:
    python -m pipeline.plan_evaluation
    python -m pipeline.plan_evaluation --plans docs/pipeline_output/plans.json --assertions docs/pipeline_output/assertions.json
"""

import json
import argparse
import time
from datetime import datetime
from typing import List, Dict, Optional

from .config import (
    Scenario,
    StructuralAssertion,
    GroundingAssertion,
    AssertionSet,
    WorkbackPlan,
    AssertionResult,
    PlanEvaluationResult,
    SCENARIOS_FILE,
    ASSERTIONS_FILE,
    PLANS_FILE,
    EVALUATION_FILE,
    save_json,
    load_json,
    call_gpt5_api,
    extract_json_from_response,
    DELAY_BETWEEN_CALLS
)


# ═══════════════════════════════════════════════════════════════════════════════
# Two-Layer Evaluation Framework
# ═══════════════════════════════════════════════════════════════════════════════

STRUCTURAL_EVALUATION_PROMPT = """
## TWO-LAYER EVALUATION: STRUCTURAL CHECK

You are evaluating whether a workback plan satisfies a STRUCTURAL assertion.

**STRUCTURAL EVALUATION RULES:**
- Question: "Does the plan HAVE this element?"
- Check for: PRESENCE/SHAPE only
- ✅ PASS if: The element EXISTS in the plan (regardless of correctness)
- ❌ FAIL if: The element is COMPLETELY MISSING

**IMPORTANT:** Do NOT evaluate whether values are correct - that's grounding's job!
- "Plan has a meeting date" → PASS if ANY date is mentioned (even if wrong)
- "Plan has task owners" → PASS if ANY names are assigned (even if fabricated)

---

**PLAN TO EVALUATE:**
{plan_content}

---

**STRUCTURAL ASSERTION:**
ID: {assertion_id}
Pattern: {pattern_id}
Text: "{assertion_text}"
Checks For: {checks_for}
Level: {level}

---

Evaluate and return JSON:
{{
    "passed": true or false,
    "explanation": "Brief explanation of what was found or missing",
    "evidence_found": "Quote from plan showing the element exists (or 'NOT FOUND')"
}}

Remember: Check PRESENCE only, not correctness!
Return ONLY valid JSON."""


GROUNDING_EVALUATION_PROMPT = """
## TWO-LAYER EVALUATION: GROUNDING CHECK

You are evaluating whether a workback plan satisfies a GROUNDING assertion.

**GROUNDING EVALUATION RULES:**
- Question: "Is this value CORRECT vs source?"
- Check for: FACTUAL ACCURACY against source data
- ✅ PASS if: Values MATCH the source data
- ❌ FAIL if: Values are HALLUCINATED or don't match source

**SOURCE DATA (Ground Truth):**
```json
{source_data}
```

---

**PLAN TO EVALUATE:**
{plan_content}

---

**GROUNDING ASSERTION:**
ID: {assertion_id}
Pattern: {pattern_id}
Text: "{assertion_text}"
Source Field: {source_field}
Verification Method: {verification_method}
Level: {level}

---

Evaluate and return JSON:
{{
    "passed": true or false,
    "explanation": "What was compared and whether it matches",
    "values_in_plan": ["List of relevant values found in the plan"],
    "values_in_source": ["List of expected values from source"],
    "mismatches": ["Any hallucinated or incorrect values (empty if passed)"]
}}

Be strict about grounding - any fabricated content should FAIL.
Return ONLY valid JSON."""


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluation Functions
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_structural_assertion(
    plan: WorkbackPlan,
    assertion: StructuralAssertion
) -> AssertionResult:
    """Evaluate a single structural assertion against a plan."""
    
    prompt = STRUCTURAL_EVALUATION_PROMPT.format(
        plan_content=plan.content[:4000],  # Truncate if too long
        assertion_id=assertion.id,
        pattern_id=assertion.pattern_id,
        assertion_text=assertion.text,
        checks_for=assertion.checks_for,
        level=assertion.level
    )
    
    try:
        response = call_gpt5_api(prompt, temperature=0.1, max_tokens=500)
        data = extract_json_from_response(response)
        
        return AssertionResult(
            assertion_id=assertion.id,
            assertion_text=assertion.text,
            layer="structural",
            level=assertion.level,
            passed=data.get("passed", False),
            explanation=data.get("explanation", ""),
            supporting_spans=[{
                "text": data.get("evidence_found", ""),
                "type": "evidence"
            }] if data.get("evidence_found") and data.get("evidence_found") != "NOT FOUND" else []
        )
    except Exception as e:
        return AssertionResult(
            assertion_id=assertion.id,
            assertion_text=assertion.text,
            layer="structural",
            level=assertion.level,
            passed=False,
            explanation=f"Evaluation error: {str(e)}",
            supporting_spans=[]
        )


def evaluate_grounding_assertion(
    plan: WorkbackPlan,
    assertion: GroundingAssertion,
    source_data: Dict
) -> AssertionResult:
    """Evaluate a single grounding assertion against a plan."""
    
    prompt = GROUNDING_EVALUATION_PROMPT.format(
        source_data=json.dumps(source_data, indent=2),
        plan_content=plan.content[:4000],
        assertion_id=assertion.id,
        pattern_id=assertion.pattern_id,
        assertion_text=assertion.text,
        source_field=assertion.source_field,
        verification_method=assertion.verification_method,
        level=assertion.level
    )
    
    try:
        response = call_gpt5_api(prompt, temperature=0.1, max_tokens=600)
        data = extract_json_from_response(response)
        
        mismatches = data.get("mismatches", [])
        
        return AssertionResult(
            assertion_id=assertion.id,
            assertion_text=assertion.text,
            layer="grounding",
            level=assertion.level,
            passed=data.get("passed", False),
            explanation=data.get("explanation", ""),
            supporting_spans=[
                {"text": v, "type": "plan_value"} for v in data.get("values_in_plan", [])
            ] + [
                {"text": m, "type": "mismatch"} for m in mismatches
            ]
        )
    except Exception as e:
        return AssertionResult(
            assertion_id=assertion.id,
            assertion_text=assertion.text,
            layer="grounding",
            level=assertion.level,
            passed=False,
            explanation=f"Evaluation error: {str(e)}",
            supporting_spans=[]
        )


def evaluate_plan(
    plan: WorkbackPlan,
    assertion_set: AssertionSet,
    source_data: Dict
) -> PlanEvaluationResult:
    """Evaluate a plan against all assertions in the set."""
    from .config import calculate_weighted_score
    
    print(f"    Evaluating {plan.quality_level} plan...")
    
    # Evaluate structural assertions
    structural_results = []
    for assertion in assertion_set.structural:
        result = evaluate_structural_assertion(plan, assertion)
        structural_results.append(result)
        time.sleep(0.5)  # Brief delay between assertions
    
    # Evaluate grounding assertions
    grounding_results = []
    for assertion in assertion_set.grounding:
        result = evaluate_grounding_assertion(plan, assertion, source_data)
        grounding_results.append(result)
        time.sleep(0.5)
    
    # Calculate scores
    structural_passed = sum(1 for r in structural_results if r.passed)
    structural_score = structural_passed / len(structural_results) if structural_results else 0
    
    grounding_passed = sum(1 for r in grounding_results if r.passed)
    grounding_score = grounding_passed / len(grounding_results) if grounding_results else 0
    
    # Calculate weighted score per Chin-Yew's rubric
    all_results = structural_results + grounding_results
    weighted_score = calculate_weighted_score(all_results)
    
    # Determine overall verdict
    if structural_score >= 0.8 and grounding_score >= 0.8:
        verdict = "pass"
    elif structural_score < 0.8 and grounding_score < 0.8:
        verdict = "fail_both"
    elif structural_score < 0.8:
        verdict = "fail_structure"
    else:
        verdict = "fail_grounding"
    
    # Generate summary (strengths, weaknesses, next_actions)
    strengths = [r.assertion_text for r in all_results if r.passed][:5]
    weaknesses = [r.assertion_text for r in all_results if not r.passed][:5]
    next_actions = [f"Address: {r.explanation}" for r in all_results if not r.passed][:3]
    
    summary = {
        "weighted_score": weighted_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "next_actions": next_actions
    }
    
    print(f"      S: {structural_passed}/{len(structural_results)} ({structural_score*100:.0f}%)")
    print(f"      G: {grounding_passed}/{len(grounding_results)} ({grounding_score*100:.0f}%)")
    print(f"      Weighted: {weighted_score*100:.1f}%")
    print(f"      Verdict: {verdict}")
    
    return PlanEvaluationResult(
        scenario_id=plan.scenario_id,
        quality_level=plan.quality_level,
        structural_results=structural_results,
        grounding_results=grounding_results,
        structural_score=structural_score,
        grounding_score=grounding_score,
        weighted_score=weighted_score,
        overall_verdict=verdict,
        summary=summary
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point for plan evaluation."""
    parser = argparse.ArgumentParser(description="Stage 4: Plan Evaluation")
    parser.add_argument("--scenarios", type=str, default=SCENARIOS_FILE, help="Input scenarios file")
    parser.add_argument("--assertions", type=str, default=ASSERTIONS_FILE, help="Input assertions file")
    parser.add_argument("--plans", type=str, default=PLANS_FILE, help="Input plans file")
    parser.add_argument("--output", type=str, default=EVALUATION_FILE, help="Output evaluation file")
    args = parser.parse_args()
    
    print("\n📊 Stage 4: Plan Evaluation")
    print("=" * 60)
    print("  Framework: Two-Layer Evaluation")
    print("    • Structural (S1-S10): Check PRESENCE")
    print("    • Grounding (G1-G5): Check ACCURACY")
    
    # Load all data
    scenarios_data = load_json(args.scenarios)
    scenarios = {s["id"]: Scenario.from_dict(s) for s in scenarios_data.get("scenarios", [])}
    
    assertions_data = load_json(args.assertions)
    assertions_by_scenario = {}
    for a in assertions_data.get("assertions", []):
        scenario_id = a["scenario_id"]
        
        # Filter out extra fields not in dataclass
        structural_list = []
        for s in a.get("structural", []):
            structural_list.append(StructuralAssertion(
                id=s.get("id", ""),
                pattern_id=s.get("pattern_id", ""),
                text=s.get("text", ""),
                level=s.get("level", "expected"),
                checks_for=s.get("checks_for", "")
            ))
        
        grounding_list = []
        for g in a.get("grounding", []):
            grounding_list.append(GroundingAssertion(
                id=g.get("id", ""),
                pattern_id=g.get("pattern_id", ""),
                text=g.get("text", ""),
                level=g.get("level", "critical"),
                source_field=g.get("source_field", ""),
                verification_method=g.get("verification_method", "")
            ))
        
        assertions_by_scenario[scenario_id] = AssertionSet(
            scenario_id=scenario_id,
            structural=structural_list,
            grounding=grounding_list
        )
    
    plans_data = load_json(args.plans)
    plans = [WorkbackPlan(**p) for p in plans_data.get("plans", [])]
    
    print(f"\n  Loaded: {len(scenarios)} scenarios, {len(assertions_by_scenario)} assertion sets, {len(plans)} plans")
    
    # Evaluate all plans
    all_results = []
    
    for plan in plans:
        scenario = scenarios.get(plan.scenario_id)
        assertion_set = assertions_by_scenario.get(plan.scenario_id)
        
        if not scenario or not assertion_set:
            print(f"  ⚠️ Skipping plan {plan.scenario_id}/{plan.quality_level}: missing data")
            continue
        
        print(f"\n  📊 {scenario.title[:40]}... ({plan.quality_level})")
        
        result = evaluate_plan(
            plan=plan,
            assertion_set=assertion_set,
            source_data=scenario.source_entities
        )
        all_results.append(result)
        
        time.sleep(DELAY_BETWEEN_CALLS)
    
    # Save results
    output = {
        "evaluated_at": datetime.now().isoformat(),
        "framework": "Two-Layer (Structural + Grounding)",
        "sources": {
            "scenarios": args.scenarios,
            "assertions": args.assertions,
            "plans": args.plans
        },
        "summary": {
            "total_plans": len(all_results),
            "by_quality": {},
            "by_verdict": {}
        },
        "results": [r.to_dict() for r in all_results]
    }
    
    # Calculate summary stats
    for result in all_results:
        # By quality
        q = result.quality_level
        if q not in output["summary"]["by_quality"]:
            output["summary"]["by_quality"][q] = {
                "count": 0,
                "avg_structural": 0,
                "avg_grounding": 0
            }
        output["summary"]["by_quality"][q]["count"] += 1
        output["summary"]["by_quality"][q]["avg_structural"] += result.structural_score
        output["summary"]["by_quality"][q]["avg_grounding"] += result.grounding_score
        
        # By verdict
        v = result.overall_verdict
        output["summary"]["by_verdict"][v] = output["summary"]["by_verdict"].get(v, 0) + 1
    
    # Average the scores
    for q, stats in output["summary"]["by_quality"].items():
        if stats["count"] > 0:
            stats["avg_structural"] = round(stats["avg_structural"] / stats["count"], 3)
            stats["avg_grounding"] = round(stats["avg_grounding"] / stats["count"], 3)
    
    save_json(output, args.output)
    
    # Summary
    print(f"\n✅ Stage 4 Complete")
    print(f"   Total Evaluations: {len(all_results)}")
    print(f"\n   Results by Quality Level:")
    for q, stats in output["summary"]["by_quality"].items():
        print(f"   • {q.capitalize()}: S={stats['avg_structural']*100:.0f}%, G={stats['avg_grounding']*100:.0f}%")
    print(f"\n   Results by Verdict:")
    for v, count in output["summary"]["by_verdict"].items():
        print(f"   • {v}: {count}")
    print(f"\n   Output: {args.output}")
    
    return all_results


if __name__ == "__main__":
    main()
