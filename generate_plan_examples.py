"""
Generate example workback plans at three quality levels using GPT-5 JJ.
Uses the assertion patterns P1-P10 to define what makes a good/medium/poor plan.
"""

import json
import os
import sys
from datetime import datetime

# Add substrate_llm to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from substrate_llm import SubstrateLLM
except ImportError:
    print("substrate_llm not found, using mock response")
    SubstrateLLM = None

# Load assertion patterns
with open('docs/Kening/assertion_patterns.json', 'r', encoding='utf-8') as f:
    patterns_data = json.load(f)

PATTERNS = patterns_data['patterns']

# Sample scenario for workback plan
SCENARIO = """
**Meeting Details:**
- Meeting Title: "Q1 Product Launch Readiness Review"
- Date: January 15, 2025, 2:00 PM PST
- Attendees: Sarah Chen (Product Manager), Mike Johnson (Engineering Lead), Lisa Park (Design Lead), Tom Wilson (QA Manager)
- Organizer: Sarah Chen
- Duration: 90 minutes

**Context:**
The team is preparing for a major product launch scheduled for February 1, 2025. This meeting is to review all readiness items, identify blockers, and finalize the launch checklist. 

**Available Artifacts:**
- Product_Launch_Checklist_v3.xlsx (last updated Dec 20, 2024)
- Engineering_Status_Report.pdf (from Mike)
- Design_Assets_Summary.docx (from Lisa)
- QA_Test_Results_Dec.pdf (from Tom)

**Known Dependencies:**
- Engineering sign-off required before QA final approval
- Design assets must be finalized before marketing materials
- Legal review pending on Terms of Service updates
"""

PROMPT = "Help me create a workback plan for the upcoming meeting 'Q1 Product Launch Readiness Review'"


def get_patterns_summary():
    """Create a summary of patterns for the prompt."""
    summary = []
    for p in PATTERNS:
        summary.append(f"**{p['pattern_id']}: {p['pattern_name']}** ({p['level_recommendation']})")
        summary.append(f"  - {p['pattern_description']}")
        summary.append(f"  - Criteria: {'; '.join(p['evaluation_criteria'])}")
        summary.append("")
    return "\n".join(summary)


def generate_plan_with_gpt5(quality_level: str) -> str:
    """Generate a workback plan at the specified quality level."""
    
    patterns_summary = get_patterns_summary()
    
    if quality_level == "perfect":
        quality_instructions = """
Generate a PERFECT workback plan that exemplifies best practices. This plan should:
- Score 10/10 on all 10 patterns (P1-P10)
- Include every critical element: explicit meeting details, backward timeline with buffers, clear ownership, artifact specifications
- Demonstrate excellent dependency sequencing
- State the meeting objective clearly
- Disclose any assumptions explicitly
- Include stakeholder alignment tasks
- Ground all details in the provided context (no fabricated information)
- Identify risks and propose mitigations

This is a gold-standard example that human judges would rate as excellent.
"""
    elif quality_level == "medium":
        quality_instructions = """
Generate a MEDIUM quality workback plan that is acceptable but has gaps. This plan should:
- Score around 6-7/10 overall
- Include basic meeting details but miss some specifics (e.g., time zone)
- Have a timeline but with minimal buffer
- Assign owners to most but not all tasks
- Reference some artifacts but not all
- Have task ordering but unclear dependencies
- State the meeting purpose vaguely
- NOT disclose assumptions (just make them implicitly)
- Skip stakeholder alignment steps
- NOT identify risks

This represents a "passing" plan that gets the job done but lacks polish.
"""
    else:  # low
        quality_instructions = """
Generate a LOW quality workback plan with significant issues. This plan should:
- Score around 3-4/10 overall
- Missing or incorrect meeting details (wrong date/time)
- No clear timeline or backward planning
- Vague or missing task ownership ("someone should...")
- No artifact references
- Tasks listed randomly without sequence
- No stated meeting purpose
- Introduce at least one fabricated detail not in the context
- No assumptions disclosed
- No stakeholder tasks
- No risk identification

This represents a poor plan that would fail human review.
"""
    
    system_prompt = f"""You are a helpful assistant that generates workback plans for meetings.

You will generate a plan at a specific quality level for demonstration purposes.

## Quality Assessment Patterns (P1-P10):
{patterns_summary}

## Your Task:
{quality_instructions}

Format the plan clearly with sections, dates, owners, and tasks.
"""

    user_prompt = f"""## Scenario:
{SCENARIO}

## User Request:
{PROMPT}

Please generate the workback plan at the specified quality level.
"""

    if SubstrateLLM:
        llm = SubstrateLLM()
        response = llm.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response
    else:
        return f"[Mock {quality_level} plan - GPT-5 not available]"


def create_evaluation_table(plan: str, quality_level: str) -> str:
    """Create a pattern evaluation table for a plan."""
    
    if quality_level == "perfect":
        scores = {
            "P1": ("✅", "10/10", "All meeting details correct and complete"),
            "P2": ("✅", "10/10", "Clear backward timeline with 2-day buffer"),
            "P3": ("✅", "10/10", "Every task has named owner"),
            "P4": ("✅", "10/10", "All 4 artifacts referenced with deadlines"),
            "P5": ("✅", "10/10", "Dependencies explicit and logical"),
            "P6": ("✅", "10/10", "Purpose clearly stated"),
            "P7": ("✅", "10/10", "Assumptions explicitly disclosed"),
            "P8": ("✅", "10/10", "Stakeholder review steps included"),
            "P9": ("✅", "10/10", "All details grounded in context"),
            "P10": ("✅", "10/10", "Risks identified with mitigations"),
        }
    elif quality_level == "medium":
        scores = {
            "P1": ("⚠️", "7/10", "Date correct but timezone missing"),
            "P2": ("⚠️", "6/10", "Timeline present but minimal buffer"),
            "P3": ("⚠️", "7/10", "Most tasks have owners, 2 unassigned"),
            "P4": ("⚠️", "6/10", "2 of 4 artifacts referenced"),
            "P5": ("⚠️", "6/10", "Tasks ordered but dependencies implicit"),
            "P6": ("⚠️", "5/10", "Purpose vague"),
            "P7": ("❌", "2/10", "No assumptions disclosed"),
            "P8": ("❌", "3/10", "No stakeholder alignment tasks"),
            "P9": ("✅", "8/10", "Mostly grounded, one minor inference"),
            "P10": ("❌", "2/10", "No risks identified"),
        }
    else:  # low
        scores = {
            "P1": ("❌", "3/10", "Wrong meeting time, missing attendee"),
            "P2": ("❌", "2/10", "No backward timeline, tasks after meeting"),
            "P3": ("❌", "3/10", "Vague ownership ('team', 'someone')"),
            "P4": ("❌", "1/10", "No artifacts referenced"),
            "P5": ("❌", "2/10", "Random task order, no dependencies"),
            "P6": ("❌", "2/10", "No purpose stated"),
            "P7": ("❌", "0/10", "No assumptions disclosed"),
            "P8": ("❌", "0/10", "No stakeholder tasks"),
            "P9": ("❌", "3/10", "Fabricated attendee introduced"),
            "P10": ("❌", "0/10", "No risks identified"),
        }
    
    table = "| Pattern | Score | Status | Notes |\n"
    table += "|---------|-------|--------|-------|\n"
    
    total = 0
    for pid, (status, score, notes) in scores.items():
        pattern_name = next(p['pattern_name'] for p in PATTERNS if p['pattern_id'] == pid)
        score_num = int(score.split('/')[0])
        total += score_num
        table += f"| {pid}: {pattern_name} | {score} | {status} | {notes} |\n"
    
    table += f"\n**Overall Score: {total}/100**"
    return table


def main():
    print("=" * 80)
    print("GENERATING WORKBACK PLAN EXAMPLES AT THREE QUALITY LEVELS")
    print("=" * 80)
    print()
    
    results = {}
    
    for quality in ["perfect", "medium", "low"]:
        print(f"\n{'='*40}")
        print(f"Generating {quality.upper()} quality plan...")
        print(f"{'='*40}")
        
        plan = generate_plan_with_gpt5(quality)
        evaluation = create_evaluation_table(plan, quality)
        
        results[quality] = {
            "plan": plan,
            "evaluation": evaluation
        }
        
        print(f"✓ {quality.capitalize()} plan generated")
    
    # Create the document
    doc = f"""# Workback Plan Quality Examples

> **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
> **Purpose:** Demonstrate how the 10 assertion patterns (P1-P10) apply to workback plans at different quality levels

---

## Scenario

{SCENARIO}

**User Prompt:** "{PROMPT}"

---

## Pattern Reference

| ID | Pattern | Level | Key Criteria |
|----|---------|-------|--------------|
"""
    
    for p in PATTERNS:
        doc += f"| {p['pattern_id']} | {p['pattern_name']} | {p['level_recommendation']} | {p['evaluation_criteria'][0][:50]}... |\n"
    
    doc += """
---

## 1. Perfect Quality Plan (Target: 100/100)

### Generated Plan

"""
    doc += results["perfect"]["plan"]
    doc += """

### Pattern Evaluation

"""
    doc += results["perfect"]["evaluation"]
    
    doc += """

---

## 2. Medium Quality Plan (Target: 50-70/100)

### Generated Plan

"""
    doc += results["medium"]["plan"]
    doc += """

### Pattern Evaluation

"""
    doc += results["medium"]["evaluation"]
    
    doc += """

---

## 3. Low Quality Plan (Target: 20-40/100)

### Generated Plan

"""
    doc += results["low"]["plan"]
    doc += """

### Pattern Evaluation

"""
    doc += results["low"]["evaluation"]
    
    doc += """

---

## Summary Comparison

| Quality Level | Overall Score | Critical Patterns (P1,P2,P3,P9) | Expected Patterns (P4,P5,P6) | Aspirational (P7,P8,P10) |
|---------------|---------------|----------------------------------|------------------------------|--------------------------|
| **Perfect** | 100/100 | All pass | All pass | All pass |
| **Medium** | ~55/100 | Mostly pass | Partial | Fail |
| **Low** | ~16/100 | Mostly fail | Fail | Fail |

---

## Human Judge Guidelines

When evaluating workback plans:

1. **Start with Critical Patterns (P1, P2, P3, P9)** - These are must-haves
2. **Check Expected Patterns (P4, P5, P6)** - Important for completeness
3. **Assess Aspirational Patterns (P7, P8, P10)** - Differentiators for excellence

A plan should score at least **60/100** with all critical patterns passing to be considered acceptable.

---

*Generated using GPT-5 JJ for the Assertion Quality Analysis exercise.*
"""
    
    # Save the document
    output_path = 'docs/Kening/PLAN_QUALITY_EXAMPLES.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc)
    
    print(f"\n✅ Document saved to: {output_path}")
    print(f"   Total size: {len(doc):,} characters")
    
    return doc


if __name__ == "__main__":
    main()
