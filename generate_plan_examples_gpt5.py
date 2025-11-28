"""
Generate Plan Quality Examples Using GPT-5 JJ

This script uses GPT-5 JJ to:
1. Generate three workback plans at different quality levels (perfect, medium, low)
2. Generate assertions based on P1-P10 patterns to evaluate each plan
3. Evaluate each plan against the assertions
4. Create a comprehensive evaluation report

Usage:
    python generate_plan_examples_gpt5.py
"""

import json
import os
import time
import ctypes
from datetime import datetime
from typing import Dict, List

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration (same as analyze_assertions_gpt5.py)
# ═══════════════════════════════════════════════════════════════════════════════

SUBSTRATE_ENDPOINT = "https://fe-26.qas.bing.net/chat/completions"
SUBSTRATE_RESOURCE = "https://substrate.office.com"
CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
JJ_MODEL = "dev-gpt-5-chat-jj"

DELAY_BETWEEN_CALLS = 2
_jj_token_cache = None

# Output file
OUTPUT_FILE = os.path.join("docs", "Kening", "PLAN_QUALITY_EXAMPLES_GPT5.md")
JSON_OUTPUT = os.path.join("docs", "Kening", "plan_examples_gpt5.json")

# ═══════════════════════════════════════════════════════════════════════════════
# Scenario & Patterns
# ═══════════════════════════════════════════════════════════════════════════════

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

USER_PROMPT = "Help me create a workback plan for the upcoming meeting 'Q1 Product Launch Readiness Review'"

# Load assertion patterns
with open(os.path.join("docs", "Kening", "assertion_patterns.json"), 'r', encoding='utf-8') as f:
    PATTERNS_DATA = json.load(f)
    PATTERNS = PATTERNS_DATA['patterns']


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════════════════

def get_substrate_token():
    """Get authentication token for Substrate API using MSAL broker."""
    global _jj_token_cache
    
    if _jj_token_cache:
        return _jj_token_cache
    
    try:
        import msal
    except ImportError:
        print("Error: msal[broker] not installed. Run: pip install msal[broker]")
        raise
    
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        enable_broker_on_windows=True,
    )
    
    scopes = [f"{SUBSTRATE_RESOURCE}/.default"]
    
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            _jj_token_cache = result["access_token"]
            return _jj_token_cache
    
    print("Authenticating with Microsoft (browser may open)...")
    
    kernel32 = ctypes.windll.kernel32
    hwnd = kernel32.GetConsoleWindow()
    
    result = app.acquire_token_interactive(
        scopes,
        parent_window_handle=hwnd,
    )
    
    if "access_token" in result:
        _jj_token_cache = result["access_token"]
        return _jj_token_cache
    else:
        raise Exception(f"Authentication failed: {result.get('error_description', result)}")


def call_gpt5_api(prompt: str, temperature: float = 0.3, max_tokens: int = 4000, max_retries: int = 3) -> str:
    """Call Substrate GPT-5 JJ API with retry logic."""
    import requests
    
    token = get_substrate_token()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-ModelType": JJ_MODEL,
    }
    
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    for attempt in range(max_retries):
        response = requests.post(
            SUBSTRATE_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        elif response.status_code == 429:
            wait_time = (attempt + 1) * 15
            print(f"      Rate limited, waiting {wait_time}s...", end="", flush=True)
            time.sleep(wait_time)
            print(" retrying")
        else:
            raise Exception(f"GPT-5 API error {response.status_code}: {response.text[:200]}")
    
    raise Exception(f"GPT-5 API rate limited after {max_retries} retries")


# ═══════════════════════════════════════════════════════════════════════════════
# Plan Generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_plan(quality_level: str) -> str:
    """Generate a workback plan at the specified quality level using GPT-5."""
    
    patterns_summary = "\n".join([
        f"- **{p['pattern_id']}: {p['pattern_name']}** ({p['level_recommendation']}): {p['pattern_description']}"
        for p in PATTERNS
    ])
    
    if quality_level == "perfect":
        quality_instructions = """
Generate a PERFECT workback plan that exemplifies best practices. This plan should:
- Score 10/10 on ALL 10 patterns (P1-P10)
- Include explicit meeting date, time (with timezone), and all attendees with full names
- Have a detailed backward timeline from T₀ with specific dates, at least 8-10 tasks, and buffer days
- Assign every task to a named owner (Sarah Chen, Mike Johnson, Lisa Park, or Tom Wilson)
- Reference all 4 artifacts by exact filename
- Make dependencies explicit (e.g., "engineering sign-off before QA")
- State the meeting objective clearly
- Include an "Assumptions" section with 2-3 explicit assumptions
- Include stakeholder alignment tasks (feedback collection, reviews)
- Identify 2-3 risks with specific mitigations

This is a gold-standard example that human judges would rate as excellent.
Format with clear sections, tables, and bullet points.
"""
    elif quality_level == "medium":
        quality_instructions = """
Generate a MEDIUM quality workback plan that is acceptable but has notable gaps. This plan should:
- Score around 5-6/10 overall
- Include the meeting date but MISS the timezone or exact time
- Use first names only for attendees (Sarah, Mike, Lisa, Tom - not full names)
- Have a basic timeline but with NO explicit buffer day
- Assign owners to MOST but NOT ALL tasks (leave 1-2 unassigned)
- Reference only 2 of the 4 artifacts
- Have tasks listed but WITHOUT explicit dependencies stated
- Have a vague or missing meeting objective
- NO assumptions section
- NO stakeholder alignment tasks
- NO risk identification

This represents a "passing but needs improvement" plan.
"""
    else:  # low
        quality_instructions = """
Generate a LOW quality workback plan with significant issues. This plan should:
- Score around 2-3/10 overall
- Have the WRONG meeting date (use January 16 instead of January 15) and WRONG time (use 3pm instead of 2pm)
- Miss the timezone entirely
- Include a FABRICATED attendee "John from Marketing" who is NOT in the scenario
- Have vague tasks WITHOUT specific dates
- Use generic ownership like "someone should" or "team will" instead of named owners
- NOT reference any specific artifacts (just say "documents" or "files")
- Have tasks in random order with NO logical sequencing
- NO meeting objective stated
- NO assumptions
- NO stakeholder tasks
- NO risks

This represents a poor plan that would fail human review.
"""
    
    prompt = f"""You are generating example workback plans for a quality evaluation exercise.

## Scenario:
{SCENARIO}

## User Request:
{USER_PROMPT}

## Quality Assessment Patterns (P1-P10):
{patterns_summary}

## Your Task:
{quality_instructions}

Generate ONLY the workback plan content, no meta-commentary about quality levels.
"""
    
    print(f"  Generating {quality_level} quality plan...", end="", flush=True)
    result = call_gpt5_api(prompt, temperature=0.4, max_tokens=3000)
    print(" done")
    time.sleep(DELAY_BETWEEN_CALLS)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Assertion Generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_assertions() -> List[Dict]:
    """Generate assertions based on P1-P10 patterns for this scenario using GPT-5."""
    
    patterns_detail = "\n\n".join([
        f"""### {p['pattern_id']}: {p['pattern_name']} ({p['level_recommendation']})
- Description: {p['pattern_description']}
- Template: {p['pattern_template']}
- Evaluation Criteria: {'; '.join(p['evaluation_criteria'])}
- Example: {p['example_instances'][0] if p['example_instances'] else 'N/A'}"""
        for p in PATTERNS
    ])
    
    prompt = f"""Generate 10 specific assertions (A1-A10) to evaluate workback plans for this scenario.
Each assertion must be based on one of the P1-P10 patterns.

## Scenario:
{SCENARIO}

## Patterns (P1-P10):
{patterns_detail}

## Task:
Generate exactly 10 assertions, one for each pattern (P1-P10).
Each assertion should be:
1. Specific to this scenario (use exact names, dates, artifacts from the scenario)
2. Testable (clear pass/fail criteria)
3. Assigned the same level as its source pattern (critical/expected/aspirational)

## Output Format (JSON):
Return a JSON array with 10 objects, each containing:
- "id": "A1" through "A10"
- "pattern": "P1" through "P10"
- "level": "critical" | "expected" | "aspirational"
- "text": The assertion text
- "pass_criteria": Brief description of what constitutes passing

Return ONLY the JSON array, no markdown or other text.
"""
    
    print("  Generating assertions...", end="", flush=True)
    result = call_gpt5_api(prompt, temperature=0.2, max_tokens=3000)
    print(" done")
    time.sleep(DELAY_BETWEEN_CALLS)
    
    # Parse JSON from response
    try:
        # Try to extract JSON from the response
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0].strip()
        else:
            json_str = result.strip()
        
        assertions = json.loads(json_str)
        return assertions
    except Exception as e:
        print(f"\n  Warning: Could not parse assertions JSON: {e}")
        print(f"  Raw response: {result[:500]}...")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# Plan Evaluation
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_plan(plan: str, assertions: List[Dict], quality_label: str) -> Dict:
    """Evaluate a plan against all assertions using GPT-5."""
    
    assertions_text = "\n".join([
        f"- **{a['id']} ({a['pattern']}, {a['level']})**: {a['text']}"
        for a in assertions
    ])
    
    prompt = f"""Evaluate this workback plan against the provided assertions.

## Scenario:
{SCENARIO}

## Plan to Evaluate:
{plan}

## Assertions to Check:
{assertions_text}

## Task:
For each assertion (A1-A10), determine if the plan PASSES or FAILS.
Provide:
1. Pass/Fail status
2. Score (0-10)
3. Brief evidence (quote from plan or note what's missing)

## Output Format (JSON):
Return a JSON object with:
- "quality_label": "{quality_label}"
- "results": array of 10 objects, each with:
  - "assertion_id": "A1" through "A10"
  - "pattern": "P1" through "P10"
  - "level": the level
  - "passed": true/false
  - "score": 0-10
  - "evidence": brief explanation
- "total_score": sum of all scores (0-100)
- "summary": 2-3 sentence overall assessment

Return ONLY the JSON, no markdown or other text.
"""
    
    print(f"  Evaluating {quality_label} plan...", end="", flush=True)
    result = call_gpt5_api(prompt, temperature=0.1, max_tokens=3000)
    print(" done")
    time.sleep(DELAY_BETWEEN_CALLS)
    
    # Parse JSON
    try:
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0].strip()
        else:
            json_str = result.strip()
        
        return json.loads(json_str)
    except Exception as e:
        print(f"\n  Warning: Could not parse evaluation JSON: {e}")
        print(f"  Raw response: {result[:500]}...")
        return {"error": str(e), "raw": result}


# ═══════════════════════════════════════════════════════════════════════════════
# Report Generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_report(plans: Dict[str, str], assertions: List[Dict], evaluations: Dict[str, Dict]) -> str:
    """Generate the final markdown report."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Build assertions table
    assertions_table = "| ID | Pattern | Level | Assertion |\n|----|---------|----|----|\n"
    for a in assertions:
        text = a['text'][:80] + "..." if len(a['text']) > 80 else a['text']
        assertions_table += f"| {a['id']} | {a['pattern']} | {a['level']} | {text} |\n"
    
    # Build evaluation sections
    eval_sections = ""
    for quality in ["perfect", "medium", "low"]:
        plan = plans[quality]
        eval_data = evaluations[quality]
        
        if "error" in eval_data:
            eval_table = f"Error evaluating: {eval_data['error']}"
            total = "N/A"
            summary = "Evaluation failed"
        else:
            total = eval_data.get('total_score', 'N/A')
            summary = eval_data.get('summary', '')
            
            eval_table = "| Assertion | Pattern | Level | Pass/Fail | Score | Evidence |\n"
            eval_table += "|-----------|---------|-------|-----------|-------|----------|\n"
            for r in eval_data.get('results', []):
                status = "✅ PASS" if r.get('passed') else "❌ FAIL"
                evidence = r.get('evidence', '')[:60] + "..." if len(r.get('evidence', '')) > 60 else r.get('evidence', '')
                eval_table += f"| {r.get('assertion_id')} | {r.get('pattern')} | {r.get('level')} | {status} | {r.get('score', 0)}/10 | {evidence} |\n"
        
        quality_emoji = {"perfect": "⭐", "medium": "📊", "low": "❌"}[quality]
        
        eval_sections += f"""
---

# {quality.upper()} Quality Plan {quality_emoji}

## Generated Plan

{plan}

## Evaluation Results

**Total Score: {total}/100**

{summary}

{eval_table}

"""
    
    report = f"""# Workback Plan Quality Examples & Evaluation Report

> **Generated by GPT-5 JJ:** {timestamp}  
> **Purpose:** Demonstrate how the 10 assertion patterns (P1-P10) apply to workback plans at different quality levels

---

## Scenario

{SCENARIO}

**User Prompt:** "{USER_PROMPT}"

---

## Assertion Patterns Reference

| ID | Pattern | Level | Key Criteria |
|----|---------|-------|--------------|
"""
    
    for p in PATTERNS:
        criteria = p['evaluation_criteria'][0][:50] + "..." if len(p['evaluation_criteria'][0]) > 50 else p['evaluation_criteria'][0]
        report += f"| {p['pattern_id']} | {p['pattern_name']} | {p['level_recommendation']} | {criteria} |\n"
    
    report += f"""
---

## Generated Assertions (A1-A10)

{assertions_table}

{eval_sections}

---

# Summary Comparison

| Quality | Total Score | Critical (P1,P2,P3,P9) | Expected (P4,P5,P6) | Aspirational (P7,P8,P10) |
|---------|-------------|------------------------|---------------------|--------------------------|
"""
    
    for quality in ["perfect", "medium", "low"]:
        eval_data = evaluations[quality]
        if "error" not in eval_data:
            total = eval_data.get('total_score', 'N/A')
            results = eval_data.get('results', [])
            
            critical_score = sum(r.get('score', 0) for r in results if r.get('pattern') in ['P1', 'P2', 'P3', 'P9'])
            expected_score = sum(r.get('score', 0) for r in results if r.get('pattern') in ['P4', 'P5', 'P6'])
            aspirational_score = sum(r.get('score', 0) for r in results if r.get('pattern') in ['P7', 'P8', 'P10'])
            
            report += f"| **{quality.capitalize()}** | {total}/100 | {critical_score}/40 | {expected_score}/30 | {aspirational_score}/30 |\n"
        else:
            report += f"| **{quality.capitalize()}** | Error | - | - | - |\n"
    
    report += """
---

## Human Judge Guidelines

1. **Critical Patterns (P1, P2, P3, P9)** - Must pass for acceptable quality
2. **Expected Patterns (P4, P5, P6)** - Should pass for good quality  
3. **Aspirational Patterns (P7, P8, P10)** - Differentiators for excellence

**Minimum Acceptable Score:** 60/100 with all critical patterns passing

---

*Generated using GPT-5 JJ for the Assertion Quality Analysis exercise*
"""
    
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("GENERATING PLAN QUALITY EXAMPLES USING GPT-5 JJ")
    print("=" * 70)
    print()
    
    # Step 1: Generate plans at three quality levels
    print("Step 1: Generating plans...")
    plans = {}
    for quality in ["perfect", "medium", "low"]:
        plans[quality] = generate_plan(quality)
    print()
    
    # Step 2: Generate assertions based on P1-P10
    print("Step 2: Generating assertions based on P1-P10 patterns...")
    assertions = generate_assertions()
    print(f"  Generated {len(assertions)} assertions")
    print()
    
    # Step 3: Evaluate each plan
    print("Step 3: Evaluating plans against assertions...")
    evaluations = {}
    for quality in ["perfect", "medium", "low"]:
        evaluations[quality] = evaluate_plan(plans[quality], assertions, quality)
    print()
    
    # Step 4: Generate report
    print("Step 4: Generating report...")
    report = generate_report(plans, assertions, evaluations)
    
    # Save outputs
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  Saved report to: {OUTPUT_FILE}")
    
    # Save JSON data
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "scenario": SCENARIO,
        "user_prompt": USER_PROMPT,
        "plans": plans,
        "assertions": assertions,
        "evaluations": evaluations
    }
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved JSON data to: {JSON_OUTPUT}")
    
    # Print summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for quality in ["perfect", "medium", "low"]:
        eval_data = evaluations[quality]
        if "error" not in eval_data:
            print(f"  {quality.capitalize():8} Plan: {eval_data.get('total_score', 'N/A')}/100")
        else:
            print(f"  {quality.capitalize():8} Plan: Error - {eval_data['error'][:50]}")
    
    print()
    print("Done!")


if __name__ == "__main__":
    main()
