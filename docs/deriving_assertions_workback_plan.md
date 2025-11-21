# Deriving Assertions for Workback Plan
Author: Weiwei Cui

A good workback plan should outline tasks, milestones, and dependencies that need completion before a meeting by planning backward from the meeting date. Some key attributes include:

## Key Attributes

- **Objective and Scope**  
  What outcome must be achieved in the meeting; What is explicitly in/out of scope for the meeting.

- **Timeline / Reverse Schedule**  
  Example: *T-10 days: finalize draft spec…*

- **Tasks and Owners**  
  Actionable, concrete, and bounded activities; Clear responsible individuals or roles for each task.

- **Critical Path and Dependencies**  
  What tasks must precede others; Tasks that, if delayed, directly threaten the meeting’s ability to achieve its goal; External risks (e.g., data not ready, unstable environments, ambiguous requirements).

- **Deliverables and Artifacts**  
  Explicit outputs for each task and when.

- **Acceptance Criteria and Decision Readiness**  
  What must be true so the meeting can produce a decision instead of devolving into discovery (e.g., performance metrics within what thresholds).

---

The assertions should be truthfully derived from the meeting context/facts and should focus on the above key attributes.

## Inputs for the Method

- **Meeting Definition**  
  Subject, body/agenda, organizer, attendees and roles, time, recurrence, and any attachments. This defines the meeting’s type, purpose, and required outcomes.

- **Available Planning Window**  
  When the workback plan request is sent relative to the meeting start. This defines the planning window available (e.g., 2 hours vs 2 weeks).

- **Requester Identity and Role**  
  Who is asking (e.g., organizer vs attendee, manager vs IC, PM vs SRE). The workback plan should be tailored to what that person can realistically own or influence.

- **Context / Background Material**  
  What materials exist and are accessible (e.g., specs, decks, metrics, chat logs, tickets). The agent should derive the plan from available context.

---

## Approach Details

Our approach consists of two stages:

### **Stage 1**  
Uses a set of prompts to collect and organize key information specific to the meeting workback plan from the context/background materials.

Questions asked to the LLM include:

- The urgency, complexity, and scale of the meeting  
- The meeting goal  
- The prerequisites to meet the meeting goal  
- The concrete task breakdown for the identified prerequisites  
- The potential dependencies between the identified tasks  
- The acceptance criteria and owner for each task  
- … (expand as needed)

Because each question is specific, outputs are expected to be concrete and reliable. Isolated questions prevent interference and allow easy expansion.

---

### **Stage 2**  
Given the meeting complexity, remaining time, and importance to the requester, determine the depth of the generated workback plan:

- **Minimal Plan**  
  3–7 key tasks, high-level ordering, suitable for short or low-risk meetings.

- **Standard Plan**  
  Clear timeline, owners, deliverables, and simple dependencies.

- **Detailed Plan**  
  Full workback including critical path, acceptance criteria, risks, and contingencies.

Based on the determined plan depth, ask the LLM to generate assertions to state:

- What **should be added** to the plan (within the depth and suitable for the requester)  
- What **should not be included** (either out of depth, not important for the requester, or not present in Stage 1 output)
