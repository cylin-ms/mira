# Two-Layer Assertion Evaluation Report

> **Generated:** 2025-11-28 15:17:28  
> **Framework:** Two-Layer Assertion Framework v2.0 (Structural S1-S10 + Grounding G1-G5)

---

## Executive Summary

This report evaluates **9 workback plans** across three quality levels using the Two-Layer Assertion Framework.

**Perfect Quality Plans:** Achieved 80% structural and 87% grounding scores, approaching expected targets.
**Medium Quality Plans:** Achieved 73% structural and 33% grounding scores, demonstrating deliberate quality degradation.
**Low Quality Plans:** Achieved 33% structural and 0% grounding scores, confirming detection of poor quality.

**Overall:** The framework correctly differentiated quality levels, with 3 plans passing and 6 failing as expected.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Plans Evaluated | 9 |
| Total Assertions | 135 |
| Overall Structural Score | 62% |
| Overall Grounding Score | 40% |
| Pass Rate | 33% |

---

## Results by Quality Level

### Perfect Quality

**Target:** 100% S, 100% G
**Actual:** 80% Structural, 87% Grounding
**Plans Evaluated:** 3

| Verdict | Count |
|---------|-------|
| ✅ pass | 3 |

### Medium Quality

**Target:** 80% S, 60% G
**Actual:** 73% Structural, 33% Grounding
**Plans Evaluated:** 3

| Verdict | Count |
|---------|-------|
| ❌ fail_both | 2 |
| ❌ fail_grounding | 1 |

### Low Quality

**Target:** 40% S, 20% G
**Actual:** 33% Structural, 0% Grounding
**Plans Evaluated:** 3

| Verdict | Count |
|---------|-------|
| ❌ fail_both | 3 |


---

## Two-Layer Framework Analysis

### Structural Assertions (S1-S10)
*Question: "Does the plan HAVE X?" (Checks PRESENCE)*

| Assertion | Pass | Fail | Rate |
|-----------|------|------|------|
| A1 | 4 | 5 | ❌ 44% |
| A10 | 0 | 9 | ❌ 0% |
| A2 | 9 | 0 | ✅ 100% |
| A3 | 6 | 3 | ⚠️ 67% |
| A4 | 9 | 0 | ✅ 100% |
| A5 | 6 | 3 | ⚠️ 67% |
| A6 | 6 | 3 | ⚠️ 67% |
| A7 | 7 | 2 | ⚠️ 78% |
| A8 | 0 | 9 | ❌ 0% |
| A9 | 9 | 0 | ✅ 100% |

### Grounding Assertions (G1-G5)
*Question: "Is X CORRECT?" (Checks ACCURACY)*

| Assertion | Pass | Fail | Rate |
|-----------|------|------|------|
| G1 | 3 | 6 | ❌ 33% |
| G2 | 5 | 4 | ⚠️ 56% |
| G3 | 3 | 6 | ❌ 33% |
| G4 | 6 | 3 | ⚠️ 67% |
| G5 | 1 | 8 | ❌ 11% |

**Sample Hallucinations Detected:**
- [perfect] G5: `February 1, 2025...`
- [medium] G1: `Alex Thompson...`
- [medium] G2: `Missing meeting time...`
- [medium] G2: `Missing timezone...`
- [medium] G3: `Marketing_Brief.pdf...`

---

## Verdict Distribution

| Verdict | Count | Percentage |
|---------|-------|------------|
| ✅ pass | 3 | 33% |
| 🔧 fail_structure | 0 | 0% |
| ⚠️ fail_grounding | 1 | 11% |
| ❌ fail_both | 5 | 56% |

**Interpretation:**
- ✅ **pass**: Plan has good structure AND is factually accurate
- 🔧 **fail_structure**: Plan is missing required elements
- ⚠️ **fail_grounding**: Plan has good structure but contains hallucinations
- ❌ **fail_both**: Plan is both incomplete and inaccurate

---

## Detailed Results

### Plan 1: scenario_001 (Perfect)

- **Structural Score:** 80%
- **Grounding Score:** 80%
- **Verdict:** ✅ pass

**Failed Structural Assertions:**
- A8: The plan does not mention any communication channels or methods for status updat
- A10: The plan lists tasks with owners, due dates, and dependencies, but there is no i

**Failed Grounding Assertions:**
- G5: Compared all entities (people, dates, files, topics) in the plan against the sou

---

### Plan 2: scenario_001 (Medium)

- **Structural Score:** 70%
- **Grounding Score:** 20%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan includes a meeting date and an organizer, but it does not provide a mee
- A8: The plan does not mention any communication channels or methods for status updat
- A10: The plan lists tasks with owners, due dates, and notes, but there is no indicati

**Failed Grounding Assertions:**
- G1: The plan mentions an additional person, Alex Thompson, who is not listed in the 
- G2: The plan specifies the meeting date as January 15, 2025, which matches the sourc
- G3: The plan references five files, but one of them (Marketing_Brief.pdf) does not e

---

### Plan 3: scenario_001 (Low)

- **Structural Score:** 30%
- **Grounding Score:** 0%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan includes meeting dates and attendees, but does not provide any meeting 
- A3: The action items list tasks but does not assign them to any specifically named i
- A5: The plan lists tasks under 'Action Items' but does not provide any completion da

**Failed Grounding Assertions:**
- G1: The plan includes additional attendees (John Smith, Emily Davis, Robert Brown) t
- G2: The plan does not mention any meeting date, time, or timezone, while the source 
- G3: The plan references files 'Launch_Overview_Plan.docx' and 'Marketing_Strategy_Q1

---

### Plan 4: scenario_002 (Perfect)

- **Structural Score:** 80%
- **Grounding Score:** 80%
- **Verdict:** ✅ pass

**Failed Structural Assertions:**
- A8: The plan does not mention any communication channels or methods for updates and 
- A10: The plan does not include any priority levels or importance indicators for the t

**Failed Grounding Assertions:**
- G5: Compared all entities (attendees, files, dates, topics) in the plan against the 

---

### Plan 5: scenario_002 (Medium)

- **Structural Score:** 70%
- **Grounding Score:** 40%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan includes meeting date, time, and timezone, but does not provide an atte
- A8: The plan does not mention any communication channels or methods for updates and 
- A10: The plan lists tasks with owners and due dates, but there are no priority levels

**Failed Grounding Assertions:**
- G1: The plan includes names not present in the source attendees list. Specifically, 
- G3: Compared all files mentioned in the plan against the source files. Four files ma
- G5: Compared all entities (attendees, files, dates, topics) in the plan against the 

---

### Plan 6: scenario_002 (Low)

- **Structural Score:** 40%
- **Grounding Score:** 0%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan does not include explicit meeting details such as date, time, timezone,
- A3: The plan lists responsibilities but does not assign any specific named individua
- A5: The plan includes an overall completion date but does not provide specific compl

**Failed Grounding Assertions:**
- G1: The plan mentions people (Sarah Johnson, Michael Smith, Laura Chen) who are not 
- G2: The plan does not mention any specific meeting date, time, or timezone, while th
- G3: The plan references files 'BudgetOverview_Draft.docx' and 'FinanceSummary2027.xl

---

### Plan 7: scenario_003 (Perfect)

- **Structural Score:** 80%
- **Grounding Score:** 100%
- **Verdict:** ✅ pass

**Failed Structural Assertions:**
- A8: The plan does not mention any communication channels or methods for updates and 
- A10: The plan lists tasks with dates, owners, artifacts, dependencies, and blockers, 

---

### Plan 8: scenario_003 (Medium)

- **Structural Score:** 80%
- **Grounding Score:** 40%
- **Verdict:** ⚠️ fail_grounding

**Failed Structural Assertions:**
- A8: The plan does not mention any communication channels or methods for updates and 
- A10: The plan lists tasks with dates, owners, and dependencies, but there are no prio

**Failed Grounding Assertions:**
- G1: The plan includes an additional person, Alex Thompson, who is not listed in the 
- G3: The plan references 'Marketing_Brief.pdf' which is not present in the source fil
- G5: The plan introduces entities not present in the source data. Specifically, an ad

---

### Plan 9: scenario_003 (Low)

- **Structural Score:** 30%
- **Grounding Score:** 0%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan includes meeting dates and an attendee list, but there is no mention of
- A3: The plan lists tasks but does not assign them to specific named individuals; tas
- A5: The plan includes a timeline with dates for milestones, but it does not specify 

**Failed Grounding Assertions:**
- G1: The plan lists participants beyond those in the source attendees list. While Jen
- G2: The plan does not explicitly mention the meeting date, time, or timezone. The so
- G3: The plan references files 'Client_Strategy_Doc.pdf' and 'Engagement_Overview.xls

---


---

## Insights & Recommendations

### Framework Effectiveness

✅ **Quality Differentiation:** The framework correctly ranked quality levels (Perfect > Medium > Low)

### Structural vs Grounding Insights

- **Medium:** 40% gap between structural (73%) and grounding (33%) scores
- **Low:** 33% gap between structural (33%) and grounding (0%) scores

### Recommendations

1. **Structural assertions** should focus on PRESENCE checking only
2. **Grounding assertions** should always reference specific source fields
3. **S9 (Grounding Meta-Check)** should be computed as AND(G1-G5)
4. Plans with high structural but low grounding scores indicate hallucinations
5. Plans with low structural scores need more complete content

---

## Appendix: Two-Layer Framework Reference

### Structural Patterns (S1-S10)

| ID | Pattern | Purpose |
|----|---------|---------|
| S1 | Explicit Meeting Details | Has date, time, timezone, attendees |
| S2 | Timeline Alignment | Has timeline working back from meeting |
| S3 | Ownership Assignment | Has named owners (not "someone") |
| S4 | Artifact Specification | Lists specific files/documents |
| S5 | Date Specification | States completion dates for tasks |
| S6 | Blocker Identification | Identifies dependencies and blockers |
| S7 | Source Traceability | Links tasks to source entities |
| S8 | Communication Channels | Mentions communication methods |
| S9 | Grounding Meta-Check | Passes when G1-G5 all pass |
| S10 | Priority Assignment | Has priority levels for tasks |

### Grounding Patterns (G1-G5)

| ID | Pattern | Source Field |
|----|---------|--------------|
| G1 | People Grounding | source.attendees |
| G2 | Temporal Grounding | source.meeting_date/time |
| G3 | Artifact Grounding | source.files |
| G4 | Topic Grounding | source.topics |
| G5 | Hallucination Check | All source fields |

---

*Report generated by the Two-Layer Assertion Pipeline*
