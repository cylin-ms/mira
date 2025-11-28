"""
GPT-5 Assertion Quality Analysis & Pattern Clustering

This script performs comprehensive analysis of workback plan assertions:
1. Critiques each assertion for quality, applicability, and robustness
2. Clusters assertions into generalizable patterns
3. Generates actionable recommendations for human judges

Usage:
    # Run full analysis (sample of assertions)
    python analyze_assertions_gpt5.py
    
    # Analyze all assertions (takes longer)
    python analyze_assertions_gpt5.py --all
    
    # Analyze specific number of samples per dimension
    python analyze_assertions_gpt5.py --samples-per-dim 5
"""

import json
import os
import re
import time
import ctypes
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import Counter, defaultdict

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

INPUT_FILE = os.path.join("docs", "Kening", "Assertions_genv2_for_LOD1126part1.jsonl")
OUTPUT_FILE = os.path.join("docs", "Kening", "assertion_analysis.json")
PATTERNS_FILE = os.path.join("docs", "Kening", "assertion_patterns.json")

# Substrate API Configuration
SUBSTRATE_ENDPOINT = "https://fe-26.qas.bing.net/chat/completions"
SUBSTRATE_RESOURCE = "https://substrate.office.com"
CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
JJ_MODEL = "dev-gpt-5-chat-jj"

# Rate limiting
DELAY_BETWEEN_CALLS = 2  # seconds

# Global token cache
_jj_token_cache = None


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication (reused from evaluate_assertions_gpt5.py)
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
# Data Loading
# ═══════════════════════════════════════════════════════════════════════════════

def load_assertions_data() -> List[Dict]:
    """Load assertions data."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def collect_all_assertions(data: List[Dict]) -> List[Dict]:
    """Flatten all assertions with context."""
    all_assertions = []
    for item_idx, item in enumerate(data):
        utterance = item.get('utterance', '')
        response = item.get('response', '')
        for a_idx, a in enumerate(item.get('assertions', [])):
            all_assertions.append({
                'item_idx': item_idx,
                'assertion_idx': a_idx,
                'utterance': utterance,
                'response': response[:1000],  # Truncate for context
                'text': a.get('text', ''),
                'level': a.get('level', 'unknown'),
                'dim': a.get('anchors', {}).get('Dim', 'Unknown'),
                'sourceID': a.get('anchors', {}).get('sourceID', ''),
            })
    return all_assertions


# ═══════════════════════════════════════════════════════════════════════════════
# GPT-5 Analysis Prompts
# ═══════════════════════════════════════════════════════════════════════════════

def build_critique_prompt(assertions_batch: List[Dict]) -> str:
    """Build prompt for critiquing a batch of assertions."""
    
    assertions_text = ""
    for i, a in enumerate(assertions_batch):
        assertions_text += f"""
---
**Assertion {i+1}:**
- Text: "{a['text']}"
- Level: {a['level']}
- Dimension: {a['dim']}
- Context (utterance): "{a['utterance'][:200]}..."
---
"""
    
    return f"""You are an expert in evaluating quality criteria for AI-generated workback plans in enterprise meeting contexts.

A workback plan helps users prepare for upcoming meetings by identifying tasks, deadlines, dependencies, and materials needed.

## TWO-LAYER ASSERTION FRAMEWORK

When critiquing assertions, classify each as STRUCTURAL or GROUNDING:

### STRUCTURAL Assertions (S1-S10) - Check PRESENCE/SHAPE
- Question: "Does the plan HAVE X?"
- Should NOT contain hardcoded values (dates, names, files)
- Examples: "Has a meeting date", "Lists attendees", "Has task owners"

### GROUNDING Assertions (G1-G5) - Check FACTUAL ACCURACY
- Question: "Is X CORRECT vs source?"
- MUST reference a source field (e.g., source.ATTENDEES, source.MEETING.StartTime)
- Examples: "Date matches source.MEETING.StartTime", "Owners exist in source.ATTENDEES"

### COMMON PITFALLS TO FLAG:
❌ Structural assertion with hardcoded values: "Plan states date as January 15" → Should be "Plan includes a meeting date"
❌ Grounding without source reference: "All attendees are correct" → Should be "Attendees match source.ATTENDEES"
❌ Mixing layers: "Plan has correct attendees" → Split into S (has attendees) + G (match source)

---

Analyze the following {len(assertions_batch)} assertions used to evaluate workback plan quality. For EACH assertion, provide a structured critique:

{assertions_text}

For EACH assertion, analyze and provide a JSON response with this structure:
{{
  "critiques": [
    {{
      "assertion_index": 1,
      "assertion_layer": "structural or grounding",
      "layer_compliance": "compliant, violation, or needs-split",
      "layer_violation_reason": "<if violation: explain what's wrong>",
      "quality_score": <1-10>,
      "issues": [
        {{
          "type": "<specificity|measurability|applicability|robustness|redundancy|ambiguity|completeness|layer-mixing|hardcoded-values|missing-source-ref>",
          "severity": "<high|medium|low>",
          "description": "<specific issue>"
        }}
      ],
      "strengths": ["<strength 1>", "<strength 2>"],
      "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"],
      "rewritten_assertion": "<improved version following two-layer framework or 'N/A' if already good>",
      "split_recommendation": {{
        "needed": true or false,
        "structural_version": "<if needs split: structural-only version>",
        "grounding_version": "<if needs split: grounding-only version with source reference>"
      }},
      "generalizability": "<high|medium|low>",
      "generalizability_notes": "<can this be applied to other workback plans?>"
    }}
  ]
}}

Focus on these quality dimensions:
1. **Layer Compliance**: Does it correctly follow the structural vs grounding distinction?
2. **Specificity**: Is it specific enough to be testable but not overly tied to one example?
3. **Measurability**: Can an evaluator objectively determine pass/fail?
4. **Applicability**: Does it apply to workback plans generally or just this specific one?
5. **Robustness**: Will it work across different meeting types, domains, and contexts?
6. **Redundancy**: Is it duplicating what other assertions already check?
7. **Ambiguity**: Are there multiple valid interpretations?
8. **Source Reference**: For grounding assertions, is the source field clearly specified?

Return ONLY valid JSON, no other text."""


def build_pattern_clustering_prompt(assertions: List[Dict], dimensions: List[str]) -> str:
    """Build prompt for clustering assertions into patterns."""
    
    # Group by dimension
    by_dim = defaultdict(list)
    for a in assertions:
        by_dim[a['dim']].append(a['text'])
    
    dim_samples = ""
    for dim in dimensions[:15]:  # Top 15 dimensions
        samples = by_dim.get(dim, [])[:5]  # Up to 5 samples per dimension
        if samples:
            dim_samples += f"\n**{dim}** ({len(by_dim.get(dim, []))} total):\n"
            for s in samples:
                dim_samples += f"  - {s[:150]}...\n" if len(s) > 150 else f"  - {s}\n"
    
    return f"""You are an expert in evaluation framework design for AI systems.

## TWO-LAYER ASSERTION FRAMEWORK (REQUIRED)

All assertions MUST be classified into exactly one of two layers:

### Layer 1: STRUCTURAL Assertions (S1-S10)
**Purpose:** Check if the plan HAS required elements (PRESENCE/SHAPE)
**Question:** "Does the plan HAVE X?"
**Key Rule:** Do NOT include specific values - only check if the element EXISTS

| ID | Pattern | Checks For |
|----|---------|------------|
| S1 | Explicit Meeting Details | Has date, time, timezone, attendees listed |
| S2 | Timeline Alignment | Has timeline working back from meeting |
| S3 | Ownership Assignment | Has named owners (not "someone", "team") |
| S4 | Artifact Specification | Lists specific files/documents |
| S5 | Date Specification | States completion dates for tasks |
| S6 | Blocker Identification | Identifies dependencies and blockers |
| S7 | Source Traceability | Links tasks to specific source entities |
| S8 | Communication Channels | Mentions appropriate communication methods |
| S9 | Grounding Meta-Check | Passes when G1-G5 all pass |
| S10 | Priority Assignment | Has priority levels for tasks |

### Layer 2: GROUNDING Assertions (G1-G5)  
**Purpose:** Check if values are CORRECT vs source (FACTUAL ACCURACY)
**Question:** "Is X CORRECT?"
**Key Rule:** MUST reference a source field for comparison

| ID | Pattern | Checks Against |
|----|---------|---------------|
| G1 | People Grounding | source.ATTENDEES |
| G2 | Temporal Grounding | source.MEETING.StartTime |
| G3 | Artifact Grounding | source.ENTITIES_TO_USE |
| G4 | Topic Grounding | source.UTTERANCE |
| G5 | No Hallucination | No fabricated entities |

## COMMON PITFALLS TO AVOID

❌ **Wrong:** "The plan states the meeting date as January 15" (This is GROUNDING mixed into structural!)
✅ **Correct Structural:** "The plan includes a meeting date"
✅ **Correct Grounding:** "The meeting date matches source.MEETING.StartTime"

❌ **Wrong:** "Tasks are assigned to Sarah, Mike, or Lisa" (Hardcoded names!)
✅ **Correct Structural:** "Each task has a named owner"
✅ **Correct Grounding:** "All task owners exist in source.ATTENDEES"

---

Analyze these workback plan assertions grouped by dimension and identify generalizable PATTERNS that human judges can use to evaluate ANY workback plan response.

Current assertions by dimension:
{dim_samples}

Your task:
1. Classify each pattern as STRUCTURAL (S1-S10) or GROUNDING (G1-G5)
2. Ensure structural patterns check PRESENCE only, not specific values
3. Ensure grounding patterns reference specific source fields
4. Suggest how patterns can be combined for comprehensive coverage

Return JSON with this structure:
{{
  "patterns": [
    {{
      "pattern_id": "S1 or G1 (use S for structural, G for grounding)",
      "pattern_layer": "structural or grounding",
      "pattern_name": "<short descriptive name>",
      "pattern_description": "<what this pattern checks>",
      "pattern_question": "For structural: 'Does the plan HAVE X?' For grounding: 'Is X CORRECT vs source?'",
      "pattern_template": "For structural: 'The plan includes/has/lists [ELEMENT]'. For grounding: 'The [ELEMENT] matches source.[FIELD]'",
      "source_reference": "For grounding only: source.ATTENDEES, source.MEETING.StartTime, etc.",
      "applies_to_dimensions": ["<dim1>", "<dim2>"],
      "level_recommendation": "<critical|expected|aspirational>",
      "evaluation_criteria": [
        "<criterion 1 for human judges>",
        "<criterion 2 for human judges>"
      ],
      "example_instances": [
        "<concrete example assertion following this pattern - NO HARDCODED VALUES for structural>"
      ],
      "anti_patterns": [
        "Mixing grounding values into structural assertions",
        "Hardcoding specific names, dates, or files",
        "<other anti-pattern>"
      ],
      "robustness_notes": "<how robust is this pattern across different contexts?>"
    }}
  ],
  "dimension_consolidation": {{
    "<suggested_merged_dimension>": ["<current_dim1>", "<current_dim2>"],
    ...
  }},
  "coverage_gaps": [
    "<quality aspect not covered by current assertions>"
  ],
  "redundancy_analysis": {{
    "highly_redundant_patterns": ["<pattern pairs that overlap significantly>"],
    "consolidation_suggestions": ["<how to merge redundant patterns>"]
  }},
  "human_judge_guidelines": {{
    "priority_order": ["<P1>", "<P2>", "..."],
    "minimum_coverage": ["<patterns that MUST be checked>"],
    "evaluation_workflow": "<suggested workflow for judges>"
  }}
}}

Return ONLY valid JSON."""


def build_comprehensive_analysis_prompt(stats: Dict, sample_assertions: List[Dict]) -> str:
    """Build prompt for comprehensive meta-analysis."""
    
    samples_text = ""
    for i, a in enumerate(sample_assertions[:20]):
        samples_text += f"{i+1}. [{a['level']}] [{a['dim']}] {a['text'][:120]}...\n"
    
    return f"""You are a senior evaluation framework architect reviewing assertions for workback plan quality evaluation.

**Dataset Statistics:**
- Total assertions: {stats['total']}
- By level: Critical={stats['critical']}, Expected={stats['expected']}, Aspirational={stats['aspirational']}
- Unique dimensions: {stats['unique_dims']}
- Top dimensions: {', '.join(f"{k}({v})" for k, v in stats['top_dims'][:10])}

**Sample Assertions:**
{samples_text}

Provide a comprehensive meta-analysis of this assertion set. Return JSON:
{{
  "overall_assessment": {{
    "quality_grade": "<A/B/C/D/F>",
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"],
    "balance_assessment": "<is the critical/expected/aspirational split appropriate?>",
    "coverage_assessment": "<are all important quality aspects covered?>"
  }},
  "level_analysis": {{
    "critical": {{
      "appropriateness": "<are the right things marked critical?>",
      "issues": ["<issue 1>"],
      "recommendations": ["<rec 1>"]
    }},
    "expected": {{
      "appropriateness": "<assessment>",
      "issues": ["<issue 1>"],
      "recommendations": ["<rec 1>"]
    }},
    "aspirational": {{
      "appropriateness": "<assessment>",
      "issues": ["<issue 1>"],
      "recommendations": ["<rec 1>"]
    }}
  }},
  "dimension_analysis": {{
    "well_defined_dimensions": ["<dim1>", "<dim2>"],
    "poorly_defined_dimensions": ["<dim1>", "<dim2>"],
    "missing_dimensions": ["<suggested new dimension 1>"],
    "over_represented_dimensions": ["<dim with too many assertions>"],
    "consolidation_map": {{
      "<new_dimension>": ["<old_dim1>", "<old_dim2>"]
    }}
  }},
  "actionable_recommendations": [
    {{
      "priority": 1,
      "category": "<category>",
      "recommendation": "<specific actionable recommendation>",
      "impact": "<expected impact>"
    }}
  ],
  "proposed_evaluation_rubric": {{
    "must_have_criteria": ["<criterion 1>", "<criterion 2>"],
    "should_have_criteria": ["<criterion 1>"],
    "nice_to_have_criteria": ["<criterion 1>"],
    "scoring_guidance": "<how to score responses>"
  }}
}}

Return ONLY valid JSON."""


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis Functions
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_assertions_batch(assertions: List[Dict], batch_size: int = 10) -> List[Dict]:
    """Analyze assertions in batches and critique each one."""
    all_critiques = []
    
    total_batches = (len(assertions) + batch_size - 1) // batch_size
    print(f"\n📊 Analyzing {len(assertions)} assertions in {total_batches} batches...")
    
    for batch_idx in range(0, len(assertions), batch_size):
        batch = assertions[batch_idx:batch_idx + batch_size]
        batch_num = batch_idx // batch_size + 1
        
        print(f"\n  Batch {batch_num}/{total_batches} ({len(batch)} assertions)...")
        
        prompt = build_critique_prompt(batch)
        
        try:
            response = call_gpt5_api(prompt, temperature=0.2, max_tokens=4000)
            
            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                critiques = result.get('critiques', [])
                
                # Attach original assertion data
                for critique in critiques:
                    idx = critique.get('assertion_index', 1) - 1
                    if 0 <= idx < len(batch):
                        critique['original_assertion'] = batch[idx]
                
                all_critiques.extend(critiques)
                print(f"    ✓ Got {len(critiques)} critiques")
            else:
                print(f"    ✗ Could not parse response")
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
        
        time.sleep(DELAY_BETWEEN_CALLS)
    
    return all_critiques


def cluster_into_patterns(assertions: List[Dict]) -> Dict:
    """Cluster assertions into generalizable patterns."""
    print("\n🔄 Clustering assertions into patterns...")
    
    # Get dimension counts
    dim_counts = Counter(a['dim'] for a in assertions)
    top_dims = [d for d, _ in dim_counts.most_common(20)]
    
    prompt = build_pattern_clustering_prompt(assertions, top_dims)
    
    try:
        response = call_gpt5_api(prompt, temperature=0.3, max_tokens=4000)
        
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            patterns = json.loads(json_match.group())
            print(f"  ✓ Identified {len(patterns.get('patterns', []))} patterns")
            return patterns
        else:
            print("  ✗ Could not parse patterns response")
            return {}
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {}


def run_comprehensive_analysis(assertions: List[Dict]) -> Dict:
    """Run comprehensive meta-analysis."""
    print("\n📈 Running comprehensive meta-analysis...")
    
    # Calculate stats
    level_counts = Counter(a['level'] for a in assertions)
    dim_counts = Counter(a['dim'] for a in assertions)
    
    stats = {
        'total': len(assertions),
        'critical': level_counts.get('critical', 0),
        'expected': level_counts.get('expected', 0),
        'aspirational': level_counts.get('aspirational', 0),
        'unique_dims': len(dim_counts),
        'top_dims': dim_counts.most_common(15)
    }
    
    # Sample diverse assertions
    samples = []
    for level in ['critical', 'expected', 'aspirational']:
        level_assertions = [a for a in assertions if a['level'] == level]
        samples.extend(level_assertions[:7])
    
    prompt = build_comprehensive_analysis_prompt(stats, samples)
    
    try:
        response = call_gpt5_api(prompt, temperature=0.3, max_tokens=4000)
        
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            analysis = json.loads(json_match.group())
            print("  ✓ Comprehensive analysis complete")
            return analysis
        else:
            print("  ✗ Could not parse analysis response")
            return {}
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# Reporting
# ═══════════════════════════════════════════════════════════════════════════════

def generate_report(critiques: List[Dict], patterns: Dict, analysis: Dict) -> str:
    """Generate a human-readable report."""
    
    report = []
    report.append("=" * 80)
    report.append("WORKBACK PLAN ASSERTIONS - QUALITY ANALYSIS REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    
    # Overall Assessment
    if analysis.get('overall_assessment'):
        oa = analysis['overall_assessment']
        report.append("\n## OVERALL ASSESSMENT")
        report.append(f"Quality Grade: {oa.get('quality_grade', 'N/A')}")
        report.append("\nStrengths:")
        for s in oa.get('strengths', []):
            report.append(f"  ✓ {s}")
        report.append("\nWeaknesses:")
        for w in oa.get('weaknesses', []):
            report.append(f"  ✗ {w}")
    
    # Pattern Summary
    if patterns.get('patterns'):
        report.append("\n" + "=" * 80)
        report.append("## IDENTIFIED PATTERNS")
        report.append(f"Total patterns: {len(patterns['patterns'])}")
        report.append("")
        
        for p in patterns['patterns']:
            report.append(f"\n### {p.get('pattern_id', '?')}: {p.get('pattern_name', 'Unknown')}")
            report.append(f"Level: {p.get('level_recommendation', 'N/A')}")
            report.append(f"Description: {p.get('pattern_description', 'N/A')}")
            report.append(f"Template: {p.get('pattern_template', 'N/A')}")
            report.append("Evaluation Criteria:")
            for c in p.get('evaluation_criteria', []):
                report.append(f"  • {c}")
    
    # Coverage Gaps
    if patterns.get('coverage_gaps'):
        report.append("\n" + "=" * 80)
        report.append("## COVERAGE GAPS")
        for gap in patterns['coverage_gaps']:
            report.append(f"  ⚠ {gap}")
    
    # Actionable Recommendations
    if analysis.get('actionable_recommendations'):
        report.append("\n" + "=" * 80)
        report.append("## ACTIONABLE RECOMMENDATIONS")
        for rec in analysis['actionable_recommendations']:
            report.append(f"\n[Priority {rec.get('priority', '?')}] {rec.get('category', 'General')}")
            report.append(f"  {rec.get('recommendation', 'N/A')}")
            report.append(f"  Impact: {rec.get('impact', 'N/A')}")
    
    # Human Judge Guidelines
    if patterns.get('human_judge_guidelines'):
        hj = patterns['human_judge_guidelines']
        report.append("\n" + "=" * 80)
        report.append("## HUMAN JUDGE GUIDELINES")
        report.append(f"\nPriority Order: {', '.join(hj.get('priority_order', []))}")
        report.append("\nMinimum Coverage (MUST check):")
        for m in hj.get('minimum_coverage', []):
            report.append(f"  ✓ {m}")
        report.append(f"\nEvaluation Workflow: {hj.get('evaluation_workflow', 'N/A')}")
    
    # Critique Summary
    if critiques:
        report.append("\n" + "=" * 80)
        report.append("## CRITIQUE SUMMARY")
        
        # Calculate stats
        scores = [c.get('quality_score', 0) for c in critiques if c.get('quality_score')]
        if scores:
            avg_score = sum(scores) / len(scores)
            report.append(f"Average Quality Score: {avg_score:.1f}/10")
        
        # Issue frequency
        issue_types = Counter()
        for c in critiques:
            for issue in c.get('issues', []):
                issue_types[issue.get('type', 'unknown')] += 1
        
        if issue_types:
            report.append("\nMost Common Issues:")
            for issue_type, count in issue_types.most_common(7):
                report.append(f"  {issue_type}: {count}")
        
        # Sample critiques with low scores
        low_score_critiques = [c for c in critiques if c.get('quality_score', 10) <= 5]
        if low_score_critiques:
            report.append("\n### Sample Low-Quality Assertions (needs improvement):")
            for c in low_score_critiques[:5]:
                orig = c.get('original_assertion', {})
                report.append(f"\n  Score: {c.get('quality_score')}/10")
                report.append(f"  Original: {orig.get('text', 'N/A')[:100]}...")
                report.append(f"  Issues: {', '.join(i.get('type', '?') for i in c.get('issues', []))}")
                if c.get('rewritten_assertion') and c['rewritten_assertion'] != 'N/A':
                    report.append(f"  Suggested: {c['rewritten_assertion'][:100]}...")
    
    return "\n".join(report)


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Analyze workback plan assertions using GPT-5")
    parser.add_argument("--all", action="store_true", help="Analyze all assertions (slower)")
    parser.add_argument("--samples-per-dim", type=int, default=3, 
                        help="Number of samples per dimension for critique analysis")
    parser.add_argument("--skip-critique", action="store_true", help="Skip individual critique analysis")
    parser.add_argument("--skip-patterns", action="store_true", help="Skip pattern clustering")
    parser.add_argument("--skip-meta", action="store_true", help="Skip meta-analysis")
    args = parser.parse_args()
    
    print("=" * 80)
    print("WORKBACK PLAN ASSERTIONS - GPT-5 QUALITY ANALYSIS")
    print("=" * 80)
    
    # Load data
    print(f"\n📂 Loading data from {INPUT_FILE}...")
    data = load_assertions_data()
    all_assertions = collect_all_assertions(data)
    
    print(f"   Total items: {len(data)}")
    print(f"   Total assertions: {len(all_assertions)}")
    
    # Sample assertions for analysis
    if args.all:
        sample_assertions = all_assertions
    else:
        # Sample by dimension to get diverse coverage
        by_dim = defaultdict(list)
        for a in all_assertions:
            by_dim[a['dim']].append(a)
        
        sample_assertions = []
        for dim, assertions in by_dim.items():
            sample_assertions.extend(assertions[:args.samples_per_dim])
        
        print(f"   Sampled: {len(sample_assertions)} assertions ({args.samples_per_dim}/dimension)")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'input_file': INPUT_FILE,
        'total_assertions': len(all_assertions),
        'sampled_assertions': len(sample_assertions),
        'critiques': [],
        'patterns': {},
        'comprehensive_analysis': {}
    }
    
    # Run analyses
    if not args.skip_critique:
        results['critiques'] = analyze_assertions_batch(sample_assertions, batch_size=8)
    
    if not args.skip_patterns:
        results['patterns'] = cluster_into_patterns(all_assertions)
    
    if not args.skip_meta:
        results['comprehensive_analysis'] = run_comprehensive_analysis(all_assertions)
    
    # Save full results
    print(f"\n💾 Saving results to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save patterns separately for easy access
    if results['patterns']:
        print(f"💾 Saving patterns to {PATTERNS_FILE}...")
        with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
            json.dump(results['patterns'], f, indent=2, ensure_ascii=False)
    
    # Generate and print report
    report = generate_report(
        results['critiques'],
        results['patterns'],
        results['comprehensive_analysis']
    )
    
    print("\n" + report)
    
    # Save report
    report_file = OUTPUT_FILE.replace('.json', '_report.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n📄 Report saved to {report_file}")
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
