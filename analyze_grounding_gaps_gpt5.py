#!/usr/bin/env python3
"""
GPT-5 Enhanced Grounding Gap Analysis

Analyzes assertions from multiple Kening JSONL files to identify grounding entity types
not covered by G2-G6, using GPT-5 for semantic classification with keyword hints.

Data Sources:
1. docs/11_25_output_with_matches.jsonl - 102 meeting instances with assertions
2. docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl - 224 records with assertions
"""

import json
import os
import re
import time
import ctypes
import requests
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════════════
# Substrate GPT-5 JJ API Configuration (from analyze_assertions_gpt5.py)
# ═══════════════════════════════════════════════════════════════════════════════

SUBSTRATE_ENDPOINT = "https://fe-26.qas.bing.net/chat/completions"
SUBSTRATE_RESOURCE = "https://substrate.office.com"
CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
JJ_MODEL = "dev-gpt-5-chat-jj"

# Rate limiting
DELAY_BETWEEN_CALLS = 2  # seconds

# Global token cache
_jj_token_cache = None


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
    
    # Try silent auth first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            _jj_token_cache = result["access_token"]
            return _jj_token_cache
    
    # Fall back to interactive
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


def call_gpt5_api(prompt: str, system_prompt: str = None, temperature: float = 0.3, max_tokens: int = 4000, max_retries: int = 3) -> str:
    """Call Substrate GPT-5 JJ API with retry logic."""
    
    token = get_substrate_token()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-ModelType": JJ_MODEL,
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "messages": messages,
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
            time.sleep(DELAY_BETWEEN_CALLS)  # Rate limiting
            return result["choices"][0]["message"]["content"]
        elif response.status_code == 429:
            wait_time = (attempt + 1) * 15
            print(f"      Rate limited, waiting {wait_time}s...", end="", flush=True)
            time.sleep(wait_time)
            print(" retrying")
        else:
            raise Exception(f"GPT-5 API error {response.status_code}: {response.text[:200]}")
    
    raise Exception(f"GPT-5 API rate limited after {max_retries} retries")

# Current G2-G6 definitions for reference
CURRENT_G_DIMENSIONS = """
G2: Attendee Grounding - Verifies attendee/participant names exist in source
G3: DateTime Grounding - Verifies dates/times/deadlines exist in source  
G4: Artifact Grounding - Verifies files/documents/links exist in source
G5: Topic Grounding - Verifies topics/subjects/agenda items exist in source
G6: Task Grounding - Verifies tasks/action items exist in source
"""

# Keyword hints from previous regex analysis
KEYWORD_HINTS = """
Patterns found NOT in G2-G6 (from regex analysis):
- email/communication (160 occurrences): email, message, thread, reply, teams, slack
- status/progress (96 occurrences): status, progress, complete, done, pending, blocked
- role/responsibility (74 occurrences): role, responsible, owner, lead, assigned, RACI
- decision/outcome (62 occurrences): decision, outcome, conclusion, agreed, approved
- constraint/limit (40 occurrences): constraint, limit, budget, cap, maximum, requirement
- location/place (28 occurrences): location, room, venue, place, building
- number/quantity (26 occurrences): budget amount, percentages, counts, costs
- priority/urgency (25 occurrences): priority, urgent, critical, P1/P2, important
"""

def load_assertions():
    """Load assertions from both JSONL files."""
    assertions = []
    
    # Source 1: 11_25_output_with_matches.jsonl
    try:
        with open('docs/11_25_output_with_matches.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                for a in record.get('assertions', []):
                    assertions.append({
                        'text': a.get('text', ''),
                        'source': '11_25_output_with_matches.jsonl',
                        'level': a.get('level', 'unknown')
                    })
    except Exception as e:
        print(f"Warning: Could not load 11_25_output_with_matches.jsonl: {e}")
    
    # Source 2: Assertions_genv2_for_LOD1126part1.jsonl
    try:
        with open('docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                for a in record.get('assertions', []):
                    assertions.append({
                        'text': a.get('text', ''),
                        'source': 'Assertions_genv2_for_LOD1126part1.jsonl',
                        'level': a.get('level', 'unknown')
                    })
    except Exception as e:
        print(f"Warning: Could not load Assertions_genv2_for_LOD1126part1.jsonl: {e}")
    
    return assertions


def classify_assertions_batch(assertions_batch, batch_num, total_batches):
    """Use GPT-5 to classify what grounding entity type each assertion verifies."""
    
    prompt = f"""You are analyzing assertions used to evaluate AI-generated workback plans.

CURRENT GROUNDING DIMENSIONS (G2-G6):
{CURRENT_G_DIMENSIONS}

KEYWORD HINTS (from regex analysis showing patterns NOT covered by G2-G6):
{KEYWORD_HINTS}

TASK: For each assertion below, identify what type of grounding entity it is verifying.
- If it fits G2-G6, label it with that dimension
- If it verifies something NOT in G2-G6, propose a new category name

For each assertion, respond with a JSON object containing:
- "assertion_id": the index number
- "grounding_type": one of [G2_Attendee, G3_DateTime, G4_Artifact, G5_Topic, G6_Task, NEW_Status, NEW_Decision, NEW_Constraint, NEW_Priority, NEW_Role, NEW_Location, NEW_Quantity, NEW_Communication, OTHER]
- "confidence": high/medium/low
- "reasoning": brief explanation (1 sentence)

ASSERTIONS TO ANALYZE:
"""
    
    for i, a in enumerate(assertions_batch):
        prompt += f"\n{i+1}. \"{a['text']}\""
    
    prompt += "\n\nRespond with a JSON array of classification objects."
    
    print(f"  Processing batch {batch_num}/{total_batches}...")
    
    try:
        system_prompt = "You are an expert at analyzing assertion semantics for grounding verification. Always respond with valid JSON."
        result_text = call_gpt5_api(prompt, system_prompt=system_prompt, temperature=0.3, max_tokens=4000)
        
        # Extract JSON from response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        return json.loads(result_text)
    except Exception as e:
        print(f"    Error in batch {batch_num}: {e}")
        return []


def analyze_with_gpt5(assertions, sample_size=500, batch_size=25):
    """Run GPT-5 analysis on a sample of assertions."""
    
    # Sample assertions (stratified by source if possible)
    import random
    random.seed(42)
    
    if len(assertions) > sample_size:
        sample = random.sample(assertions, sample_size)
    else:
        sample = assertions
    
    print(f"\n{'='*70}")
    print(f"GPT-5 GROUNDING ENTITY CLASSIFICATION")
    print(f"{'='*70}")
    print(f"Total assertions available: {len(assertions)}")
    print(f"Analyzing sample of: {len(sample)}")
    print(f"Batch size: {batch_size}")
    print()
    
    all_classifications = []
    total_batches = (len(sample) + batch_size - 1) // batch_size
    
    for i in range(0, len(sample), batch_size):
        batch = sample[i:i+batch_size]
        batch_num = i // batch_size + 1
        classifications = classify_assertions_batch(batch, batch_num, total_batches)
        
        # Add source info to classifications
        for j, c in enumerate(classifications):
            if i + j < len(sample):
                c['original_text'] = sample[i + j]['text']
                c['source_file'] = sample[i + j]['source']
        
        all_classifications.extend(classifications)
    
    return all_classifications, sample


def summarize_results(classifications):
    """Summarize the GPT-5 classification results."""
    
    type_counts = defaultdict(int)
    type_examples = defaultdict(list)
    confidence_counts = defaultdict(lambda: defaultdict(int))
    
    for c in classifications:
        gtype = c.get('grounding_type', 'UNKNOWN')
        type_counts[gtype] += 1
        confidence_counts[gtype][c.get('confidence', 'unknown')] += 1
        
        if len(type_examples[gtype]) < 3:
            type_examples[gtype].append({
                'text': c.get('original_text', '')[:100],
                'reasoning': c.get('reasoning', '')
            })
    
    print(f"\n{'='*70}")
    print("CLASSIFICATION SUMMARY")
    print(f"{'='*70}\n")
    
    # Separate current G dimensions from NEW ones
    current_g = {k: v for k, v in type_counts.items() if k.startswith('G')}
    new_types = {k: v for k, v in type_counts.items() if k.startswith('NEW')}
    other = {k: v for k, v in type_counts.items() if not k.startswith('G') and not k.startswith('NEW')}
    
    print("CURRENT G2-G6 COVERAGE:")
    print("-" * 40)
    for gtype, count in sorted(current_g.items(), key=lambda x: -x[1]):
        conf = confidence_counts[gtype]
        print(f"  {gtype}: {count} (high:{conf['high']}, med:{conf['medium']}, low:{conf['low']})")
    
    print(f"\nNEW GROUNDING TYPES IDENTIFIED:")
    print("-" * 40)
    for gtype, count in sorted(new_types.items(), key=lambda x: -x[1]):
        conf = confidence_counts[gtype]
        print(f"\n  {gtype}: {count} occurrences")
        print(f"    Confidence: high={conf['high']}, medium={conf['medium']}, low={conf['low']}")
        print(f"    Examples:")
        for ex in type_examples[gtype][:2]:
            print(f"      - \"{ex['text']}...\"")
            print(f"        Reasoning: {ex['reasoning']}")
    
    if other:
        print(f"\nOTHER/UNCATEGORIZED:")
        print("-" * 40)
        for gtype, count in sorted(other.items(), key=lambda x: -x[1]):
            print(f"  {gtype}: {count}")
    
    # Recommendations
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS FOR NEW G DIMENSIONS")
    print(f"{'='*70}\n")
    
    threshold = 10  # Minimum occurrences to recommend
    recommendations = []
    
    for gtype, count in sorted(new_types.items(), key=lambda x: -x[1]):
        if count >= threshold:
            # Extract dimension name
            dim_name = gtype.replace('NEW_', '')
            recommendations.append({
                'name': dim_name,
                'count': count,
                'examples': type_examples[gtype]
            })
    
    for i, rec in enumerate(recommendations, start=7):
        print(f"G{i}: {rec['name']} Grounding ({rec['count']} occurrences)")
        print(f"    Purpose: Verify {rec['name'].lower()} information matches source")
        print(f"    Example assertion:")
        if rec['examples']:
            print(f"      \"{rec['examples'][0]['text']}...\"")
        print()
    
    return {
        'current_g': current_g,
        'new_types': new_types,
        'recommendations': recommendations,
        'total_classified': len(classifications)
    }


def main():
    print("="*70)
    print("GPT-5 ENHANCED GROUNDING GAP ANALYSIS")
    print("="*70)
    print("\nLoading assertions from multiple sources...")
    
    assertions = load_assertions()
    print(f"  Loaded {len(assertions)} total assertions")
    
    # Count by source
    source_counts = defaultdict(int)
    for a in assertions:
        source_counts[a['source']] += 1
    print("\n  By source:")
    for src, count in source_counts.items():
        print(f"    - {src}: {count}")
    
    # Run GPT-5 analysis
    classifications, sample = analyze_with_gpt5(assertions, sample_size=300, batch_size=20)
    
    # Summarize results
    results = summarize_results(classifications)
    
    # Save detailed results
    output_file = 'docs/grounding_gap_analysis_gpt5.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_assertions': len(assertions),
            'sample_size': len(sample),
            'classifications': classifications,
            'summary': {
                'current_g': dict(results['current_g']),
                'new_types': dict(results['new_types']),
                'recommendations': results['recommendations']
            }
        }, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")


if __name__ == '__main__':
    main()
