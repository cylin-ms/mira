# Step 4 Comparison Report: Static Mapping vs GPT-5 Selection

**Author**: Chin-Yew Lin  
**Date**: 2025-11-29  
**Test Assertion**: "The plan arranges draft slides before review slides"

---

## Executive Summary

| Metric | Before (Static) | After (GPT-5) | Improvement |
|--------|-----------------|---------------|-------------|
| G Dimensions Generated | 2 | 1 | 50% reduction |
| Relevant G Dimensions | 1 | 1 | Same accuracy |
| Irrelevant G Dimensions | 1 | 0 | 100% removed |

---

## Test Case Analysis

### Input Assertion
```
"The plan arranges draft slides before review slides"
```

### Step 3 Classification (Same for Both)
- **Dimension**: S2 - Timeline Alignment
- **Layer**: structural
- **Level**: critical
- **Rationale**: The assertion addresses the correct sequencing of tasks (draft before review)

---

## Before: Static S→G Mapping

The static mapping table blindly applies ALL mapped G dimensions:

```
S_TO_G_MAP = {
    "S2": ["G3", "G6"],  # Timeline → Date/Time, Action Items
    ...
}
```

### Generated Assertions (Static)

| ID | Dimension | Name | Relevant? | Rationale |
|----|-----------|------|-----------|-----------|
| A0000_S2 | S2 | Timeline Alignment | ✓ Yes | Primary structural assertion |
| A0000_G3_0 | G3 | Date/Time Grounding | ✗ **NO** | No dates mentioned in assertion |
| A0000_G6_1 | G6 | Action Item Grounding | ✓ Yes | "draft slides" and "review slides" are tasks |

**Problem**: G3 (Date/Time Grounding) is included but the assertion says NOTHING about dates!

The static rationale for G3 was:
> "Timeline sequencing requires verifying that scheduled dates are consistent with the actual meeting date and don't conflict"

But this assertion is about **task ordering**, not **date scheduling**.

---

## After: GPT-5 Intelligent Selection

GPT-5 analyzes the actual assertion text to determine relevance:

### GPT-5 Reasoning Process

```
Input: "The plan arranges draft slides before review slides"

Available G dimensions for S2: [G3, G6]

Analysis:
- G3 (Date/Time Grounding): Does the assertion mention dates? NO
  → EXCLUDE - no dates to verify

- G6 (Action Item Grounding): Does the assertion mention tasks? YES
  → "draft slides" and "review slides" are specific tasks
  → INCLUDE - task ordering needs verification
```

### Generated Assertions (GPT-5)

| ID | Dimension | Name | Relevance Reason |
|----|-----------|------|------------------|
| A0000_S2 | S2 | Timeline Alignment | Primary structural assertion |
| A0000_G6_0 | G6 | Action Item Grounding | The assertion specifies the order of tasks (draft before review) |

**Result**: Only 1 grounding assertion, and it's actually relevant!

---

## Side-by-Side Comparison

```
BEFORE (Static Mapping)              AFTER (GPT-5 Selection)
========================             =======================

A0000_S2 (structural)                A0000_S2 (structural)
    │                                    │
    ├── A0000_G3_0 (grounding)           └── A0000_G6_0 (grounding)
    │   "Date/Time Grounding"                "Action Item Grounding"
    │   ⚠️ NOT RELEVANT                      ✓ RELEVANT
    │   (no dates in assertion)              (tasks: draft, review)
    │
    └── A0000_G6_1 (grounding)
        "Action Item Grounding"
        ✓ RELEVANT
        (tasks: draft, review)
```

---

## Impact Analysis

### Quality Improvement
1. **Precision**: From 50% (1/2 relevant) to 100% (1/1 relevant)
2. **No False Grounding Checks**: Eliminates checking dates when none exist
3. **Clearer Rationales**: GPT-5 provides assertion-specific reasons

### Efficiency Improvement
1. **Fewer Assertions**: 50% reduction in grounding assertions
2. **Faster WBP Verification**: Less to verify in Step 5
3. **Cleaner Reports**: No irrelevant dimensions cluttering output

### Cost Improvement
1. **One Extra GPT-5 Call**: For G selection (small overhead)
2. **Net Savings**: Fewer irrelevant verifications in downstream steps

---

## Conclusion

The GPT-5-based G selection transforms Step 4 from a **blind lookup** to an **intelligent analysis**:

| Aspect | Before | After |
|--------|--------|-------|
| Method | Static table lookup | GPT-5 semantic analysis |
| Input considered | Only S dimension ID | S dimension + assertion text |
| Output | All mapped Gs | Only relevant Gs |
| Rationale | Generic template | Assertion-specific |

This ensures that grounding assertions are **meaningful** and **testable** for each specific input.
