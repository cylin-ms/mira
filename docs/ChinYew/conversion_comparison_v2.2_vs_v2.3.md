# Kening Assertion Conversion Comparison Report

**Author**: Chin-Yew Lin  
**Date**: November 30, 2025  
**Versions Compared**: v2.2 (2025-11-30 08:43) vs v2.3 (2025-11-30)

## Executive Summary

Version 2.3 introduces **G10 (Relation Grounding)** to track relationships between entities (DEPENDS_ON, OWNS, BLOCKS, PRODUCES). This resulted in 795 new G10 assertions being generated from the same input data.

## Input/Output Comparison

| Metric | v2.2 | v2.3 | Delta | % Change |
|--------|------|------|-------|----------|
| Input assertions | 2,307 | 2,318 | +11 | +0.5% |
| Output S+G units | 5,238 | 5,600 | +362 | +6.9% |
| S assertions | 5,001 | 5,347 | +346 | +6.9% |
| G slots | 7,313 | 8,831 | +1,518 | +20.8% |
| Unknown | 237 | 253 | +16 | +6.8% |

### Expansion Ratio
- **v2.2**: 2,307 input → 5,238 output (2.27x expansion)
- **v2.3**: 2,318 input → 5,600 output (2.42x expansion)

## S Dimension Distribution

| S Dim | Name | v2.2 | v2.3 | Delta |
|-------|------|------|------|-------|
| S8 | Parallel Workstreams | 1,302 | 1,362 | +60 |
| S5 | Task Dates | 1,153 | 1,108 | -45 |
| S2 | Timeline Alignment | 205 | 626 | **+421** |
| S3 | Ownership Assignment | 517 | 530 | +13 |
| S16 | Assumptions & Prerequisites | 465 | 443 | -22 |
| S17 | Cross-team Coordination | 336 | 294 | -42 |
| S19 | Open Questions & Decision Points | 262 | 234 | -28 |
| S4 | Deliverables & Artifacts | 201 | 202 | +1 |
| S1 | Meeting Details | 184 | 178 | -6 |
| S6 | Dependencies, Blockers & Mitigation | 105 | 141 | +36 |
| S10 | Resource-Aware Planning | 165 | 134 | -31 |
| S9 | Checkpoints | 58 | 49 | -9 |
| S18 | Post-Event Actions | 41 | 38 | -3 |
| S20 | Clarity & First Impression | 7 | 8 | +1 |

**Notable Changes**:
- **S2 (Timeline Alignment)**: +421 increase - likely due to better decomposition with G10 for dependency ordering
- **S6 (Dependencies, Blockers)**: +36 increase - more assertions classified here with relation awareness

## G Dimension Distribution

| G Dim | Name | v2.2 | v2.3 | Delta | Notes |
|-------|------|------|------|-------|-------|
| G6 | Action Item Grounding | 2,608 | 3,082 | +474 | |
| G3 | Date/Time Grounding | 1,373 | 1,462 | +89 | |
| G5 | Topic Grounding | 799 | 905 | +106 | |
| G2 | Attendee Grounding | 812 | 806 | -6 | |
| **G10** | **Relation Grounding** | **0** | **795** | **+795** | **NEW!** |
| G4 | Artifact Grounding | 596 | 588 | -8 | |
| G8 | Instruction Adherence | 579 | 583 | +4 | |
| G9 | Planner-Generated Consistency | 442 | 507 | +65 | |
| G7 | Context Preservation | 102 | 100 | -2 | |
| G18 | (Unexpected) | 0 | 2 | +2 | **INVESTIGATE** |
| G1 | Hallucination Check | 2 | 1 | -1 | **INVESTIGATE** |

**Key Findings**:
1. **G10 (Relation Grounding)**: 795 new instances tracking DEPENDS_ON, OWNS, BLOCKS relations
2. **G18**: 2 unexpected instances - GPT-5 hallucinated a non-existent dimension
3. **G1**: Only 1 instance - may indicate pure hallucination checks are rare

## Level Distribution

| Level | v2.2 | v2.3 | Delta |
|-------|------|------|-------|
| critical | 2,928 | 3,080 | +152 |
| expected | 1,903 | 2,107 | +204 |
| aspirational | 407 | 413 | +6 |

## Processing Statistics

| Metric | v2.2 | v2.3 |
|--------|------|------|
| Meetings processed | 223 | 224 |
| Stages | 6 | 5 |
| Stage size | 50 | 50 |

## Files Generated

### v2.2 (Previous)
- `assertions_sg_classified.jsonl` (6.0 MB)
- `sg_classification_report.json`
- `sg_stages/stage_001-006.jsonl`

### v2.3 (Current)
- `assertions_sg_classified_v2.3.jsonl`
- `sg_classification_report_v2.3.json`
- `sg_stages_v2.3/stage_001-005.jsonl`

## Issues to Investigate

### 1. "Unknown" Count (253 instances) - CLARIFIED
The 253 "unknown" count represents **pure G assertions** with `s_dimension: null` - these are grounding-only assertions with no structural parent. This is expected behavior for assertions like "don't hallucinate attendees."

Breakdown:
- **111 are G1** (Hallucination Check) - "response should not introduce any attendee other than..."
- **142 are other pure G** assertions

This is NOT an error - these are valid pure grounding assertions that don't fit any S dimension.

### 2. G18 Hallucination (2 instances) - CONFIRMED BUG
GPT-5 generated "G18" which doesn't exist in our framework (we only have G1-G10).

**Source assertion**: "The response should include a risk mitigation step if OpenSCAP details are not confirmed by the identified mid-week milestone."

**Root cause**: GPT-5 tried to create a slot for `[MILESTONE]` but couldn't map it to an existing G dimension, so it hallucinated G18.

**Fix needed**: 
- Add post-processing validation to filter out G11+ dimensions
- Or add G dimension for milestones (could be G3 Date/Time or create new category)

### 3. G1 Count Discrepancy - EXPLAINED
The report showed G1 = 1 in `by_g_dimension`, but there are actually 111 G1 assertions.

**Reason**: The statistics count `g_slots` (G dimensions nested inside S assertions), not standalone pure G assertions. Pure G1 assertions have `dimension: "G1"` at the top level, not in `g_slots`.

**Actual counts**:
- Pure G1 assertions: 111 (top-level `dimension: "G1"`)
- G1 in g_slots: 1 (nested inside an S assertion)

## Recommendations

1. **Add G dimension validation**: Filter out invalid G dimensions (G11+) in post-processing
2. **Fix statistics counting**: Update script to count pure G assertions separately from g_slots
3. **Handle MILESTONE slots**: Map `[MILESTONE]` to G3 (Date/Time Grounding) since milestones are temporal checkpoints
4. **Keep pure G assertions**: The 253 "unknown" are valid - rename category from "unknown" to "pure_g" for clarity

---

## Fixes Applied (v6.0 Prompt)

Based on investigation, updated `decomposition_prompt.json` to v6.0:

### Key Changes
1. **Every G MUST have an S parent** - removed "pure G" concept
2. **Added rule**: "NEVER return s_dimension: null. Always find the appropriate S dimension."
3. **Fixed Example 4**: Changed from `s_dimension: null` to `S4 + G2 + G1`
4. **Added Example 5**: Milestone checkpoint using `S18 + G3 + G6`
5. **Added [MILESTONE] to G3 slots** for milestone dates
6. **Added S4 → G1 mapping** for anti-hallucination of attendees
7. **Added S18 → G3, G6 mapping** for milestone checkpoints
8. **Added Rule 7**: Use ONLY G1-G10 dimensions (no G11+)

### Test Results
```
Anti-hallucination: "don't introduce attendees other than Tisa and Nila"
  Before: s_dimension: null, linked_g: [G1]
  After:  S4 (Participant Identification) + G2 (attendees) + G1 (constraint) ✓

Milestone: "risk mitigation if OpenSCAP not confirmed by mid-week milestone"  
  Before: S6 + G6 + G18 (hallucinated!) + G9
  After:  S6 + G6 + G3 (milestone) + G9 ✓
```

## Appendix: Version Changes

### decomposition_prompt.json v5.0 (from v4.0)
- Added G10 (Relation Grounding) dimension
- Added G10 slot names: `[DEPENDS_ON]`, `[OWNS]`, `[BLOCKS]`, `[PRODUCES]`, `[REQUIRES_INPUT]`
- Updated S→G mappings: S2, S3, S6, S17 now include G10

### convert_kening_assertions_v2.py
- Added G10 to `G_SLOT_DESCRIPTIONS`
- Output files renamed to v2.3 suffix
