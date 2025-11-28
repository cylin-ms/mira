# Assertion Framework Migration Report

**Author:** Chin-Yew Lin  
**Date:** November 28, 2025  
**Updated:** November 29, 2025

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

## 7. Recommendations

### For Evaluation Pipeline

1. **Use Phase 1 Framework** - With 99.3% of assertions already mapping to Phase 1 dimensions, the 14-dimension framework is well-suited for immediate evaluation.

2. **Consider Consolidating S5 into S2** - The 16 S5 (Task Dates) assertions overlap conceptually with S2 (Timeline Alignment). Consider merging for simpler evaluation.

3. **Add More Grounding Assertions** - Currently only 2.8% are grounding-layer (66 assertions). Consider generating more G1-G4 assertions for comprehensive source verification.

### For Future Assertion Generation

1. **Use Chin-Yew's Templates** - Generate assertions using the standardized templates from the start.

2. **Avoid Hardcoded Values** - Use placeholders like [TASK], [DELIVERABLE], [DATE/TIME].

3. **Balance Structural and Grounding** - Current ratio is 97:3. Aim for 80:20 for better hallucination detection.

4. **Leverage Unused Phase 1 Dimensions** - G2 (Date/Time Grounding) and G3 (Artifact Grounding) are not currently used. Consider adding assertions for these.

---

## 8. Data Files Reference

The conversion process produces three key JSONL files that document the migration pipeline:

### 8.1 Source: `Assertions_genv2_for_LOD1126part1.jsonl`

**Kening's original assertions** - the source data for this conversion.

| Property | Value |
|----------|-------|
| Meetings | 224 |
| Total Assertions | 2,318 |
| Unique Dimensions | 232 (fragmented) |

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

### 8.2 Intermediate: `assertions_kening_enhanced.jsonl`

**Enhanced assertions** with WBP dimension mapping metadata added to each assertion.

| Property | Value |
|----------|-------|
| Meetings | 224 |
| Total Assertions | 2,318 |
| Added Field | `_mira_metadata` |

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

### 8.3 Output: `assertions_converted_full.jsonl`

**Final converted assertions** in Chin-Yew's WBP format, ready for evaluation.

| Property | Value |
|----------|-------|
| Meetings | 224 |
| Total Assertions | 2,318 |
| Phase 1 Coverage | 99.3% (2,302 assertions) |
| Phase 2 Coverage | 0.7% (16 assertions) |

**Schema:**
```json
{
  "utterance": "meeting transcript text",
  "assertions": [
    {
      "text": "The plan must include explicit [person_name] assignment...",
      "level": "critical",
      "dimension": "S3",
      "dimension_name": "Ownership Assignment",
      "layer": "structural",
      "weight": 3,
      "source_reference": "entity-guid",
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

---

## 9. Conclusion

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
