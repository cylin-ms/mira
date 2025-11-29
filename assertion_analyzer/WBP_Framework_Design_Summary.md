# WBP Evaluation Framework - Design Summary

**Authors**: Chin-Yew Lin, Haidong Zhang  
**Date**: November 30, 2025  
**Version**: 1.0

This document summarizes the design principles and decisions that shaped the WBP (Work-Back Plan) Quality Evaluation Framework.

---

## Executive Summary

The framework evaluates WBP quality through **20 Structural dimensions (S1-S20)** and **9 Grounding dimensions (G1-G9)**, with **28 slot types** for semantic annotation. Key innovations include:

1. **Four-tier classification**: REQUIRED, ASPIRATIONAL, CONDITIONAL, N/A
2. **Hallucination vs Good Planning distinction**: G9 enables creative planning while preventing contradictions
3. **S→G linkage**: Every S assertion links to relevant G dimensions for dual verification
4. **Slot type grounding taxonomy**: GROUNDED, DERIVED, CONDITIONAL, PLANNER-GEN, N/A

---

## Design Principles

### Principle 1: Planning vs Operational Separation

> **"Evaluate the PLAN, not the EXECUTION"**

A WBP is a planning artifact. We evaluate its structure and completeness, not how well it will be executed.

**Applied to:**
- S7 (Meeting Outcomes) → N/A - outcomes are inputs to WBP, not WBP content
- S14 (Feedback Integration) → N/A - feedback loops are execution governance
- S15 (Progress Tracking) → N/A - tracking happens during execution; STATUS column (S20) provides structure
- S17_A3 (Communication methods) → Removed - how teams communicate is operational

### Principle 2: Required vs Aspirational Classification

> **"Don't penalize absence of excellence"**

Some elements indicate mature planning but aren't required for a valid WBP.

| Classification | Description | Penalty if Missing |
|---------------|-------------|-------------------|
| **REQUIRED** | Core structural elements | Yes - WBP is incomplete |
| **ASPIRATIONAL** | Mature planning indicators | No - but bonus if present |
| **CONDITIONAL** | Depends on scenario input | Only if scenario provides context |
| **N/A** | Outside WBP scope | Not evaluated |

**Applied to:**
- S6 (Blockers) → ASPIRATIONAL - identifying blockers depends on experience
- S8 (Parallel Workstreams) → ASPIRATIONAL - not all plans have parallelism
- S9 (Checkpoints) → ASPIRATIONAL - explicit verification points show maturity
- S16 (Assumptions) → ASPIRATIONAL - documenting assumptions is foresight
- S18 (Post-T-0 Actions) → ASPIRATIONAL - retrospectives are outside core scope
- S19 (Open Questions) → ASPIRATIONAL - identifies planner intelligence

### Principle 3: Conditional Dimensions

> **"Can't evaluate what wasn't provided"**

Some dimensions require additional scenario input to be evaluable.

| Dimension | Required Input |
|-----------|---------------|
| S10 (Resource-Aware) | Expertise mapping, availability windows, resource dependencies |
| S17 (Cross-team) | Explicit cross-team dependencies in scenario |

### Principle 4: Hallucination vs Good Planning

> **"Creative planning is GOOD; inventing facts is BAD"**

The grounding layer (G dimensions) distinguishes:

| Type | Example | Grounding |
|------|---------|-----------|
| **Hallucination (BAD)** | Inventing attendee "John Smith" not in scenario | Penalized by G1, G2 |
| **Good Planning (GOOD)** | Identifying blocker "budget approval delayed" | Allowed if consistent (G9) |

**G9 (Consistency Check)** enables this by:
- Allowing planner-generated content (assumptions, blockers, mitigations, open questions)
- Checking that content doesn't contradict scenario facts
- Verifying contextual plausibility

### Principle 5: Conceptual Consolidation

> **"Merge synonymous concepts; separate distinct ones"**

| Merged | Into | Rationale |
|--------|------|-----------|
| S11 (Risk Mitigation) | S6 | "Risk" and "Blocker" are synonymous in WBP context |
| S13 (Escalation) | S6 | Escalation is a type of mitigation |
| S12 (Communication) | S17 | Communication only relevant for cross-team work |

| Kept Separate | Reason |
|---------------|--------|
| S16 (Assumptions) vs S6 (Blockers) | Assumption = believed TRUE; Blocker = known obstacle NOW |
| S19 (Open Questions) vs S16 | Open Question = known UNKNOWN; Assumption = believed TRUE |

### Principle 6: Slot Type Grounding Taxonomy

> **"Different slot types have different truth sources"**

| Grounding | Description | Penalty |
|-----------|-------------|---------|
| **GROUNDED** | Must come from scenario | Hard fail if violated |
| **DERIVED** | Inferable from scenario context | Soft check |
| **CONDITIONAL** | Only grounded if scenario provides | N/A if not provided |
| **PLANNER-GEN** | Planner creates; G9 checks consistency | Allowed unless contradicts |
| **N/A** | Structural element, no grounding | Not checked |

### Principle 7: Flexibility Over Prescription

> **"Catch real issues, not style preferences"**

**Applied to S20 (Clarity):**
- Date format: "consistent and unambiguous" (not "must be YYYY-MM-DD")
- Ordering: "clear, logical order" (not "must be chronological")
- Task length: "ideally ≤12 words" (aspirational, not required)

---

## Framework Summary

### Structural Dimensions (S1-S20)

| Dimension | Status | Key Insight |
|-----------|--------|-------------|
| **S1-S5** | REQUIRED | Core WBP structure: details, timeline, ownership, deliverables, dates |
| **S6** | REQUIRED + ASPIRATIONAL | Dependencies required; blockers/mitigations aspirational |
| **S7** | N/A | Meeting outcomes are inputs, not WBP content |
| **S8** | ASPIRATIONAL | Parallel workstreams show mature planning |
| **S9** | ASPIRATIONAL | Explicit checkpoints show mature planning |
| **S10** | CONDITIONAL | Requires resource constraints input |
| **S11** | → Merged into S6 | Risk = Blocker |
| **S12** | → Merged into S17 | Communication relevant for cross-team only |
| **S13** | → Merged into S6 | Escalation is a type of mitigation |
| **S14** | N/A | Feedback loops are execution governance |
| **S15** | N/A | Progress tracking is operational |
| **S16** | ASPIRATIONAL | Assumptions show planner foresight |
| **S17** | CONDITIONAL | Requires cross-team dependency input |
| **S18** | ASPIRATIONAL | Post-T-0 tasks are outside core scope |
| **S19** | ASPIRATIONAL | Open questions show planner intelligence |
| **S20** | REQUIRED | Clarity is foundational for usability |

### Grounding Dimensions (G1-G9)

| Dimension | Purpose | Slot Types |
|-----------|---------|------------|
| **G1** | Hallucination check | ENTITY, ATTENDEE, ARTIFACT |
| **G2** | Attendee grounding | OWNER, ESCALATION_CONTACT, SKILL |
| **G3** | Date/time grounding | DATE, DUE_DATE, UNAVAILABLE_PERIOD |
| **G4** | Artifact grounding | ARTIFACT, DELIVERABLE, RESOURCE |
| **G5** | Topic grounding | TOPIC |
| **G6** | Action item grounding | TASK, ACTION_ITEM |
| **G7** | Context preservation | MEETING_DATE, ATTENDEE, ARTIFACT, GOAL |
| **G8** | Instruction adherence | ACTION_ITEM |
| **G9** | Planner-generated consistency | ASSUMPTION, BLOCKER, MITIGATION, OPEN_QUESTION, ESCALATION_TRIGGER |

### Key Slot Types Added

| Slot Type | Classification | Purpose |
|-----------|---------------|---------|
| ASSUMPTION | PLANNER-GEN | Condition believed TRUE at planning time |
| BLOCKER | PLANNER-GEN | Known obstacle (task or plan level) |
| MITIGATION | PLANNER-GEN | Action to address blocker |
| OPEN_QUESTION | PLANNER-GEN | Known unknown needing resolution |
| GOAL | CONDITIONAL | Plan objective/target outcome |
| SKILL | DERIVED | Expertise required for task |
| RESOURCE | CONDITIONAL | Non-people resource |
| ESCALATION_CONTACT | CONDITIONAL | Person for escalation |
| ESCALATION_TRIGGER | PLANNER-GEN | Condition triggering escalation |
| UNAVAILABLE_PERIOD | CONDITIONAL | Owner unavailability window |

---

## What Makes a Great WBP Agent?

A sophisticated WBP agent demonstrates **planning intelligence** by:

1. **Complete Structure** (REQUIRED): All core elements present - tasks, owners, dates, deliverables, dependencies

2. **Risk Awareness** (ASPIRATIONAL): Identifies blockers with mitigations and owners

3. **Foresight** (ASPIRATIONAL): Documents assumptions and their impacts if invalidated

4. **Intelligence** (ASPIRATIONAL): Proactively identifies open questions by analyzing data gaps

5. **Lifecycle Thinking** (ASPIRATIONAL): Includes post-T-0 tasks like retrospectives

6. **Clarity** (REQUIRED): Presents information in a clear, scannable, consistent format

---

## Evaluation Philosophy

```
+----------------------------------------------------------+
|                    WBP Quality Tiers                     |
+----------------------------------------------------------+
| TIER 1: Valid WBP                                        |
|   - All REQUIRED dimensions pass                         |
|   - No hallucinations (G1-G8 pass)                       |
|   - Clear presentation (S20 pass)                        |
+----------------------------------------------------------+
| TIER 2: Good WBP                                         |
|   - Tier 1 + Some ASPIRATIONAL dimensions present        |
|   - Blockers identified with mitigations (S6)            |
|   - Assumptions documented (S16)                         |
+----------------------------------------------------------+
| TIER 3: Excellent WBP                                    |
|   - Tier 2 + Most ASPIRATIONAL dimensions present        |
|   - Open questions identified (S19)                      |
|   - Post-T-0 planning (S18)                              |
|   - Checkpoints defined (S9)                             |
|   - Parallel workstreams identified (S8)                 |
+----------------------------------------------------------+
```

---

## Document References

- **Full Framework**: `dimension_examples_tables.md` - Complete S and G dimensions with assertions
- **Slot Types**: See "Slot Types Reference" section in `dimension_examples_tables.md`
- **GPT-5 Q&A Sessions**: `gpt5_prompts/2025-11-30/` - Design decision discussions

---

*This framework was developed through iterative GPT-5 consultation (3-run consolidation pattern) to ensure robust, well-reasoned design decisions.*
