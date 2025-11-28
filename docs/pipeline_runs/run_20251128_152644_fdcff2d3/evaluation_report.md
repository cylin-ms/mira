# Two-Layer Assertion Evaluation Report

> **Generated:** 2025-11-28 15:33:18  
> **Framework:** Two-Layer Assertion Framework v2.0 (Structural S1-S10 + Grounding G1-G5)

---

## Executive Summary

This report evaluates **9 workback plans** across three quality levels using the Two-Layer Assertion Framework.

**Perfect Quality Plans:** Achieved 77% structural and 87% grounding scores, approaching expected targets.
**Medium Quality Plans:** Achieved 63% structural and 40% grounding scores, demonstrating deliberate quality degradation.
**Low Quality Plans:** Achieved 33% structural and 0% grounding scores, confirming detection of poor quality.

**Overall:** The framework correctly differentiated quality levels, with 2 plans passing and 7 failing as expected.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Scenarios | 3 |
| Total Plans Evaluated | 9 |
| Total Assertions | 135 |
| Overall Structural Score | 58% |
| Overall Grounding Score | 42% |
| Pass Rate | 22% |

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
| A3 | S3 | The workback plan assigns a specific named owner for each ta... | critical |
| A4 | S4 | The workback plan lists specific artifacts or documents to b... | expected |
| A5 | S5 | The workback plan specifies completion dates for each task | critical |
| A6 | S6 | The workback plan identifies any blockers or dependencies th... | expected |
| A7 | S7 | The workback plan links tasks to specific source materials o... | expected |
| A8 | S8 | The workback plan specifies communication channels for updat... | expected |
| A9 | S9 | The workback plan is grounded in the provided context and pa... | aspirational |
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

### scenario_002

**Structural Assertions (S1-S10):** _Check PRESENCE_

| ID | Pattern | Assertion | Level |
|----|---------|-----------|-------|
| A1 | S1 | The workback plan includes explicit meeting details (date, t... | critical |
| A2 | S2 | The workback plan includes a timeline that works back from t... | critical |
| A3 | S3 | The workback plan assigns ownership of each task to a specif... | critical |
| A4 | S4 | The workback plan lists specific artifacts or documents requ... | expected |
| A5 | S5 | The workback plan specifies completion dates for each task | critical |
| A6 | S6 | The workback plan identifies dependencies or potential block... | expected |
| A7 | S7 | The workback plan links tasks to specific source materials o... | expected |
| A8 | S8 | The workback plan specifies communication channels for updat... | expected |
| A9 | S9 | The workback plan includes grounding elements that align wit... | aspirational |
| A10 | S10 | The workback plan assigns priority levels or importance indi... | aspirational |

**Grounding Assertions (G1-G5):** _Check ACCURACY_

| ID | Pattern | Assertion | Source Field |
|----|---------|-----------|--------------|
| G1 | G1 | All people mentioned in the plan exist in source.attendees | source.attendees |
| G2 | G2 | The meeting date, time, and timezone in the plan match sourc... | source.meeting_date, source.meeting_time, source.timezone |
| G3 | G3 | All artifacts referenced in the plan exist in source.files | source.files |
| G4 | G4 | The topics or meeting purpose in the plan align with source.... | source.topics |
| G5 | G5 | The plan does not introduce any people, files, dates, or top... | ALL source fields |

---

### scenario_003

**Structural Assertions (S1-S10):** _Check PRESENCE_

| ID | Pattern | Assertion | Level |
|----|---------|-----------|-------|
| A1 | S1 | The workback plan includes explicit meeting details (date, t... | critical |
| A2 | S2 | The workback plan includes a timeline that works back from t... | critical |
| A3 | S3 | The workback plan assigns ownership of each task to specific... | critical |
| A4 | S4 | The workback plan lists specific artifacts or documents requ... | expected |
| A5 | S5 | The workback plan specifies due dates for each task | critical |
| A6 | S6 | The workback plan identifies any dependencies or potential b... | expected |
| A7 | S7 | The workback plan links tasks to their relevant source mater... | expected |
| A8 | S8 | The workback plan specifies communication channels for updat... | expected |
| A9 | S9 | The workback plan demonstrates grounding by including all re... | aspirational |
| A10 | S10 | The workback plan assigns priority levels or importance indi... | aspirational |

**Grounding Assertions (G1-G5):** _Check ACCURACY_

| ID | Pattern | Assertion | Source Field |
|----|---------|-----------|--------------|
| G1 | G1 | All people mentioned in the plan exist in source.attendees | source.attendees |
| G2 | G2 | Meeting date, time, and timezone in the plan match source.me... | source.meeting_date, source.meeting_time, source.timezone |
| G3 | G3 | All artifacts referenced in the plan exist in source.files | source.files |
| G4 | G4 | The topics or agenda items in the plan align with source.top... | source.topics |
| G5 | G5 | The plan contains no fabricated entities such as extra atten... | ALL source fields |

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

## Objective
Ensure all readiness items for the Q1 product launch (scheduled for February 1, 2025) are on track, identify blockers, and finalize the launch checklist.

---

## Timeline & Tasks

### 1. **Review Engineering Status**
- **Owner:** Mike Johnson
- **Due Date:** January 10, 2025
- **Artifact:** Engineering_Status_Report.pdf
- **Details:** Confirm 100% feature completion and obtain engineering sign-off.
- **Blocker:** Engineering sign-off required before QA final approval.

### 2. **Finalize QA Testing**
- **Owner:** Lisa Park
- **Start Date:** January 11, 2025 (after engineering sign-off)
- **Due Date:** January 20, 2025
- **Artifact:** QA_Test_Results_Dec.pdf
- **Details:** Complete final QA cycle and document results.
- **Blocker:** Dependent on engineering sign-off.

### 3. **Design Asset Completion**
- **Owner:** Tom Wilson
- **Due Date:** January 12, 2025
- **Artifact:** Design_Assets_Summary.docx
- **Details:** Finalize all design assets for marketing.
- **Blocker:** Design assets must be finalized before marketing materials.

### 4. **Legal Review of Terms of Service**
- **Owner:** Sarah Chen
- **Due Date:** January 18, 2025
- **Artifact:** Product_Launch_Checklist_v3.x
... (truncated)
```

</details>

#### ⚡ Medium Quality Plan

**Intended Scores:** Structural 80%, Grounding 60%
**Deliberate Issues:** Fabricated attendee name: Alex Thompson assigned as task owner for Marketing Materials, Reference to non-existent file: Marketing_Brief.pdf, One date misalignment: Marketing task due January 23, but milestone is January 24

<details>
<summary>📋 View Plan Content</summary>

```
# Q1 Product Launch Readiness Review - Workback Plan

**Meeting Date:** January 15, 2025  
**Organizer:** Sarah Chen  
**Attendees:** Sarah Chen, Mike Johnson, Lisa Park, Tom Wilson  

---

## Objective
Ensure all readiness tasks are completed in time for the February 1, 2025 product launch. Review dependencies, finalize QA, and confirm marketing and legal readiness.

---

## Timeline Overview
- **Launch Date:** February 1, 2025
- **Current Date:** January 15, 2025
- **Time Remaining:** ~17 days

---

## Key Milestones
| Milestone | Date |
|-----------|------|
| Engineering Sign-off | January 18, 2025 |
| QA Final Approval | January 21, 2025 |
| Marketing Assets Finalized | January 24, 2025 |
| Legal Review Complete | January 28, 2025 |
| Launch | February 1, 2025 |

---

## Tasks & Owners

### 1. Engineering Sign-off
- **Task:** Complete final code merge and sign-off
- **Owner:** Mike Johnson
- **Due:** January 18, 2025
- **Notes:** Refer to `Engineering_Status_Report.pdf`

### 2. QA Final Approval
- **Task:** Complete regression testing and approve build
- **Owner:** Lisa Park
- **Due:** January 21, 2025
- **Notes:** Use `QA_Test_Results_Dec.pdf` for reference

### 3. Marketing Materials
- **Task:** Finalize launch email and social media assets
- **Owner:** Alex Thompson  
- **Due:** January 23, 2025 *(Note: This date is earlier than the milestone of January 24, slight misalignment)*
- **Notes:** Drafts in `Marketing_Brief.pdf`

### 4. Legal Review
- **Task:** Complete Term
... (truncated)
```

</details>

#### ⚠️ Low Quality Plan

**Intended Scores:** Structural 40%, Grounding 20%
**Deliberate Issues:** No explicit meeting date/time included or incorrect date mentioned (early February instead of Jan 15), Used generic owners like 'someone should', 'the team will', 'TBD', Referenced non-existent files: Launch_Overview_Final.docx, Marketing_Strategy_2025.pdf, System_Design_v4.docx

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan for Product Launch Meeting

## Overview
This plan is to prepare for the big product launch discussion. The team will ensure everything is ready and address any issues that come up. The meeting will happen sometime in early February.

## Key Steps
- Someone should gather all the documents like Launch_Overview_Final.docx and Marketing_Strategy_2025.pdf.
- The team will review the roadmap and check for any missing components.
- TBD will confirm that all stakeholders are aligned on the vision and objectives.
- Someone should schedule a follow-up sync with the extended leadership group.

## Attendees
- Sarah Chen
- Mike Johnson
- Lisa Park
- Tom Wilson
- Jennifer Lee
- Robert Smith
- Alex Martinez

## Action Items
- Review technical specs and make sure the architecture diagram in System_Design_v4.docx is updated.
- The team should finalize the promotional video and upload it to the shared drive.
- Someone should draft an email announcement for internal teams.

## Timeline
- By March 10: All QA checks should be completed.
- By March 15: Marketing assets finalized.
- By March 20: Legal review completed.

## Notes
- Ensure everyone is comfortable with the new branding guidelines.
- Discuss opportunities for cross-team collaboration in future quarters.

---

No blockers or dependencies identified at this time.

```

</details>

---

### scenario_002

#### 🌟 Perfect Quality Plan

**Intended Scores:** Structural 100%, Grounding 100%

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan: Budget Planning FY26 Kickoff

## Meeting Details
- **Title:** Budget Planning FY26 Kickoff
- **Date:** December 5, 2024
- **Time:** 10:00 AM EST
- **Duration:** 120 minutes
- **Organizer:** James Miller
- **Attendees:** James Miller, Emily Davis, Robert Brown, Amanda Lee, Chris Taylor

---

## Objective
Prepare all necessary data, documents, and analysis to ensure a productive FY26 Budget Planning Kickoff meeting. Align departmental budgets with strategic priorities and incorporate the CFO’s 5% cost reduction target.

---

## Timeline & Tasks

### **Task 1: Collect Department Budget Requests**
- **Owner:** Amanda Lee
- **Description:** Ensure all department heads submit their budget requests for FY26.
- **Due Date:** November 15, 2024
- **Dependencies:** Department heads must submit requests before consolidation.
- **Artifacts:** Department_Budget_Requests.xlsx
- **Potential Blockers:** Delayed submissions from department heads.

---

### **Task 2: Gather Strategic Priorities Document**
- **Owner:** James Miller
- **Description:** Obtain the finalized strategic priorities presentation from the CEO.
- **Due Date:** November 18, 2024
- **Dependencies:** Strategic priorities document from CEO required.
- **Artifacts:** Strategic_Priorities_FY26.pptx
- **Potential Blockers:** Delay in CEO approval.

---

### **Task 3: Compile HR Headcount Projections**
- **Owner:** Emily Davis
- **Description:** Collect HR’s headcount and salary projections for FY26.
- **Due Date
... (truncated)
```

</details>

#### ⚡ Medium Quality Plan

**Intended Scores:** Structural 80%, Grounding 60%
**Deliberate Issues:** Added fabricated attendee name 'Alex Thompson' as task owner for November 25 task, Referenced non-existent file 'Marketing_Brief.pdf', Included a task on December 6, 2024, which is after the meeting date (misaligned timeline)

<details>
<summary>📋 View Plan Content</summary>

```
# FY26 Budget Planning Kickoff - Workback Plan

**Meeting Title:** Budget Planning FY26 Kickoff  
**Meeting Date:** December 5, 2024  
**Time:** 10:00 AM EST  
**Duration:** 120 minutes  
**Organizer:** James Miller  

---

## Objective
Prepare all necessary financial data, departmental inputs, and strategic alignment materials for the FY26 Budget Planning Kickoff meeting.

---

## Timeline & Tasks

### November 10, 2024
- **Task:** Distribute cost reduction guidelines to department heads  
- **Owner:** Emily Davis  
- **Dependencies:** None  
- **Notes:** Ensure all departments understand the 5% reduction target.

### November 15, 2024
- **Task:** Collect departmental budget requests  
- **Owner:** Robert Brown  
- **Dependencies:** Department heads must submit requests before consolidation  
- **Reference:** Department_Budget_Requests.xlsx

### November 18, 2024
- **Task:** Gather HR headcount projections for salary planning  
- **Owner:** Amanda Lee  
- **Dependencies:** HR team input required  

### November 20, 2024
- **Task:** Review historical spending data and identify cost-saving opportunities  
- **Owner:** Chris Taylor  
- **Reference:** FY25_Actual_Spending.xlsx

### November 25, 2024
- **Task:** Prepare consolidated budget draft  
- **Owner:** Alex Thompson  
- **Dependencies:** Completion of departmental requests and HR projections  
- **Reference:** Marketing_Brief.pdf

### November 30, 2024
- **Task:** Align consolidated draft with strategic priorities  
- **O
... (truncated)
```

</details>

#### ⚠️ Low Quality Plan

**Intended Scores:** Structural 40%, Grounding 20%
**Deliberate Issues:** No explicit meeting date/time from the actual meeting; wrong date (January 15, 2025 instead of December 5, 2024), Generic owners used (team, someone, TBD), Referenced non-existent files: Annual_Spending_Overview.docx, Budget_Projections_FY30.xlsx

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan for Budget Planning Meeting

## Overview
This plan outlines the steps to prepare for the upcoming budget discussion. The team will ensure everything is ready for the session.

## Key Actions
- Someone should gather all the necessary financial data from previous years.
- The team will review the long-term strategy and prepare slides.
- TBD will collect reports from all relevant departments.
- Someone should check compliance guidelines and update the documents.

## Tasks
1. Collect data from **Annual_Spending_Overview.docx** and **Budget_Projections_FY30.xlsx**.
2. Schedule a pre-meeting sync with Sarah Johnson, Michael Smith, and Laura Chen to align on talking points.
3. Draft initial talking points on cost optimization and future investment opportunities.
4. Prepare a summary document for leadership review.

## Notes
- Ensure that marketing plans and new product launch timelines are included in the discussion.
- Consider adding a section on vendor management and technology upgrades.

## Next Steps
- The team will finalize everything before the meeting scheduled for January 15, 2025.
- Someone should upload all files to the shared drive.

## Additional Considerations
- Review any pending legal approvals.
- Check if the sustainability roadmap needs to be included.

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

---

## Objective
Prepare for critical escalation review with Acme Corp to address service outages, analyze root causes, and align on resolution plan to prevent contract termination.

---

## Timeline & Tasks

| Date       | Task                                                      | Owner           | Artifact(s)                                  | Dependencies                                      | Potential Blockers                      |
|------------|-----------------------------------------------------------|-----------------|----------------------------------------------|---------------------------------------------------|------------------------------------------|
| Nov 12, 2024 | Complete engineering post-mortem reports for 3 incidents | David Kim       | Acme_Incident_Report_Nov.pdf                | Engineering post-mortem reports due before meeting | Delay in root cause analysis completion |
| Nov 14, 2024 | Provide customer sentiment update                        | Rachel Green    | Previous_Meeting_Notes.docx                 | Account manager to provide customer sentiment update | Awaiting customer feedback              |
| Nov 15, 2024 | Legal review of SL
... (truncated)
```

</details>

#### ⚡ Medium Quality Plan

**Intended Scores:** Structural 80%, Grounding 60%
**Deliberate Issues:** Task on Nov 15 assigned to fabricated attendee 'Alex Thompson' (not in attendee list), Reference to non-existent file 'Marketing_Brief.pdf', Task scheduled for November 21, which is after the meeting date (November 20)

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan: Customer Escalation Review - Acme Corp

**Meeting Date:** November 20, 2024  
**Time:** 3:30 PM PST  
**Organizer:** Jennifer White  

---

## Objective
Prepare for the escalation review meeting with Acme Corp to address recent service outages, identify root causes, and present an action plan to prevent future incidents.

---

## Timeline & Tasks

### November 10, 2024
- **Task:** Draft initial summary of incidents and key metrics.
- **Owner:** Rachel Green
- **Notes:** Use data from Acme_Incident_Report_Nov.pdf and Marketing_Brief.pdf for context.

### November 12, 2024
- **Task:** Collect engineering post-mortem reports.
- **Owner:** David Kim
- **Dependencies:** Engineering team must complete analysis by this date.

### November 14, 2024
- **Task:** Legal review of SLA breach implications.
- **Owner:** Mark Thompson
- **Reference:** Service_Level_Agreement.pdf

### November 15, 2024
- **Task:** Gather customer sentiment update from account manager.
- **Owner:** Alex Thompson
- **Notes:** Ensure insights are aligned with escalation context.

### November 18, 2024
- **Task:** Compile final meeting deck and circulate for review.
- **Owner:** Jennifer White
- **Reference:** Include system diagrams from System_Architecture_Diagram.png

### November 21, 2024
- **Task:** Finalize post-meeting action items.
- **Owner:** Jennifer White
- **Notes:** Summarize decisions and next steps.

---

## Dependencies
- Engineering post-mortem reports ready by Nov 12.
- Legal r
... (truncated)
```

</details>

#### ⚠️ Low Quality Plan

**Intended Scores:** Structural 40%, Grounding 20%
**Deliberate Issues:** No explicit meeting date/time included, Used generic owners like 'someone should', 'the team will', 'TBD', Referenced non-existent files: Summary_Notes.docx, Customer_Feedback_Analysis.xlsx, Performance_Improvement_Strategy.pdf, Technical_Roadmap_2025.docx

<details>
<summary>📋 View Plan Content</summary>

```
# Workback Plan for Upcoming Discussion

## Objective
Prepare for the upcoming discussion about recent challenges and ensure everything is ready for review.

## Key Steps
- Someone should gather all relevant documents, including the Summary_Notes.docx and Customer_Feedback_Analysis.xlsx.
- The team will review the Performance_Improvement_Strategy.pdf to align on next steps.
- TBD will confirm if all stakeholders like Alex Johnson, Maria Lopez, and Kevin Smith are informed.
- Someone should check if the draft of the Technical_Roadmap_2025.docx is complete.
- The team will brainstorm ideas for improving customer engagement and marketing campaigns.

## Action Items
- Review historical data from the last quarter.
- Draft a preliminary response plan for any potential issues.
- Ensure that all team members have access to the shared folder with these files.

## Next Steps
- Team will meet again after the holiday season to finalize decisions.
- TBD will send out a summary email after the meeting.

## Notes
This plan is flexible and can be adjusted as needed. The team should stay aligned and communicate frequently.

```

</details>

---


---

## Evaluation Results by Quality Level

### Perfect Quality

**Target:** 100% S, 100% G
**Actual:** 77% Structural, 87% Grounding
**Plans Evaluated:** 3

| Verdict | Count |
|---------|-------|
| ❌ fail_structure | 1 |
| ✅ pass | 2 |

### Medium Quality

**Target:** 80% S, 60% G
**Actual:** 63% Structural, 40% Grounding
**Plans Evaluated:** 3

| Verdict | Count |
|---------|-------|
| ❌ fail_both | 3 |

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
| A1 | 3 | 6 | ❌ 33% |
| A10 | 0 | 9 | ❌ 0% |
| A2 | 7 | 2 | ⚠️ 78% |
| A3 | 6 | 3 | ⚠️ 67% |
| A4 | 9 | 0 | ✅ 100% |
| A5 | 6 | 3 | ⚠️ 67% |
| A6 | 7 | 2 | ⚠️ 78% |
| A7 | 9 | 0 | ✅ 100% |
| A8 | 0 | 9 | ❌ 0% |
| A9 | 5 | 4 | ⚠️ 56% |

### Grounding Assertions (G1-G5)
*Question: "Is X CORRECT?" (Checks ACCURACY)*

| Assertion | Pass | Fail | Rate |
|-----------|------|------|------|
| G1 | 4 | 5 | ❌ 44% |
| G2 | 5 | 4 | ⚠️ 56% |
| G3 | 3 | 6 | ❌ 33% |
| G4 | 6 | 3 | ⚠️ 67% |
| G5 | 1 | 8 | ❌ 11% |

**Sample Hallucinations Detected:**
- [perfect] G5: `February 1, 2025...`
- [medium] G2: `Meeting Time missing...`
- [medium] G2: `Timezone missing...`
- [medium] G3: `Marketing_Brief.pdf...`
- [medium] G5: `Alex Thompson...`

---

## Verdict Distribution

| Verdict | Count | Percentage |
|---------|-------|------------|
| ✅ pass | 2 | 22% |
| 🔧 fail_structure | 1 | 11% |
| ⚠️ fail_grounding | 0 | 0% |
| ❌ fail_both | 6 | 67% |

**Interpretation:**
- ✅ **pass**: Plan has good structure AND is factually accurate
- 🔧 **fail_structure**: Plan is missing required elements
- ⚠️ **fail_grounding**: Plan has good structure but contains hallucinations
- ❌ **fail_both**: Plan is both incomplete and inaccurate

---

## Detailed Results

### Plan 1: scenario_001 (Perfect)

- **Structural Score:** 70%
- **Grounding Score:** 80%
- **Verdict:** 🔧 fail_structure

**Failed Structural Assertions:**
- A8: The plan does not mention any communication channels or methods for updates and 
- A9: The assertion refers to grounding and alignment with context, which is not a str
- A10: The plan lists tasks with owners, due dates, and details, but does not include a

**Failed Grounding Assertions:**
- G5: Compared all people, dates, times, files, and topics in the plan against the sou

---

### Plan 2: scenario_001 (Medium)

- **Structural Score:** 60%
- **Grounding Score:** 40%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan includes a meeting date and attendees but does not mention a meeting ti
- A8: The plan does not mention any communication channels or methods for updates and 
- A9: The assertion refers to grounding and alignment with context (G1-G5), which is a

**Failed Grounding Assertions:**
- G2: The plan includes the meeting date (January 15, 2025) which matches the source, 
- G3: Compared all file references in the plan against the source files list. The plan
- G5: Compared all people, dates, times, files, and topics mentioned in the plan again

---

### Plan 3: scenario_001 (Low)

- **Structural Score:** 40%
- **Grounding Score:** 0%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan includes attendees but does not provide an explicit meeting date, time,
- A3: The plan lists tasks but does not assign a specific named owner to each task; ow
- A5: The plan includes a timeline with some dates, but the individual tasks in the Ke

**Failed Grounding Assertions:**
- G1: The plan includes attendees not present in the source data. The source lists onl
- G2: The plan states the meeting will happen sometime in early February, which does n
- G3: The plan references files that do not appear in the source files list. Specifica

---

### Plan 4: scenario_002 (Perfect)

- **Structural Score:** 80%
- **Grounding Score:** 80%
- **Verdict:** ✅ pass

**Failed Structural Assertions:**
- A8: The plan does not mention any communication channels or tools for updates and co
- A10: The workback plan lists tasks with owners, descriptions, due dates, and other de

**Failed Grounding Assertions:**
- G5: Compared attendees, organizer, meeting date/time, files, and topics from the pla

---

### Plan 5: scenario_002 (Medium)

- **Structural Score:** 70%
- **Grounding Score:** 40%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan includes meeting date and time with timezone, but does not list attende
- A8: The plan does not mention any communication channels or tools for updates and co
- A10: The plan lists tasks with dates, owners, dependencies, and references, but does 

**Failed Grounding Assertions:**
- G1: The plan mentions an additional person, Alex Thompson, who is not listed in the 
- G3: The plan references files that do not exist in the source list. Specifically, 'M
- G5: The plan introduces entities not present in the source data. Specifically, 'Alex

---

### Plan 6: scenario_002 (Low)

- **Structural Score:** 30%
- **Grounding Score:** 0%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan includes a meeting date (January 15, 2025) and mentions some attendees 
- A2: The plan mentions a meeting date but does not include a structured timeline or s
- A3: The plan lists tasks but does not assign ownership of each task to specifically 

**Failed Grounding Assertions:**
- G1: The plan mentions Sarah Johnson, Michael Smith, and Laura Chen, none of whom are
- G2: The plan states the meeting is scheduled for January 15, 2025, but the source sp
- G3: The plan references files 'Annual_Spending_Overview.docx' and 'Budget_Projection

---

### Plan 7: scenario_003 (Perfect)

- **Structural Score:** 80%
- **Grounding Score:** 100%
- **Verdict:** ✅ pass

**Failed Structural Assertions:**
- A8: The plan does not mention any communication channels or methods for updates and 
- A10: The workback plan lists tasks with dates, owners, artifacts, dependencies, and b

---

### Plan 8: scenario_003 (Medium)

- **Structural Score:** 60%
- **Grounding Score:** 40%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan includes meeting date, time, and timezone, but does not provide an expl
- A8: The plan does not mention any communication channels or methods for providing up
- A9: The plan includes meeting details and contextual information (objective, referen

**Failed Grounding Assertions:**
- G1: The plan mentions an additional person, Alex Thompson, who is not listed in the 
- G3: Compared all file names mentioned in the plan against the source files. The plan
- G5: The plan introduces an extra attendee/owner 'Alex Thompson' and references a fil

---

### Plan 9: scenario_003 (Low)

- **Structural Score:** 30%
- **Grounding Score:** 0%
- **Verdict:** ❌ fail_both

**Failed Structural Assertions:**
- A1: The plan mentions a future meeting but does not provide explicit meeting details
- A2: The plan does not include a structured timeline that works back from the meeting
- A3: The plan does not assign ownership of each task to specifically named individual

**Failed Grounding Assertions:**
- G1: The plan mentions people (Alex Johnson, Maria Lopez, Kevin Smith) who do not app
- G2: The plan does not mention any meeting date, time, or timezone, so it cannot matc
- G3: The plan references files that do not exist in the source data. None of the file

---


---

## Insights & Recommendations

### Framework Effectiveness

✅ **Quality Differentiation:** The framework correctly ranked quality levels (Perfect > Medium > Low)

### Structural vs Grounding Insights

- **Medium:** 23% gap between structural (63%) and grounding (40%) scores
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
