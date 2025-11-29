# Lessons Learned: Two-Layer Assertion Framework

> **Author:** Chin-Yew Lin  
> **Date:** November 28, 2025  
> **Purpose:** Real-world examples demonstrating common pitfalls in assertion design and how to avoid them using the Structural (S1-S19) + Grounding (G1-G8) framework.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [The Core Distinction](#the-core-distinction)
3. [Lesson 1: Don't Mix Grounding into Structural](#lesson-1-dont-mix-grounding-into-structural)
4. [Lesson 2: Structural Checks Shape, Not Values](#lesson-2-structural-checks-shape-not-values)
5. [Lesson 3: Grounding Requires Source References](#lesson-3-grounding-requires-source-references)
6. [Lesson 4: S9 is a Meta-Pattern](#lesson-4-s9-is-a-meta-pattern)
7. [Lesson 5: Avoid Over-Specificity in Structural](#lesson-5-avoid-over-specificity-in-structural)
8. [Lesson 6: Grounding Assertions Need Parameterization](#lesson-6-grounding-assertions-need-parameterization)
9. [Common Pitfalls Summary](#common-pitfalls-summary)
10. [Quick Reference Checklist](#quick-reference-checklist)

---

## Executive Summary

When designing assertions for evaluating AI-generated content (like workback plans), it's critical to separate **structural checks** (does the output have the right shape?) from **grounding checks** (is the content factually accurate?). Mixing these leads to:

- Assertions that don't generalize across different inputs
- False positives (passes structure but contains hallucinations)
- False negatives (fails because of wrong specific values, even if structure is good)

This document provides concrete before/after examples from our GPT-5 simulation to illustrate how to apply the framework correctly.

---

## The Core Distinction

| Layer | Question | What It Checks | Example Question |
|-------|----------|----------------|------------------|
| **Structural (S1-S19)** | "Does the plan **HAVE** X?" | Presence, Shape, Structure | "Is there a meeting date in the plan?" |
| **Grounding (G1-G8)** | "Is X **CORRECT**?" | Factual Accuracy vs Source | "Does the date match source.MEETING.StartTime?" |

### The Two-Step Evaluation Process

```
Step 1: STRUCTURAL CHECK (S1-S19)
┌───────────────────────────────────────────────────────────┐
│ Does the plan have a meeting date?          [pass/fail]   │
│ Does the plan have task owners?             [pass/fail]   │
│ Does the plan list artifacts?               [pass/fail]   │
└───────────────────────────────────────────────────────────┘
                    ↓
Step 2: GROUNDING CHECK (G1-G8)
┌───────────────────────────────────────────────────────────┐
│ G1: No hallucinated entities overall?       [pass/fail]   │
│ G2: Do owners exist in ATTENDEES?           [pass/fail]   │
│ G3: Is the date correct per source?         [pass/fail]   │
│ G4: Do files exist in ENTITIES?             [pass/fail]   │
│ G5: Do topics align with source?            [pass/fail]   │
│ G6: Do tasks exist in source?               [pass/fail]   │
└───────────────────────────────────────────────────────────┘
```

---

## Lesson 1: Don't Mix Grounding into Structural

### ❌ BEFORE (Wrong)

```markdown
**Assertion A1 (Pattern S1 - Explicit Meeting Details):**
"The workback plan explicitly states the meeting date as January 15, 2025, 
the time as 2:00 PM PST, and lists Sarah Chen, Mike Johnson, Lisa Park, 
and Tom Wilson as attendees."
```

### ✅ AFTER (Correct)

```markdown
**Structural Assertion A1 (Pattern S1):**
"The workback plan explicitly states a meeting date, time, timezone, and 
lists attendees."

**Grounding Assertion G1 (People Grounding):**
"All attendees mentioned must exist in source.ATTENDEES."

**Grounding Assertion G2 (Temporal Grounding):**
"The stated date/time must match source.MEETING.StartTime."
```

### 📝 Rationale

| Issue | Explanation |
|-------|-------------|
| **The Problem** | The original assertion hardcodes specific values ("January 15, 2025", "Sarah Chen"). This makes the assertion useless for any other meeting. |
| **Why It's Wrong** | Structural assertions should check for **presence** ("does it exist?"), not **correctness** ("is it the right value?"). |
| **The Fix** | Split into two layers: (1) Structural checks if elements exist, (2) Grounding verifies they match the source. |
| **Generalization** | The corrected structural assertion works for ANY meeting. The grounding assertion parameterizes the check against the source data. |

### 🎯 Key Takeaway

> **Structural assertions should NEVER contain hardcoded values.** If you see a specific date, name, or file in a structural assertion, it's wrong.

---

## Lesson 2: Structural Checks Shape, Not Values

### ❌ BEFORE (Wrong)

```markdown
**Assertion A3 (Pattern S3 - Ownership Assignment):**
"Every task in the workback plan has an explicitly named owner, using only 
the known attendees: Sarah Chen, Mike Johnson, Lisa Park, or Tom Wilson."
```

### ✅ AFTER (Correct)

```markdown
**Structural Assertion A3 (Pattern S3):**
"Every task in the workback plan has an explicitly named owner 
(not 'someone' or 'team')."

**Grounding Assertion G1 (People Grounding):**
"All task owners must exist in source.ATTENDEES."
```

### 📝 Rationale

| Issue | Explanation |
|-------|-------------|
| **The Problem** | The original mixes structure ("has a named owner") with grounding ("using only known attendees"). |
| **Shape vs Value** | "Has a named owner" is **shape** - checking the structure of the task. "Owner is Sarah Chen" is **value** - checking against source data. |
| **The Fix** | Structural checks ONLY that each task has an owner field with a person's name. Grounding verifies the person exists in the source. |
| **Why This Matters** | A plan could have every task owned by "John Doe" (good structure) but fail grounding (John doesn't exist in attendees). These are different failure modes! |

### 🎯 Key Takeaway

> **Structural = "Is the field present and well-formed?"**  
> **Grounding = "Is the value in the field correct?"**

---

## Lesson 3: Grounding Requires Source References

### ❌ BEFORE (Wrong)

```markdown
**Grounding Assertion G2:**
"All dates and times in the workback plan must match or logically derive 
from the meeting date."
```

### ✅ AFTER (Correct)

```markdown
**Grounding Assertion G2 (Temporal Grounding):**
"All dates/times must match or be logically derivable from 
source.MEETING.StartTime."

**Source Reference:** source.MEETING.StartTime
**Verification:** Compare plan dates against source meeting date
**Failure Mode:** Date doesn't match (e.g., plan says Jan 16, source says Jan 15)
```

### 📝 Rationale

| Issue | Explanation |
|-------|-------------|
| **The Problem** | The original is vague - "the meeting date" doesn't specify WHERE to find the correct date. |
| **Why Source Matters** | Grounding assertions MUST reference the authoritative source field. Without it, evaluators don't know what to compare against. |
| **The Fix** | Explicitly reference `source.MEETING.StartTime` as the ground truth. |
| **Automation Benefit** | With explicit source references, the check can be automated: `if plan_date != source['MEETING']['StartTime']: FAIL` |

### 🎯 Key Takeaway

> **Every grounding assertion must specify: (1) What to check, (2) Where the truth is (source field), (3) What constitutes failure.**

---

## Lesson 4: S9 is a Meta-Pattern

### ❌ BEFORE (Wrong)

```markdown
**Assertion A9 (Pattern S9 - Grounding in Provided Context):**
"The workback plan avoids introducing any attendees, files, or topics 
not mentioned in the source context."
```

### ✅ AFTER (Correct)

```markdown
**Structural Assertion A9 (Pattern S9 - Meta-Check):**
"The workback plan does not introduce fabricated elements."

**Implementation:** This structural pattern is verified by passing ALL 
grounding assertions (G1-G8):
- G1: No hallucinated entities (overall) ✓
- G2: People exist in source.ATTENDEES ✓
- G3: Dates match source.MEETING.StartTime ✓
- G4: Files exist in source.ENTITIES ✓
- G5: Topics align with source.UTTERANCE ✓
- G6: Tasks exist in source material ✓

**Note:** S9 passes if and only if G1-G8 all pass.
```

### 📝 Rationale

| Issue | Explanation |
|-------|-------------|
| **The Problem** | S9 looks like a structural assertion but is actually checking factual accuracy (which is grounding's job). |
| **The Insight** | S9 is a "meta-pattern" - it's a structural requirement that the plan be grounded, but the actual verification is delegated to G1-G8. |
| **The Fix** | Define S9 as passing when all grounding assertions pass. This avoids duplicating grounding logic. |
| **Architectural Clarity** | S1-S8, S10 check specific structural elements. S9 is special - it aggregates grounding results. |

### 🎯 Key Takeaway

> **S9 (Grounding in Context) is not independently evaluated - it passes when G1-G8 all pass. Think of it as `S9 = G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5 ∧ G6 ∧ G7 ∧ G8`.**

---

## Lesson 5: Avoid Over-Specificity in Structural

### ❌ BEFORE (Wrong)

```markdown
**Assertion A4 (Pattern S4 - Artifact Specification):**
"The workback plan specifies preparation or distribution tasks for the 
following files: Product_Launch_Checklist_v3.xlsx, Engineering_Status_Report.pdf, 
Design_Assets_Summary.docx, and QA_Test_Results_Dec.pdf."
```

### ✅ AFTER (Correct)

```markdown
**Structural Assertion A4 (Pattern S4):**
"The workback plan lists specific artifacts (files, documents, decks) 
with preparation or distribution tasks."

**Grounding Assertion G3 (Artifact Grounding):**
"All referenced files must exist in source.ENTITIES_TO_USE where type=File."
```

### 📝 Rationale

| Issue | Explanation |
|-------|-------------|
| **The Problem** | Listing specific filenames makes the assertion useless for any meeting with different files. |
| **Over-Specificity** | This is "bad specificity" - hardcoding values that should be parameterized. |
| **The Fix** | Structural: "Does the plan mention files?" Grounding: "Do those files exist in source?" |
| **Reusability** | The corrected assertions work for ANY meeting, regardless of what files are involved. |

### 🎯 Key Takeaway

> **If your structural assertion lists specific filenames, dates, or names, STOP. Extract those values into grounding assertions that check against source data.**

---

## Lesson 6: Grounding Assertions Need Parameterization

### ❌ BEFORE (Wrong)

```markdown
**Grounding Check:**
"The plan mentions Sarah Chen as the organizer, which matches the source."
```

### ✅ AFTER (Correct)

```markdown
**Grounding Assertion G1 (People Grounding):**
Template: "All people mentioned in the workback plan must appear in 
{source.ATTENDEES}."

Evaluation:
- Extract all person names from the plan
- For each name, check: name ∈ source.ATTENDEES?
- If any name NOT in source.ATTENDEES → FAIL with "Fabricated: {name}"

**Example Check:**
- Plan mentions: Sarah Chen, Mike Johnson, Lisa Park, Tom Wilson
- source.ATTENDEES: [Sarah Chen, Mike Johnson, Lisa Park, Tom Wilson]
- Result: ✅ PASS (all names found in source)
```

### 📝 Rationale

| Issue | Explanation |
|-------|-------------|
| **The Problem** | The original assertion is a one-off check for a specific person, not a reusable pattern. |
| **Parameterization** | Good grounding assertions use templates with `{source.FIELD}` references that can be evaluated against any source data. |
| **The Fix** | Define the assertion as a parameterized check: "For all X in plan, X must exist in source.Y" |
| **Automation** | Parameterized assertions can be automated: `for person in plan.people: assert person in source['ATTENDEES']` |

### 🎯 Key Takeaway

> **Grounding assertions should be parameterized templates, not hardcoded checks. Use `{source.FIELD}` syntax to reference source data.**

---

## Common Pitfalls Summary

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| **Mixing Grounding into Structural** | Structural assertion contains specific values | Split into S (presence) + G (accuracy) |
| **No Source Reference** | Grounding says "must match" but doesn't say match WHAT | Add explicit `source.FIELD` reference |
| **Over-Specific Structural** | Lists specific files, dates, or names | Remove values, check only for presence |
| **Hardcoded Grounding** | "Must mention Sarah Chen" | Parameterize: "must exist in {source.ATTENDEES}" |
| **S9 Standalone Evaluation** | Trying to evaluate S9 without G1-G5 | S9 = aggregation of G1-G5 results |
| **Vague Failure Mode** | "Should be grounded" without specifics | Define: what fails, why, and how to detect |

---

## Quick Reference Checklist

### ✅ Structural Assertion Checklist (S1-S10)

- [ ] Does NOT contain hardcoded values (dates, names, files)
- [ ] Checks for PRESENCE/SHAPE only
- [ ] Can be applied to ANY meeting without modification
- [ ] Uses language like "has", "includes", "lists", "states"
- [ ] Does NOT use language like "correct", "matches", "accurate"

### ✅ Grounding Assertion Checklist (G1-G5)

- [ ] References a specific source field (e.g., `source.ATTENDEES`)
- [ ] Is parameterized with `{source.FIELD}` syntax
- [ ] Defines a clear failure mode
- [ ] Checks VALUES against source data
- [ ] Uses language like "matches", "exists in", "accurate to"

### ✅ Two-Layer Evaluation Checklist

- [ ] Structural evaluation runs FIRST
- [ ] Grounding evaluation runs SECOND (only if structure passes)
- [ ] S9 result = AND(G1, G2, G3, G4, G5)
- [ ] Final verdict considers BOTH layers
- [ ] Hallucination (grounding fail) trumps structural completeness

---

## Example: Complete Two-Layer Evaluation

### Input Context

```json
{
  "MEETING": {
    "Subject": "Q1 Product Launch Review",
    "StartTime": "2025-01-15T14:00:00-08:00"
  },
  "ATTENDEES": ["Sarah Chen", "Mike Johnson", "Lisa Park", "Tom Wilson"],
  "ENTITIES_TO_USE": [
    {"type": "File", "Name": "Product_Launch_Checklist_v3.xlsx"},
    {"type": "File", "Name": "Engineering_Status_Report.pdf"}
  ]
}
```

### Generated Plan (Snippet)

```
Meeting: Q1 Product Launch Review
Date: January 15, 2025, 2:00 PM PST
Attendees: Sarah Chen, Mike Johnson, Lisa Park, Tom Wilson, **John Smith**
...
```

### Layer 1: Structural Evaluation

| Assertion | Check | Result |
|-----------|-------|--------|
| S1 | Has meeting date, time, attendees? | ✅ PASS |
| S3 | Has named task owners? | ✅ PASS |
| S4 | Lists artifacts? | ✅ PASS |

**Structural Score: 100%** - All elements present!

### Layer 2: Grounding Evaluation

| Assertion | Check | Result |
|-----------|-------|--------|
| G1 | All people in source.ATTENDEES? | ❌ FAIL |
| | - Sarah Chen ✓ | |
| | - Mike Johnson ✓ | |
| | - Lisa Park ✓ | |
| | - Tom Wilson ✓ | |
| | - **John Smith ✗ (FABRICATED)** | |
| G2 | Date matches source? | ✅ PASS |

**Grounding Score: 80%** - One hallucination detected!

### Final Verdict

| Layer | Score | Status |
|-------|-------|--------|
| Structural | 100% | ✅ Complete |
| Grounding | 80% | ⚠️ Hallucination |
| **Overall** | **REJECT** | Fabricated attendee |

> **A structurally perfect plan with hallucinations is WORSE than an incomplete but accurate plan!**

---

## Conclusion

The two-layer assertion framework provides a principled way to evaluate AI-generated content:

1. **Structural assertions** ensure the output has the right **shape** and **completeness**
2. **Grounding assertions** ensure the content is **factually accurate** to the source

By keeping these layers separate, we can:
- Build reusable assertions that work across different inputs
- Clearly identify whether failures are structural (missing elements) or grounding (wrong values)
- Prioritize grounding over structure (hallucinations are worse than incompleteness)

**Remember:** If your structural assertion contains a specific value, it's probably wrong. Extract that value into a grounding assertion.

---

*Document version: 1.0*  
*Last updated: November 28, 2025*  
*Framework version: 2.0 (Structural S1-S10 + Grounding G1-G5)*
