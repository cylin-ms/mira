# Workback Plan Quality Examples & Evaluation Report

> **Generated:** November 28, 2025  
> **Purpose:** Demonstrate how the 10 assertion patterns (P1-P10) apply to workback plans at different quality levels  
> **GitHub:** [docs/Kening](https://github.com/cylin-ms/mira/tree/master/docs/Kening)

---

## Scenario

**Meeting Details:**
- **Title:** "Q1 Product Launch Readiness Review"
- **Date:** January 15, 2025, 2:00 PM PST
- **Attendees:** Sarah Chen (Product Manager), Mike Johnson (Engineering Lead), Lisa Park (Design Lead), Tom Wilson (QA Manager)
- **Organizer:** Sarah Chen
- **Duration:** 90 minutes

**Context:**
The team is preparing for a major product launch scheduled for February 1, 2025. This meeting is to review all readiness items, identify blockers, and finalize the launch checklist.

**Available Artifacts:**
- `Product_Launch_Checklist_v3.xlsx` (last updated Dec 20, 2024)
- `Engineering_Status_Report.pdf` (from Mike)
- `Design_Assets_Summary.docx` (from Lisa)
- `QA_Test_Results_Dec.pdf` (from Tom)

**Known Dependencies:**
- Engineering sign-off required before QA final approval
- Design assets must be finalized before marketing materials
- Legal review pending on Terms of Service updates

**User Prompt:** "Help me create a workback plan for the upcoming meeting 'Q1 Product Launch Readiness Review'"

---

## Pattern Reference (P1-P10)

| ID | Pattern | Level | Key Criteria |
|----|---------|-------|--------------|
| P1 | Explicit Meeting Details | Critical | Correct date, time, attendees |
| P2 | Timeline Backward Planning | Critical | Tasks scheduled before T₀ with buffers |
| P3 | Ownership Assignment | Critical | Every task has named owner |
| P4 | Artifact Specification | Expected | Key artifacts listed with deadlines |
| P5 | Dependency Sequencing | Expected | Tasks logically ordered |
| P6 | Meeting Objective Clarity | Expected | Purpose clearly stated |
| P7 | Assumption Disclosure | Aspirational | Gaps explicitly noted |
| P8 | Stakeholder Alignment | Aspirational | Review steps with stakeholders |
| P9 | Grounding in Context | Critical | No fabricated details |
| P10 | Risk Identification | Aspirational | Risks and mitigations noted |

---

# 1. Perfect Quality Plan

## Generated Plan

### Workback Plan: Q1 Product Launch Readiness Review

**Meeting:** Q1 Product Launch Readiness Review  
**Date & Time:** January 15, 2025, 2:00 PM PST  
**Duration:** 90 minutes  
**Organizer:** Sarah Chen (Product Manager)  
**Attendees:** Mike Johnson (Engineering Lead), Lisa Park (Design Lead), Tom Wilson (QA Manager)

---

#### Meeting Objective
Review all launch readiness items for the February 1, 2025 product launch, identify any blockers, finalize the launch checklist, and ensure cross-functional alignment on remaining tasks.

---

#### Assumptions
- **Assumption 1:** All attendees are available on January 15, 2025, at 2:00 PM PST as per the calendar invite.
- **Assumption 2:** The product launch date of February 1, 2025 is firm and not subject to change.
- **Assumption 3:** Legal review for Terms of Service will be completed by January 10, 2025.

---

#### Backward Timeline (T₀ = January 15, 2025, 2:00 PM PST)

| Date | Task | Owner | Dependencies | Artifacts |
|------|------|-------|--------------|-----------|
| **Jan 6 (T-9)** | Request updated status reports from all leads | Sarah Chen | None | Email template |
| **Jan 7 (T-8)** | Mike submits Engineering Status Report update | Mike Johnson | None | `Engineering_Status_Report.pdf` |
| **Jan 7 (T-8)** | Lisa submits Design Assets Summary update | Lisa Park | None | `Design_Assets_Summary.docx` |
| **Jan 7 (T-8)** | Tom submits QA Test Results update | Tom Wilson | Engineering sign-off | `QA_Test_Results_Dec.pdf` |
| **Jan 8 (T-7)** | Sarah consolidates all reports into master checklist | Sarah Chen | Status reports received | `Product_Launch_Checklist_v3.xlsx` |
| **Jan 9 (T-6)** | Draft meeting agenda based on consolidated status | Sarah Chen | Master checklist updated | Draft agenda |
| **Jan 10 (T-5)** | Confirm Legal review status on Terms of Service | Sarah Chen | Legal team | Legal sign-off status |
| **Jan 10 (T-5)** | Share draft agenda with all attendees for feedback | Sarah Chen | Draft agenda complete | Email with agenda |
| **Jan 12 (T-3)** | Collect feedback on agenda from Mike, Lisa, Tom | Sarah Chen | Agenda shared | Feedback responses |
| **Jan 13 (T-2)** | Finalize meeting agenda incorporating feedback | Sarah Chen | Feedback received | Final agenda |
| **Jan 13 (T-2)** | Send final agenda + pre-read materials to all attendees | Sarah Chen | Final agenda ready | Email with attachments |
| **Jan 14 (T-1)** | **BUFFER DAY** - Handle any last-minute updates | Sarah Chen | All prior tasks | - |
| **Jan 15 (T₀)** | Conduct meeting at 2:00 PM PST | Sarah Chen | All materials ready | Meeting recording |

---

#### Risk Identification & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| QA report delayed due to pending engineering sign-off | Medium | High | Mike to provide engineering sign-off by Jan 6 EOD |
| Legal review not complete by Jan 10 | Low | Medium | Escalate to Legal director by Jan 8 if no update |
| Attendee unavailable on meeting day | Low | High | Confirm attendance by Jan 10; identify backup delegates |

---

#### Stakeholder Alignment Tasks
- **Jan 6:** Sarah sends reminder to Mike for engineering sign-off needed for QA
- **Jan 10:** Sarah confirms alignment with all leads on agenda topics
- **Jan 12:** Quick sync with Mike and Tom on engineering-QA dependency status

---

## Assertions for Perfect Plan (Based on P1-P10)

### Critical Level Assertions

**A1 (P1 - Explicit Meeting Details):**
> "The response should explicitly state the meeting date as January 15, 2025, time as 2:00 PM PST, and list all four attendees: Sarah Chen, Mike Johnson, Lisa Park, and Tom Wilson."

**A2 (P2 - Timeline Backward Planning):**
> "The response should include a backward timeline from T₀ (January 15, 2025) with at least 8 preparation tasks scheduled between January 6-14, including at least one buffer day before the meeting."

**A3 (P3 - Ownership Assignment):**
> "The response should assign an explicit owner (Sarah Chen, Mike Johnson, Lisa Park, or Tom Wilson) to every listed task, with no tasks left unassigned or assigned to generic terms like 'team' or 'someone'."

**A4 (P9 - Grounding in Context):**
> "The response should only reference attendees listed in the scenario (Sarah Chen, Mike Johnson, Lisa Park, Tom Wilson) and should not introduce any fictitious participants or artifacts not mentioned in the context."

### Expected Level Assertions

**A5 (P4 - Artifact Specification):**
> "The response should reference at least 3 of the 4 available artifacts: Product_Launch_Checklist_v3.xlsx, Engineering_Status_Report.pdf, Design_Assets_Summary.docx, QA_Test_Results_Dec.pdf, with specific tasks for their preparation or distribution."

**A6 (P5 - Dependency Sequencing):**
> "The response should explicitly state that engineering sign-off is required before QA final approval, and sequence related tasks accordingly (engineering tasks before QA tasks)."

**A7 (P6 - Meeting Objective Clarity):**
> "The response should clearly state the meeting purpose: reviewing launch readiness items, identifying blockers, and finalizing the launch checklist for the February 1, 2025 product launch."

### Aspirational Level Assertions

**A8 (P7 - Assumption Disclosure):**
> "The response should include an 'Assumptions' section that explicitly lists at least 2 assumptions about attendee availability, timeline, or dependencies."

**A9 (P8 - Stakeholder Alignment):**
> "The response should include at least 2 stakeholder alignment tasks, such as sharing drafts for feedback or confirming input from attendees before finalizing materials."

**A10 (P10 - Risk Identification):**
> "The response should identify at least 2 risks (e.g., delayed reports, unavailable attendees) and propose specific mitigation strategies for each."

---

## Evaluation: Perfect Plan

| Assertion | Pattern | Level | Pass/Fail | Score | Evidence |
|-----------|---------|-------|-----------|-------|----------|
| A1 | P1 | Critical | ✅ PASS | 10/10 | States "January 15, 2025, 2:00 PM PST" and lists all 4 attendees |
| A2 | P2 | Critical | ✅ PASS | 10/10 | 12 tasks from Jan 6-15, includes Jan 14 buffer day |
| A3 | P3 | Critical | ✅ PASS | 10/10 | All 12 tasks have named owners |
| A4 | P9 | Critical | ✅ PASS | 10/10 | Only scenario attendees and artifacts mentioned |
| A5 | P4 | Expected | ✅ PASS | 10/10 | All 4 artifacts referenced with specific tasks |
| A6 | P5 | Expected | ✅ PASS | 10/10 | Engineering sign-off → QA dependency explicit |
| A7 | P6 | Expected | ✅ PASS | 10/10 | Objective section clearly states purpose |
| A8 | P7 | Aspirational | ✅ PASS | 10/10 | 3 assumptions explicitly listed |
| A9 | P8 | Aspirational | ✅ PASS | 10/10 | 3 stakeholder alignment tasks included |
| A10 | P10 | Aspirational | ✅ PASS | 10/10 | 3 risks with mitigations in table |

**Perfect Plan Total Score: 100/100** ⭐

---

# 2. Medium Quality Plan

## Generated Plan

### Workback Plan for Product Launch Meeting

**Meeting:** Q1 Product Launch Readiness Review  
**Date:** January 15, 2025  
**Attendees:** Sarah, Mike, Lisa, Tom

---

#### Tasks to Complete Before Meeting

1. **Jan 8** - Collect status updates from team (Sarah)
2. **Jan 10** - Review engineering status (Mike)
3. **Jan 10** - Check design assets (Lisa)
4. **Jan 11** - Compile QA results
5. **Jan 12** - Create meeting agenda (Sarah)
6. **Jan 13** - Send agenda to attendees (Sarah)
7. **Jan 14** - Finalize materials (Sarah)
8. **Jan 15** - Meeting

---

#### Key Documents
- Product Launch Checklist
- Engineering Status Report

---

## Assertions for Medium Plan (Based on P1-P10)

*(Same assertions as Perfect Plan - A1 through A10)*

---

## Evaluation: Medium Plan

| Assertion | Pattern | Level | Pass/Fail | Score | Evidence |
|-----------|---------|-------|-----------|-------|----------|
| A1 | P1 | Critical | ⚠️ PARTIAL | 6/10 | Date correct, but missing time (2:00 PM PST) and timezone; attendees use first names only |
| A2 | P2 | Critical | ⚠️ PARTIAL | 7/10 | Has backward timeline but no explicit buffer day; tasks start Jan 8 (only 7 days before) |
| A3 | P3 | Critical | ⚠️ PARTIAL | 6/10 | 6 of 8 tasks have owners; Task 4 "Compile QA results" has no owner |
| A4 | P9 | Critical | ✅ PASS | 9/10 | No fabricated attendees; minor: first names only |
| A5 | P4 | Expected | ⚠️ PARTIAL | 5/10 | Only 2 of 4 artifacts mentioned; no file extensions |
| A6 | P5 | Expected | ❌ FAIL | 3/10 | Dependencies not explicit; engineering and QA tasks not sequenced properly |
| A7 | P6 | Expected | ❌ FAIL | 2/10 | No meeting objective stated |
| A8 | P7 | Aspirational | ❌ FAIL | 0/10 | No assumptions section |
| A9 | P8 | Aspirational | ❌ FAIL | 2/10 | Only "send agenda" task; no feedback collection |
| A10 | P10 | Aspirational | ❌ FAIL | 0/10 | No risks identified |

**Medium Plan Total Score: 40/100** 📊

### Issues Identified:
1. Missing meeting time and timezone
2. One task without owner assigned
3. Dependencies not explicit
4. No meeting objective stated
5. Missing assumptions and risk sections
6. Only partial artifact coverage

---

# 3. Low Quality Plan

## Generated Plan

### Meeting Prep

Get ready for the launch meeting next week.

**Things to do:**
- Update the checklist
- Talk to the team about status
- Someone should prepare the slides
- Send out the invite
- Make sure everyone knows what to discuss
- Check with legal

**Meeting:** January 16, 2025 at 3pm  
**People:** Sarah, Mike, Lisa, Tom, and possibly John from Marketing

---

## Assertions for Low Plan (Based on P1-P10)

*(Same assertions as Perfect Plan - A1 through A10)*

---

## Evaluation: Low Plan

| Assertion | Pattern | Level | Pass/Fail | Score | Evidence |
|-----------|---------|-------|-----------|-------|----------|
| A1 | P1 | Critical | ❌ FAIL | 2/10 | **Wrong date** (Jan 16 vs Jan 15), **wrong time** (3pm vs 2pm), missing timezone |
| A2 | P2 | Critical | ❌ FAIL | 1/10 | No dates on tasks, no backward timeline, no buffer |
| A3 | P3 | Critical | ❌ FAIL | 1/10 | Most tasks have no owner; uses "someone should" |
| A4 | P9 | Critical | ❌ FAIL | 3/10 | **Introduces "John from Marketing"** who is not in the scenario |
| A5 | P4 | Expected | ❌ FAIL | 1/10 | Generic "checklist" and "slides" - no specific artifacts |
| A6 | P5 | Expected | ❌ FAIL | 0/10 | No task sequencing or dependencies |
| A7 | P6 | Expected | ❌ FAIL | 1/10 | Vague "launch meeting" - no specific objective |
| A8 | P7 | Aspirational | ❌ FAIL | 0/10 | No assumptions |
| A9 | P8 | Aspirational | ❌ FAIL | 0/10 | No stakeholder alignment tasks |
| A10 | P10 | Aspirational | ❌ FAIL | 0/10 | No risks |

**Low Plan Total Score: 9/100** ❌

### Critical Failures:
1. **Factual errors:** Wrong date (Jan 16) and wrong time (3pm)
2. **Fabrication:** Introduces "John from Marketing" not in scenario
3. **No structure:** Tasks without dates or owners
4. **Vague language:** "Someone should", "talk to the team"
5. **Missing everything:** No objective, assumptions, dependencies, risks

---

# Summary Comparison

## Score Breakdown by Pattern Category

| Category | Patterns | Perfect | Medium | Low |
|----------|----------|---------|--------|-----|
| **Critical** | P1, P2, P3, P9 | 40/40 | 28/40 | 7/40 |
| **Expected** | P4, P5, P6 | 30/30 | 10/30 | 2/30 |
| **Aspirational** | P7, P8, P10 | 30/30 | 2/30 | 0/30 |
| **TOTAL** | All | **100/100** | **40/100** | **9/100** |

## Visual Summary

```
Perfect Plan:  ████████████████████████████████████████ 100%
Medium Plan:   ████████████████                         40%
Low Plan:      ████                                      9%
```

## Quality Bands

| Score Range | Quality Level | Recommendation |
|-------------|---------------|----------------|
| 90-100 | ⭐ Excellent | Ready for use |
| 70-89 | ✅ Good | Minor improvements needed |
| 50-69 | ⚠️ Acceptable | Significant gaps to address |
| 30-49 | 📊 Below Average | Major revision required |
| 0-29 | ❌ Poor | Reject and regenerate |

---

# Human Judge Guidelines

## Evaluation Workflow

1. **Start with Critical Patterns (P1, P2, P3, P9)**
   - These are must-haves
   - Failing any critical pattern should cap the score at 60%

2. **Check Expected Patterns (P4, P5, P6)**
   - Important for completeness
   - Missing these reduces practical usefulness

3. **Assess Aspirational Patterns (P7, P8, P10)**
   - Differentiators for excellence
   - Bonus points for plans that include these

## Quick Checklist

- [ ] **P1:** Are date, time, timezone, and all attendees correct?
- [ ] **P2:** Is there a backward timeline with dates and buffer?
- [ ] **P3:** Does every task have a named owner?
- [ ] **P9:** Are all details grounded in provided context?
- [ ] **P4:** Are specific artifacts referenced?
- [ ] **P5:** Are dependencies explicit and sequenced correctly?
- [ ] **P6:** Is the meeting objective clearly stated?
- [ ] **P7:** Are assumptions disclosed?
- [ ] **P8:** Are there stakeholder alignment tasks?
- [ ] **P10:** Are risks identified with mitigations?

## Minimum Acceptable Score

A workback plan should score **at least 60/100** with **all critical patterns (P1, P2, P3, P9) passing** to be considered acceptable for production use.

---

# Appendix: Assertion Definitions

## Complete Assertion Set for This Scenario

```json
{
  "scenario_id": "q1_launch_readiness",
  "assertions": [
    {
      "id": "A1",
      "pattern": "P1",
      "level": "critical",
      "text": "The response should explicitly state the meeting date as January 15, 2025, time as 2:00 PM PST, and list all four attendees: Sarah Chen, Mike Johnson, Lisa Park, and Tom Wilson."
    },
    {
      "id": "A2",
      "pattern": "P2",
      "level": "critical",
      "text": "The response should include a backward timeline from T₀ (January 15, 2025) with at least 8 preparation tasks scheduled between January 6-14, including at least one buffer day before the meeting."
    },
    {
      "id": "A3",
      "pattern": "P3",
      "level": "critical",
      "text": "The response should assign an explicit owner (Sarah Chen, Mike Johnson, Lisa Park, or Tom Wilson) to every listed task, with no tasks left unassigned or assigned to generic terms like 'team' or 'someone'."
    },
    {
      "id": "A4",
      "pattern": "P9",
      "level": "critical",
      "text": "The response should only reference attendees listed in the scenario (Sarah Chen, Mike Johnson, Lisa Park, Tom Wilson) and should not introduce any fictitious participants or artifacts not mentioned in the context."
    },
    {
      "id": "A5",
      "pattern": "P4",
      "level": "expected",
      "text": "The response should reference at least 3 of the 4 available artifacts: Product_Launch_Checklist_v3.xlsx, Engineering_Status_Report.pdf, Design_Assets_Summary.docx, QA_Test_Results_Dec.pdf, with specific tasks for their preparation or distribution."
    },
    {
      "id": "A6",
      "pattern": "P5",
      "level": "expected",
      "text": "The response should explicitly state that engineering sign-off is required before QA final approval, and sequence related tasks accordingly (engineering tasks before QA tasks)."
    },
    {
      "id": "A7",
      "pattern": "P6",
      "level": "expected",
      "text": "The response should clearly state the meeting purpose: reviewing launch readiness items, identifying blockers, and finalizing the launch checklist for the February 1, 2025 product launch."
    },
    {
      "id": "A8",
      "pattern": "P7",
      "level": "aspirational",
      "text": "The response should include an 'Assumptions' section that explicitly lists at least 2 assumptions about attendee availability, timeline, or dependencies."
    },
    {
      "id": "A9",
      "pattern": "P8",
      "level": "aspirational",
      "text": "The response should include at least 2 stakeholder alignment tasks, such as sharing drafts for feedback or confirming input from attendees before finalizing materials."
    },
    {
      "id": "A10",
      "pattern": "P10",
      "level": "aspirational",
      "text": "The response should identify at least 2 risks (e.g., delayed reports, unavailable attendees) and propose specific mitigation strategies for each."
    }
  ]
}
```

---

*Generated for the Assertion Quality Analysis exercise - November 28, 2025*
