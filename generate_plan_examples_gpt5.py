"""
Generate Plan Quality Examples Using GPT-5 JJ

This script uses GPT-5 JJ to:
1. Generate three workback plans at different quality levels (perfect, medium, low)
2. Generate assertions based on P1-P10 patterns (Structural) AND G1-G5 (Grounding)
3. Evaluate each plan against both structural and grounding assertions
4. Create a comprehensive evaluation report with two-layer scoring

The key insight is:
- Structural Patterns (P1-P10): "Does the plan HAVE the right shape?"
- Grounding Assertions (G1-G5): "Are those elements FACTUALLY CORRECT to source?"

A plan that passes structural checks but fails grounding is WORSE than one that is 
incomplete but accurate - hallucinated plans with good structure can mislead users.

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
    GROUNDING_ASSERTIONS = PATTERNS_DATA.get('grounding_assertions', {}).get('assertions', [])

# Define source entities explicitly for grounding verification
SOURCE_ENTITIES = {
    "attendees": ["Sarah Chen", "Mike Johnson", "Lisa Park", "Tom Wilson"],
    "organizer": "Sarah Chen",
    "meeting_date": "January 15, 2025",
    "meeting_time": "2:00 PM PST",
    "files": [
        "Product_Launch_Checklist_v3.xlsx",
        "Engineering_Status_Report.pdf", 
        "Design_Assets_Summary.docx",
        "QA_Test_Results_Dec.pdf"
    ],
    "topics": [
        "Q1 Product Launch",
        "February 1, 2025 launch",
        "readiness items",
        "blockers",
        "launch checklist"
    ],
    "dependencies": [
        "Engineering sign-off before QA final approval",
        "Design assets before marketing materials",
        "Legal review on Terms of Service"
    ]
}


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

def generate_structural_assertions() -> List[Dict]:
    """Generate structural assertions based on P1-P10 patterns for this scenario using GPT-5."""
    
    patterns_detail = "\n\n".join([
        f"""### {p['pattern_id']}: {p['pattern_name']} ({p['level_recommendation']})
- Description: {p['pattern_description']}
- Template: {p['pattern_template']}
- Evaluation Criteria: {'; '.join(p['evaluation_criteria'])}
- Example: {p['example_instances'][0] if p['example_instances'] else 'N/A'}"""
        for p in PATTERNS
    ])
    
    prompt = f"""Generate 10 specific STRUCTURAL assertions (A1-A10) to evaluate workback plans for this scenario.
Each assertion checks if the plan HAS certain elements (shape/structure).

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
- "type": "structural"
- "text": The assertion text
- "pass_criteria": Brief description of what constitutes passing

Return ONLY the JSON array, no markdown or other text.
"""
    
    print("  Generating structural assertions (P1-P10)...", end="", flush=True)
    result = call_gpt5_api(prompt, temperature=0.2, max_tokens=3000)
    print(" done")
    time.sleep(DELAY_BETWEEN_CALLS)
    
    # Parse JSON from response
    try:
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
        return []


def generate_grounding_assertions() -> List[Dict]:
    """Generate grounding assertions (G1-G5) to verify factual accuracy against source."""
    
    source_json = json.dumps(SOURCE_ENTITIES, indent=2)
    
    prompt = f"""Generate 5 specific GROUNDING assertions (G1-G5) to verify factual accuracy of workback plans.
These check if claims in the plan are CORRECT according to the source data.

## Scenario:
{SCENARIO}

## Source Entities (Ground Truth):
{source_json}

## Grounding Assertion Types:
- G1: People Grounding - All people mentioned must exist in source attendees
- G2: Temporal Grounding - All dates/times must match or derive from source meeting time
- G3: Artifact Grounding - All files must exist in source files list
- G4: Topic Grounding - Topics must align with source meeting purpose/topics
- G5: No Hallucination - No fabricated entities not in source

## Task:
Generate exactly 5 grounding assertions, one for each type (G1-G5).
Each assertion should:
1. Reference the specific source entities for verification
2. Be testable against the source data
3. Detect hallucinations or inaccuracies

## Output Format (JSON):
Return a JSON array with 5 objects, each containing:
- "id": "G1" through "G5"
- "type": "grounding"
- "name": Brief name (e.g., "People Grounding")
- "level": "critical" (all grounding assertions are critical)
- "text": The assertion text
- "sourceID": What source data to check against
- "failure_examples": Examples of what would fail this check

Return ONLY the JSON array, no markdown or other text.
"""
    
    print("  Generating grounding assertions (G1-G5)...", end="", flush=True)
    result = call_gpt5_api(prompt, temperature=0.2, max_tokens=2000)
    print(" done")
    time.sleep(DELAY_BETWEEN_CALLS)
    
    try:
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0].strip()
        else:
            json_str = result.strip()
        
        assertions = json.loads(json_str)
        return assertions
    except Exception as e:
        print(f"\n  Warning: Could not parse grounding assertions JSON: {e}")
        return []


def generate_assertions() -> Dict[str, List[Dict]]:
    """Generate both structural and grounding assertions."""
    structural = generate_structural_assertions()
    grounding = generate_grounding_assertions()
    return {
        "structural": structural,
        "grounding": grounding
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Plan Evaluation
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_plan_structural(plan: str, assertions: List[Dict], quality_label: str) -> Dict:
    """Evaluate a plan against structural assertions (P1-P10) using GPT-5."""
    
    assertions_text = "\n".join([
        f"- **{a['id']} ({a.get('pattern', 'N/A')}, {a['level']})**: {a['text']}"
        for a in assertions
    ])
    
    prompt = f"""Evaluate this workback plan against the STRUCTURAL assertions.
Structural assertions check if the plan HAS certain elements (shape/completeness).

## Scenario:
{SCENARIO}

## Plan to Evaluate:
{plan}

## Structural Assertions to Check:
{assertions_text}

## Task:
For each assertion (A1-A10), determine if the plan PASSES or FAILS.
Provide:
1. Pass/Fail status
2. Score (0-10)
3. Brief evidence (quote from plan or note what's missing)

## Output Format (JSON):
Return a JSON object with:
- "evaluation_type": "structural"
- "quality_label": "{quality_label}"
- "results": array of 10 objects, each with:
  - "assertion_id": "A1" through "A10"
  - "pattern": "P1" through "P10"
  - "level": the level
  - "passed": true/false
  - "score": 0-10
  - "evidence": brief explanation
- "total_score": sum of all scores (0-100)
- "summary": 2-3 sentence assessment of structural completeness

Return ONLY the JSON, no markdown or other text.
"""
    
    print(f"    Structural eval...", end="", flush=True)
    result = call_gpt5_api(prompt, temperature=0.1, max_tokens=3000)
    print(" done", end="")
    time.sleep(DELAY_BETWEEN_CALLS)
    
    try:
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0].strip()
        else:
            json_str = result.strip()
        return json.loads(json_str)
    except Exception as e:
        return {"error": str(e), "raw": result}


def evaluate_plan_grounding(plan: str, assertions: List[Dict], quality_label: str) -> Dict:
    """Evaluate a plan against grounding assertions (G1-G5) using GPT-5."""
    
    source_json = json.dumps(SOURCE_ENTITIES, indent=2)
    
    assertions_text = "\n".join([
        f"- **{a['id']} ({a.get('name', 'N/A')})**: {a['text']}\n  Source to check: {a.get('sourceID', 'N/A')}"
        for a in assertions
    ])
    
    prompt = f"""Evaluate this workback plan against the GROUNDING assertions.
Grounding assertions check if claims are FACTUALLY ACCURATE to the source data.

## Source Entities (Ground Truth):
{source_json}

## Plan to Evaluate:
{plan}

## Grounding Assertions to Check:
{assertions_text}

## Task:
For each grounding assertion (G1-G5), determine if the plan PASSES or FAILS.
A plan FAILS if it contains ANY entity not in the source data.

Provide:
1. Pass/Fail status
2. Score (0-10) - 10 if fully grounded, 0 if hallucinations detected
3. Supporting spans - QUOTE the specific text from the plan that proves grounding
4. Violations - List any entities NOT found in source (hallucinations)

## Output Format (JSON):
Return a JSON object with:
- "evaluation_type": "grounding"
- "quality_label": "{quality_label}"
- "results": array of 5 objects, each with:
  - "assertion_id": "G1" through "G5"
  - "name": assertion name
  - "passed": true/false
  - "score": 0-10
  - "supporting_spans": array of quoted text from plan proving correctness
  - "violations": array of entities not in source (empty if passed)
  - "evidence": brief explanation
- "total_score": sum of all scores (0-50)
- "hallucination_count": total fabricated entities found
- "summary": 2-3 sentence assessment of factual accuracy

Return ONLY the JSON, no markdown or other text.
"""
    
    print(f" Grounding eval...", end="", flush=True)
    result = call_gpt5_api(prompt, temperature=0.1, max_tokens=3000)
    print(" done")
    time.sleep(DELAY_BETWEEN_CALLS)
    
    try:
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0].strip()
        else:
            json_str = result.strip()
        return json.loads(json_str)
    except Exception as e:
        return {"error": str(e), "raw": result}


def evaluate_plan(plan: str, assertions: Dict[str, List[Dict]], quality_label: str) -> Dict:
    """Evaluate a plan against both structural and grounding assertions."""
    print(f"  Evaluating {quality_label} plan:")
    
    structural_eval = evaluate_plan_structural(plan, assertions.get("structural", []), quality_label)
    grounding_eval = evaluate_plan_grounding(plan, assertions.get("grounding", []), quality_label)
    
    # Compute combined score and quality determination
    structural_score = structural_eval.get("total_score", 0) if "error" not in structural_eval else 0
    grounding_score = grounding_eval.get("total_score", 0) if "error" not in grounding_eval else 0
    
    # Quality matrix
    structural_pass = structural_score >= 60  # 60% threshold
    grounding_pass = grounding_score >= 40   # 80% of 50 = 40
    
    if structural_pass and grounding_pass:
        quality_verdict = "EXCELLENT - Complete and Accurate"
    elif structural_pass and not grounding_pass:
        quality_verdict = "REJECT - Good structure but contains hallucinations"
    elif not structural_pass and grounding_pass:
        quality_verdict = "NEEDS WORK - Accurate but incomplete"
    else:
        quality_verdict = "POOR - Incomplete and inaccurate"
    
    return {
        "quality_label": quality_label,
        "structural": structural_eval,
        "grounding": grounding_eval,
        "combined_score": {
            "structural_score": structural_score,
            "structural_max": 100,
            "grounding_score": grounding_score,
            "grounding_max": 50,
            "total": structural_score + grounding_score,
            "max": 150
        },
        "quality_verdict": quality_verdict
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Report Generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_report(plans: Dict[str, str], assertions: Dict[str, List[Dict]], evaluations: Dict[str, Dict]) -> str:
    """Generate the final markdown report with two-layer evaluation."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Build structural assertions table
    structural_assertions = assertions.get("structural", [])
    struct_table = "| ID | Pattern | Level | Assertion |\n|----|---------|----|----|\n"
    for a in structural_assertions:
        text = a['text'][:80] + "..." if len(a['text']) > 80 else a['text']
        struct_table += f"| {a['id']} | {a.get('pattern', 'N/A')} | {a['level']} | {text} |\n"
    
    # Build grounding assertions table  
    grounding_assertions = assertions.get("grounding", [])
    ground_table = "| ID | Name | Source Reference | Assertion |\n|----|------|------------------|----|\n"
    for a in grounding_assertions:
        text = a['text'][:60] + "..." if len(a['text']) > 60 else a['text']
        source = a.get('sourceID', 'N/A')[:30] + "..." if len(a.get('sourceID', '')) > 30 else a.get('sourceID', 'N/A')
        ground_table += f"| {a['id']} | {a.get('name', 'N/A')} | {source} | {text} |\n"
    
    # Build evaluation sections
    eval_sections = ""
    for quality in ["perfect", "medium", "low"]:
        plan = plans[quality]
        eval_data = evaluations[quality]
        
        structural_eval = eval_data.get("structural", {})
        grounding_eval = eval_data.get("grounding", {})
        combined = eval_data.get("combined_score", {})
        verdict = eval_data.get("quality_verdict", "Unknown")
        
        # Structural results table
        if "error" in structural_eval:
            struct_eval_table = f"Error: {structural_eval['error']}"
        else:
            struct_eval_table = "| Assertion | Pattern | Level | Pass/Fail | Score | Evidence |\n"
            struct_eval_table += "|-----------|---------|-------|-----------|-------|----------|\n"
            for r in structural_eval.get('results', []):
                status = "✅ PASS" if r.get('passed') else "❌ FAIL"
                evidence = r.get('evidence', '')[:50] + "..." if len(r.get('evidence', '')) > 50 else r.get('evidence', '')
                struct_eval_table += f"| {r.get('assertion_id')} | {r.get('pattern')} | {r.get('level')} | {status} | {r.get('score', 0)}/10 | {evidence} |\n"
        
        # Grounding results table
        if "error" in grounding_eval:
            ground_eval_table = f"Error: {grounding_eval['error']}"
        else:
            ground_eval_table = "| Assertion | Name | Pass/Fail | Score | Violations | Supporting Spans |\n"
            ground_eval_table += "|-----------|------|-----------|-------|------------|------------------|\n"
            for r in grounding_eval.get('results', []):
                status = "✅ PASS" if r.get('passed') else "❌ FAIL"
                violations = ", ".join(r.get('violations', []))[:40] or "None"
                spans = r.get('supporting_spans', [])
                span_text = spans[0][:30] + "..." if spans and len(spans[0]) > 30 else (spans[0] if spans else "N/A")
                ground_eval_table += f"| {r.get('assertion_id')} | {r.get('name', 'N/A')} | {status} | {r.get('score', 0)}/10 | {violations} | {span_text} |\n"
        
        quality_emoji = {"perfect": "⭐", "medium": "📊", "low": "❌"}[quality]
        verdict_emoji = "✅" if "EXCELLENT" in verdict else ("⚠️" if "NEEDS" in verdict else "🚫")
        
        eval_sections += f"""
---

# {quality.upper()} Quality Plan {quality_emoji}

## Generated Plan

{plan}

## Two-Layer Evaluation Results

### Quality Verdict: {verdict_emoji} {verdict}

| Layer | Score | Max | Percentage |
|-------|-------|-----|------------|
| Structural (P1-P10) | {combined.get('structural_score', 'N/A')} | {combined.get('structural_max', 100)} | {round(combined.get('structural_score', 0) / combined.get('structural_max', 100) * 100)}% |
| Grounding (G1-G5) | {combined.get('grounding_score', 'N/A')} | {combined.get('grounding_max', 50)} | {round(combined.get('grounding_score', 0) / max(combined.get('grounding_max', 50), 1) * 100)}% |
| **Combined** | **{combined.get('total', 'N/A')}** | **{combined.get('max', 150)}** | **{round(combined.get('total', 0) / max(combined.get('max', 150), 1) * 100)}%** |

### Layer 1: Structural Evaluation (Does the plan HAVE the right elements?)

{structural_eval.get('summary', 'N/A')}

{struct_eval_table}

### Layer 2: Grounding Evaluation (Are those elements FACTUALLY CORRECT?)

{grounding_eval.get('summary', 'N/A')}

**Hallucinations detected:** {grounding_eval.get('hallucination_count', 'N/A')}

{ground_eval_table}

"""
    
    report = f"""# Workback Plan Quality Examples & Evaluation Report

> **Generated by GPT-5 JJ:** {timestamp}  
> **Framework Version:** 2.0 (with Grounding Assertions)  
> **Purpose:** Demonstrate two-layer evaluation: Structural (P1-P10) + Grounding (G1-G5)

---

## Key Insight: Specificity ≠ Grounding

| Concept | Description | Example |
|---------|-------------|---------|
| **Bad Specificity** | Hardcoded values that don't generalize | "Must mention Sarah Chen" |
| **Good Grounding** | Parameterized verification against source | "All people must exist in source.attendees" |

**The Two-Layer Framework:**
- **Structural Patterns (P1-P10):** "Does the plan HAVE the right shape?"
- **Grounding Assertions (G1-G5):** "Are those elements FACTUALLY CORRECT?"

**Critical Rule:** A plan that passes structural checks but fails grounding is **WORSE** than one that is incomplete but accurate. Hallucinated plans with good structure can mislead users.

---

## Scenario

{SCENARIO}

**User Prompt:** "{USER_PROMPT}"

**Source Entities (Ground Truth for Grounding Verification):**
```json
{json.dumps(SOURCE_ENTITIES, indent=2)}
```

---

## Assertion Patterns Reference

### Structural Patterns (P1-P10) - "Does the plan have X?"

| ID | Pattern | Level | Key Criteria |
|----|---------|-------|--------------|
"""
    
    for p in PATTERNS:
        criteria = p['evaluation_criteria'][0][:50] + "..." if len(p['evaluation_criteria'][0]) > 50 else p['evaluation_criteria'][0]
        report += f"| {p['pattern_id']} | {p['pattern_name']} | {p['level_recommendation']} | {criteria} |\n"
    
    report += f"""

### Grounding Assertions (G1-G5) - "Is X accurate to source?"

| ID | Name | Verification | Failure Mode |
|----|------|--------------|--------------|
| G1 | People Grounding | All people → source.attendees | Fabricated attendee |
| G2 | Temporal Grounding | All dates → source.meeting_date | Wrong date/time |
| G3 | Artifact Grounding | All files → source.files | Non-existent file |
| G4 | Topic Grounding | Topics → source.topics | Invented purpose |
| G5 | No Hallucination | No novel entities | Any fabrication |

---

## Generated Structural Assertions (A1-A10)

{struct_table}

## Generated Grounding Assertions (G1-G5)

{ground_table}

{eval_sections}

---

# Summary Comparison

| Quality | Structural | Grounding | Combined | Verdict |
|---------|------------|-----------|----------|---------|
"""
    
    for quality in ["perfect", "medium", "low"]:
        eval_data = evaluations[quality]
        combined = eval_data.get("combined_score", {})
        verdict = eval_data.get("quality_verdict", "Unknown")
        
        verdict_short = verdict.split(" - ")[0] if " - " in verdict else verdict
        report += f"| **{quality.capitalize()}** | {combined.get('structural_score', 'N/A')}/100 | {combined.get('grounding_score', 'N/A')}/50 | {combined.get('total', 'N/A')}/150 | {verdict_short} |\n"
    
    report += """

---

## Quality Matrix

| Scenario | Structural (P1-P10) | Grounding (G1-G5) | Verdict |
|----------|---------------------|-------------------|---------|
| Complete & Accurate | ✅ Pass | ✅ Pass | **EXCELLENT** |
| Complete but Hallucinated | ✅ Pass | ❌ Fail | **REJECT** ⚠️ |
| Accurate but Incomplete | ❌ Fail | ✅ Pass | **NEEDS WORK** |
| Neither | ❌ Fail | ❌ Fail | **POOR** |

**Minimum Requirements for Acceptance:**
- Structural: ≥60/100 with all critical patterns (P1, P2, P3, P9) passing
- Grounding: ≥40/50 (no more than 1 hallucination)

---

## Human Judge Guidelines

### Priority Order (Revised)
1. **Grounding (G1-G5)** - Factual accuracy FIRST
2. **Critical Structural (P1, P2, P3, P9)** - Essential elements
3. **Expected Structural (P4, P5, P6)** - Standard quality
4. **Aspirational (P7, P8, P10)** - Excellence indicators

### Why Grounding First?
A beautifully structured plan with the wrong meeting date, fabricated attendees, or non-existent files is **worse than useless** - it actively misleads the user.

---

*Generated using GPT-5 JJ for the Assertion Quality Analysis exercise*  
*Framework Version 2.0 - November 2025*
"""
    
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("GENERATING PLAN QUALITY EXAMPLES USING GPT-5 JJ")
    print("Framework v2.0: Structural (P1-P10) + Grounding (G1-G5)")
    print("=" * 70)
    print()
    
    # Step 1: Generate plans at three quality levels
    print("Step 1: Generating plans...")
    plans = {}
    for quality in ["perfect", "medium", "low"]:
        plans[quality] = generate_plan(quality)
    print()
    
    # Step 2: Generate assertions (both structural and grounding)
    print("Step 2: Generating assertions...")
    assertions = generate_assertions()
    print(f"  Generated {len(assertions.get('structural', []))} structural assertions (P1-P10)")
    print(f"  Generated {len(assertions.get('grounding', []))} grounding assertions (G1-G5)")
    print()
    
    # Step 3: Evaluate each plan (two-layer evaluation)
    print("Step 3: Evaluating plans (two-layer: structural + grounding)...")
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
        "framework_version": "2.0",
        "scenario": SCENARIO,
        "user_prompt": USER_PROMPT,
        "source_entities": SOURCE_ENTITIES,
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
    print("SUMMARY - TWO-LAYER EVALUATION")
    print("=" * 70)
    print(f"{'Quality':<10} | {'Structural':>12} | {'Grounding':>10} | {'Combined':>10} | Verdict")
    print("-" * 70)
    for quality in ["perfect", "medium", "low"]:
        eval_data = evaluations[quality]
        combined = eval_data.get("combined_score", {})
        verdict = eval_data.get("quality_verdict", "Unknown")
        verdict_short = verdict.split(" - ")[0] if " - " in verdict else verdict
        
        struct_score = combined.get('structural_score', 'N/A')
        ground_score = combined.get('grounding_score', 'N/A')
        total_score = combined.get('total', 'N/A')
        
        print(f"{quality.capitalize():<10} | {struct_score:>8}/100 | {ground_score:>6}/50 | {total_score:>6}/150 | {verdict_short}")
    
    print()
    print("Key Insight: A plan with good structure but hallucinations is REJECTED.")
    print("             Grounding (factual accuracy) takes priority over structure.")
    print()
    print("Done!")


if __name__ == "__main__":
    main()
