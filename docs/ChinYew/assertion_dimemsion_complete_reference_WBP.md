# WBP Dimension Assertion Examples

**Author**: Chin-Yew Lin and Haidong Zhang
**Date**: November 29, 2025  
**Format**: GPT-5 Generated Hybrid Assertions (Template + Instantiated)

This document shows examples of the GPT-5 generated hybrid assertion format used in `dimensions.py`. Each assertion has:
- **template**: Contains `[SLOT_TYPE]` placeholders for generalization
- **instantiated**: Concrete example with actual values from the reference scenario
- **slot_types**: List of slot types used
- **sub_aspect**: Specific aspect being checked
- **linked_g_dims**: G dimensions that apply when evaluating this S assertion

---

## Reference Scenario

The examples below use this reference scenario:
- **Plan Completion Date (T-0)**: April 30, 2025
- **Meeting Date (T-45)**: March 15, 2025, 10:00 AM PST *(45 days before T-0)*
- **Meeting Title**: Q1 Marketing Strategy Review
- **Attendees**: Alice Chen (PM), Bob Smith (Designer), Carol Davis (Engineer), David Lee (Marketing Lead)
- **Artifacts**: Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx
- **Topics**: Q1 priorities, budget allocation, campaign timeline
- **Action Items**: finalize slides, review budget, launch campaign

---

## Structural Dimensions (S1-S20)

### S1: Meeting Details (Weight: 3, Core)
**Definition**: Subject, date, time, timezone, attendee list clearly stated.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S1_A1 | The meeting title must be explicitly stated as [MEETING_TITLE]. | The meeting title must be explicitly stated as Q1 Marketing Strategy Review. | MEETING_TITLE | Meeting title clarity | - |
| S1_A2 | The meeting date must be clearly stated as [MEETING_DATE] at [MEETING_TIME] [TIMEZONE]. | The meeting date must be clearly stated as March 15, 2025 at 10:00 AM PST. | MEETING_DATE, MEETING_TIME, TIMEZONE | Meeting date, time, and timezone specification | G3 |
| S1_A3 | The attendee list must include all required attendees: [ATTENDEE]+. | The attendee list must include all required attendees: Alice Chen (PM), Bob Smith (Designer), Carol Davis (Engineer), David Lee (Marketing Lead). | ATTENDEE | Attendee list completeness and accuracy | G2 |

---

### S2: Timeline Alignment (Weight: 3, Core)
**Definition**: Backward scheduling (T-minus) with dependency-aware sequencing from meeting date.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S2_A1 | All [TASK] entries must be scheduled using T-minus notation relative to [MEETING_DATE]. | All task entries must be scheduled using T-minus notation relative to March 15, 2025. | TASK, MEETING_DATE | T-minus scheduling notation | G3 |
| S2_A2 | Each [TASK] must have a [DUE_DATE] that occurs before [MEETING_DATE]. | Each task such as 'finalize slides' must have a due date that occurs before March 15, 2025. | TASK, DUE_DATE, MEETING_DATE | Task deadline alignment | G3, G6 |
| S2_A3 | Tasks must be ordered by dependency, with prerequisite [TASK] scheduled before dependent [TASK]. | Tasks must be ordered by dependency, with 'finalize slides' scheduled before 'launch campaign'. | TASK | Dependency-aware sequencing | G6 |
| S2_A4 | The timeline must include buffer/contingency time between the last [TASK] and [MEETING_DATE]. | The timeline must include buffer/contingency time between the last task and March 15, 2025. | TASK, MEETING_DATE | Buffer time inclusion | G3, G6 |

---

### S3: Ownership Assignment (Weight: 3, Core)
**Definition**: Named owners per task OR role/skill placeholder if names unavailable.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S3_A1 | Each [TASK] must have a named [OWNER] assigned. | Each task such as 'finalize slides' must have a named owner like Alice Chen assigned. | TASK, OWNER | Owner assignment presence | G2, G6 |
| S3_A2 | If a specific [OWNER] name is unavailable, a role/skill placeholder must be provided for [TASK]. | If a specific owner name is unavailable, a role/skill placeholder like 'Designer' must be provided for 'review slides'. | OWNER, TASK | Role/skill placeholder | G2, G6 |

---

### S4: Deliverables & Artifacts (Weight: 2, Core)
**Definition**: All planned outputs listed with expected location/format; input artifacts must have valid references.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S4_A1 | Every planned [DELIVERABLE] must specify its expected name, format, and storage location. | Every planned deliverable like 'final presentation deck' must specify its expected name (Q1_final_deck.pptx), format (PowerPoint), and storage location (SharePoint/Marketing). | DELIVERABLE | Planned deliverable specification | G4 |
| S4_A2 | Every referenced input [ARTIFACT] must have a valid link or file reference. | Every referenced input artifact must be accessible: Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx. | ARTIFACT | Input artifact validity | G4 |

---

### S5: Task Dates (Weight: 2, Core)
**Definition**: Due dates for every task aligned with S2/S12 sequencing.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S5_A1 | Every [TASK] must have a [DUE_DATE] explicitly specified. | Every task like 'review budget' must have a due date explicitly specified. | TASK, DUE_DATE | Due date presence | G3 |
| S5_A2 | All [DUE_DATE] values must be before or on [MEETING_DATE]. | All due dates must be before or on March 15, 2025. | DUE_DATE, MEETING_DATE | Date consistency | G3 |

---

### S6: Dependencies, Blockers & Mitigation (Weight: 2, Core)
**Definition**: Predecessors identified; blockers documented with mitigations, owners, contingency tasks, and escalation paths.

> **Design Note - Aspirational**: Identifying blockers is **aspirational** - they are elusive and depend on the planner's experience. A WBP without identified blockers is not penalized; however, if blockers ARE identified, each must have a mitigation with an owner. A WBP with well-identified blockers and mitigations is a sign of a high-quality, mature plan.

> **Design Note - Scope**: S6 covers blockers at **both levels**: (1) Task-level blockers that affect a specific task, and (2) Plan-level blockers that affect the overall goal. The same structure applies: `BLOCKER → MITIGATION → OWNER`. This consolidation eliminates the redundant S11 (Risk Mitigation) and S13 (Escalation Protocol) dimensions.

> **Design Note - Escalation**: Escalation is a **type of mitigation** - when a blocker cannot be resolved at the current level, escalating to higher authority IS the mitigation. Escalation protocols are not standard in WBPs (they're usually in risk management docs), so S6_A6 is **aspirational**.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S6_A1 | Each [TASK] with prerequisites must list its dependencies on other [TASK] items. | Each task with prerequisites must list its dependencies, e.g., 'launch campaign' depends on 'finalize slides'. | TASK | Dependency declaration | G6 |
| S6_A2 | Each [TASK] with an identified [BLOCKER] must have a documented [MITIGATION]. | Task 'finalize slides' with blocker 'designer unavailable' must have mitigation 'use backup designer Carol'. | TASK, BLOCKER, MITIGATION | Task-level blocker mitigation | G6, G9 |
| S6_A3 | Each plan-level [BLOCKER] affecting [GOAL] must have a documented [MITIGATION]. | Plan-level blocker 'budget approval delayed' affecting goal 'Launch AI Search Feature' must have mitigation 'request emergency approval from VP'. | BLOCKER, GOAL, MITIGATION | Plan-level blocker mitigation | G7, G9 |
| S6_A4 | Each [MITIGATION] must have an assigned [OWNER]. | Mitigation 'use backup designer Carol' must have an assigned owner like Carol Davis. | MITIGATION, OWNER | Mitigation ownership | G2, G6 |
| S6_A5 | If [MITIGATION] requires action, a contingency [TASK] with [DUE_DATE] must be defined. | If mitigation requires action, a contingency task 'contact backup designer' with due date (April 20, 2025) must be defined. | MITIGATION, TASK, DUE_DATE | Contingency task planning | G3, G6, G9 |
| S6_A6 | If [MITIGATION] requires escalation, an [ESCALATION_CONTACT] and [ESCALATION_TRIGGER] should be defined. | If mitigation requires escalation, contact 'VP Engineering' and trigger 'blocker unresolved for 48 hours' should be defined. | MITIGATION, ESCALATION_CONTACT, ESCALATION_TRIGGER | Escalation path (aspirational) | G2, G9 |

---

### S7: Meeting Outcomes (N/A for WBP)
> **Design Note**: S7 (Meeting Outcomes) is **not applicable** to WBP evaluation. A WBP is the *output* of a planning meeting, not a document that records meeting outcomes. "Meeting outcomes" (decisions made, agreements reached) are *inputs* to creating the WBP, not something the WBP should contain. WBP quality is evaluated by the plan's structure and completeness, not by recording what happened in a meeting.

---

### S8: Parallel Workstreams (Weight: 1, Core)
**Definition**: Concurrent tasks identified with resource allocation.

> **Design Note**: Identifying parallel tasks is **aspirational**. A WBP that explicitly identifies parallel workstreams shows mature planning, but not all plans will have obvious parallelism. S8_A2 (no dependencies between parallel tasks) is particularly hard to verify - it requires proving a negative. A WBP without explicit parallel task identification is not penalized.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S8_A1 | [TASK] items that can run in parallel must be identified with separate [OWNER] assignments. | Parallel tasks 'finalize slides' (Alice) and 'review budget' (Bob) must have separate owners. | TASK, OWNER | Parallel task identification | G2, G6 |
| S8_A2 | If [TASK] items are marked as parallel, they must not have dependencies on each other. | If tasks 'finalize slides' and 'review budget' are marked parallel, they must not depend on each other. | TASK | Parallel task independence (aspirational) | G6 |

---

### S9: Checkpoints (Weight: 2, Core)
**Definition**: Verification points to validate progress before T-0.

> **Design Note**: A "checkpoint" is a **special type of TASK** whose purpose is to verify completion of other tasks. It has the same structure: TASK + DUE_DATE + OWNER. Including explicit checkpoint/verification tasks is **aspirational** - it shows mature planning but is not required. Many simple WBPs rely on implicit verification (deliverable exists = task done). A WBP without explicit checkpoints is not penalized.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S9_A1 | Verification [TASK] items should be included to check progress of dependent [TASK] items before T-0. | Verification task 'Review slides progress' (due April 15) should check progress of 'finalize slides' before T-0 (April 30). | TASK, DATE | Checkpoint task presence (aspirational) | G3, G6 |
| S9_A2 | Each verification [TASK] must have an [OWNER] and [DUE_DATE]. | Verification task 'Review slides progress' must have owner Alice Chen and due date April 15. | TASK, OWNER, DUE_DATE | Checkpoint task specification | G2, G3 |

---

### S10: Resource-Aware Planning (Weight: 2, Core)
**Definition**: Tasks are assigned considering expertise, availability, and resource dependencies.

> **Design Note - Conditional Dimension**: S10 is **conditional on resource constraints being provided** as additional input beyond the basic WBP prompt. A plan can pass all structural checks (S1-S9) yet still be a bad plan if it assigns the wrong person, ignores availability, or misses resource dependencies. From a manager's perspective, a credible WBP must demonstrate awareness of its resources.
>
> **Input Required**: Resource constraints (expertise mapping, availability windows, budget/resource dependencies) must be provided to enable these checks. Without this input, S10 assertions cannot be evaluated.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S10_A1 | [TASK] requiring [SKILL] must be assigned to [OWNER] with that expertise. | Task 'design UI mockups' requiring 'design expertise' must be assigned to Bob Smith (Designer). | TASK, SKILL, OWNER | Right person for the job | G2, G6 |
| S10_A2 | [TASK] assigned to [OWNER] must have [DUE_DATE] outside [OWNER]'s [UNAVAILABLE_PERIOD]. | Task 'finalize slides' assigned to Alice must have due date outside Alice's unavailable period (April 20-25). | TASK, OWNER, DUE_DATE, UNAVAILABLE_PERIOD | Availability respected | G2, G3 |
| S10_A3 | If [TASK] requires [RESOURCE] (e.g., budget, equipment), a prerequisite task for [RESOURCE] approval/acquisition must exist. | If task 'hire vendor' requires 'budget approval', a prerequisite task 'get VP budget approval' must exist. | TASK, RESOURCE | Resource dependency | G4, G6 |
| S10_A4 | [OWNER] with limited capacity should not be assigned [TASK] items exceeding their available bandwidth. | Owner Carol (new hire, 50% capacity) should not be assigned tasks totaling more than 20 hours/week. | OWNER, TASK | Capacity awareness | G2 |

---

### S11: Risk Mitigation Strategy (Merged into S6)
> **Design Note**: S11 (Risk Mitigation Strategy) has been **merged into S6** (Dependencies, Blockers & Mitigation). "Risk" and "Blocker" are synonymous in WBP context - both represent obstacles that may prevent task completion. The consolidated S6 uses a single term `[BLOCKER]` and pattern: `BLOCKER → MITIGATION → OWNER`. See S6_A2 through S6_A5 for all blocker/mitigation assertions.

---

### S12: Communication Plan (Merged into S17)
> **Design Note**: S12 (Communication Plan) has been **merged into S17** (Cross-team Coordination). Communication channel specification is not standard WBP practice - it's typically assumed based on organizational context. However, for cross-team coordination (S17), specifying communication methods becomes relevant when different teams may use different tools. See S17_A3 for the merged assertion.

---

### S13: Escalation Protocol (Merged into S6)
> **Design Note**: S13 (Escalation Protocol) has been **merged into S6** (Dependencies, Blockers & Mitigation). Escalation is a **type of mitigation** - when a blocker cannot be resolved at the current level, escalating to higher authority IS the mitigation strategy. Escalation protocols are not standard in WBPs (they're typically in risk management or governance documents), so this is **aspirational**. See S6_A6 for the merged assertion.
>
> **Definitions:**
> - **Escalation**: Raising a blocker to someone with more authority/resources when it can't be resolved at the task owner level
> - **Escalation Contact**: WHO to escalate to (manager, VP, specialist)
> - **Escalation Trigger**: WHEN to escalate - a condition like "blocker unresolved for 48 hours" or "blocker affects critical path"

---

### S14: Feedback Integration (N/A for WBP)
> **Design Note**: S14 (Feedback Integration) is **not applicable** to WBP evaluation. WBPs are typically static reference plans once approved; continuous feedback loops and iteration are more common in agile/adaptive planning, not classic WBPs. The assertions ("feedback loops tied to TOPIC", "feedback collection method") are vague, operational, and hard to verify objectively. The concept overlaps with S9 (Checkpoints) - if feedback is needed, it would happen at checkpoint verification tasks. Keeping S14 would dilute the framework with execution governance rather than plan structure.

---

### S15: Progress Tracking (Weight: 2, Extended) — N/A
**Definition**: Metrics and methods for tracking task completion.

> **Design Note**: S15 (Progress Tracking) is **not applicable** to WBP evaluation. Progress tracking is an **execution/operational** concern, not a planning artifact quality indicator. When we evaluate a WBP, we check whether it has the structural elements needed for tracking (STATUS column - already verified by S20), not whether tracking is being performed correctly. S15_A1 ("track completion of each task") is implicit/obvious - any plan with tasks implies tracking them. S15_A2 ("define progress indicators") describes values filled during execution, not planning. The structural requirement (having a STATUS column) is already covered by S20_A1.

---

### S16: Assumptions & Prerequisites (Weight: 2, Extended)
**Definition**: Stated assumptions and conditions that must be true for the plan to succeed.

> **Design Note - Aspirational**: Documenting assumptions is **aspirational** - it depends on planner experience and foresight. A WBP without an explicit assumptions section is not penalized. However, if assumptions ARE documented, they should specify what happens if invalidated. A WBP with well-documented assumptions is a sign of a mature, risk-aware plan.

> **Design Note - Assumption vs Blocker**: An [ASSUMPTION] is a condition believed TRUE at planning time (future uncertainty). A [BLOCKER] is a known obstacle NOW. If an assumption is later invalidated, it becomes a blocker (handled by S6). Assumptions capture planner foresight about underlying conditions; blockers capture current impediments.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S16_A1 | Each [ASSUMPTION] must be explicitly stated and relate to [TOPIC] or [TASK] prerequisites. | Assumption 'budget will be approved by April 10' must be explicitly stated as a prerequisite for task 'launch campaign'. | ASSUMPTION, TOPIC, TASK | Assumption documentation | G5, G6, G9 |
| S16_A2 | Each [ASSUMPTION] should state its impact if invalidated. | Assumption 'budget approved by April 10' should state impact: 'if not approved, campaign launch delayed 2 weeks'. | ASSUMPTION | Impact assessment (aspirational) | G9 |

---

### S17: Cross-team Coordination (Weight: 1, Extended) — CONDITIONAL
**Definition**: If the scenario involves multiple teams, the WBP should clearly represent cross-team dependencies and responsibilities.

> **Design Note - Conditional Dimension**: S17 is **conditional on the scenario specifying cross-team dependencies**. Without scenario input identifying which tasks involve external teams, we cannot evaluate cross-team coordination. This is similar to S10 (Resource-Aware Planning) which requires resource constraints to be provided.
>
> **What qualifies as cross-team?** A task is cross-team if it requires input from, handoff to, or collaboration with people/teams NOT in the primary attendee list. The scenario must explicitly identify these dependencies.
>
> **Removed**: S17_A3 (communication method specification) was removed as it is **operational** - how teams communicate is an execution detail, not a planning structure element.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S17_A1 | For each cross-team dependency, the external team and contact [ATTENDEE] must be identified. | Cross-team dependency on 'Legal team' must identify contact 'Carol Davis (Engineer)' as liaison. | ATTENDEE | Cross-team contact | G2 |
| S17_A2 | For each cross-team [TASK], handoff or dependency [DATE] must be specified. | Cross-team task 'legal review' must have explicit handoff date (April 18, 2025). | TASK, DATE | Handoff date specification | G3, G6 |

---

### S18: Post-Event Actions (Weight: 1, Extended) — ASPIRATIONAL
**Definition**: Post-T-0 tasks planned beyond the completion date (e.g., retrospectives, lessons learned, project closure activities).

> **Design Note - Aspirational**: Post-T-0 tasks are **outside the core WBP scope** - a WBP works backward FROM T-0 to the present, focusing on tasks that lead to completion. However, including post-T-0 tasks (retrospectives, post-mortems, lessons learned) signals **mature, end-to-end lifecycle planning**. A WBP without post-T-0 tasks is not penalized; a WBP with them demonstrates advanced planning maturity.
>
> **Relationship to G4_A4**: G4_A4 already handles post-T-0 artifact verification ("Post-mortem ARTIFACT existence verified after T-0"). S18 focuses on the structural presence of post-T-0 TASKS in the plan.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S18_A1 | Post-T-0 [TASK] items (e.g., retrospective, lessons learned) must have assigned [OWNER] and [DUE_DATE]. | Post-T-0 task 'conduct retrospective' must have assigned owner Alice Chen and due date May 7, 2025 (after T-0 April 30). | TASK, OWNER, DUE_DATE | Post-T-0 task specification (aspirational) | G2, G3 |
| S18_A2 | Post-T-0 [TASK] items should be traceable to project closure best practices. | Post-T-0 task 'document lessons learned' should be traceable to project closure activities. | TASK | Post-T-0 traceability (aspirational) | G6 |

---

### S19: Open Questions & Decision Points (Weight: 2, Extended) — ASPIRATIONAL
**Definition**: Known unknowns identified by analyzing plan data that need resolution for plan success.

> **Design Note - Aspirational**: Identifying open questions is **aspirational** - it requires sophisticated analysis of available data to discover gaps in knowledge that could affect plan success. A basic WBP without open questions is not penalized. However, a WBP that identifies open questions and assigns owners to resolve them demonstrates **advanced planning intelligence**.
>
> **Open Question vs Assumption**:
> - **Assumption** = condition believed TRUE at planning time (e.g., "Budget will be approved by April 10")
> - **Open Question** = known UNKNOWN that needs an answer (e.g., "Who has final approval authority for budgets over $50K?")
>
> **What makes a great WBP agent?** A sophisticated WBP agent analyzes all available data, thinks through dependencies and risks, and proactively identifies questions that must be answered for the plan to succeed. Examples:
> - "Who has final approval authority for the budget?" (discovered by analyzing approval chain)
> - "Is the design tool license renewed for Q2?" (discovered by analyzing resource dependencies)
> - "What's the fallback if the vendor doesn't deliver by April 15?" (discovered by analyzing critical path)
> - "Does Legal need 2 weeks or 4 weeks for contract review?" (discovered by analyzing timeline gaps)
>
> **Note**: S19_A1 from the original definition (assumptions with impact) is redundant with S16 and has been removed. S19 now focuses solely on open questions.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S19_A1 | Each [OPEN_QUESTION] must be explicitly documented with context explaining why it matters for plan success. | Open question 'Who approves budgets over $50K?' must be documented with context: 'needed to determine approval timeline for vendor contract'. | OPEN_QUESTION | Open question documentation (aspirational) | G9 |
| S19_A2 | Each [OPEN_QUESTION] must have a designated [OWNER] responsible for finding the answer. | Open question 'Does Legal need 2 or 4 weeks for review?' must have owner David Lee responsible for getting the answer. | OPEN_QUESTION, OWNER | Question ownership (aspirational) | G2, G9 |
| S19_A3 | Each [OPEN_QUESTION] should have a resolution [DUE_DATE] aligned with dependent [TASK] timelines. | Open question about Legal review timeline should have resolution date before task 'submit contract' begins. | OPEN_QUESTION, DUE_DATE, TASK | Resolution timeline (aspirational) | G3, G6 |

---

### S20: Clarity & First Impression (Weight: 2, Core) — REQUIRED
**Definition**: UX-focused presentation for instant recognition and intuitive interaction.

> **Design Note - Required**: Clarity is **foundational** for WBP usability. Without clear presentation, even correct content is hard to consume. S20 assertions are split into **Required** (core clarity) and **Aspirational** (enhanced polish).
>
> **Required assertions** (A1, A2, A4, A5, A6, A7, A9): Must be met for basic WBP clarity.
> **Aspirational assertions** (A3, A8): Nice-to-have improvements, not penalized if missing.

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S20_A1 | The WBP must contain a [HEADER_ROW] with columns: Task, Owner, Deadline, Status. | The WBP must contain a header row with columns: Task, Owner, Deadline, Status. | HEADER_ROW | Required columns | - |
| S20_A2 | The first 3 lines must include a [GOAL_STATEMENT] summarizing the plan objective. | The first 3 lines must include a goal statement like "Prepare for Q1 Marketing Strategy Review". | GOAL_STATEMENT | Goal statement presence | G5, G7 |
| S20_A3 | Each [TASK] description should be concise (ideally ≤12 words) for scannability. | Each task description like "Finalize Q1 slides" should be concise for quick scanning. | TASK | Task conciseness (aspirational) | - |
| S20_A4 | All [DATE] values must use a consistent and unambiguous format (YYYY-MM-DD recommended). | All dates must use consistent format like 2025-03-15 or "March 15, 2025" throughout. | DATE | Date format consistency | G3 |
| S20_A5 | [TASK] items must be in a clear, logical order (chronological by [DUE_DATE], or grouped by workstream/owner). | Tasks must be in logical order - chronological by due date, or clearly grouped by workstream. | TASK, DUE_DATE | Logical ordering | G3 |
| S20_A6 | No required cell (Task, Owner, Deadline, Status) may be empty. | No required cell in the WBP table may be empty. | - | Cell completeness | - |
| S20_A7 | [OWNER] names must be spelled consistently throughout the WBP. | Owner names like "Alice Chen" must be spelled consistently throughout. | OWNER | Owner spelling consistency | G2 |
| S20_A8 | If non-standard [STATUS] values are used, a legend should be present. | If non-standard status values like "Blocked" are used, a legend should be present. | STATUS | Status legend (aspirational) | - |
| S20_A9 | The WBP should include a title and version/date for context. | The WBP should include title "Q1 Marketing Campaign WBP" and version "v1.0 - March 10, 2025". | - | Title and version (aspirational) | - |

---

## Grounding Dimensions (G1-G9)

> **Grounding Design Principle**: Grounding prevents HALLUCINATION (inventing false facts about the scenario). However, planners adding reasonable blockers, assumptions, or mitigations is GOOD PLANNING, not hallucination. We distinguish:
> - **Hallucination (BAD)**: Inventing attendees, dates, artifacts not in scenario
> - **Good Planning (GOOD)**: Identifying reasonable blockers, assumptions, mitigations that don't contradict scenario
>
> Slot types are classified as:
> - **GROUNDED**: Must come from scenario (hard requirement)
> - **DERIVED**: Can be inferred from scenario context
> - **PLANNER-GENERATED**: Planner can create reasonable values (checked by G9 for consistency)
> - **CONDITIONAL**: Only grounded if scenario provides the information

### G1: Hallucination Check (Weight: 3)
**Definition**: Entities (people, dates, artifacts) must not be fabricated.
**Verification**: Compare all entities against scenario ground truth.

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G1_A1 | No [ENTITY] should appear in the WBP that is not present in the scenario. | No entity should appear in the WBP that is not present in the scenario (e.g., no invented attendees or artifacts). | ENTITY | Entity existence check |
| G1_A2 | Every [ATTENDEE] mentioned must match a name from the scenario attendee list. | Every attendee mentioned must match a name from: Alice Chen, Bob Smith, Carol Davis, David Lee. | ATTENDEE | Attendee verification |
| G1_A3 | Every [ARTIFACT] mentioned must match a file from the scenario artifact list. | Every artifact mentioned must match a file from: Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx. | ARTIFACT | Artifact verification |

---

### G2: Attendee Grounding (Weight: 2)
**Definition**: All attendee names must match scenario's attendee list exactly; skills must be derivable from attendee roles.
**Verification**: Check all names against scenario.attendees; verify skills align with roles.
**Extended for**: OWNER (grounded), ESCALATION_CONTACT (conditional), SKILL (derived)

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G2_A1 | All task owners [OWNER] in the WBP must be from the attendee list: [ATTENDEE]+. | All task owners in the WBP must be from the attendee list: Alice Chen, Bob Smith, Carol Davis, David Lee. | OWNER, ATTENDEE | Owner verification |
| G2_A2 | No [OWNER] in the WBP may be a name not present in the scenario attendees. | No owner in the WBP may be a name not present in the scenario attendees. | OWNER | No fabricated owners |
| G2_A3 | If scenario specifies [ESCALATION_CONTACT], WBP must use that contact; otherwise, contact should be from attendee list or reasonable organizational role. | If scenario specifies escalation contact 'VP Engineering', WBP must use that; otherwise, escalation contact like 'Alice Chen (PM)' should be from attendee list. | ESCALATION_CONTACT | Escalation contact (conditional) |
| G2_A4 | [SKILL] requirements must be derivable from scenario attendee roles or task context. | Skill 'design expertise' must be derivable from attendee role 'Bob Smith (Designer)' or task 'finalize slides'. | SKILL | Skill derivation (derived) |

---

### G3: Date/Time Grounding (Weight: 2)
**Definition**: All dates/times must be consistent with scenario's meeting date and timeline.
**Verification**: Check dates against scenario.date; verify unavailability periods if provided.
**Extended for**: DUE_DATE, DATE (grounded), UNAVAILABLE_PERIOD (conditional)

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G3_A1 | All [DUE_DATE] values must be on or before [MEETING_DATE]. | All due dates must be on or before March 15, 2025. | DUE_DATE, MEETING_DATE | Pre-meeting date check |
| G3_A2 | Any post-meeting [DATE] must be after [MEETING_DATE]. | Any post-meeting date must be after March 15, 2025. | DATE, MEETING_DATE | Post-meeting date check |
| G3_A3 | No [DATE] in the WBP may be unrealistic given the scenario timeframe. | No date in the WBP may be unrealistic given the scenario timeframe around March 2025. | DATE | Date realism |
| G3_A4 | If scenario specifies [UNAVAILABLE_PERIOD] for an [OWNER], WBP must respect it; otherwise, planner-added unavailability must be realistic. | If scenario specifies 'Bob Smith unavailable April 20-25', WBP must not assign tasks to Bob during that period. | UNAVAILABLE_PERIOD, OWNER | Unavailability period (conditional) |

---

### G4: Artifact Grounding (Weight: 2)
**Definition**: Input artifacts must exist and be accessible; planned deliverables must have complete specifications; resources must match scenario if provided.
**Verification**: 
- **Input Artifacts**: Check file references against scenario.artifacts (must exist NOW)
- **Planned Deliverables**: Verify specification completeness (name, format, location); verify existence at producing task's due date
- **Post-Mortem Artifacts**: Verify specification; existence verified after T-0
- **Resources**: If scenario mentions specific resources, must match; otherwise planner can add reasonable ones
- **Note**: Task due date constraints (before T-0) are enforced by G3 (Temporal Grounding)
**Extended for**: ARTIFACT (grounded), DELIVERABLE (grounded), RESOURCE (conditional)

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G4_A1 | Every input [ARTIFACT] referenced in the WBP must exist in the scenario artifacts list. | Every input artifact referenced in the WBP must exist in: Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx. | ARTIFACT | Input artifact existence |
| G4_A2 | Every planned [DELIVERABLE] must have a verifiable specification: name, format, and storage location. | Every planned deliverable like 'Q1_final_deck.pptx (PowerPoint, SharePoint/Marketing)' must have a verifiable specification. | DELIVERABLE | Planned deliverable specification completeness |
| G4_A3 | Planned [DELIVERABLE] existence is verified at the [DUE_DATE] of the [TASK] that produces it. | Planned deliverable 'Q1_final_deck.pptx' existence is verified at the due date of task 'finalize slides' (April 25, 2025). | DELIVERABLE, TASK, DUE_DATE | Deliverable-task linkage verification |
| G4_A4 | Post-mortem [ARTIFACT] (e.g., retrospective, lessons learned) existence is verified after T-0. | Post-mortem artifact 'Project_Retrospective.docx' existence is verified after T-0 (April 30, 2025). | ARTIFACT | Post-T-0 artifact verification |
| G4_A5 | If scenario specifies [RESOURCE] requirements, WBP must include them; otherwise, planner-added resources must be reasonable for the tasks. | If scenario specifies 'budget approval required', WBP must include it; planner can add reasonable resources like 'server access' for deployment tasks. | RESOURCE | Resource grounding (conditional) |

---

### G5: Topic Grounding (Weight: 2)
**Definition**: All topics/agenda items must align with scenario's discussion_points.
**Verification**: Check topics against scenario.discussion_points.

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G5_A1 | Each agenda topic [TOPIC] in the work-back plan must exist in the scenario discussion points. | Each agenda topic (e.g., Q1 priorities, budget allocation, campaign timeline) must exist in the scenario discussion points. | TOPIC | Topic alignment |
| G5_A2 | No agenda topic [TOPIC] should introduce content not present in the scenario. | No agenda topic (e.g., introducing new product launch) should introduce content not present in the scenario. | TOPIC | No hallucinated topics |

---

### G6: Action Item Grounding (Weight: 2)
**Definition**: All action items must be traceable to scenario's action_items_discussed.
**Verification**: Compare action items against scenario.action_items_discussed.

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G6_A1 | Every [TASK] in the work-back plan must correspond to an [ACTION_ITEM] from the scenario. | Every task must correspond to an action item from: finalize slides, review budget, launch campaign. | TASK, ACTION_ITEM | Task-to-action-item traceability |
| G6_A2 | The work-back plan must include a corresponding [TASK] for each scenario [ACTION_ITEM]. | The work-back plan must include a corresponding task for each action item: finalize slides, review budget, launch campaign. | ACTION_ITEM, TASK | Action item coverage completeness |

---

### G7: Context Preservation (Weight: 2)
**Definition**: Original context, constraints, and objectives from scenario are maintained.
**Verification**: Verify WBP preserves scenario.context meaning; verify goal aligns with scenario purpose.
**Extended for**: MEETING_DATE, ATTENDEE, ARTIFACT (grounded), GOAL (conditional)

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G7_A1 | The Work-Back Plan includes the original meeting date [MEETING_DATE] without modification. | The Work-Back Plan includes the original meeting date March 15, 2025 without modification. | MEETING_DATE | Meeting date preservation |
| G7_A2 | The Work-Back Plan includes only attendees from the original scenario: [ATTENDEE]+. | The Work-Back Plan includes only attendees from the original scenario: Alice Chen, Bob Smith, Carol Davis, David Lee. | ATTENDEE | Attendee list preservation |
| G7_A3 | The Work-Back Plan references only original scenario artifacts: [ARTIFACT]+. | The Work-Back Plan references only original scenario artifacts: Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx. | ARTIFACT | Artifact reference preservation |
| G7_A4 | If scenario states a [GOAL], WBP must align with it; otherwise, planner-defined goal must be consistent with scenario context. | If scenario states goal 'Launch Q1 Marketing Campaign', WBP goal must align; if not stated, planner goal 'Complete Q1 Marketing Preparation' must be consistent with scenario context. | GOAL | Goal alignment (conditional) |

---

### G8: Instruction Adherence (Weight: 2)
**Definition**: Any specific instructions from the meeting are followed.
**Verification**: Check compliance with any instructions in scenario.

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G8_A1 | The WBP includes a task for each [ACTION_ITEM] mentioned in the scenario instructions. | The WBP includes a task for each action item: finalize slides, review budget, launch campaign. | ACTION_ITEM | Instruction coverage |
| G8_A2 | Each task for an [ACTION_ITEM] is assigned to an [ATTENDEE] from the scenario. | Each task for an action item like review budget is assigned to an attendee from the scenario. | ACTION_ITEM, ATTENDEE | Instruction-task-owner alignment |
| G8_A3 | The WBP references each [ARTIFACT] mentioned in the scenario instructions. | The WBP references each artifact: Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx mentioned in the scenario. | ARTIFACT | Artifact instruction adherence |

---

### G9: Consistency Check for Planner-Generated Elements (Weight: 2)
**Definition**: Planner-generated elements (assumptions, blockers, mitigations, open questions) must not contradict scenario facts.
**Verification**: Check that planner-added content is consistent with scenario; allows creative planning but prevents contradictions.
**Purpose**: Enables GOOD PLANNING (identifying reasonable risks/assumptions/questions) while preventing HALLUCINATION (contradicting scenario facts).
**Applies to**: ASSUMPTION, BLOCKER, MITIGATION, OPEN_QUESTION, ESCALATION_TRIGGER (all planner-generated)

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G9_A1 | No [ASSUMPTION] may contradict facts stated in the scenario. | Assumption 'budget will be approved by April 10' must not contradict scenario (e.g., if scenario says 'budget already rejected'). | ASSUMPTION | Assumption consistency |
| G9_A2 | No [BLOCKER] may contradict facts stated in the scenario. | Blocker 'designer unavailable' must not contradict scenario (e.g., if scenario says 'Bob Smith (Designer) confirmed available'). | BLOCKER | Blocker consistency |
| G9_A3 | [MITIGATION] must be logically related to its [BLOCKER] and not contradict scenario constraints. | Mitigation 'use backup designer Carol' must be logically related to blocker 'designer unavailable' and Carol must be in attendee list. | MITIGATION, BLOCKER | Mitigation consistency |
| G9_A4 | Planner-generated [ASSUMPTION], [BLOCKER], and [MITIGATION] should be plausible given scenario context. | Assumption 'legal review will pass' is plausible if scenario mentions legal tasks; blocker 'server outage' is implausible if scenario is about marketing slides. | ASSUMPTION, BLOCKER, MITIGATION | Contextual plausibility |
| G9_A5 | [OPEN_QUESTION] must be relevant to plan success and not contradict known scenario facts. | Open question 'Who approves budgets over $50K?' is relevant if scenario mentions budget approval; question 'What color should the logo be?' is irrelevant if scenario is about budget planning. | OPEN_QUESTION | Open question relevance |
| G9_A6 | [OPEN_QUESTION] should identify genuine gaps in knowledge, not ask about information already provided in the scenario. | Open question 'Who is the project manager?' is invalid if scenario already states 'Alice Chen (PM)'. | OPEN_QUESTION | No redundant questions |

---

## Key Insight: Artifact Verification Timeline

In a Work-Back Plan (WBP), artifacts have different verification timelines based on when they exist:

### Timeline Context
- **T-45 (or T-30)**: Planning meeting date - when the WBP is created
- **T-0**: Plan completion date - when all work should be done

### Artifact Types and Verification

| Artifact Type | When It Exists | When Verified | Example |
|--------------|----------------|---------------|---------|
| **Input Artifact** | Already exists at T-45 | Immediately (link must work) | `budget_2025.xlsx` |
| **Planned Deliverable** | Before T-0 (at task due date) | At producing task's due date | `Q1_final_deck.pptx` |
| **Post-Mortem Artifact** | After T-0 | After T-0 | `Project_Retrospective.docx` |

### Key Constraints

1. **Planned Deliverables are linked to Tasks**: Each deliverable is produced by a specific task. The deliverable's verification date = the task's due date.

2. **Task due dates must be before T-0**: This constraint is enforced by **G3 (Temporal Grounding)**, not G4. G4 focuses on artifact specification and existence.

3. **At planning time (T-45), we can only verify**:
   - Input artifacts exist and are accessible
   - Planned deliverables have complete specifications (name, format, location)
   - Post-mortem artifacts have specifications

---

## Key Insight: G Dimension Interdependencies

The G (Grounding) dimensions work together with clear separation of concerns:

```
+------------------+----------------------------------------+-----------------------------+
| G Dimension      | What It Checks                         | Depends On                  |
+------------------+----------------------------------------+-----------------------------+
| G2 (Entity)      | Names exist in scenario                | -                           |
| G3 (Temporal)    | Dates are valid, due dates < T-0       | -                           |
| G4 (Artifact)    | Files exist or have specifications     | G3 (for task due dates)     |
| G5 (Topic)       | Topics match scenario                  | -                           |
| G6 (Logical)     | Relationships are coherent             | G2, G3, G4 (entities exist) |
| G7 (Context)     | Original context preserved             | G2, G4, G5                  |
| G8 (Instruction) | Instructions followed                  | G2, G4, G6                  |
+------------------+----------------------------------------+-----------------------------+
```

### Example: Verifying a Task-Deliverable Relationship

When checking: *"Task 'finalize slides' produces deliverable 'Q1_final_deck.pptx' due April 25, 2025"*

| Check | G Dimension | Question |
|-------|-------------|----------|
| 1 | G2 | Is 'finalize slides' a valid task from the scenario? |
| 2 | G3 | Is April 25, 2025 a valid date before T-0 (April 30, 2025)? |
| 3 | G4 | Does 'Q1_final_deck.pptx' have a complete specification? |
| 4 | G6 | Is it logically coherent that this task produces this deliverable? |

---

## Key Concept: S→G Linkage

**G assertions are NEVER standalone** - they are instantiated through S assertions via the `linked_g_dims` field.

Example: When evaluating S3_A1 (ownership assignment):
- **S Assertion**: "Each task such as 'finalize slides' must have a named owner like Alice Chen assigned."
- **Linked G dims**: G2, G6
- **G2 check**: Is "Alice Chen" in the attendee list?
- **G6 check**: Is "finalize slides" in the action items?

This linkage ensures both structural completeness AND factual accuracy are verified together.

---

## Slot Types Reference

| Slot Type | Description | Example Values | Grounding | G Dim |
|-----------|-------------|----------------|-----------|-------|
| [MEETING_TITLE] | Title of the meeting | Q1 Marketing Strategy Review | GROUNDED | G7 |
| [MEETING_DATE] | Date of the meeting | March 15, 2025 | GROUNDED | G3, G7 |
| [MEETING_TIME] | Time of the meeting | 10:00 AM | GROUNDED | G3 |
| [TIMEZONE] | Timezone for the meeting | PST, EST, UTC | GROUNDED | G3 |
| [DATE] | Any date reference | 2025-03-10 | GROUNDED | G3 |
| [DUE_DATE] | Task deadline | March 12, 2025 | GROUNDED | G3 |
| [ATTENDEE] | Person from attendee list | Alice Chen, Bob Smith | GROUNDED | G1, G2 |
| [OWNER] | Task owner (subset of attendees) | Alice Chen | GROUNDED | G2 |
| [TASK] | A work item | finalize slides | GROUNDED | G6 |
| [ACTION_ITEM] | Discussed action from meeting | review budget | GROUNDED | G6, G8 |
| [ARTIFACT] | File or document (input, exists now) | Q1_slides.pptx | GROUNDED | G1, G4 |
| [DELIVERABLE] | Planned output of a task (future) | Q1_final_deck.pptx | GROUNDED | G4 |
| [TOPIC] | Discussion topic | budget allocation | GROUNDED | G5 |
| [ENTITY] | Any named element | person, file, date | GROUNDED | G1 |
| [GOAL] | The plan's objective/target outcome | Launch AI Search Feature | CONDITIONAL | G7 |
| [GOAL_STATEMENT] | Meeting objective summary | Prepare for Q1 review | DERIVED | G5, G7 |
| [STATUS] | Task status value | Done, In Progress, Blocked | N/A | - |
| [HEADER_ROW] | Table column headers | Task, Owner, Deadline, Status | N/A | - |
| [ASSUMPTION] | Condition believed true at planning time | budget approved by April 10 | PLANNER-GEN | G9 |
| [BLOCKER] | Obstacle (task-level or plan-level) | designer unavailable | PLANNER-GEN | G9 |
| [MITIGATION] | Action/plan to address a blocker | use backup designer | PLANNER-GEN | G9 |
| [ESCALATION_CONTACT] | Person with authority for escalation | VP Engineering | CONDITIONAL | G2 |
| [ESCALATION_TRIGGER] | Condition that initiates escalation | blocker unresolved 48h | PLANNER-GEN | G9 |
| [SKILL] | Expertise/capability required for a task | design expertise | DERIVED | G2 |
| [RESOURCE] | Non-people resource (budget, equipment) | budget approval, server access | CONDITIONAL | G4 |
| [UNAVAILABLE_PERIOD] | Time window when OWNER unavailable | April 20-25 | CONDITIONAL | G3 |
| [OPEN_QUESTION] | Known unknown identified by analyzing plan data; needs answer for plan success | Who approves budgets over $50K? Does Legal need 2 or 4 weeks? | PLANNER-GEN | G9 |

**Grounding Legend:**
- **GROUNDED**: Must come from scenario (hard requirement, penalized if violated)
- **DERIVED**: Can be reasonably inferred from scenario context
- **CONDITIONAL**: Only grounded if scenario provides the information
- **PLANNER-GEN**: Planner can create reasonable values (checked by G9 for consistency, not grounded)
- **N/A**: Structural element, no grounding needed
