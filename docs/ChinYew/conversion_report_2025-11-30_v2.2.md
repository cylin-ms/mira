# Kening Assertions Conversion Report

**Report ID**: `conversion_report_2025-11-30_v2.2`  
**Author**: Chin-Yew Lin  
**Date**: November 30, 2025  
**Framework Version**: assertion_analyzer v2.2 (before G10)

---

## Executive Summary

Converted 2,307 free-form assertions from Kening's dataset into 5,238 atomic S+G units using the assertion_analyzer framework. This represents a 2.27x expansion ratio, indicating that most free-form assertions contain multiple testable requirements.

---

## Input/Output

| Metric | Value |
|--------|-------|
| **Input File** | `docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl` |
| **Output File** | `docs/ChinYew/assertions_sg_classified.jsonl` |
| **Report File** | `docs/ChinYew/sg_classification_report.json` |
| **Stage Files** | `docs/ChinYew/sg_stages/stage_001.jsonl` through `stage_006.jsonl` |

---

## Conversion Statistics

### Overall Metrics

| Metric | Count |
|--------|-------|
| Meetings Processed | 224 |
| Input Assertions | 2,307 |
| Output S+G Units | 5,238 |
| S (Structural) Count | 5,001 |
| G (Grounding) Slots | 7,313 |
| Unknown/Unclassified | 237 |
| **Expansion Ratio** | 2.27x |
| **Success Rate** | 89.7% |

### Processing Configuration

| Parameter | Value |
|-----------|-------|
| Stage Size | 50 assertions per stage |
| Number of Stages | 6 |
| Token Refresh | Between each stage |
| Timestamp | 2025-11-30T08:43:46 |

---

## Distribution by S Dimension

| Rank | Dimension | Name | Count | % | Status |
|------|-----------|------|-------|---|--------|
| 1 | S8 | Parallel Workstreams | 1,302 | 26.0% | ASPIRATIONAL |
| 2 | S5 | Task Dates | 1,153 | 23.0% | REQUIRED |
| 3 | S3 | Ownership Assignment | 517 | 10.3% | REQUIRED |
| 4 | S16 | Assumptions & Prerequisites | 465 | 9.3% | ASPIRATIONAL |
| 5 | S17 | Cross-team Coordination | 336 | 6.7% | CONDITIONAL |
| 6 | S19 | Open Questions | 262 | 5.2% | ASPIRATIONAL |
| 7 | S2 | Timeline Alignment | 205 | 4.1% | REQUIRED |
| 8 | S4 | Deliverables & Artifacts | 201 | 4.0% | REQUIRED |
| 9 | S1 | Meeting Details | 184 | 3.7% | REQUIRED |
| 10 | S10 | Resource-Aware Planning | 165 | 3.3% | CONDITIONAL |
| 11 | S6 | Dependencies & Blockers | 105 | 2.1% | REQUIRED+ASPIRATIONAL |
| 12 | S9 | Checkpoints | 58 | 1.2% | ASPIRATIONAL |
| 13 | S18 | Post-Event Actions | 41 | 0.8% | ASPIRATIONAL |
| 14 | S20 | Clarity & First Impression | 7 | 0.1% | REQUIRED |

### S Dimension Distribution Chart

```
S8  ████████████████████████████████████████████████████ 1302 (26.0%)
S5  ██████████████████████████████████████████████ 1153 (23.0%)
S3  ████████████████████ 517 (10.3%)
S16 ██████████████████ 465 (9.3%)
S17 █████████████ 336 (6.7%)
S19 ██████████ 262 (5.2%)
S2  ████████ 205 (4.1%)
S4  ████████ 201 (4.0%)
S1  ███████ 184 (3.7%)
S10 ██████ 165 (3.3%)
S6  ████ 105 (2.1%)
S9  ██ 58 (1.2%)
S18 █ 41 (0.8%)
S20 ▏ 7 (0.1%)
```

---

## Distribution by G Dimension

| Rank | Dimension | Name | Count | % | Category |
|------|-----------|------|-------|---|----------|
| 1 | G6 | Action Item Grounding | 2,608 | 35.7% | Entity |
| 2 | G3 | Date/Time Grounding | 1,373 | 18.8% | Entity |
| 3 | G2 | Attendee Grounding | 812 | 11.1% | Entity |
| 4 | G5 | Topic Grounding | 799 | 10.9% | Entity |
| 5 | G4 | Artifact Grounding | 596 | 8.2% | Entity |
| 6 | G8 | Instruction Adherence | 579 | 7.9% | Semantic |
| 7 | G9 | Planner-Generated Consistency | 442 | 6.0% | Semantic |
| 8 | G7 | Context Preservation | 102 | 1.4% | Semantic |
| 9 | G1 | Hallucination Check | 2 | 0.03% | Entity |

### G Dimension Distribution Chart

```
G6  ████████████████████████████████████████████████████ 2608 (35.7%)
G3  ███████████████████████████ 1373 (18.8%)
G2  ████████████████ 812 (11.1%)
G5  ███████████████ 799 (10.9%)
G4  ███████████ 596 (8.2%)
G8  ███████████ 579 (7.9%)
G9  ████████ 442 (6.0%)
G7  ██ 102 (1.4%)
G1  ▏ 2 (0.03%)
```

**Note**: G10 (Relation Grounding) was added AFTER this conversion run.

---

## Distribution by Assertion Level

| Level | Count | % | Description |
|-------|-------|---|-------------|
| Critical | 2,928 | 55.9% | Must-have requirements |
| Expected | 1,903 | 36.3% | Should-have requirements |
| Aspirational | 407 | 7.8% | Nice-to-have requirements |

```
Critical     ████████████████████████████████████████████████████████ 2928 (55.9%)
Expected     ████████████████████████████████████ 1903 (36.3%)
Aspirational ████████ 407 (7.8%)
```

---

## Key Observations

### 1. High S8 (Parallel Workstreams) Count
- 26% of assertions relate to parallel/concurrent tasks
- Kening's dataset emphasizes multi-track planning
- S8 is ASPIRATIONAL, so these are bonus criteria

### 2. G6 (Action Item) Dominance
- 35.7% of grounding checks are for action items
- Makes sense: WBPs are fundamentally about tasks
- Shows strong focus on task validity

### 3. ~90% Success Rate
- Only 237 unknown out of 2,307 input assertions
- 10.3% unclassified may need manual review or dimension expansion

### 4. 2.27x Expansion Ratio
- Each input assertion expands to ~2.27 S+G units
- Confirms that free-form assertions often combine multiple requirements
- Framework successfully decomposes into atomic units

### 5. Missing G10 (Relation Grounding)
- This run was done BEFORE G10 was added
- Dependency assertions were classified under S2/S6 with G6
- Next run with v2.3 should show G10 being used

---

## Framework Version Notes

This conversion was performed with **assertion_analyzer v2.2**, which included:
- S1-S20 structural dimensions
- G1-G9 grounding dimensions (entity + semantic)
- Staged processing with token refresh
- Decomposition prompt v4.0

**NOT included in this run:**
- G10 (Relation Grounding) - added after this conversion
- RELATION_TYPES (DEPENDS_ON, BLOCKS, OWNS, PRODUCES, REQUIRES_INPUT)

---

## Files Generated

```
docs/ChinYew/
├── assertions_sg_classified.jsonl      # Main output (5,238 S+G units)
├── sg_classification_report.json       # Statistics and metadata
├── .sg_classification_checkpoint.json  # Processing checkpoint
└── sg_stages/
    ├── stage_001.jsonl                 # Assertions 1-50
    ├── stage_002.jsonl                 # Assertions 51-100
    ├── stage_003.jsonl                 # Assertions 101-150
    ├── stage_004.jsonl                 # Assertions 151-200
    ├── stage_005.jsonl                 # Assertions 201-250
    └── stage_006.jsonl                 # Remaining assertions
```

---

## Next Steps

1. **Re-run with v2.3**: Use updated analyzer with G10 to capture relation grounding
2. **Compare results**: Check if G10 is selected for dependency assertions
3. **Manual review**: Examine 237 unknown assertions for pattern improvements
4. **Quality check**: Sample verification of converted S+G units

---

## Appendix: Sample Converted Assertion

**Input** (free-form):
```
"The response sequences tasks logically, ensuring that prerequisite activities are scheduled before dependent tasks"
```

**Output** (atomic S+G units):
```json
{
  "s_dimension": "S2",
  "s_dimension_name": "Timeline Alignment",
  "level": "critical",
  "linked_g_dims": ["G3", "G6"],
  "g_slots": [
    {"g_dim": "G3", "slot_type": "DUE_DATE", "grounding": "GROUNDED"},
    {"g_dim": "G6", "slot_type": "TASK", "grounding": "GROUNDED"}
  ]
}
```

**Note**: With v2.3, this would also include G10 for DEPENDS_ON relation grounding.

---

*Report generated by assertion_analyzer conversion pipeline*
