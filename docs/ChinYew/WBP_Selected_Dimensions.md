# WBP Evaluation — Complete Dimension Reference

**Author:** Chin-Yew Lin  
**Date:** November 28, 2025  
**Version:** 1.1

**Purpose:** A comprehensive reference of all 23 WBP evaluation dimensions (S1-S19 + G1-G5), organized into Phase 1 (core) and Phase 2 (extended) evaluation frameworks.

---

## Overview

This document defines the complete set of **23 evaluation dimensions** for Workback Plan (WBP) assessment:

| Layer | Total | Phase 1 | Phase 2 |
|-------|:-----:|:-------:|:-------:|
| Structural (S1-S19) | 19 | 9 | 10 |
| Grounding (G1-G5) | 5 | 5 | 0 |
| **Total** | **24** | **14** | **10** |

**Phase Legend:**
- ✅ **Phase 1** — Core dimensions for initial evaluation framework (14 dimensions)
- ⬜ **Phase 2** — Extended dimensions for comprehensive evaluation (10 dimensions)

---

## Scoring Model
- **Scale:** 0 = Missing · 1 = Partial · 2 = Fully Met  
- **Weighted Quality Score:** Σ(score × weight) / max_possible
- **Weights:** Critical = 3 · Moderate = 2 · Light = 1

---

## Structural Dimensions (S1-S19)

### Core Dimensions (S1-S10)

The original 10 structural dimensions covering essential WBP elements.

| ID | Dimension | Weight | Phase | Template | Definition |
|----|-----------|:------:|:-----:|----------|------------|
| **S1** | Meeting Details | 3 | ✅ P1 | "The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES] accurately" | Subject, date, time, timezone, attendee list clearly stated |
| **S2** | Timeline Alignment | 3 | ✅ P1 | "The response should include a backward timeline from T₀ with dependency-aware sequencing" | Backward scheduling (T-minus) with dependency-aware sequencing |
| **S3** | Ownership Assignment | 3 | ✅ P1 | "The response should assign an owner for each [TASK] or specify role/skill placeholder if name unavailable" | Named owners per task OR role/skill placeholder |
| **S4** | Deliverables & Artifacts | 2 | ✅ P1 | "The response should list [DELIVERABLES] with working links, version/format specified" | All outputs listed with working links, version/format |
| S5 | Task Dates | 2 | ⬜ P2 | "The response should include due dates for every [TASK] aligned with timeline sequencing" | Due dates for every task aligned with S2 sequencing |
| **S6** | Dependencies & Blockers | 2 | ✅ P1 | "The response should identify [DEPENDENCIES/BLOCKERS] with mitigation steps documented" | Predecessors and risks identified; mitigation steps documented |
| S7 | Source Traceability | 2 | ⬜ P2 | "The response should link [TASKS/ARTIFACTS] back to original source priorities/files" | Tasks/artifacts link back to original source |
| S8 | Communication Channels | 1 | ⬜ P2 | "The response should specify [COMMUNICATION CHANNELS] (Teams, email, meeting cadence)" | Collaboration methods specified |
| S9 | Grounding Meta-Check | 2 | ⬜ P2 | "The response should only reference [ENTITIES] verified against source (meta-grounding check)" | All Grounding assertions (G1-G5) pass |
| S10 | Priority Assignment | 2 | ⬜ P2 | "The response should rank [TASKS] by critical path/impact on meeting success" | Tasks ranked by critical path/impact |

### Extended Dimensions (S11-S19)

Additional structural dimensions for comprehensive planning aspects.

| ID | Dimension | Weight | Phase | Template | Definition |
|----|-----------|:------:|:-----:|----------|------------|
| **S11** | Risk Mitigation Strategy | 2 | ✅ P1 | "The response should include concrete [RISK MITIGATION] strategies with owners" | Concrete contingencies for top risks with owners |
| S12 | Milestone Validation | 2 | ⬜ P2 | "The response should validate [MILESTONES] are feasible, right-sized, and verifiable" | Milestones feasible, right-sized, coherent |
| S13 | Goal & Success Criteria | 2 | ⬜ P2 | "The response should state clear [GOALS] and measurable [SUCCESS CRITERIA]" | Clear objectives and measurable success indicators |
| S14 | Resource Allocation | 2 | ⬜ P2 | "The response should specify [RESOURCE ALLOCATION] (people/time/tools/budget)" | People/time/tools/budget availability visible |
| S15 | Compliance & Governance | 1 | ⬜ P2 | "The response should note [COMPLIANCE/GOVERNANCE] requirements (security, privacy, regulatory)" | Security, privacy, regulatory checks noted |
| S16 | Review & Feedback Loops | 1 | ⬜ P2 | "The response should include [REVIEW/FEEDBACK] checkpoints to validate the plan" | Scheduled checkpoints to validate and iterate |
| S17 | Escalation Path | 1 | ⬜ P2 | "The response should define [ESCALATION PATH] with owners for critical risks" | Escalation owners and steps defined |
| **S18** | Post-Event Actions | 1 | ✅ P1 | "The response should list [POST-EVENT ACTIONS] (wrap-up, retrospectives, reporting)" | Wrap-up tasks, retrospectives, and reporting |
| **S19** | Caveat & Clarification | 2 | ✅ P1 | "The response should disclose [CAVEATS], [ASSUMPTIONS], and [CLARIFICATIONS] about information gaps or uncertainties" | Assumptions, information gaps, uncertainties disclosed |

---

## Grounding Dimensions (G1-G5)

Grounding dimensions verify factual accuracy against source data. **All 5 are Phase 1** dimensions for the evaluation framework.

| ID | Dimension | Weight | Phase | Template | Definition |
|----|-----------|:------:|:-----:|----------|------------|
| **G1** | Attendee Grounding | 3 | ✅ P1 | "All people mentioned must exist in {source.ATTENDEES}" | Attendees match source; no hallucinated names |
| **G2** | Date/Time Grounding | 3 | ✅ P1 | "Meeting date must match {source.MEETING.StartTime}" | Meeting date/time/timezone match the source |
| **G3** | Artifact Grounding | 2 | ✅ P1 | "All files must exist in {source.ENTITIES where type=File}" | Files/decks referenced exist in source repository |
| **G4** | Topic Grounding | 2 | ✅ P1 | "Topics must align with {source.UTTERANCE} or {source.MEETING.Subject}" | Agenda topics align with source priorities/context |
| **G5** | Hallucination Check | 3 | ✅ P1 | "No entities introduced that don't exist in source" | No extraneous entities or fabricated details |

---

## Phase 1 Dimensions Summary (14 Total)

### By Layer

| Layer | Phase 1 Dimensions | Count |
|-------|---------------------|:-----:|
| Structural | S1, S2, S3, S4, S6, S11, S18, S19 | 9 |
| Grounding | G1, G2, G3, G4, G5 | 5 |
| **Total** | | **14** |

### By Weight

| Weight | Level | Phase 1 Dimensions | Count |
|:------:|-------|---------------------|:-----:|
| 3 | Critical | S1, S2, S3, G1, G2, G5 | 6 |
| 2 | Moderate | S4, S6, S11, S19, G3, G4 | 6 |
| 1 | Light | S18 | 1 |

**Note:** S19 weight was updated from 1 to 2 to reflect its importance for transparency.

### By Evaluation Level

| Level | Dimensions | Description |
|-------|------------|-------------|
| **Event/Meeting** | S1 | Meeting metadata and context |
| **Overall Plan** | S2 | Timeline structure and sequencing |
| **Task** | S3, S4, S6 | Task-level ownership, deliverables, dependencies |
| **Risk** | S11 | Risk mitigation strategies |
| **Post-Event** | S18 | Wrap-up and follow-through actions |
| **Transparency** | S19 | Caveats, assumptions, and clarifications |
| **Grounding** | G1-G5 | Factual accuracy verification |

---

## Conversion Statistics (from Kening's Assertions)

Based on conversion of 2,318 assertions from 224 meetings:

### Actively Used Dimensions

| ID | Dimension | Count | % of Total |
|----|-----------|------:|:----------:|
| S2 | Timeline Alignment | 449 | 19.4% |
| S3 | Ownership Assignment | 414 | 17.9% |
| S4 | Deliverables & Artifacts | 399 | 17.2% |
| S6 | Dependencies & Blockers | 322 | 13.9% |
| S1 | Meeting Details | 321 | 13.8% |
| S19 | Caveat & Clarification | 279 | 12.0% |
| G5 | Hallucination Check | 60 | 2.6% |
| **Subtotal (Selected)** | | **2,244** | **96.8%** |

### Unmapped Dimensions (Outside 14 Selected)

| ID | Dimension | Count | Reason Not Selected |
|----|-----------|------:|---------------------|
| S11 | Risk Mitigation Strategy | 42 | Advanced planning, not core |
| S5 | Task Dates | 16 | Overlaps with S2 |
| S18 | Post-Event Actions | 10 | Advanced planning |
| G1 | Attendee Grounding | 3 | Covered by G5 |
| G4 | Topic Grounding | 3 | Covered by G5 |
| **Subtotal (Unmapped)** | | **74** | **3.2%** |

---

## Success & Fail Examples

### Structural Dimensions

| ID | Dimension | Success Example | Fail Example |
|----|-----------|-----------------|--------------|
| S1 | Meeting Details | "Board Review — Dec 15, 2025, 10:00 AM CST; Attendees: Alice Chen, Bob Li" | "Board Review next month" (no date/time/attendees) |
| S2 | Timeline Alignment | T–30: Draft → T–15: Review → T–1: Dry run → Meeting Day | Tasks listed randomly; "Review after meeting" |
| S3 | Ownership Assignment | "Draft deck — Owner: Alice Chen" or "Role: Staff PM" | "Draft deck — Owner: TBD" |
| S4 | Deliverables & Artifacts | "Final deck (link); v3.2 PDF" | "Prepare documents" (no links/versions) |
| S6 | Dependencies & Blockers | "Dependency: Finance approval; Mitigation: escalate to CFO" | No blockers mentioned |
| S11 | Risk Mitigation Strategy | "Risk: Vendor delay; Mitigation: backup vendor PO" | "Monitor vendor" (vague) |
| S18 | Post-Event Actions | "Post-meeting: send summary; retrospective" | No post-event tasks |
| S19 | Caveat & Clarification | "Assumption: Budget approved; Gap: Vendor TBD" | Hidden assumptions presented as facts |

### Grounding Dimensions

| ID | Dimension | Success Example | Fail Example |
|----|-----------|-----------------|--------------|
| G1 | Attendee Grounding | Attendees exactly match invite roster | Adds "John Doe" not in source |
| G2 | Date/Time Grounding | Date/time exactly match invite | Uses Dec 16 instead of Dec 15 |
| G3 | Artifact Grounding | Deck link points to real file | Links to non-existent file |
| G4 | Topic Grounding | Topics match source agenda | Adds "New launch" not in source |
| G5 | Hallucination Check | No extra entities beyond source | Includes fabricated task |

---

## Dimension Groups by Evaluation Scope

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRUCTURAL DIMENSIONS                        │
├─────────────────────────────────────────────────────────────────┤
│  CORE (S1-S10) — Essential WBP elements                         │
│    ✅ P1: S1: Meeting Details                                   │
│    ✅ P1: S2: Timeline Alignment                                │
│    ✅ P1: S3: Ownership Assignment                              │
│    ✅ P1: S4: Deliverables & Artifacts                          │
│    ⬜ P2: S5: Task Dates (overlaps with S2)                     │
│    ✅ P1: S6: Dependencies & Blockers                           │
│    ⬜ P2: S7-S10: Source Traceability, Communication,           │
│                   Meta-Check, Priority Assignment               │
├─────────────────────────────────────────────────────────────────┤
│  EXTENDED (S11-S19) — Advanced planning aspects                 │
│    ✅ P1: S11: Risk Mitigation Strategy                         │
│    ⬜ P2: S12-S17: Milestones, Goals, Resources, Compliance,    │
│                    Review Loops, Escalation                     │
│    ✅ P1: S18: Post-Event Actions                               │
│    ✅ P1: S19: Caveat & Clarification                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    GROUNDING DIMENSIONS                         │
│              "Are those elements FACTUALLY CORRECT?"            │
├─────────────────────────────────────────────────────────────────┤
│  ✅ P1: G1: Attendee Grounding — People exist in source?        │
│  ✅ P1: G2: Date/Time Grounding — Dates match source?           │
│  ✅ P1: G3: Artifact Grounding — Files exist in source?         │
│  ✅ P1: G4: Topic Grounding — Topics align with source?         │
│  ✅ P1: G5: Hallucination Check — No fabricated entities?       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quality Score Matrix

| Scenario | Structural (S) | Grounding (G) | Overall Quality |
|----------|----------------|---------------|-----------------|
| Complete & Accurate | ✅ Pass | ✅ Pass | **Excellent** |
| Complete but Hallucinated | ✅ Pass | ❌ Fail | **Reject** ⚠️ |
| Accurate but Incomplete | ❌ Fail | ✅ Pass | **Needs Work** |
| Neither | ❌ Fail | ❌ Fail | **Poor** |

**CRITICAL:** A plan that passes structural checks but fails grounding is **worse** than one that is incomplete but accurate. Hallucinated plans with good structure can mislead users.

---

## Evaluation Priority Order

1. **Grounding First (G1-G5)** — Factual accuracy is paramount
2. **Critical Structural (S1, S2, S3)** — Weight = 3
3. **Moderate Structural (S4, S6, S11, S19)** — Weight = 2
4. **Light Structural (S18)** — Weight = 1

---

## Phase 2 Dimensions Reference (10 Total)

These dimensions are available for extended/comprehensive evaluation in Phase 2:

| ID | Dimension | Weight | Reason for Phase 2 |
|----|-----------|:------:|---------------------|
| S5 | Task Dates | 2 | Overlaps significantly with S2 (Timeline Alignment) |
| S7 | Source Traceability | 2 | Covered indirectly by G5 (Hallucination Check) |
| S8 | Communication Channels | 1 | Low priority, optional |
| S9 | Grounding Meta-Check | 2 | Redundant with G1-G5 |
| S10 | Priority Assignment | 2 | Nice-to-have, not essential |
| S12 | Milestone Validation | 2 | Advanced planning aspect |
| S13 | Goal & Success Criteria | 2 | Advanced planning aspect |
| S14 | Resource Allocation | 2 | Advanced planning aspect |
| S15 | Compliance & Governance | 1 | Situational, not universal |
| S16 | Review & Feedback Loops | 1 | Advanced planning aspect |
| S17 | Escalation Path | 1 | Advanced planning aspect |

---

## References

- **WBP_Evaluation_Rubric.md** — Full rubric with all dimension definitions
- **ASSERTION_QUALITY_REPORT.md** — Quality analysis and framework recommendations
- **conversion_analysis_report.md** — Conversion statistics from Kening's assertions

---

*Document Version: 1.2*  
*Last Updated: November 28, 2025*  
*Author: Chin-Yew Lin*
