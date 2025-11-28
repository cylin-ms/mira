# Framework Comparison Report

## Kening's WBP Evaluation Rubric vs. Our Current Pipeline

**Date:** November 28, 2025  
**Purpose:** Compare Kening's comprehensive WBP Evaluation Rubric with our current Two-Layer Assertion Pipeline and recommend next steps for alignment.

---

## Executive Summary

Kening's rubric is **significantly more comprehensive** than our current implementation:
- **Structural Dimensions:** 18 (Kening) vs 10 (ours)
- **Grounding Dimensions:** 5 (same)
- **Scoring:** Weighted 3-tier (Kening) vs Binary pass/fail (ours)
- **Output:** Includes suggested fixes and actionable next steps (Kening)

### Key Recommendations
1. **Expand structural patterns** from S1-S10 to S1-S18
2. **Add weighted scoring** (Critical=3, Moderate=2, Light=1)
3. **Add suggested fixes** to evaluation output
4. **Add role/skill-based ownership** support

---

## Detailed Comparison

### Structural Dimensions Alignment

| Kening ID | Kening Name | Our ID | Our Name | Status | Gap |
|-----------|-------------|--------|----------|--------|-----|
| S1 | Meeting Details | S1 | Explicit Meeting Details | ✅ Aligned | Minor wording |
| S2 | Timeline Alignment | S2 | Timeline Alignment | ✅ Aligned | - |
| S3 | Ownership Assignment | S3 | Ownership Assignment | ⚠️ Partial | Kening supports role/skill placeholders |
| S4 | Deliverables & Artifacts | S4 | Artifact Specification | ⚠️ Partial | Kening adds links, versions, formats |
| S5 | Task Dates | S5 | Date Specification | ✅ Aligned | - |
| S6 | Dependencies & Blockers | S6 | Blocker Identification | ⚠️ Partial | Kening adds mitigation steps |
| S7 | Source Traceability | S7 | Source Traceability | ✅ Aligned | - |
| S8 | Communication Channels | S8 | Communication Channels | ✅ Aligned | - |
| S9 | Grounding Meta-Check | S9 | Grounding Meta-Check | ✅ Aligned | - |
| S10 | Priority Assignment | S10 | Priority Assignment | ⚠️ Partial | Kening adds critical path justification |
| S11 | Risk Mitigation Strategy | ❌ Missing | - | 🔴 Gap | New pattern needed |
| S12 | Milestone Validation | ❌ Missing | - | 🔴 Gap | New pattern needed |
| S13 | Goal & Success Criteria | ❌ Missing | - | 🔴 Gap | New pattern needed |
| S14 | Resource Allocation | ❌ Missing | - | 🔴 Gap | New pattern needed |
| S15 | Compliance & Governance | ❌ Missing | - | 🔴 Gap | New pattern needed |
| S16 | Review & Feedback Loops | ❌ Missing | - | 🔴 Gap | New pattern needed |
| S17 | Escalation Path | ❌ Missing | - | 🔴 Gap | New pattern needed |
| S18 | Post-Event Actions | ❌ Missing | - | 🔴 Gap | New pattern needed |

### Grounding Dimensions Alignment

| Kening ID | Kening Name | Our ID | Our Name | Status |
|-----------|-------------|--------|----------|--------|
| G1 | Attendee Grounding | G1 | People Grounding | ✅ Aligned |
| G2 | Date/Time Grounding | G2 | Temporal Grounding | ✅ Aligned |
| G3 | Artifact Grounding | G3 | Artifact Grounding | ✅ Aligned |
| G4 | Topic Grounding | G4 | Topic Grounding | ✅ Aligned |
| G5 | Hallucination Check | G5 | Hallucination Check | ✅ Aligned |

---

## Feature Comparison

### Scoring System

| Feature | Kening | Ours | Gap |
|---------|--------|------|-----|
| Score Scale | 0/1/2 (Missing/Partial/Fully Met) | 0/1 (Fail/Pass) | 🔴 Missing partial scores |
| Weights | Critical=3, Moderate=2, Light=1 | All equal | 🔴 No weighting |
| Aggregation | Weighted average | Simple average | 🔴 No weighted calculation |
| Priority Classification | ✅ Explicit | ❌ Implicit | 🔴 Need priority tags |

### Output Quality

| Feature | Kening | Ours | Gap |
|---------|--------|------|-----|
| Rationale per assertion | ✅ Yes | ✅ Yes (explanation) | ✅ Aligned |
| Suggested fix per assertion | ✅ Yes | ❌ No | 🔴 Missing |
| Strengths summary | ✅ Yes | ❌ No | 🔴 Missing |
| Weaknesses summary | ✅ Yes | ❌ No | 🔴 Missing |
| Next actions | ✅ Yes | ❌ No | 🔴 Missing |

### Ownership Model

| Feature | Kening | Ours | Gap |
|---------|--------|------|-----|
| Named owner | ✅ Yes | ✅ Yes | ✅ Aligned |
| Role placeholder | ✅ Yes ("Role: Staff PM") | ❌ No | 🔴 Missing |
| Skill requirements | ✅ Yes ("Skills: exec storytelling") | ❌ No | 🔴 Missing |

---

## Priority Weights from Kening's Rubric

### Critical (Weight = 3)
- S1: Meeting Details
- S2: Timeline Alignment  
- S3: Ownership Assignment
- G1: Attendee Grounding
- G2: Date/Time Grounding
- G5: Hallucination Check

### Moderate (Weight = 2)
- S4: Deliverables & Artifacts
- S5: Task Dates
- S6: Dependencies & Blockers
- S7: Source Traceability
- S9: Grounding Meta-Check
- S10: Priority Assignment
- S11: Risk Mitigation Strategy
- S12: Milestone Validation
- S13: Goal & Success Criteria
- S14: Resource Allocation
- G3: Artifact Grounding
- G4: Topic Grounding

### Light (Weight = 1)
- S8: Communication Channels
- S15: Compliance & Governance
- S16: Review & Feedback Loops
- S17: Escalation Path
- S18: Post-Event Actions

---

## Gap Analysis Summary

### 🔴 Major Gaps (High Priority)

1. **8 Missing Structural Patterns (S11-S18)**
   - S11: Risk Mitigation Strategy
   - S12: Milestone Validation
   - S13: Goal & Success Criteria
   - S14: Resource Allocation
   - S15: Compliance & Governance
   - S16: Review & Feedback Loops
   - S17: Escalation Path
   - S18: Post-Event Actions

2. **No Weighted Scoring**
   - Current: Binary pass/fail
   - Needed: 0/1/2 with weights (3/2/1)

3. **No Suggested Fixes**
   - Current: Only pass/fail with rationale
   - Needed: Actionable fix suggestions

### ⚠️ Moderate Gaps (Medium Priority)

4. **Enhanced Ownership Model**
   - Add support for role/skill placeholders
   - "Owner: Staff PM (Skills: exec storytelling)"

5. **Enhanced Artifact Checks**
   - Add link validity checking
   - Add version/format specification
   - Add acceptance criteria

6. **Summary Generation**
   - Add strengths/weaknesses summary
   - Add next actions list

### ✅ Aligned Areas (No Action Needed)

- All 5 Grounding patterns (G1-G5)
- Core 10 Structural patterns (S1-S10) conceptually aligned
- Two-layer separation principle
- Source reference requirement for grounding

---

## Recommended Next Steps

### Phase 1: Quick Wins (1-2 days)

1. **Add weighted scoring to config.py**
   ```python
   ASSERTION_WEIGHTS = {
       "S1": 3, "S2": 3, "S3": 3,  # Critical
       "S4": 2, "S5": 2, "S6": 2, "S7": 2, "S9": 2, "S10": 2,  # Moderate
       "S8": 1,  # Light
       "G1": 3, "G2": 3, "G5": 3,  # Critical
       "G3": 2, "G4": 2,  # Moderate
   }
   ```

2. **Change scoring from binary to 3-tier**
   - 0 = Missing
   - 1 = Partial
   - 2 = Fully Met

3. **Add weighted score calculation**
   ```python
   weighted_score = sum(score * weight) / sum(max_score * weight)
   ```

### Phase 2: Pattern Expansion (3-5 days)

4. **Add S11-S18 patterns** to assertion generation
   - S11: Risk Mitigation Strategy
   - S12: Milestone Validation
   - S13: Goal & Success Criteria
   - S14: Resource Allocation
   - S15: Compliance & Governance
   - S16: Review & Feedback Loops
   - S17: Escalation Path
   - S18: Post-Event Actions

5. **Update prompts** to generate assertions for new patterns

### Phase 3: Enhanced Output (2-3 days)

6. **Add suggested_fix field** to evaluation output
7. **Add summary generation** with strengths/weaknesses/next_actions
8. **Update report template** to show weighted scores and fixes

### Phase 4: Advanced Features (1 week)

9. **Role/skill ownership support**
10. **Link validation for artifacts**
11. **JSON schema alignment** with Kening's spec

---

## Implementation Priority Matrix

| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| Weighted scoring | High | Low | **P1** |
| 3-tier scores (0/1/2) | High | Medium | **P1** |
| Add S11-S18 patterns | High | Medium | **P2** |
| Suggested fixes | Medium | Medium | **P2** |
| Summary generation | Medium | Low | **P3** |
| Role/skill ownership | Low | Medium | **P3** |
| Link validation | Low | High | **P4** |

---

## Conclusion

Kening's rubric provides a **comprehensive and production-ready** evaluation framework. Our current pipeline has the right conceptual foundation (two-layer separation) but needs:

1. **Expansion**: 8 more structural patterns
2. **Refinement**: Weighted scoring instead of binary
3. **Enhancement**: Suggested fixes and summaries

The recommended phased approach allows incremental adoption while maintaining pipeline stability.

---

*Report generated: November 28, 2025*
