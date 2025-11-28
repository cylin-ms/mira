# WBP Evaluation — Selected Dimensions

**Purpose:** A streamlined rubric containing the selected structural and grounding dimensions for Workback Plan (WBP) evaluation.

**GitHub Link:** [WBP_Selected_Dimensions.md](https://github.com/cylin-ms/mira/blob/master/docs/ChinYew/WBP_Selected_Dimensions.md)

---

## Scoring Model
- **Scale:** 0 = Missing · 1 = Partial · 2 = Fully Met  
- **Weighted Quality Score:** Σ(score × weight) / max_possible
- **Weights:** Critical = 3 · Moderate = 2 · Light = 1

---

## Selected Structural Dimensions (S)

### By Evaluation Level

| Level | Dimensions | Description |
|-------|------------|-------------|
| **Event/Meeting** | S1 | Meeting metadata and context |
| **Overall Plan** | S2 | Timeline structure and sequencing |
| **Task** | S3, S4, S5, S6 | Task-level ownership, deliverables, dates, dependencies |
| **Risk** | S11 | Risk mitigation strategies |
| **Post-Event** | S18 | Wrap-up and follow-through actions |
| **Transparency** | S19 | Caveats, assumptions, and clarifications |

---

## Complete Dimension Reference Table

| ID | Dimension | Weight | Template | Concise Definition | Objective Evaluation Statement | Success Example | Fail Example |
|----|-----------|:------:|----------|-------------------|-------------------------------|-----------------|--------------|
| **S1** | Meeting Details | 3 | "The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES] accurately" | Subject, date, time, timezone, attendee list clearly stated. | Plan includes all meeting metadata; missing any field = fail. | "Board Review — Dec 15, 2025, 10:00 AM CST; Attendees: Alice Chen, Bob Li; TZ: CST." | "Board Review next month" (no date/time/timezone or attendee list). |
| **S2** | Timeline Alignment | 3 | "The response should include a backward timeline from T₀ with dependency-aware sequencing" | Backward scheduling (T-minus) with dependency-aware sequencing from meeting date. | Tasks arranged in reverse order from meeting date; dependencies respected. | T–30: Draft deck → T–15: Review → T–1: Dry run → Meeting Day. | Tasks listed randomly; e.g., "Review deck after meeting." |
| **S3** | Ownership Assignment | 3 | "The response should assign an owner for each [TASK] or specify role/skill placeholder if name unavailable" | Named owners per task **or** role/skill placeholder if names unavailable. | Every task has named owner **or** role/skill requirement stated. | "Draft deck — Owner: Alice Chen; If name pending: Role: Staff PM; Skills: exec storytelling." | "Draft deck — Owner: TBD." |
| **S4** | Deliverables & Artifacts | 2 | "The response should list [DELIVERABLES] with working links, version/format specified" | All outputs listed with working links, version/format specified. | Deliverables traceable and accessible; missing links or versions = fail. | "Final deck (link); Budget sheet (link); Risk log (link); v3.2 PDF." | "Prepare documents" (no links or specifics). |
| **S5** | Task Dates | 2 | "The response should include due dates for every [TASK] aligned with timeline sequencing" | Due dates for every task aligned with S2 sequencing. | All tasks have due dates; dates match milestone/timeline logic. | "Draft deck due Dec 1; Review Dec 10; Dry run Dec 14." | No dates provided for any task. |
| **S6** | Dependencies & Blockers | 2 | "The response should identify [DEPENDENCIES/BLOCKERS] with mitigation steps documented" | Predecessors and risks identified; mitigation steps documented. | Blockers and mitigations listed; absence = fail. | "Dependency: Finance approval; Mitigation: escalate to CFO by Dec 5; Owner: Ops PM." | No mention of blockers or mitigation. |
| **S11** | Risk Mitigation Strategy | 2 | "The response should include concrete [RISK MITIGATION] strategies with owners" | Concrete contingencies for top risks with owners. | Mitigation steps documented; vague "monitor" = fail. | "Risk: Vendor delay; Mitigation: backup vendor PO in place; Owner: Procurement Lead." | Risks listed with "monitor" and no mitigation. |
| **S18** | Post-Event Actions | 1 | "The response should list [POST-EVENT ACTIONS] (wrap-up, retrospectives, reporting)" | Wrap-up tasks, retrospectives, and reporting. | Post-event steps listed; none = fail. | "Post-meeting: send summary; archive deck; retrospective; publish decisions." | No post-event tasks listed. |
| **S19** | Caveat & Clarification | 1 | "The response should disclose [CAVEATS], [ASSUMPTIONS], and [CLARIFICATIONS] about information gaps or uncertainties" | Explicit disclosure of assumptions, missing information, uncertainties, and clarifications needed. | Caveats and assumptions clearly stated; hidden assumptions = fail. | "Caveat: Budget figures pending CFO approval; Assumption: All attendees confirmed; Clarification needed: Venue capacity." | Plan presents uncertain items as facts; no disclosure of assumptions or gaps. |

---

## Grounding Dimensions (G)

| ID | Dimension | Weight | Template | Concise Definition | Objective Evaluation Statement | Success Example | Fail Example |
|----|-----------|:------:|----------|-------------------|-------------------------------|-----------------|--------------|
| **G1** | Attendee Grounding | 3 | "All people mentioned must exist in {source.ATTENDEES}" | Attendees match source; no hallucinated names. | All attendees verified against source list. | Attendees exactly match the invite roster. | Adds "John Doe" not in source. |
| **G2** | Date/Time Grounding | 3 | "Meeting date must match {source.MEETING.StartTime}" | Meeting date/time/timezone match the source. | No deviation from source meeting schedule. | Date/time/timezone exactly match the invite. | Uses Dec 16 instead of Dec 15. |
| **G3** | Artifact Grounding | 2 | "All files must exist in {source.ENTITIES where type=File}" | Files/decks referenced exist in the source repository. | Artifacts validated; missing or fabricated = fail. | Deck link points to real file in repo; opens correctly. | Links to non-existent or fabricated file. |
| **G4** | Topic Grounding | 2 | "Topics must align with {source.UTTERANCE} or {source.MEETING.Subject}" | Agenda topics align with source priorities/context. | Topics match source; unrelated topics = fail. | Agenda topics: Budget, Strategy — match the source agenda. | Adds "New product launch" not in source. |
| **G5** | Hallucination Check | 3 | "No entities introduced that don't exist in source" | No extraneous entities or fabricated details. | Plan contains only source-backed entities. | No extra tasks or entities beyond source-backed items. | Includes "Prepare marketing video" not in source. |

---

## Summary Statistics

| Category | Count | Max Weight | Total Weight Points |
|----------|:-----:|:----------:|:-------------------:|
| **Structural (S)** | 9 | 3 | 19 |
| **Grounding (G)** | 5 | 3 | 13 |
| **Total** | 14 | — | 32 |

### Weight Distribution

| Weight | Level | Dimensions | Count |
|:------:|-------|------------|:-----:|
| 3 | Critical | S1, S2, S3, G1, G2, G5 | 6 |
| 2 | Moderate | S4, S5, S6, S11, G3, G4 | 6 |
| 1 | Light | S18, S19 | 2 |

---

## Dimension Groups by Evaluation Scope

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRUCTURAL DIMENSIONS                        │
├─────────────────────────────────────────────────────────────────┤
│  EVENT/MEETING LEVEL                                            │
│    S1: Meeting Details (subject, date, time, attendees)         │
├─────────────────────────────────────────────────────────────────┤
│  OVERALL PLAN LEVEL                                             │
│    S2: Timeline Alignment (backward scheduling, sequencing)     │
├─────────────────────────────────────────────────────────────────┤
│  TASK LEVEL                                                     │
│    S3: Ownership Assignment (named owner or role/skill)         │
│    S4: Deliverables & Artifacts (links, versions)               │
│    S5: Task Dates (due dates aligned with timeline)             │
│    S6: Dependencies & Blockers (predecessors, mitigations)      │
├─────────────────────────────────────────────────────────────────┤
│  RISK LEVEL                                                     │
│    S11: Risk Mitigation Strategy (contingencies with owners)    │
├─────────────────────────────────────────────────────────────────┤
│  POST-EVENT LEVEL                                               │
│    S18: Post-Event Actions (wrap-up, retrospective, reporting)  │
├─────────────────────────────────────────────────────────────────┤
│  TRANSPARENCY LEVEL                                             │
│    S19: Caveat & Clarification (assumptions, gaps, uncertainties)│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    GROUNDING DIMENSIONS                         │
│              "Are those elements FACTUALLY CORRECT?"            │
├─────────────────────────────────────────────────────────────────┤
│  G1: Attendee Grounding — People exist in source?               │
│  G2: Date/Time Grounding — Dates match source?                  │
│  G3: Artifact Grounding — Files exist in source?                │
│  G4: Topic Grounding — Topics align with source?                │
│  G5: Hallucination Check — No fabricated entities?              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quality Score Matrix

| Scenario | Structural (S1-S19) | Grounding (G1-G5) | Overall Quality |
|----------|---------------------|-------------------|-----------------|
| Complete & Accurate | ✅ Pass | ✅ Pass | **Excellent** |
| Complete but Hallucinated | ✅ Pass | ❌ Fail | **Reject** |
| Accurate but Incomplete | ❌ Fail | ✅ Pass | **Needs Work** |
| Neither | ❌ Fail | ❌ Fail | **Poor** |

---

## Notes

- **S19 (Caveat & Clarification)** is a new dimension added to ensure transparency about assumptions, information gaps, and uncertainties in the plan.
- Grounding dimensions (G1-G5) verify factual accuracy against source data.
- A plan that passes structural checks but fails grounding is **worse** than one that is incomplete but accurate.

---

*Document created: November 28, 2025*  
*Author: Chin-Yew Lin*
