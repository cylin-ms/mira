# Two-Layer Assertion Evaluation Report

> **Generated:** 2025-11-28 15:22:14  
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
| Total Scenarios | 3 |
| Total Plans Evaluated | 9 |
| Total Assertions | 135 |
| Overall Structural Score | 62% |
| Overall Grounding Score | 40% |
| Pass Rate | 33% |

---

## Scenarios

### scenario_001: Q1 Product Launch Readiness Review

**Meeting Details:**
- 📅 **Date:** January 15, 2025
- ⏰ **Time:** 2:00 PM (PST)
- 👤 **Organizer:** Sarah Chen
- 👥 **Attendees:** Sarah Chen, Mike Johnson, Lisa Park, Tom Wilson

**Context:** The team is preparing for a major product launch scheduled for February 1, 2025. 
This meeting is to review all readiness items, identify blockers, and finalize the launch checklist.
Engineering has c...

**Artifacts:** Product_Launch_Checklist_v3.xlsx, Engineering_Status_Report.pdf, Design_Assets_Summary.docx, QA_Test_Results_Dec.pdf

**User Prompt:** _Help me create a workback plan for the upcoming meeting 'Q1 Product Launch Readiness Review'_

---

### scenario_002: Budget Planning FY26 Kickoff

**Meeting Details:**
- 📅 **Date:** December 5, 2024
- ⏰ **Time:** 10:00 AM (EST)
- 👤 **Organizer:** James Miller
- 👥 **Attendees:** James Miller, Emily Davis, Robert Brown, Amanda Lee, Chris Taylor

**Context:** Annual budget planning kickoff for FY26. Finance team needs to consolidate 
departmental requests, review historical spending, and align with strategic priorities.
CFO has requested 5% overall cost re...

**Artifacts:** FY25_Actual_Spending.xlsx, Department_Budget_Requests.xlsx, Strategic_Priorities_FY26.pptx, Cost_Reduction_Guidelines.pdf

**User Prompt:** _Create a workback plan to prepare for the FY26 Budget Planning Kickoff meeting_

---

### scenario_003: Customer Escalation Review - Acme Corp

**Meeting Details:**
- 📅 **Date:** November 20, 2024
- ⏰ **Time:** 3:30 PM (PST)
- 👤 **Organizer:** Jennifer White
- 👥 **Attendees:** Jennifer White, David Kim, Rachel Green, Mark Thompson

**Context:** Critical customer escalation from Acme Corp regarding service outages. 
Customer is threatening contract termination unless issues are resolved.
Three major incidents in the past month need root cause...

**Artifacts:** Acme_Incident_Report_Nov.pdf, Service_Level_Agreement.pdf, System_Architecture_Diagram.png, Previous_Meeting_Notes.docx

**User Prompt:** _Help me prepare a workback plan for the Acme Corp escalation review meeting_

---


---

## Assertions

### scenario_001

**Structural Assertions (S1-S10):** _Check PRESENCE_

| ID | Pattern | Assertion | Level |
|----|---------|-----------|-------|
| A1 | S1 | The workback plan includes explicit meeting details (date, t... | critical |
| A2 | S2 | The workback plan includes a timeline that works back from t... | critical |
| A3 | S3 | The workback plan assigns ownership of each task to a specif... | critical |
| A4 | S4 | The workback plan lists specific artifacts or documents requ... | expected |
| A5 | S5 | The workback plan specifies completion dates for individual ... | critical |
| A6 | S6 | The workback plan identifies any blockers or dependencies th... | expected |
| A7 | S7 | The workback plan links tasks to specific source materials o... | aspirational |
| A8 | S8 | The workback plan specifies communication channels for statu... | expected |
| A9 | S9 | The workback plan demonstrates grounding by including all re... | aspirational |
| A10 | S10 | The workback plan assigns priority levels or importance indi... | aspirational |

**Grounding Assertions (G1-G5):** _Check ACCURACY_

| ID | Pattern | Assertion | Source Field |
|----|---------|-----------|--------------|
| G1 | G1 | All people mentioned in the plan exist in source.attendees | source.attendees |
| G2 | G2 | The meeting date, time, and timezone in the plan match sourc... | source.meeting_date, source.meeting_time, source.timezone |
| G3 | G3 | All artifacts referenced in the plan exist in source.files | source.files |
| G4 | G4 | The topics in the plan align with source.topics | source.topics |
| G5 | G5 | The plan contains no fabricated entities not present in any ... | ALL source fields |

---

### scenario_002

**Structural Assertions (S1-S10):** _Check PRESENCE_

| ID | Pattern | Assertion | Level |
|----|---------|-----------|-------|
| A1 | S1 | The workback plan includes explicit meeting details (date, t... | critical |
| A2 | S2 | The workback plan includes a timeline that works backward fr... | critical |
| A3 | S3 | The workback plan assigns specific owners to each task | critical |
| A4 | S4 | The workback plan lists specific artifacts or documents requ... | expected |
| A5 | S5 | The workback plan specifies completion dates for all tasks | critical |
| A6 | S6 | The workback plan identifies dependencies or potential block... | expected |
| A7 | S7 | The workback plan links tasks to relevant source materials o... | expected |
| A8 | S8 | The workback plan specifies communication channels for updat... | expected |
| A9 | S9 | The workback plan content is grounded in the provided contex... | critical |
| A10 | S10 | The workback plan assigns priority levels or importance indi... | aspirational |

**Grounding Assertions (G1-G5):** _Check ACCURACY_

| ID | Pattern | Assertion | Source Field |
|----|---------|-----------|--------------|
| G1 | G1 | All people mentioned in the plan exist in source.attendees | source.attendees |
| G2 | G2 | The meeting date, time, and timezone in the plan match sourc... | source.meeting_date, source.meeting_time, source.timezone |
| G3 | G3 | All artifacts referenced in the plan exist in source.files | source.files |
| G4 | G4 | The topics or agenda items in the plan align with source.top... | source.topics |
| G5 | G5 | The plan does not introduce any fabricated entities not pres... | ALL source fields |

---

### scenario_003

**Structural Assertions (S1-S10):** _Check PRESENCE_

| ID | Pattern | Assertion | Level |
|----|---------|-----------|-------|
| A1 | S1 | The workback plan includes explicit meeting details (date, t... | critical |
| A2 | S2 | The workback plan includes a timeline that works back from t... | critical |
| A3 | S3 | The workback plan assigns ownership of each task to a specif... | critical |
| A4 | S4 | The workback plan lists specific artifacts or documents requ... | expected |
| A5 | S5 | The workback plan specifies completion dates for each task | critical |
| A6 | S6 | The workback plan identifies potential blockers or dependenc... | expected |
| A7 | S7 | The workback plan links tasks to relevant source materials o... | expected |
| A8 | S8 | The workback plan specifies communication channels for updat... | expected |
| A9 | S9 | The workback plan content is grounded in the provided contex... | aspirational |
| A10 | S10 | The workback plan assigns priority levels or importance indi... | aspirational |

**Grounding Assertions (G1-G5):** _Check ACCURACY_

| ID | Pattern | Assertion | Source Field |
|----|---------|-----------|--------------|
| G1 | G1 | All people mentioned in the plan exist in source.attendees | source.attendees |
| G2 | G2 | Meeting date, time, and timezone in the plan match source.me... | source.meeting_date, source.meeting_time, source.timezone |
| G3 | G3 | All artifacts referenced in the plan exist in source.files | source.files |
| G4 | G4 | Meeting topics in the plan align with source.topics | source.topics |
| G5 | G5 | The plan does not introduce any fabricated entities not pres... | ALL source fields |

---


---

## Plans

### scenario_001

#### 🌟 Perfect Quality Plan

**Intended Scores:** Structural 100%, Grounding 100%

<details>
<summary>📋 View Plan Content</summary>

```
# Q1 Product Launch Readiness Review – Workback Plan

## Meeting Details
- **Title:** Q1 Product Launch Readiness Review
- **Date:** January 15, 2025
- **Time:** 2:00 PM PST
- **Duration:** 90 minutes
- **Organizer:** Sarah Chen
- **Attendees:** Sarah Chen, Mike Johnson, Lisa Park, Tom Wilson

---

## Objective
Prepare for the February 1, 2025 product launch by reviewing readiness items, confirming dependencies, and resolving any blockers.

---

## Timeline & Key Milestones
| Task | Owner | Due Date | Related Artifact | Dependencies |
|------|-------|----------|------------------|-------------|
| Finalize Engineering Features & Sign-off | Mike Johnson | Jan 17, 2025 | Engineering_Status_Report.pdf | Engineering sign-off required before QA final approval |
| Complete QA Testing & Approval | Lisa Park | Jan 24, 2025 | QA_Test_Results_Dec.pdf | Requires Engineering sign-off |
| Finalize Design Assets | Tom Wilson | Jan 20, 2025 | Design_Assets_Summary.docx | Design assets must be finalized before marketing materials |
| Complete Legal Review of TOS | Sarah Chen | Jan 22, 2025 | Product_Launch_Checklist_v3.xlsx | Legal review pending on Terms of Service updates |
| Final Launch Checklist Review | Sarah Chen | Jan 29, 2025 | Product_Launch_Checklist_v3.xlsx | All previous tasks completed |

---

## Artifacts
- Product_Launch_Checklist_v3.xlsx
- Engineering_Status_Report.pdf
- Design_Assets_Summary.docx
- QA_Test_Results_Dec.pdf

---

## Blockers & Risks
- **Engineering sign-off** 
... (truncated)
```

</details>

#### ⚡ Medium Quality Plan

**Intended Scores:** Structural 80%, Grounding 60%
**Deliberate Issues:** Missing priority assignments for tasks, Task assigned to fabricated attendee (Alex Thompson), Reference to non-existent file (Marketing_Brief.pdf)

<details>
<summary>📋 View Plan Content</summary>

```
# Q1 Product Launch Readiness Review - Workback Plan

**Meeting Date:** January 15, 2025  
**Organizer:** Sarah Chen  
**Launch Date:** February 1, 2025  

---

## Objective
Ensure all readiness items for the Q1 product launch are completed, dependencies are managed, and the team is aligned on final deliverables.

---

## Timeline Overview
- **Jan 15, 2025:** Readiness review meeting
- **Jan 18, 2025:** Engineering sign-off (Note: This date is slightly off given dependency timing)
- **Jan 22, 2025:** QA final approval
- **Jan 25, 2025:** Marketing materials finalized
- **Feb 1, 2025:** Product Launch

---

## Key Tasks & Owners

| Task | Owner | Due Date | Notes |
|------|-------|----------|-------|
| Complete Engineering sign-off | Mike Johnson | Jan 18, 2025 | Based on Engineering_Status_Report.pdf |
| Finalize QA testing and approval | Lisa Park | Jan 22, 2025 | QA_Test_Results_Dec.pdf reference |
| Finalize marketing content | Alex Thompson | Jan 25, 2025 | Refer to Marketing_Brief.pdf |
| Complete legal review of ToS | Tom Wilson | Jan 24, 2025 | Dependency: Legal review pending |
| Validate launch checklist | Sarah Chen | Jan 28, 2025 | Use Product_Launch_Checklist_v3.xlsx |

---

## Dependencies
- Engineering sign-off required before QA final approval
- Design assets must be finalized before marketing materials
- Legal review pending on Terms of Service updates

---

## Risks & Mitigation
- **Risk:** QA timeline compressed if engineering slips  
  **Mitigation:** Daily
... (truncated)
```

</details>

#### ⚠️ Low Quality Plan

**Intended Scores:** Structural 40%, Grounding 20%
**Deliberate Issues:** No explicit meeting date/time included, Used generic owners like 'someone', 'the team', 'TBD', Referenced non-existent files: Launch_Overview_Plan.docx, Marketing_Strategy_Q1.pdf

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan for Q1 Launch

## Overview
This plan is for the upcoming review session about launch activities. The team will make sure everything is on track for the big event later this year.

## Objectives
- Go over general progress updates
- Make sure everyone knows what to do next
- Discuss some marketing ideas and maybe future product enhancements

## Action Items
- Someone should review the final integration plan and confirm readiness.
- The team will check the new compliance guidelines and update as needed.
- TBD to consolidate notes from the previous brainstorming session.
- Someone should upload the latest versions of `Launch_Overview_Plan.docx` and `Marketing_Strategy_Q1.pdf`.

## Key People
- Sarah Chen
- Mike Johnson
- Lisa Park
- Tom Wilson
- **Additional attendees:** John Smith, Emily Davis, Robert Brown

## Files to Prepare
- `Launch_Overview_Plan.docx`
- `Marketing_Strategy_Q1.pdf`

## Timeline
- Kickoff alignment: February 10, 2025
- Mid-review checkpoint: February 20, 2025
- Final wrap-up: March 1, 2025

## Notes
We should also consider adding a discussion about expanding into new markets and potential partnerships, as this could influence our roadmap.

```

</details>

---

### scenario_002

#### 🌟 Perfect Quality Plan

**Intended Scores:** Structural 100%, Grounding 100%

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan: FY26 Budget Planning Kickoff

## Meeting Details
- **Title:** Budget Planning FY26 Kickoff
- **Date:** December 5, 2024
- **Time:** 10:00 AM EST
- **Duration:** 120 minutes
- **Organizer:** James Miller
- **Attendees:** James Miller, Emily Davis, Robert Brown, Amanda Lee, Chris Taylor

## Objective
Prepare all necessary materials and inputs to ensure a productive FY26 Budget Planning Kickoff meeting. Align on cost reduction target and strategic priorities.

---

## Timeline & Tasks

### 1. Confirm Strategic Priorities
- **Description:** Ensure the strategic priorities for FY26 are finalized and available.
- **Owner:** Emily Davis
- **Artifact:** Strategic_Priorities_FY26.pptx
- **Due Date:** November 18, 2024
- **Blocker:** Strategic priorities document from CEO required

### 2. Collect Department Budget Requests
- **Description:** Gather all departmental budget requests for FY26.
- **Owner:** Robert Brown
- **Artifact:** Department_Budget_Requests.xlsx
- **Due Date:** November 22, 2024
- **Blocker:** Department heads must submit requests before consolidation

### 3. Compile Historical Spending Data
- **Description:** Prepare FY25 actual spending data for reference.
- **Owner:** Amanda Lee
- **Artifact:** FY25_Actual_Spending.xlsx
- **Due Date:** November 25, 2024
- **Blocker:** None

### 4. Apply Cost Reduction Guidelines
- **Description:** Review and integrate 5% cost reduction target into preliminary analysis.
- **Owner:** Chris Taylor
- **Artifact:** Cost
... (truncated)
```

</details>

#### ⚡ Medium Quality Plan

**Intended Scores:** Structural 80%, Grounding 60%
**Deliberate Issues:** Added fabricated attendee name: Alex Thompson as task owner, Referenced non-existent file: Marketing_Brief.pdf, Introduced a date misalignment: Pre-read materials sharing date (Dec 2) after finalization date (Nov 30) but close to meeting date

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan: FY26 Budget Planning Kickoff

**Meeting Title:** Budget Planning FY26 Kickoff  
**Meeting Date:** December 5, 2024 (Thursday)  
**Meeting Time:** 10:00 AM EST  
**Organizer:** James Miller  

---

## Objective
Prepare all necessary financial data, departmental inputs, and strategic alignment materials to ensure a productive FY26 budget planning kickoff meeting.

---

## Key Milestones
- **Nov 1, 2024**: Gather historical spending data
- **Nov 10, 2024**: Collect departmental budget requests
- **Nov 18, 2024**: Review strategic priorities and cost reduction guidelines
- **Nov 22, 2024**: Consolidate initial budget draft
- **Nov 30, 2024**: Finalize pre-read materials

---

## Tasks & Owners

| Task | Owner | Due Date |
|------|-------|----------|
| Compile FY25 actual spending data from `FY25_Actual_Spending.xlsx` | Emily Davis | Nov 1, 2024 |
| Collect all departmental budget requests from `Department_Budget_Requests.xlsx` | Robert Brown | Nov 10, 2024 |
| Review strategic priorities from `Strategic_Priorities_FY26.pptx` and summarize key points | Amanda Lee | Nov 14, 2024 |
| Align budget targets with 5% cost reduction guidelines (`Cost_Reduction_Guidelines.pdf`) | Chris Taylor | Nov 16, 2024 |
| Draft consolidated budget proposal | Alex Thompson | Nov 22, 2024 |
| Prepare pre-read deck for meeting referencing `Marketing_Brief.pdf` | Emily Davis | Nov 30, 2024 |

---

## Dependencies
- Department heads must submit requests before consolidation
- Strategic pr
... (truncated)
```

</details>

#### ⚠️ Low Quality Plan

**Intended Scores:** Structural 40%, Grounding 20%
**Deliberate Issues:** No explicit meeting date/time included, Generic owners like 'someone' and 'the team', Referenced non-existent files: BudgetOverview_Draft.docx, FinanceSummary2027.xlsx

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan for Budget Planning Meeting

## Overview
The team will need to prepare for the upcoming budget discussion. Someone should gather all necessary materials and ensure everything is ready. The meeting will happen sometime soon, so preparations should start immediately.

## Key Steps
- The team will review last year's performance and some future goals.
- Someone should check the new compliance regulations and marketing trends.
- Prepare the following files: **BudgetOverview_Draft.docx** and **FinanceSummary2027.xlsx**.
- Team should brainstorm ideas for innovation and sustainability.

## Responsibilities
- TBD will collect data from various departments.
- Someone should compile reports into a single document.
- The team will align on overall objectives and vision.

## Timeline
- Start working on this next week.
- Complete all tasks by March 15, 2025.

## Additional Notes
- Include feedback from stakeholders like Sarah Johnson, Michael Smith, and Laura Chen.
- Ensure everyone has access to the files in the shared drive.
- Prepare a summary for leadership review.

```

</details>

---

### scenario_003

#### 🌟 Perfect Quality Plan

**Intended Scores:** Structural 100%, Grounding 100%

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan: Customer Escalation Review - Acme Corp

## Meeting Details
- **Title:** Customer Escalation Review - Acme Corp
- **Date:** November 20, 2024
- **Time:** 3:30 PM PST
- **Duration:** 60 minutes
- **Organizer:** Jennifer White
- **Attendees:** Jennifer White, David Kim, Rachel Green, Mark Thompson

## Objective
Prepare for the critical customer escalation review with Acme Corp to address recent service outages, prevent contract termination, and review root cause analyses for three major incidents in the past month.

---

## Timeline & Tasks

### 1. November 12, 2024 (8 days before meeting)
- **Task:** Request engineering post-mortem reports for the three incidents.
- **Owner:** David Kim
- **Artifact(s):** Acme_Incident_Report_Nov.pdf
- **Dependencies:** Engineering post-mortem reports due before meeting
- **Blockers:** Delay in engineering analysis could impact preparation.

### 2. November 14, 2024 (6 days before meeting)
- **Task:** Account manager to compile and share customer sentiment update.
- **Owner:** Rachel Green
- **Artifact(s):** Previous_Meeting_Notes.docx
- **Dependencies:** Account manager to provide customer sentiment update
- **Blockers:** Lack of timely feedback from customer.

### 3. November 15, 2024 (5 days before meeting)
- **Task:** Legal review of SLA breach implications.
- **Owner:** Mark Thompson
- **Artifact(s):** Service_Level_Agreement.pdf
- **Dependencies:** Legal to review SLA breach implications
- **Blockers:** Legal team availab
... (truncated)
```

</details>

#### ⚡ Medium Quality Plan

**Intended Scores:** Structural 80%, Grounding 60%
**Deliberate Issues:** Assigned task to fabricated attendee 'Alex Thompson' who is not in the attendee list, Referenced non-existent file 'Marketing_Brief.pdf', Included a task on November 21, 2024 (dry run) which is after the meeting date of November 20, 2024

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan: Customer Escalation Review - Acme Corp

**Meeting Date:** November 20, 2024  
**Time:** 3:30 PM PST  
**Organizer:** Jennifer White  
**Attendees:** Jennifer White, David Kim, Rachel Green, Mark Thompson  

---

## Objective
Prepare for the critical Acme Corp escalation review to address recent service outages, analyze root causes, and define next steps to prevent contract termination.

---

## Timeline & Tasks

### November 10, 2024
- **Task:** Draft initial incident summary based on engineering reports.
- **Owner:** David Kim
- **Dependencies:** Engineering post-mortem reports must be available.

### November 13, 2024
- **Task:** Compile customer sentiment update.
- **Owner:** Rachel Green
- **Dependencies:** Account manager feedback.

### November 15, 2024
- **Task:** Legal review of SLA breach implications.
- **Owner:** Mark Thompson
- **Dependencies:** Access to Service_Level_Agreement.pdf.

### November 18, 2024
- **Task:** Prepare consolidated escalation briefing deck.
- **Owner:** Alex Thompson
- **Dependencies:** Incident summary, legal input, customer sentiment.
- **Reference File:** Marketing_Brief.pdf

### November 21, 2024
- **Task:** Final dry run with leadership team.
- **Owner:** Jennifer White
- **Dependencies:** Completed briefing deck.

---

## Deliverables
- Updated incident summary
- Customer sentiment report
- Legal SLA assessment
- Escalation briefing deck

---

## Risks & Mitigation
- **Risk:** Engineering reports delayed.
  - **Mitiga
... (truncated)
```

</details>

#### ⚠️ Low Quality Plan

**Intended Scores:** Structural 40%, Grounding 20%
**Deliberate Issues:** No explicit meeting date/time mentioned in context of the actual meeting, Generic owners like 'someone', 'the team', 'TBD', No specific artifacts from the actual meeting context mentioned

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan for Customer Escalation Review

## Overview
This plan is to prepare for the upcoming discussion about customer engagement and potential marketing strategies. The team will need to ensure all aspects are covered before the session.

## Key Steps
- Someone should review the client happiness metrics and summarize findings.
- The team will gather all relevant documents like Client_Strategy_Doc.pdf and Engagement_Overview.xlsx.
- TBD will prepare the financial forecast for next quarter.
- Someone should check with operations about inventory levels.

## Participants
- Jennifer White
- David Kim
- Rachel Green
- Mark Thompson
- Alex Rivera
- Sophia Chen
- Brian Lopez

## Files to Review
- Client_Strategy_Doc.pdf
- Engagement_Overview.xlsx

## Timeline
- November 15, 2024: Initial brainstorming session
- November 18, 2024: Draft presentation ready
- November 25, 2024: Final review meeting

## Additional Notes
Focus on aligning marketing and sales for better customer satisfaction. Consider adding new product lines to address client concerns.

```

</details>

---


---

## Evaluation Results by Quality Level

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
