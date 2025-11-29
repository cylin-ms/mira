# Assertion Framework Migration Report

**Author:** Chin-Yew Lin  
**Date:** November 28, 2025  
**Updated:** November 29, 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Conversion Statistics](#1-conversion-statistics)
3. [Original Kening Assertions Analysis](#2-original-kening-assertions-analysis)
4. [Converted Assertions (Chin-Yew's WBP Framework)](#3-converted-assertions-chin-yews-wbp-framework)
5. [Phase 1 vs Phase 2 Distribution](#4-phase-1-vs-phase-2-distribution)
6. [Quality Assessment](#5-quality-assessment)
7. [Insights & Analysis](#6-insights--analysis)
8. [Grounding Layer Design Rationale](#7-grounding-layer-design-rationale) ← **NEW**
9. [Recommendations](#8-recommendations)
10. [Data Files Reference](#9-data-files-reference)
11. [Scripts Reference](#10-scripts-reference)
12. [Conclusion](#11-conclusion)

---

## Executive Summary

This report analyzes the conversion of **2,318 assertions** from Kening's original format across **224 meetings** to Chin-Yew's WBP (Workback Plan) Evaluation Framework.

### Key Results

| Metric | Value |
|--------|-------|
| GPT-5 Conversion Rate | **99.6%** |
| Phase 1 Alignment | **99.3%** (2,302 of 2,318 assertions) |
| Phase 2 Assertions | 0.7% (16 assertions, all S5: Task Dates) |
| Active Dimensions | 11 of 14 Phase 1 dimensions used |

The conversion demonstrates **excellent alignment** with Chin-Yew's Phase 1 evaluation framework. Almost all assertions (99.3%) map directly to Phase 1 dimensions, with only 16 assertions (0.7%) mapping to S5 (Task Dates), a Phase 2 dimension that overlaps with S2 (Timeline Alignment).

---

## 1. Conversion Statistics

| Metric | Value |
|--------|-------|
| Total Meetings | 224 |
| Total Assertions | 2,318 |
| GPT-5 Conversions | 2,308 (99.6%) |
| Heuristic Fallbacks | 10 (0.4%) |
| Processing Time | ~73 minutes |
| Avg. Time per Meeting | 19.6 seconds |
| Avg. Time per Assertion | 1.89 seconds |

---

## 2. Original Kening Assertions Analysis

### Problem: Dimension Fragmentation

Kening's original assertions used **232 unique dimension names**, leading to:
- Inconsistent naming conventions (e.g., "Dependencies & sequencing" vs "Dependencies & Sequencing")
- Overlapping concepts (e.g., "Ownership clarity" vs "Ownership Clarity" vs "Ownership")
- Lack of standardized evaluation framework

**Top 15 Original Kening Dimensions:**

| Dimension | Count | % |
|-----------|-------|---|
| Timeline & Buffers | 337 | 14.5% |
| Meeting Objective & Scope | 279 | 12.0% |
| Artifact readiness | 263 | 11.3% |
| Ownership clarity | 241 | 10.4% |
| Dependencies & sequencing | 142 | 6.1% |
| Dependencies & Sequencing | 120 | 5.2% |
| Artifact Readiness | 108 | 4.7% |
| Timeline | 87 | 3.8% |
| Disclosure of missing info | 70 | 3.0% |
| Ownership Clarity | 56 | 2.4% |
| Ownership | 55 | 2.4% |
| Dependencies | 44 | 1.9% |
| Disclosure of assumptions | 29 | 1.3% |
| Grounding & traceability | 26 | 1.1% |
| Stakeholder Alignment | 26 | 1.1% |

### Original Level Distribution
| Level | Count | % |
|-------|-------|---|
| critical | 1,288 | 55.6% |
| expected | 843 | 36.4% |
| aspirational | 187 | 8.1% |

---

## 3. Converted Assertions (Chin-Yew's WBP Framework)

### Consolidated to 12 Dimensions

The conversion consolidated 232 dimensions into Chin-Yew's 14 selected dimensions, with 12 dimensions actively used:

| Dimension | Name | Count | % | Phase |
|-----------|------|-------|---|-------|
| S2 | Timeline Alignment | 449 | 19.4% | Phase 1 |
| S3 | Ownership Assignment | 414 | 17.9% | Phase 1 |
| S4 | Deliverables & Artifacts | 399 | 17.2% | Phase 1 |
| S6 | Dependencies & Blockers | 322 | 13.9% | Phase 1 |
| S1 | Meeting Details | 321 | 13.8% | Phase 1 |
| S19 | Caveat & Clarification | 279 | 12.0% | Phase 1 |
| G5 | Hallucination Check | 60 | 2.6% | Phase 1 |
| S11 | Risk Mitigation Strategy | 42 | 1.8% | Phase 1 |
| S5 | Task Dates | 16 | 0.7% | Phase 2 |
| S18 | Post-Event Actions | 10 | 0.4% | Phase 1 |
| G1 | Attendee Grounding | 3 | 0.1% | Phase 1 |
| G4 | Topic Grounding | 3 | 0.1% | Phase 1 |

### Layer Distribution
| Layer | Count | % |
|-------|-------|---|
| Structural | 2,252 | 97.2% |
| Grounding | 66 | 2.8% |

### Weight Distribution (Preserved from Original Levels)
| Weight | Level | Count | % |
|--------|-------|-------|---|
| 3 (High) | critical | 1,288 | 55.6% |
| 2 (Medium) | expected | 842 | 36.3% |
| 1 (Low) | aspirational | 188 | 8.1% |

### Phase 1 vs Phase 2 Distribution

Based on the 14 Phase 1 dimensions (9 structural + 5 grounding):

| Phase | Assertions | Percentage |
|-------|------------|------------|
| **Phase 1** | 2,302 | **99.3%** |
| Phase 2 | 16 | 0.7% |

**Key Finding:** Almost all assertions (99.3%) map to Phase 1 dimensions, demonstrating excellent alignment with the core evaluation framework.

### Phase 1 Dimension Breakdown

| Dimension | Name | Count | % of Total |
|-----------|------|-------|------------|
| S2 | Timeline Alignment | 449 | 19.4% |
| S3 | Ownership Assignment | 414 | 17.9% |
| S4 | Deliverables & Artifacts | 399 | 17.2% |
| S6 | Dependencies & Blockers | 322 | 13.9% |
| S1 | Meeting Details | 321 | 13.8% |
| S19 | Caveat & Clarification | 279 | 12.0% |
| G5 | Hallucination Check | 60 | 2.6% |
| S11 | Risk Mitigation Strategy | 42 | 1.8% |
| S18 | Post-Event Actions | 10 | 0.4% |
| G1 | Attendee Grounding | 3 | 0.1% |
| G4 | Topic Grounding | 3 | 0.1% |
| **Phase 1 Total** | | **2,302** | **99.3%** |

### Phase 2 Dimension Breakdown

Only **16 assertions (0.7%)** mapped to Phase 2 dimensions:

| Dimension | Name | Count | Notes |
|-----------|------|-------|-------|
| S5 | Task Dates | 16 | Overlaps with S2 (Timeline Alignment) |

**Observation:** S5 (Task Dates) is the only Phase 2 dimension used. These assertions focus specifically on due dates, which conceptually overlaps with S2 (Timeline Alignment). For practical evaluation, S5 assertions could be consolidated into S2.

---

## 4. Quality Assessment

### Strengths of Kening's Original Assertions

1. **Good Coverage of Core Concepts**
   - Timeline-related assertions (14.5%) show focus on scheduling
   - Ownership clarity (10.4%) ensures accountability
   - Artifact readiness (11.3%) covers deliverables

2. **Reasonable Level Classification**
   - 55.6% critical assertions show appropriate prioritization
   - Clear distinction between critical/expected/aspirational

3. **Detailed Content**
   - Original assertions contained specific names, dates, times
   - Referenced actual meeting artifacts and attendees

### Weaknesses of Kening's Original Assertions

1. **Dimension Fragmentation (232 unique dimensions)**
   - Inconsistent capitalization: "Dependencies & sequencing" vs "Dependencies & Sequencing"
   - Duplicate concepts: "Ownership clarity", "Ownership Clarity", "Ownership"
   - Makes automated evaluation unreliable

2. **Hardcoded Values**
   - Specific dates: "July 26, 2025 at 14:00 PST"
   - Specific names: "Tisa Odonoghue", "Nila Tanguma"
   - Makes assertions non-reusable and evaluation brittle

3. **Missing Grounding Layer**
   - Only ~3% of assertions check for hallucination/grounding
   - No systematic verification against source material

4. **No Standardized Templates**
   - Each assertion is uniquely phrased
   - Inconsistent structure makes comparison difficult

---

## 5. How Chin-Yew's WBP Framework Improves Evaluation

### 5.1 Standardized Dimensions (14 → 7 active)

| Problem | Solution |
|---------|----------|
| 232 fragmented dimensions | 14 well-defined dimensions with clear scope |
| Inconsistent naming | Standardized codes (S1, S2, S3...) |
| Overlapping concepts | Clear boundaries between dimensions |

**Example Consolidation:**
- "Timeline & Buffers", "Timeline", "Scheduling" → **S2: Timeline Alignment**
- "Ownership clarity", "Ownership Clarity", "Ownership" → **S3: Ownership Assignment**
- "Dependencies & sequencing", "Dependencies" → **S6: Dependencies & Blockers**

### 5.2 Template-Based Assertions

The conversion uses Chin-Yew's templates, making assertions:

| Original (Kening) | Converted (WBP) |
|-------------------|-----------------|
| "The response should confirm the meeting is scheduled for July 26, 2025 at 14:00 PST" | "The response should include a backward timeline from T₀ with dependency-aware sequencing" |
| "Tisa Odonoghue should be assigned as the owner for reviewing the config changes" | "The response should assign an owner for each [TASK] or specify role/skill placeholder if name unavailable" |

**Benefits:**
- ✅ Reusable across different meetings
- ✅ Consistent evaluation criteria
- ✅ Clear pass/fail criteria

### 5.3 Two-Layer Architecture

| Layer | Focus | Count |
|-------|-------|-------|
| **Structural** | Format, completeness, organization | 2,252 (97.2%) |
| **Grounding** | Factual accuracy, no hallucination | 66 (2.8%) |

The grounding layer (G5: Hallucination Check) is critical for:
- Ensuring no fabricated entities
- Verifying claims against source material
- Preventing AI hallucinations

### 5.4 Weighted Scoring System

| Weight | Meaning | Use |
|--------|---------|-----|
| 3 | Critical requirement | Must-have for valid WBP |
| 2 | Expected quality | Good practice |
| 1 | Aspirational | Nice-to-have |

---

## 6. Sample Conversions

### S1: Meeting Details
**Original:** "The response should confirm the meeting is scheduled for July 26, 2025 at 14:00 PST"

**Converted:** "The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES] accurately"

**Improvement:** Generic template works for any meeting, not just this specific date.

### S2: Timeline Alignment
**Original:** "The response should include a timeline showing all pre-read materials shared by July 26, 00:15 PST"

**Converted:** "The response should include a backward timeline from T₀ with dependency-aware sequencing"

**Improvement:** Focus on methodology (backward planning) rather than specific dates.

### S3: Ownership Assignment
**Original:** "Tisa Odonoghue should be assigned as the owner for all action items"

**Converted:** "The response should assign an owner for each [TASK] or specify role/skill placeholder if name unavailable"

**Improvement:** Works even when specific names aren't known; handles role-based assignment.

### G5: Hallucination Check
**Original:** "The response should not introduce attendees beyond Tisa Odonoghue and Nila Tanguma"

**Converted:** "No entities introduced that don't exist in source"

**Improvement:** Generic hallucination check applicable to any entity type.

---

## 7. Grounding Layer Design Rationale

### 7.1 Updated Grounding Dimensions (G1-G8)

The Grounding layer has been reorganized for clarity and extensibility:

| Code | Name | Entity Type | Description |
|------|------|-------------|-------------|
| **G1** | **Hallucination Check** | **All** | Overall recall check - catches any fabricated entity |
| G2 | Attendee Grounding | People | Names/people exist in source |
| G3 | Date/Time Grounding | Temporal | Dates/times match source |
| G4 | Artifact Grounding | Files | Documents/files exist in source |
| G5 | Topic Grounding | Nouns | Topics/subjects align with source |
| G6 | Task Grounding | Verbs | Tasks/action items exist in source |
| G7 | Role Grounding | Roles | Role/responsibility assignments accurate |
| G8 | Constraint Grounding | Limits | Constraints/limits derivable from source |

### 7.2 Why G1 (Hallucination Check) is First

**Design Decision:** G1 is placed first as the **overall grounding recall check**.

**Relationship:** `G1 = G2 ∧ G3 ∧ G4 ∧ G5 ∧ G6 ∧ G7 ∧ G8 ∧ (uncategorized entities)`

If all specific checks (G2-G8) pass → G1 should pass.
If any specific check fails → G1 fails.

### 7.3 Why G1 is Valuable Beyond Being a "Catch-All"

G1 serves important purposes beyond just aggregating G2-G6:

#### Example 1: Uncategorized Entity Types

**Scenario:** LLM response mentions a project code not covered by G2-G6.

- **Source:** Email says "Project Alpha has $50K budget"
- **LLM Output:** "Project Beta requires $75K budget" ← Hallucination!

Neither G2-G6 covers "project names" or "budget figures" specifically.
**G1 catches this** because "Project Beta" and "$75K" don't exist in source.

#### Example 2: Fabricated Relationships

**Scenario:** LLM invents a relationship between real entities.

- **Source:** "Alice owns Task A. Bob owns Task B."
- **LLM Output:** "Alice should coordinate with Bob on Task A" ← Fabricated coordination!

G2 passes (Alice & Bob exist), G6 passes (Task A exists).
**G1 catches this** because the "coordination relationship" doesn't exist in source.

#### Example 3: Invented Meeting Outcomes

**Scenario:** LLM creates conclusions not in the source.

- **Source:** Meeting transcript discusses options, no decision made
- **LLM Output:** "The team decided to proceed with Option B" ← Hallucination!

No specific G2-G6 covers "decisions" or "outcomes".
**G1 catches this** because the decision entity doesn't exist in source.

#### Example 4: Hallucinated Context/Assumptions

**Scenario:** LLM adds context not present in source.

- **Source:** "Review the config changes before deployment"
- **LLM Output:** "Due to the production outage last week, review config changes urgently"

The "production outage" is fabricated context.
**G1 catches this** as an entity/fact not in source.

### 7.4 Extensibility

By placing G1 first, future grounding dimensions can be added without burying the overall recall check:

```
G1  - Overall Hallucination Check (always first)
G2  - Attendee Grounding
G3  - Date/Time Grounding
G4  - Artifact Grounding
G5  - Topic Grounding
G6  - Task Grounding
G7  - Role Grounding (NEW - roles/responsibilities)
G8  - Constraint Grounding (NEW - limits/constraints)
G9  - (Future: Quantitative Grounding - budgets, counts, percentages)
G10 - (Future: Location Grounding - places, rooms, addresses)
...
```

### 7.5 How G7 and G8 Were Discovered (Data-Driven Analysis)

G7 (Role Grounding) and G8 (Constraint Grounding) were identified through a **two-phase analysis** of 3,700 assertions from Kening's data.

#### Data Sources Analyzed

| Source | Assertions | Description |
|--------|------------|-------------|
| `11_25_output_with_matches.jsonl` | 1,382 | 102 meeting instances |
| `Assertions_genv2_for_LOD1126part1.jsonl` | 2,318 | 224 meeting instances |
| **Total** | **3,700** | Combined corpus |

#### Phase 1: Keyword Pattern Analysis (Regex)

First, a regex-based analysis (`analyze_grounding_gaps.py`) scanned assertion text for entity patterns:

```python
GROUNDING_PATTERNS = {
    # Current G2-G6 coverage
    'attendee/people': r'attendee|participant|name|person|owner',
    'date/time': r'date|time|deadline|schedule|timeline',
    'file/artifact': r'file|document|deck|slide|attachment',
    'topic/subject': r'topic|subject|agenda|scope|objective',
    'task/action': r'task|action|step|deliverable|milestone',
    # Potential gaps (NOT in G2-G6)
    'role/responsibility': r'role|responsible|accountable|raci|approver',
    'constraint/limit': r'constraint|limit|restriction|requirement|must not',
    ...
}
```

**Regex Results (patterns NOT in G2-G6):**

| Pattern | Count | Potential New G |
|---------|-------|-----------------|
| status/progress | 96 | Low signal |
| role/responsibility | 74 | **G7 candidate** |
| decision/outcome | 62 | Low signal |
| constraint/limit | 40 | **G8 candidate** |

#### Phase 2: GPT-5 Semantic Classification

Simple regex over-counts due to incidental keyword matches. To get accurate classification, GPT-5 JJ analyzed a 300-assertion sample to identify **what each assertion is actually verifying**.

**GPT-5 Classification Prompt:**
```
For each assertion, identify what type of grounding entity it is verifying.
- If it fits G2-G6, label it with that dimension
- If it verifies something NOT in G2-G6, propose a new category name

Categories: [G2_Attendee, G3_DateTime, G4_Artifact, G5_Topic, G6_Task,
            NEW_Status, NEW_Decision, NEW_Constraint, NEW_Priority,
            NEW_Role, NEW_Location, NEW_Quantity, NEW_Communication, OTHER]
```

**GPT-5 Results (300 sample):**

| Dimension | Count | % | Confidence |
|-----------|-------|---|------------|
| G6_Task | 65 | 22% | High: 62 |
| G3_DateTime | 61 | 20% | High: 57 |
| G5_Topic | 41 | 14% | High: 34 |
| **NEW_Role** | **37** | **12%** | **High: 33** |
| G4_Artifact | 34 | 11% | High: 32 |
| G2_Attendee | 27 | 9% | High: 25 |
| **NEW_Constraint** | **18** | **6%** | **Medium: 11** |
| Other | 17 | 6% | - |

#### Key Findings

1. **G7 (Role Grounding)** - 37 occurrences (12% of sample)
   - Example: *"The response should assign Markita Sitra and Rufina Ganie as owners for 'Gather current cache settings'..."*
   - GPT-5 reasoning: "Assigns owners for a task, which relates to role/responsibility."

2. **G8 (Constraint Grounding)** - 18 occurrences (6% of sample)
   - Example: *"The response should disclose assumptions around weekend availability or owner confirmation due to the compressed timeline..."*
   - GPT-5 reasoning: "Mentions assumptions around availability due to a compressed timeline, which is a constraint."

3. **Why Other Candidates Were Rejected:**
   - `NEW_Status` (1 occurrence) - Too rare in sample
   - `NEW_Decision` (1 occurrence) - Overlaps with G5 (Topic)
   - `NEW_Communication` (5 occurrences) - Overlaps with G4 (Artifact)

#### Comparison: Regex vs GPT-5

| Pattern | Regex Count | GPT-5 Count | Insight |
|---------|-------------|-------------|---------|
| role/responsibility | 74 | 37 | Regex over-counted by 2x |
| constraint/limit | 40 | 18 | Regex over-counted by 2.2x |
| status/progress | 96 | 1 | Regex massively over-counted |
| decision/outcome | 62 | 1 | Regex massively over-counted |

**Conclusion:** GPT-5 semantic classification filtered out false positives where keywords appeared incidentally rather than as the assertion's focus.

#### Analysis Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| `analyze_grounding_gaps.py` | Regex keyword analysis | Console output |
| `analyze_grounding_gaps_gpt5.py` | GPT-5 semantic classification | `docs/grounding_gap_analysis_gpt5.json` |

---

## 8. Recommendations

### 8.1 For Evaluation Pipeline

1. **Use Phase 1 Framework** - With 99.3% of assertions already mapping to Phase 1 dimensions, the 14-dimension framework is well-suited for immediate evaluation.

2. **Consider Consolidating S5 into S2** - The 16 S5 (Task Dates) assertions overlap conceptually with S2 (Timeline Alignment). Consider merging for simpler evaluation.

3. **Add More Grounding Assertions** - Currently only 2.8% are grounding-layer (66 assertions). Consider generating more G1-G8 assertions for comprehensive source verification, especially G7 (Role) and G8 (Constraint).

### 8.2 For Future Assertion Generation

1. **Use Chin-Yew's Templates** - Generate assertions using the standardized templates from the start.

2. **Avoid Hardcoded Values** - Use placeholders like [TASK], [DELIVERABLE], [DATE/TIME].

3. **Balance Structural and Grounding** - Current ratio is 97:3. Aim for 80:20 for better hallucination detection.

4. **Leverage Unused Phase 1 Dimensions** - G2 (Date/Time Grounding) and G3 (Artifact Grounding) are not currently used. Consider adding assertions for these.

---

## 9. Data Files Reference

The conversion process produces three key JSONL files that document the migration pipeline:

### 8.1 Source: [`Assertions_genv2_for_LOD1126part1.jsonl`](https://github.com/cylin-ms/mira/blob/master/docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl)

**Kening's original assertions** - the source data for this conversion.

| Property | Value |
|----------|-------|
| Meetings | 224 |
| Total Assertions | 2,318 |
| Unique Dimensions | 232 (fragmented) |
| **Schema Compatibility** | ✅ **Kening's original format** |

**Schema:**
```json
{
  "utterance": "meeting transcript text",
  "assertions": [
    {
      "text": "The plan must include explicit owner assignment for...",
      "level": "critical|expected|aspirational",
      "anchors": {
        "Dim": "Timeline & Meeting Details",
        "sourceID": "entity-guid"
      }
    }
  ]
}
```

### 8.2 Intermediate: [`assertions_kening_enhanced.jsonl`](https://github.com/cylin-ms/mira/blob/master/docs/ChinYew/assertions_kening_enhanced.jsonl)

**Enhanced assertions** with WBP dimension mapping metadata added to each assertion.

| Property | Value |
|----------|-------|
| Meetings | 224 |
| Total Assertions | 2,318 |
| Added Field | `_mira_metadata` |
| **Schema Compatibility** | ✅ **Backward compatible with Kening** (preserves `text`, `level`, `anchors`) |

**Schema (additional fields):**
```json
{
  "assertions": [
    {
      "text": "...",
      "level": "...",
      "anchors": { ... },
      "_mira_metadata": {
        "dimension_id": "S2",
        "dimension_name": "Timeline Alignment",
        "layer": "structural",
        "weight": 3,
        "sourceID": "entity-guid",
        "mapping_rationale": "This assertion evaluates timeline consistency..."
      }
    }
  ]
}
```

### 8.3 Output: [`assertions_converted_full.jsonl`](https://github.com/cylin-ms/mira/blob/master/docs/ChinYew/assertions_converted_full.jsonl)

**Final converted assertions** in Chin-Yew's WBP format, ready for evaluation.

| Property | Value |
|----------|-------|
| Meetings | 224 |
| Total Assertions | 2,318 |
| Phase 1 Coverage | 99.3% (2,302 assertions) |
| Phase 2 Coverage | 0.7% (16 assertions) |
| **Schema Compatibility** | ⚠️ **New WBP format** (not backward compatible with Kening) |

**Schema:**
```json
{
  "user": {
    "id": "lod_username",
    "displayName": "Full Name",
    "mailNickName": "lod_username",
    "url": "https://ms.portal.azure.com/..."
  },
  "utterance": "meeting transcript text",
  "response": "Here's your workback plan...",
  "assertions": [
    {
      "text": "The plan must include explicit [person_name] assignment...",
      "level": "critical",
      "dimension": "S3",
      "dimension_name": "Ownership Assignment",
      "layer": "structural",
      "weight": 3,
      "sourceID": "entity-guid",
      "original_text": "The plan must include explicit owner assignment for...",
      "rationale": "Maps to S3 because it evaluates task ownership clarity",
      "quality_assessment": { ... },
      "conversion_method": "gpt5"
    }
  ]
}
```

### File Relationships

```
Assertions_genv2_for_LOD1126part1.jsonl (Source)
        │
        ▼ [GPT-5 dimension mapping]
assertions_kening_enhanced.jsonl (Intermediate)
        │
        ▼ [GPT-5 format conversion]
assertions_converted_full.jsonl (Output)
```

### Schema Compatibility Summary

| File | Kening Compatible | Changes |
|------|-------------------|---------|
| `Assertions_genv2_for_LOD1126part1.jsonl` | ✅ **Yes** | Original Kening format |
| `assertions_kening_enhanced.jsonl` | ✅ **Yes** | Adds `_mira_metadata` (preserves `text`, `level`, `anchors`) |
| `assertions_converted_full.jsonl` | ⚠️ **No** | New WBP schema (removes `anchors`, adds WBP fields) |

**Key Schema Differences in Output:**
- **Preserved:** `utterance`, `response`, `text`, `level`, `sourceID` (extracted from `anchors.sourceID`)
- **Added from Weiwei:** `user` object with `id`, `displayName`, `mailNickName`, `url` (from Weiwei's entity file)
- **Removed:** `anchors.Dim` (replaced by structured `dimension` fields)
- **Added:** `dimension`, `dimension_name`, `layer`, `weight`, `original_text`, `rationale`, `quality_assessment`, `conversion_method`

---

## 10. Scripts Reference

The conversion pipeline uses the following Python scripts:

### 9.1 Primary Conversion Script

| Script | Description | GitHub |
|--------|-------------|--------|
| [`convert_kening_assertions.py`](https://github.com/cylin-ms/mira/blob/master/convert_kening_assertions.py) | Main conversion script. Maps Kening's 232 dimensions to WBP format using GPT-5 JJ. Produces enhanced and converted JSONL files. | [View](https://github.com/cylin-ms/mira/blob/master/convert_kening_assertions.py) |

**Usage:**
```bash
python convert_kening_assertions.py
```

### 9.2 Analysis & Evaluation Scripts

| Script | Description | GitHub |
|--------|-------------|--------|
| [`analyze_assertions_gpt5.py`](https://github.com/cylin-ms/mira/blob/master/analyze_assertions_gpt5.py) | GPT-5 assertion quality analysis & pattern clustering | [View](https://github.com/cylin-ms/mira/blob/master/analyze_assertions_gpt5.py) |
| [`evaluate_kening_assertions.py`](https://github.com/cylin-ms/mira/blob/master/evaluate_kening_assertions.py) | Evaluates assertions against selected WBP dimensions | [View](https://github.com/cylin-ms/mira/blob/master/evaluate_kening_assertions.py) |
| [`evaluate_kening_gpt5.py`](https://github.com/cylin-ms/mira/blob/master/evaluate_kening_gpt5.py) | Evaluates assertions against Chin-Yew's rubric | [View](https://github.com/cylin-ms/mira/blob/master/evaluate_kening_gpt5.py) |
| [`evaluate_assertions_gpt5.py`](https://github.com/cylin-ms/mira/blob/master/evaluate_assertions_gpt5.py) | GPT-5 assertion evaluation with span highlighting | [View](https://github.com/cylin-ms/mira/blob/master/evaluate_assertions_gpt5.py) |
| [`score_assertions.py`](https://github.com/cylin-ms/mira/blob/master/score_assertions.py) | Score assertions against responses using GPT-5 JJ | [View](https://github.com/cylin-ms/mira/blob/master/score_assertions.py) |

### 9.3 Visualization Scripts

| Script | Description | GitHub |
|--------|-------------|--------|
| [`mira.py`](https://github.com/cylin-ms/mira/blob/master/mira.py) | Main Streamlit visualization UI | [View](https://github.com/cylin-ms/mira/blob/master/mira.py) |
| [`view_assertions.py`](https://github.com/cylin-ms/mira/blob/master/view_assertions.py) | Fluent Design assertions viewer | [View](https://github.com/cylin-ms/mira/blob/master/view_assertions.py) |
| [`view_analysis.py`](https://github.com/cylin-ms/mira/blob/master/view_analysis.py) | Visualize GPT-5 analysis results | [View](https://github.com/cylin-ms/mira/blob/master/view_analysis.py) |
| [`show_assertion_html.py`](https://github.com/cylin-ms/mira/blob/master/show_assertion_html.py) | Generate HTML showing assertions matched to segments | [View](https://github.com/cylin-ms/mira/blob/master/show_assertion_html.py) |
| [`show_assertion_details.py`](https://github.com/cylin-ms/mira/blob/master/show_assertion_details.py) | Generate detailed HTML for assertion matches | [View](https://github.com/cylin-ms/mira/blob/master/show_assertion_details.py) |

### 9.4 Utility Scripts

| Script | Description | GitHub |
|--------|-------------|--------|
| [`compute_assertion_matches.py`](https://github.com/cylin-ms/mira/blob/master/compute_assertion_matches.py) | Offline script to compute assertion matches using LLM | [View](https://github.com/cylin-ms/mira/blob/master/compute_assertion_matches.py) |
| [`check_sourceid_recovery.py`](https://github.com/cylin-ms/mira/blob/master/check_sourceid_recovery.py) | Verify SourceID recovery against entity IDs | [View](https://github.com/cylin-ms/mira/blob/master/check_sourceid_recovery.py) |
| [`generate_plan_examples_gpt5.py`](https://github.com/cylin-ms/mira/blob/master/generate_plan_examples_gpt5.py) | Generate plan quality examples using GPT-5 JJ | [View](https://github.com/cylin-ms/mira/blob/master/generate_plan_examples_gpt5.py) |
| [`generate_plan_examples.py`](https://github.com/cylin-ms/mira/blob/master/generate_plan_examples.py) | Generate example workback plans at three quality levels | [View](https://github.com/cylin-ms/mira/blob/master/generate_plan_examples.py) |

---

## 11. Conclusion

The conversion from Kening's 232-dimension assertions to Chin-Yew's WBP framework represents a significant improvement:

| Aspect | Before | After |
|--------|--------|-------|
| Dimensions | 232 (fragmented) | 11 active (consolidated) |
| Phase 1 Coverage | N/A | **99.3%** |
| Consistency | Variable | Template-based |
| Reusability | Low (hardcoded values) | High (placeholders) |
| Evaluation | Difficult | Standardized |

### Key Findings

1. **Excellent Phase 1 Alignment** - 99.3% of assertions (2,302 of 2,318) map to Phase 1 dimensions
2. **Minimal Phase 2 Usage** - Only 16 assertions (0.7%) use S5 (Task Dates)
3. **11 of 14 Phase 1 Dimensions Active** - Good coverage of the core framework
4. **GPT-5 Conversion Success** - 99.6% converted via GPT-5 (only 10 heuristic fallbacks)

### Active Dimension Summary

| Category | Dimensions Used | Coverage |
|----------|-----------------|----------|
| Structural (Phase 1) | S1, S2, S3, S4, S6, S11, S18, S19 | 8 of 8 |
| Grounding (Phase 1) | G1, G4, G5 | 3 of 5 |
| Structural (Phase 2) | S5 | 1 of 10 |

The conversion has effectively:

1. ✅ Consolidated 232 fragmented dimensions into 11 active dimensions
2. ✅ Achieved 99.3% Phase 1 alignment
3. ✅ Removed hardcoded values with template placeholders
4. ✅ Preserved severity weighting (critical/expected/aspirational → 3/2/1)
5. ✅ Enabled standardized, consistent evaluation

---

*Report generated: November 28, 2025*  
*Updated: November 29, 2025*  
*Analysis: 224 meetings, 2,318 assertions*  
*Conversion tool: convert_kening_assertions.py with Substrate GPT-5 JJ*
