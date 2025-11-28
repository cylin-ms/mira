# Workback Plan Assertion Quality Analysis

> **Executive Summary**: GPT-5 JJ analysis of 2,318 assertions used to evaluate workback plan quality, identifying systematic issues and proposing actionable improvements.

## Quick Reference

| Metric | Value |
|--------|-------|
| **Overall Grade** | B |
| **Total Assertions** | 2,318 |
| **Quality Score** | 7.4/10 |
| **Critical Issues** | Over-specificity (43%), Limited applicability (32%) |
| **Patterns Identified** | 10 generalizable patterns |
| **Dimensions** | 232 → 12 (consolidation needed) |

---

## Key Findings

### ✅ Strengths
- Comprehensive coverage of timeline, ownership, and artifact readiness
- Clear level differentiation (critical/expected/aspirational)
- Specific and actionable assertions

### ⚠️ Weaknesses
1. **Over-Specificity (43%)** - Assertions too tied to specific names, dates, files
2. **Limited Applicability (32%)** - Cannot evaluate new meetings without original context
3. **Dimension Chaos** - 232 dimensions should be ~12 canonical categories
4. **Unbalanced Levels** - 55% critical (should be 30-35%)
5. **Coverage Gaps** - Missing: communication quality, feasibility, risk management

---

## Top 10 Assertion Patterns

| ID | Pattern | Level |
|----|---------|-------|
| P1 | Explicit Meeting Details | Critical |
| P2 | Timeline Backward Planning | Critical |
| P3 | Ownership Assignment | Critical |
| P4 | Artifact Specification | Expected |
| P5 | Dependency Sequencing | Expected |
| P6 | Meeting Objective Clarity | Expected |
| P7 | Assumption Disclosure | Aspirational |
| P8 | Stakeholder Alignment | Aspirational |
| P9 | Grounding in Context | Critical |
| P10 | Risk Identification | Aspirational |

---

## Priority Actions

### Week 1-2 (Quick Wins)
- [ ] Normalize dimension naming (2 hrs)
- [ ] Merge duplicate dimensions (4 hrs)
- [ ] Document level assignment criteria (4 hrs)

### Week 3-4 (Systematic)
- [ ] Build assertion templatization pipeline
- [ ] Rebalance critical/expected/aspirational levels
- [ ] Add missing quality dimensions

### Month 2 (Evolution)
- [ ] Implement parameterized assertions
- [ ] Build human evaluation UI
- [ ] Pilot with 50 new meetings

---

## Files Generated

| File | Description |
|------|-------------|
| `assertion_analysis.json` | Full GPT-5 critique data (804KB) |
| `assertion_patterns.json` | 10 patterns + dimension mapping |
| `ASSERTION_QUALITY_REPORT.md` | Detailed report with mitigations |
| `mitigation_plan.json` | Structured implementation plan |

---

## How to Run Analysis

```powershell
# Run GPT-5 analysis (requires MSAL authentication)
python analyze_assertions_gpt5.py --samples-per-dim 2

# View results in Streamlit
streamlit run view_analysis.py --server.port 8503

# View raw assertions
streamlit run view_assertions.py --server.port 8502
```

---

## Expected Outcomes

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Quality Score | 7.4 | 8.5+ | 4 weeks |
| Specificity Issues | 43% | <15% | 4 weeks |
| Applicability Issues | 32% | <10% | 4 weeks |
| Inter-rater Reliability | Unknown | >85% | 6 weeks |

---

## Contact

**Project**: Mira - Workback Plan Evaluation Framework  
**Branch**: `cylin-mira`  
**Analysis Date**: November 28, 2025
