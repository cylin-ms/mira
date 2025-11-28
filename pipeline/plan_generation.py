"""
Stage 3: Plan Generation

Generates workback plans at three quality levels:
- Perfect: Complete structure + Fully grounded (100% S, 100% G)
- Medium: Good structure + Some grounding issues (80% S, 60% G)  
- Low: Poor structure + Multiple hallucinations (40% S, 20% G)

This creates controlled test data for evaluating the assertion framework.

Usage:
    python -m pipeline.plan_generation
    python -m pipeline.plan_generation --scenarios docs/pipeline_output/scenarios.json
"""

import json
import argparse
import time
from datetime import datetime
from typing import List, Dict, Tuple

from .config import (
    Scenario,
    WorkbackPlan,
    SCENARIOS_FILE,
    PLANS_FILE,
    save_json,
    load_json,
    call_gpt5_api,
    extract_json_from_response,
    DELAY_BETWEEN_CALLS
)


# ═══════════════════════════════════════════════════════════════════════════════
# Quality Level Specifications
# ═══════════════════════════════════════════════════════════════════════════════

QUALITY_SPECS = {
    "perfect": {
        "name": "Perfect Quality",
        "description": "Complete structure with fully grounded content",
        "intended_structural_score": 1.0,
        "intended_grounding_score": 1.0,
        "instructions": """
Generate a PERFECT workback plan that:
1. ✅ Includes ALL structural elements (meeting details, timeline, owners, artifacts, dates, blockers)
2. ✅ Every element is EXACTLY grounded in source data
3. ✅ Uses ONLY attendees from the provided list
4. ✅ References ONLY files that exist in artifacts
5. ✅ All dates logically align with the meeting date
6. ✅ NO fabricated or hallucinated content

This plan should pass 100% of structural AND grounding assertions.
"""
    },
    "medium": {
        "name": "Medium Quality",
        "description": "Good structure with some grounding issues",
        "intended_structural_score": 0.8,
        "intended_grounding_score": 0.6,
        "instructions": """
Generate a MEDIUM quality workback plan that:
1. ✅ Has MOST structural elements but is missing 1-2 (e.g., no blockers section, missing priorities)
2. ⚠️ Contains 2-3 MINOR grounding issues:
   - One task assigned to a person NOT in the attendee list (fabricated name)
   - One reference to a file that doesn't exist
   - One date that doesn't quite align with the timeline
3. ✅ Overall readable and useful, but has accuracy problems

Deliberate issues to introduce:
- Add one fabricated attendee name (e.g., "Alex Thompson" if not in list)
- Reference one file that wasn't in artifacts (e.g., "Marketing_Brief.pdf")
- Missing one structural element (e.g., no priority assignments)
"""
    },
    "low": {
        "name": "Low Quality", 
        "description": "Poor structure with multiple hallucinations",
        "intended_structural_score": 0.4,
        "intended_grounding_score": 0.2,
        "instructions": """
Generate a LOW quality workback plan that:
1. ❌ Missing MANY structural elements:
   - No explicit meeting date/time
   - Generic owners ("someone should...", "the team will...")
   - No specific artifacts mentioned
   - No timeline with dates
2. ❌ Multiple MAJOR grounding issues:
   - Several fabricated attendees
   - Multiple non-existent files referenced
   - Dates that don't match the meeting
   - Topics that drift from the actual meeting subject
3. ❌ Feels generic and could apply to any meeting

Deliberate issues to introduce:
- Use generic owner language ("team", "someone", "TBD")
- Add 3+ fabricated people names
- Reference 2+ non-existent files
- Omit meeting date/time entirely or use wrong date
- Missing blockers, dependencies, priorities
"""
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# Plan Generation Prompts
# ═══════════════════════════════════════════════════════════════════════════════

def build_plan_generation_prompt(scenario: Scenario, quality_level: str) -> str:
    """Build prompt for generating a workback plan at specified quality level."""
    
    spec = QUALITY_SPECS[quality_level]
    source = scenario.source_entities
    
    return f"""You are generating a workback plan for evaluation testing purposes.

## QUALITY LEVEL: {spec['name'].upper()}
{spec['description']}

{spec['instructions']}

---

## SCENARIO

**Meeting Details:**
- Title: {scenario.title}
- Date: {scenario.date}
- Time: {scenario.time} {scenario.timezone}
- Duration: {scenario.duration_minutes} minutes
- Organizer: {scenario.organizer}
- Attendees: {', '.join(scenario.attendees)}

**Context:**
{scenario.context}

**Available Artifacts:**
{chr(10).join(f'- {f}' for f in scenario.artifacts)}

**Dependencies:**
{chr(10).join(f'- {d}' for d in scenario.dependencies)}

**User Request:** "{scenario.user_prompt}"

---

## SOURCE DATA (Ground Truth for Grounding)
```json
{json.dumps(source, indent=2)}
```

---

## TASK

Generate a workback plan at {spec['name'].upper()} level.

Return JSON with:
{{
    "plan_content": "The full workback plan in markdown format",
    "deliberate_issues": ["List of deliberate issues introduced (for medium/low quality)"],
    "expected_structural_failures": ["Which S patterns should fail"],
    "expected_grounding_failures": ["Which G patterns should fail"]
}}

For PERFECT quality: deliberate_issues, expected_*_failures should be empty arrays.
For MEDIUM/LOW quality: List the specific issues you intentionally introduced.

Return ONLY valid JSON."""


# ═══════════════════════════════════════════════════════════════════════════════
# Plan Generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_plan(scenario: Scenario, quality_level: str) -> WorkbackPlan:
    """Generate a workback plan at the specified quality level."""
    
    spec = QUALITY_SPECS[quality_level]
    prompt = build_plan_generation_prompt(scenario, quality_level)
    
    try:
        response = call_gpt5_api(prompt, temperature=0.4, max_tokens=3000)
        data = extract_json_from_response(response)
        
        return WorkbackPlan(
            scenario_id=scenario.id,
            quality_level=quality_level,
            content=data.get("plan_content", ""),
            intended_structural_score=spec["intended_structural_score"],
            intended_grounding_score=spec["intended_grounding_score"],
            deliberate_issues=data.get("deliberate_issues", [])
        )
    except Exception as e:
        print(f"  ⚠️ Plan generation failed: {e}")
        return WorkbackPlan(
            scenario_id=scenario.id,
            quality_level=quality_level,
            content=f"ERROR: Failed to generate plan - {str(e)}",
            intended_structural_score=spec["intended_structural_score"],
            intended_grounding_score=spec["intended_grounding_score"],
            deliberate_issues=["Generation failed"]
        )


def generate_plans_for_scenario(scenario: Scenario) -> List[WorkbackPlan]:
    """Generate all three quality levels of plans for a scenario."""
    print(f"\n  📄 Generating plans for: {scenario.title[:40]}...")
    
    plans = []
    for quality_level in ["perfect", "medium", "low"]:
        spec = QUALITY_SPECS[quality_level]
        print(f"    → {spec['name']} (target: S={spec['intended_structural_score']*100:.0f}%, G={spec['intended_grounding_score']*100:.0f}%)...")
        
        plan = generate_plan(scenario, quality_level)
        plans.append(plan)
        
        # Show deliberate issues for non-perfect plans
        if plan.deliberate_issues and quality_level != "perfect":
            print(f"      Deliberate issues: {len(plan.deliberate_issues)}")
        
        time.sleep(DELAY_BETWEEN_CALLS)
    
    return plans


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point for plan generation."""
    parser = argparse.ArgumentParser(description="Stage 3: Plan Generation")
    parser.add_argument("--scenarios", type=str, default=SCENARIOS_FILE, help="Input scenarios file")
    parser.add_argument("--output", type=str, default=PLANS_FILE, help="Output plans file")
    parser.add_argument("--quality", type=str, choices=["all", "perfect", "medium", "low"], 
                        default="all", help="Quality level(s) to generate")
    args = parser.parse_args()
    
    print("\n📄 Stage 3: Plan Generation")
    print("=" * 60)
    print("  Quality Levels:")
    for level, spec in QUALITY_SPECS.items():
        print(f"    • {spec['name']}: S={spec['intended_structural_score']*100:.0f}%, G={spec['intended_grounding_score']*100:.0f}%")
    
    # Load scenarios
    scenarios_data = load_json(args.scenarios)
    scenarios = [Scenario.from_dict(s) for s in scenarios_data.get("scenarios", [])]
    print(f"\n  Loaded {len(scenarios)} scenarios from {args.scenarios}")
    
    # Generate plans
    all_plans = []
    
    for scenario in scenarios:
        if args.quality == "all":
            plans = generate_plans_for_scenario(scenario)
        else:
            print(f"\n  📄 Generating {args.quality} plan for: {scenario.title[:40]}...")
            plans = [generate_plan(scenario, args.quality)]
        
        all_plans.extend(plans)
    
    # Save plans
    output = {
        "generated_at": datetime.now().isoformat(),
        "scenarios_source": args.scenarios,
        "quality_levels": list(QUALITY_SPECS.keys()) if args.quality == "all" else [args.quality],
        "count": len(all_plans),
        "plans_by_quality": {
            level: len([p for p in all_plans if p.quality_level == level])
            for level in QUALITY_SPECS.keys()
        },
        "plans": [p.to_dict() for p in all_plans]
    }
    
    save_json(output, args.output)
    
    # Summary
    print(f"\n✅ Stage 3 Complete")
    print(f"   Total Plans: {len(all_plans)}")
    for level, count in output["plans_by_quality"].items():
        if count > 0:
            spec = QUALITY_SPECS[level]
            print(f"   • {spec['name']}: {count} plans")
    print(f"   Output: {args.output}")
    
    return all_plans


if __name__ == "__main__":
    main()
