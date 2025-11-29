# Workback Plan (WBP) Evaluation Rubric & Gold Reference

**Purpose:** A compact, non-redundant rubric to evaluate Workback Plans (WBPs), score them objectively, and generate actionable fixes. Structural (S) and Grounding (G) dimensions are separated and sorted by priority. Ownership supports role/skill placeholders when names are missing.

---
## Scoring Model
- **Scale:** 0 = Missing · 1 = Partial · 2 = Fully Met  
- **Weighted Quality Score:** Σ(score × weight) / max_possible
- **Weights:** Critical = 3 · Moderate = 2 · Light = 1  
- **Priority Emphasis:** S1, S2, S3, G1, G2 are most critical for correctness and actionability.

---
## Structural Dimensions (S) — Sorted by Priority

### Dimension Groups
- **S1–S10 (Core):** The original 10 structural dimensions covering essential WBP elements (meeting details, timeline, ownership, deliverables, dates, dependencies, traceability, communication, grounding meta-check, priorities).
- **S11–S18 (Extended):** Additional structural dimensions added for completeness covering advanced planning aspects (risk mitigation, milestones, goals, resources, compliance, review loops, escalation, post-event actions).

Each dimension is evaluated independently with its own definition, weight, and success/fail criteria.

### Core Dimensions (S1–S10)

| ID  | Dimension                | Weight | Concise Definition                                                               | Objective Evaluation Statement                                                 |
|-----|--------------------------|:------:|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| S1  | Meeting Details          |   3    | Subject, date, time, timezone, attendee list clearly stated.                     | Plan includes all meeting metadata; missing any field = fail.                  |
| S2  | Timeline Alignment       |   3    | Backward scheduling (T-minus) with dependency-aware sequencing from meeting date.| Tasks arranged in reverse order from meeting date; dependencies respected.     |
| S3  | Ownership Assignment     |   3    | Named owners per task **or** role/skill placeholder if names unavailable.        | Every task has named owner **or** role/skill requirement stated.               |
| S4  | Deliverables & Artifacts |   2    | All outputs listed with working links, version/format specified.                 | Deliverables traceable and accessible; missing links or versions = fail.       |
| S5  | Task Dates               |   2    | Due dates for every task aligned with S2/S12 sequencing.                         | All tasks have due dates; dates match milestone/timeline logic.                |
| S6  | Dependencies & Blockers  |   2    | Predecessors and risks identified; mitigation steps documented.                  | Blockers and mitigations listed; absence = fail.                               |
| S7  | Source Traceability      |   2    | Tasks/artifacts link back to original source priorities/files.                   | Every task/artifact maps to source; missing links = fail.                      |
| S8  | Communication Channels   |   1    | Collaboration methods specified (Teams, email, meeting cadence).                 | Channels explicitly stated; absence = fail.                                    |
| S9  | Grounding Meta-Check     |   2    | All Grounding assertions (G1–G8) pass; no factual drift.                         | Plan aligns fully with source; any hallucination = fail.                       |
| S10 | Priority Assignment      |   2    | Tasks ranked by critical path/impact on meeting success.                         | Priority tags present; high-impact tasks appear before dependent milestones.   |

### Extended Dimensions (S11–S18)

| ID  | Dimension                | Weight | Concise Definition                                                               | Objective Evaluation Statement                                                 |
|-----|--------------------------|:------:|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| S11 | Risk Mitigation Strategy |   2    | Concrete contingencies for top risks with owners.                                | Mitigation steps documented; vague "monitor" = fail.                           |
| S12 | Milestone Validation     |   2    | Milestones feasible, right-sized, coherent, and verifiable via acceptance criteria.| Milestones achievable and coherent; unrealistic or unordered = fail.         |
| S13 | Goal & Success Criteria  |   2    | Clear objectives and measurable indicators of success.                           | Goals and metrics stated; absence = fail.                                      |
| S14 | Resource Allocation      |   2    | People/time/tools/budget availability and constraints visible.                   | Required resources listed; missing allocation = fail.                          |
| S15 | Compliance & Governance  |   1    | Security, privacy, regulatory checks noted.                                      | Compliance considerations present; absence = fail.                             |
| S16 | Review & Feedback Loops  |   1    | Scheduled checkpoints to validate and iterate the plan.                          | Review dates included; none = fail.                                            |
| S17 | Escalation Path          |   1    | Escalation owners and steps for critical risks defined.                          | Escalation path clear; missing owner = fail.                                   |
| S18 | Post-Event Actions       |   1    | Wrap-up tasks, retrospectives, and reporting.                                    | Post-event steps listed; none = fail.                                          |

**Difference between S2 & S12:**  
- **S2 Timeline Alignment** focuses on structural *sequencing* (reverse schedule, dependency awareness).  
- **S12 Milestone Validation** focuses on *feasibility* and *coherence* (right-sized, realistic, verifiable).

---
## Grounding Dimensions (G) — Sorted by Priority

**Note:** G1 (Hallucination Check) is the **overall grounding recall check** placed first. If G2-G8 all pass, G1 passes. G1 also catches entity types not covered by G2-G8 (e.g., project names, budget figures, fabricated relationships).

| ID  | Dimension              | Weight | Concise Definition                                        | Objective Evaluation Statement                                |
|-----|------------------------|:------:|------------------------------------------------------------|----------------------------------------------------------------|
| G1  | Hallucination Check    |   3    | No extraneous entities or fabricated details (overall).    | Plan contains only source-backed entities; if G2-G8 pass, G1 passes. |
| G2  | Attendee Grounding     |   3    | Attendees match source; no hallucinated names.             | All attendees verified against source list.                    |
| G3  | Date/Time Grounding    |   3    | Meeting date/time/timezone match the source.               | No deviation from source meeting schedule.                     |
| G4  | Artifact Grounding     |   2    | Files/decks referenced exist in the source repository.     | Artifacts validated; missing or fabricated = fail.             |
| G5  | Topic Grounding        |   2    | Agenda topics align with source priorities/context (nouns).| Topics match source; unrelated topics = fail.                  |
| G6  | Task Grounding         |   3    | Tasks/action items derived from source material (verbs).   | All tasks traceable to source; fabricated tasks = fail.        |
| G7  | Role Grounding         |   2    | Role/responsibility assignments match source or context.   | All role assignments verified; fabricated roles = fail.        |
| G8  | Constraint Grounding   |   2    | Constraints/limits derivable from source material.         | All constraints traceable to source; fabricated limits = fail. |

---
## Success & Fail Examples — Each Dimension

### Structural (S) — Core Dimensions

| ID  | Success Example                                                                                      | Fail Example                                                                                 |
|-----|-------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| S1  | "Board Review — Dec 15, 2025, 10:00 AM CST; Attendees: Alice Chen, Bob Li; TZ: CST."                 | "Board Review next month" (no date/time/timezone or attendee list).                         |
| S2  | T–30: Draft deck → T–15: Review → T–1: Dry run → Meeting Day.                                         | Tasks listed randomly; e.g., "Review deck after meeting."                                    |
| S3  | "Draft deck — Owner: Alice Chen; If name pending: Role: Staff PM; Skills: exec storytelling."        | "Draft deck — Owner: TBD."                                                                   |
| S4  | "Final deck (link); Budget sheet (link); Risk log (link); v3.2 PDF."                                  | "Prepare documents" (no links or specifics).                                                 |
| S5  | "Draft deck due Dec 1; Review Dec 10; Dry run Dec 14."                                                | No dates provided for any task.                                                              |
| S6  | "Dependency: Finance approval; Mitigation: escalate to CFO by Dec 5; Owner: Ops PM."                 | No mention of blockers or mitigation.                                                        |
| S7  | "Task references: meeting invite link; project doc URL; Planner plan ID."                             | Tasks listed without source references.                                                      |
| S8  | "Coordination via Teams channel; weekly email updates; standup Tue/Thu."                              | No mention of how the team will communicate.                                                 |
| S9  | All attendees, dates, artifacts match the source meeting invite.                                       | Plan includes attendee not in source (hallucination).                                        |
| S10 | Tasks labeled P1/P2/P3; critical path scheduled first; justification ties to success criteria.        | No priority tags; tasks in random order.                                                     |

### Structural (S) — Extended Dimensions

| ID  | Success Example                                                                                      | Fail Example                                                                                 |
|-----|-------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| S11 | "Risk: Vendor delay; Mitigation: backup vendor PO in place; Owner: Procurement Lead."                 | Risks listed with "monitor" and no mitigation.                                               |
| S12 | "Kickoff → Draft → Review → Final; 30 days; acceptance criteria: 'CFO-approved deck.'"               | "Kickoff → Final deck tomorrow" (unrealistic, unordered).                                    |
| S13 | "Goal: Exec-ready deck; Success: CFO sign-off ≥ Dec 12; Metric: review cycle ≤2."                     | No stated goal or success metric.                                                            |
| S14 | "Resources: 2 PMs; $5K budget; Adobe CC licenses; analyst 0.5 FTE."                                   | No mention of resources or budget.                                                           |
| S15 | "Check NDA before sharing; redact sensitive financials; storage in compliant repo."                   | No compliance checks mentioned.                                                              |
| S16 | "Checkpoints: Dec 1 (draft), Dec 10 (review), Dec 12 (exec sign-off)."                                | No review schedule provided.                                                                 |
| S17 | "Escalate to Director if blocker unresolved in 48h; contact chain listed."                            | No escalation process defined.                                                               |
| S18 | "Post-meeting: send summary; archive deck; retrospective; publish decisions."                         | No post-event tasks listed.                                                                  |

### Grounding (G)

| ID  | Success Example                                                | Fail Example                                  |
|-----|----------------------------------------------------------------|-----------------------------------------------|
| G1  | No extra entities or relationships beyond source-backed items. | Invents "Project Beta" or fabricated coordination. |
| G2  | Attendees exactly match the invite roster.                     | Adds "John Doe" not in source.                |
| G3  | Date/time/timezone exactly match the invite.                   | Uses Dec 16 instead of Dec 15.                |
| G4  | Deck link points to real file in repo; opens correctly.        | Links to non-existent or fabricated file.     |
| G5  | Agenda topics: Budget, Strategy — match the source agenda.     | Adds "New product launch" not in source.      |
| G6  | Tasks match action items mentioned in source emails/chats.     | Includes "Review Q4 budget" not in any source.|
| G7  | Owner assigned as "Project Lead" matches source role.          | Assigns "Architect" role to attendee who is PM.|
| G8  | "Budget cap $50K" constraint matches source email.             | Claims "Must complete by Friday" not in source.|

---
## Gold Reference — Ideal WBP (One-Page Checklist)

A plan **fulfills the goal of an ideal WBP** when it:
1. States meeting fundamentals (S1), is backward scheduled (S2), and contains feasible milestones (S12).  
2. Assigns accountable owners (S3) — or role/skill placeholders when names are pending.  
3. Lists deliverables with working links and versions (S4), and sets dates per task (S5).  
4. Captures dependencies/risks plus mitigations (S6, S11) and prioritizes the critical path (S10).  
5. Grounds all entities to source (S7, G1–G6, S9); **no hallucinations**.  
6. Plans for execution quality (S14, S16, S17), closes the loop (S18), and states clear success criteria (S13).  
7. Meets compliance needs (S15) and specifies channels (S8) for coordination.  

**Deliverables "Good Things to Check" (S4):**
- Link validity & access; correct repo/location.  
- Version & format (v#, date, file type).  
- Owner & due date for each deliverable.  
- Acceptance criteria (ready/usable).  
- Traceability (maps to task/milestone and source).  
- Readiness tag (Draft/Review/Final).

---
## Minimal JSON Schema for Automated Evaluation

Use in an LLM-as-Judge pipeline; supports role/skill-based ownership.

```json
{
  "wbp_eval": {
    "metadata": {
      "meeting_id": "string",
      "source_refs": {
        "attendees": "string[]",
        "meeting_datetime": "YYYY-MM-DDTHH:mm:ssZ",
        "artifacts": "url[]",
        "topics": "string[]"
      }
    },
    "assertions": {
      "S1": { "score": 0, "weight": 3, "rationale": "string", "suggested_fix": "string" },
      "S2": { "score": 0, "weight": 3, "rationale": "string", "suggested_fix": "string" },
      "S3": {
        "score": 0, "weight": 3, "rationale": "string",
        "suggested_fix": "string",
        "ownership": { "type": "name|role", "value": "string", "skills": ["string"] }
      },
      "S4": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S5": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S6": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S7": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S8": { "score": 0, "weight": 1, "rationale": "string", "suggested_fix": "string" },
      "S9": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S10": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S11": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S12": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S13": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S14": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "S15": { "score": 0, "weight": 1, "rationale": "string", "suggested_fix": "string" },
      "S16": { "score": 0, "weight": 1, "rationale": "string", "suggested_fix": "string" },
      "S17": { "score": 0, "weight": 1, "rationale": "string", "suggested_fix": "string" },
      "S18": { "score": 0, "weight": 1, "rationale": "string", "suggested_fix": "string" },
      "G1": { "score": 0, "weight": 3, "rationale": "string", "suggested_fix": "string" },
      "G2": { "score": 0, "weight": 3, "rationale": "string", "suggested_fix": "string" },
      "G3": { "score": 0, "weight": 3, "rationale": "string", "suggested_fix": "string" },
      "G4": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "G5": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "G6": { "score": 0, "weight": 3, "rationale": "string", "suggested_fix": "string" },
      "G7": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" },
      "G8": { "score": 0, "weight": 2, "rationale": "string", "suggested_fix": "string" }
    },
    "summary": {
      "weighted_score": 0.0,
      "strengths": ["string"],
      "weaknesses": ["string"],
      "next_actions": ["string"]
    }
  }
}
```

---
## Priority Evaluation (S10) — Objective Checks

- Priority column/tags present (High/Medium/Low or P1/P2/P3).  
- High-impact tasks scheduled earlier than dependent milestones.  
- Justification for priority ties to success criteria (S13).  
- Resource bias reflects priority (S14): earlier dates/more capable owners for P1 items.

---
## Notes & Alignment (Internal)

Aligned with internal materials on WBP assertions and evaluation: *Deriving Assertions for Workback Plan*, *Workback Plan Quality Evaluation Framework V1.0*, *TimeBerry Evaluation Proposal*.
