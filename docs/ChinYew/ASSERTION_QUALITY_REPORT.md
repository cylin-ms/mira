# Workback Plan Assertion Quality Analysis Report

## Comprehensive Review & Mitigation Strategies

**Author:** Chin-Yew Lin  
**Date:** November 28, 2025  
**Analyst:** GPT-5 JJ Automated Analysis  
**Dataset:** Assertions_genv2_for_LOD1126part1.jsonl  
**Total Assertions Analyzed:** 2,318 (308 sampled for detailed critique)

---

## Executive Summary

This report presents a comprehensive analysis of the workback plan assertion framework, identifying systemic weaknesses and proposing actionable mitigation strategies. The analysis reveals a **critical insight**: the distinction between **bad specificity** (hardcoded values that don't generalize) and **good grounding** (parameterized verification against source data).

### Overall Assessment: Grade B

The current assertion set demonstrates solid foundational coverage with significant room for improvement.

### Key Findings

| Category | Finding | Impact |
|----------|---------|--------|
| **Core Issue** | 42% of assertions are overly specific | Cannot generalize to new meetings |
| **Framework Gap** | No distinction between structural and grounding checks | Hallucinations not detected |
| **Taxonomy** | 232 dimensions with 7 duplicate groups | Inflated metrics, inconsistent reporting |
| **Level Balance** | 55.6% marked critical (should be ~30%) | Evaluation fatigue |

### Key Recommendations

1. **Adopt Two-Layer Evaluation Framework**
   - Layer 1: Structural Patterns (S1-S19) - "Does the plan have X?"
     - S1-S10 (Core): Original 10 structural dimensions for essential WBP elements
     - S11-S18 (Extended): Additional dimensions for advanced planning aspects
   - Layer 2: Grounding Assertions (G1-G8) - "Is X factually correct?"

2. **Prioritize Grounding Over Structure**
   - A plan with good structure but hallucinations is **WORSE** than one that is incomplete but accurate

3. **Templatize Assertions**
   - Convert hardcoded values to parameterized templates
   - Target: Reduce specificity issues from 43% to <15%

4. **Consolidate Dimensions**
   - Reduce 232 dimensions to 12 canonical categories
   - Normalize naming conventions

### Quality Matrix (New Framework)

| Scenario | Structural | Grounding | Verdict |
|----------|------------|-----------|---------|
| Complete & Accurate | ✅ Pass | ✅ Pass | **EXCELLENT** |
| Complete but Hallucinated | ✅ Pass | ❌ Fail | **REJECT** ⚠️ |
| Accurate but Incomplete | ❌ Fail | ✅ Pass | **NEEDS WORK** |
| Neither | ❌ Fail | ❌ Fail | **POOR** |

### Estimated Improvement Potential

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Quality Score | 7.4/10 | 8.5+/10 | +15% |
| Applicability | 68% | 90%+ | +32% |
| Inter-rater Reliability | Unknown | >85% | Measurable |

---

## Table of Contents

1. [Part 1: Core Framework - Specificity vs. Grounding](#part-1-core-framework---specificity-vs-grounding)
   - [The Apparent Contradiction](#the-apparent-contradiction)
   - [Resolution: Specificity ≠ Grounding](#resolution-specificity--grounding)
   - [Two-Layer Evaluation Framework](#two-layer-evaluation-framework)
   - [Grounding Assertions (G1-G5)](#grounding-assertions-g1-g5)
   - [Quality Score Matrix](#quality-score-matrix)

2. [Part 2: Detailed Weakness Analysis](#part-2-detailed-weakness-analysis)
   - [Issue Distribution](#21-issue-distribution)
   - [Root Cause Analysis](#12-root-cause-analysis)

3. [Part 3: Mitigation Strategies](#part-3-mitigation-strategies)
   - [Strategy 1: Assertion Templatization](#strategy-1-assertion-templatization)
   - [Strategy 2: Dimension Consolidation](#strategy-2-dimension-consolidation)
   - [Strategy 3: Level Rebalancing](#strategy-3-level-rebalancing)
   - [Strategy 4: Generalization Pipeline](#strategy-4-generalization-pipeline)
   - [Strategy 5: Robustness Testing Framework](#strategy-5-robustness-testing-framework)
   - [Strategy 6: Human Judge Evaluation Framework](#strategy-6-human-judge-evaluation-framework)

4. [Part 4: Implementation Roadmap](#part-4-implementation-roadmap)
   - [Phase 1: Quick Wins (Week 1-2)](#phase-1-quick-wins-week-1-2)
   - [Phase 2: Systematic Improvements (Week 3-4)](#phase-2-systematic-improvements-week-3-4)
   - [Phase 3: Framework Evolution (Month 2)](#phase-3-framework-evolution-month-2)

5. [Part 5: Success Metrics](#part-5-success-metrics)
   - [Quality Metrics](#quality-metrics)
   - [Evaluation Metrics](#evaluation-metrics)

6. [Part 6: Appendices](#part-6-appendices)
   - [Appendix A: Low-Quality Assertion Examples](#appendix-a-low-quality-assertion-examples-with-rewrites)
   - [Appendix B: Pattern-to-Dimension Mapping](#appendix-b-pattern-to-dimension-mapping)
   - [Appendix C: Recommended Tool Enhancements](#appendix-c-recommended-tool-enhancements)
   - [Appendix D: GPT-5 Simulation & Examples](#appendix-d-gpt-5-simulation--examples)

7. [Conclusion](#conclusion)

---

## Part 1: Core Framework - Specificity vs. Grounding

> **This section establishes the foundational distinction between bad specificity and good grounding—a critical insight that underpins the entire assertion generation and evaluation methodology.**

### The Apparent Contradiction

| Earlier Finding | Grounding Requirement |
|-----------------|----------------------|
| "42% of assertions are overly specific" | "Assertions must verify facts against source" |

**Question:** If assertions need to be grounded to source facts, doesn't that require specificity?

### Resolution: Specificity ≠ Grounding

#### ❌ **Bad Specificity** (the 42% problem)
Assertions that are **tautologically tied to one example** and can't generalize:

```
"The response must mention Sarah Chen as the meeting organizer"
"The plan must reference Product_Launch_Checklist_v3.xlsx"
"The meeting is on January 15, 2025 at 2:00 PM"
```

These **only work for this one meeting** - useless as evaluation templates.

#### ✅ **Good Grounding** (parameterized verification)
Assertions with **parameterized references** that verify against source at runtime:

```
"All people mentioned must exist in {source.ATTENDEES}"
"All files must exist in {source.ENTITIES_TO_USE where type=File}"
"Meeting date must match {source.MEETING.StartTime}"
```

### Two-Layer Evaluation Framework

```
┌─────────────────────────────────────────────────────────────┐
│              STRUCTURAL PATTERNS (S1-S19)                   │
│         "Does the plan HAVE the right shape?"               │
├─────────────────────────────────────────────────────────────┤
│  S1-S10 (Core): Essential WBP elements                      │
│    S1: Has meeting date/time?              [pass/fail]      │
│    S2: Has backward timeline?              [pass/fail]      │
│    S3: Has task owners?                    [pass/fail]      │
│    ...S4-S10                                                │
│  S11-S19 (Extended): Advanced planning aspects              │
│    S11: Has risk mitigation strategy?      [pass/fail]      │
│    S12: Has milestone validation?          [pass/fail]      │
│    ...S13-S19                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              GROUNDING ASSERTIONS (G1-G8)                   │
│        "Are those elements FACTUALLY CORRECT?"              │
├─────────────────────────────────────────────────────────────┤
│  G1: Hallucination Check (overall)         [pass/fail]      │
│  G2: People exist in source.ATTENDEES?    [pass/fail]      │
│  G3: Dates derivable from source.MEETING? [pass/fail]      │
│  G4: Files exist in source.ENTITIES?      [pass/fail]      │
│  G5: Topics align with source.UTTERANCE?  [pass/fail]      │
│  G6: Tasks exist in source material?      [pass/fail]      │
└─────────────────────────────────────────────────────────────┘
```

### Key Concept: G Assertions Are Instantiated Through S Assertions

**G-level (grounding) assertions are never standalone.** They are always instantiated in the context of validating elements identified by S-level (structural) assertions:

1. **S-level assertions** define **what** structural elements should exist
2. **G-level assertions** define **grounding constraints** that validate those elements
3. The `linked_g_dims` field in each S assertion specifies which G checks apply

**Example:**
```
S2: "Each [TASK] must have a [DUE_DATE]..."
    └── linked_g_dims: ["G3", "G6"]
        ├── G3: Validate [DUE_DATE] consistency with meeting date
        └── G6: Validate [TASK] traces to action_items_discussed
```

### Grounding Assertions (G1-G8)

| ID | Name | Template | Applies To |
|----|------|----------|------------|
| G1 | Hallucination Check | No entities introduced that don't exist in source (overall) | All |
| G2 | People Grounding | All people mentioned must exist in {source.ATTENDEES} | S1, S3, S8 |
| G3 | Temporal Grounding | All dates must be derivable from {source.MEETING.StartTime} | S1, S2 |
| G4 | Artifact Grounding | All files must exist in {source.ENTITIES where type=File} | S4, S9 |
| G5 | Topic Grounding | Topics must align with {source.UTTERANCE} or {source.MEETING.Subject} | S5, S6 |
| G6 | Task Grounding | All tasks must exist in source material (verbs/to-dos) | S3, S6 |

### Evidence-Based Scoring

Require evaluators to cite **supporting spans** for grounding assertions:

```json
{
  "assertion": "G2 - Meeting date is accurate",
  "passed": true,
  "supporting_spans": [
    {
      "source": "MEETING_ENTITY",
      "text": "StartTime: 2025-01-15T14:00:00",
      "confidence": 1.0
    }
  ]
}
```

**Rule:** If `supporting_spans` is empty → grounding assertion cannot pass.

### Quality Score Matrix

| Scenario | Structural (S1-S19) | Grounding (G1-G8) | Overall Quality |
|----------|---------------------|-------------------|-----------------|
| Complete & Accurate | ✅ Pass | ✅ Pass | **Excellent** |
| Complete but Hallucinated | ✅ Pass | ❌ Fail | **Reject** |
| Accurate but Incomplete | ❌ Fail | ✅ Pass | **Needs Work** |
| Neither | ❌ Fail | ❌ Fail | **Poor** |

### Priority Order for Human Judges

**CRITICAL:** A plan that passes structural checks but fails grounding is **worse** than one that is incomplete but accurate. Hallucinated plans with good structure can mislead users.

**Priority Order (Revised):**
1. **Grounding (G1-G8)** - Factual accuracy first
2. **Critical Structural (S1, S2, S3, S9)** - Essential elements (weight=3)
3. **Expected Structural (S4, S5, S6, S7, S8, S10)** - Standard quality (weight=2)
4. **Extended Structural (S11-S18)** - Advanced planning aspects (weight=2)
   - S11: Risk Mitigation Strategy, S12: Milestone Validation
   - S13: Constraint Recognition, S14: Dependency Mapping
   - S15: Deliverable Specification, S16: Communication Plan
   - S17: Progress Tracking, S18: Contingency Planning

---

## Part 2: Detailed Weakness Analysis

### 2.1 Issue Distribution

Based on GPT-5 critique of 308 sampled assertions:

| Issue Type | Count | % of Total | Severity Distribution |
|------------|-------|------------|----------------------|
| **Specificity** | 186 | 43% | Mostly Medium |
| **Applicability** | 137 | 32% | Mixed |
| **Robustness** | 33 | 8% | High severity |
| **Redundancy** | 30 | 7% | Low severity |
| **Ambiguity** | 28 | 6% | Medium severity |
| **Measurability** | 13 | 3% | High severity |
| **Completeness** | 5 | 1% | Low severity |

### 1.2 Root Cause Analysis

#### **WEAKNESS 1: Over-Specificity (43% of issues)**

**Description:** Assertions are too tightly bound to specific instances, making them non-transferable to other workback plans.

**Examples of Problematic Assertions:**
```
❌ "The response should state that the meeting '1:1 Action Items Review' is scheduled for July 26, 2025"
❌ "The response should reference the file 'FeatureFlagRollout_ComplianceDeepDive.pptx'"
❌ "The response should identify Shakia Gencarelli as the meeting organizer"
```

**Root Causes:**
1. Assertions generated from specific examples without abstraction
2. Hardcoded dates, names, and file references
3. No separation between instance-specific and pattern-level requirements

---

#### **WEAKNESS 2: Limited Applicability (32% of issues)**

**Description:** Many assertions cannot be evaluated without access to the original context, making them unsuitable for general evaluation.

**Problem Pattern:**
- Assertions assume evaluators have access to specific entity data
- References to specific files, attendees, or dates that vary per meeting
- No fallback criteria for when expected data is unavailable

**Impact:**
- Evaluators cannot assess workback plans for new meetings
- High false-negative rate when context differs
- Increased evaluation time due to context lookup

---

#### **WEAKNESS 3: Dimension Taxonomy Chaos**

**Description:** The dimension naming is inconsistent, with duplicates and case variations creating confusion.

**Current State (232 unique dimensions):**
```
DUPLICATES FOUND:
├── "Timeline & Buffers" (337) vs "Timeline" (87)
├── "Artifact readiness" (263) vs "Artifact Readiness" (108)
├── "Ownership clarity" (241) vs "Ownership Clarity" (56) vs "Ownership" (55)
├── "Dependencies & sequencing" (142) vs "Dependencies & Sequencing" (120) vs "Dependencies" (44)
└── "Disclosure of missing info and assumptions" (70) vs "Disclosure of assumptions" (29)
```

**Impact:**
- Inflated dimension count (232 → should be ~15-20)
- Difficult to aggregate metrics by dimension
- Inconsistent reporting and analysis

---

#### **WEAKNESS 4: Unbalanced Level Distribution**

**Current Distribution:**
| Level | Count | Percentage |
|-------|-------|------------|
| Critical | 1,288 | 55.6% |
| Expected | 843 | 36.4% |
| Aspirational | 187 | 8.1% |

**Issues:**
- Too many assertions marked as "critical" (55% is excessive)
- Aspirational assertions underrepresented (only 8%)
- Level assignment appears inconsistent across dimensions

---

#### **WEAKNESS 5: Coverage Gaps**

**Missing Quality Dimensions:**
1. **Communication Quality** - Clarity, conciseness, tone
2. **Feasibility Assessment** - Are proposed timelines realistic?
3. **Progress Tracking** - Status indicators, checkpoints
4. **Risk Management** - Contingency plans, risk identification
5. **Prioritization** - Task priority ordering
6. **Resource Allocation** - Who has capacity?

---

#### **WEAKNESS 6: Low Robustness (8% of issues)**

**Description:** Assertions fail when applied to different meeting types or domains.

**Vulnerable Assertions:**
- Those assuming specific meeting formats (1:1 vs. team meeting vs. all-hands)
- Those expecting specific artifact types (presentations vs. documents)
- Those tied to specific organizational roles

---

## Part 3: Mitigation Strategies

### Strategy 1: Assertion Templatization

**Objective:** Convert specific assertions into parameterized templates

**Implementation:**

```python
# BEFORE: Specific assertion
"The response should state that the meeting '1:1 Action Items Review' is scheduled for July 26, 2025"

# AFTER: Parameterized template
"The response should state the meeting name and scheduled date/time accurately"

# WITH EVALUATION CRITERIA:
- Check if meeting name matches the provided context
- Check if date/time matches the calendar event
- Allow for reasonable time zone variations
```

**Template Library (19 Structural Patterns — S1-S19):**

#### Core Patterns (S1–S10) — Original 10 structural dimensions

| ID | Template | Dimension | Weight |
|----|----------|-----------|:------:|
| S1 | "The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES] accurately" | Meeting Details | 3 |
| S2 | "The response should include a backward timeline from T₀ with dependency-aware sequencing" | Timeline Alignment | 3 |
| S3 | "The response should assign an owner for each [TASK] or specify role/skill placeholder if name unavailable" | Ownership Assignment | 3 |
| S4 | "The response should list [DELIVERABLES] with working links, version/format specified" | Deliverables & Artifacts | 2 |
| S5 | "The response should include due dates for every [TASK] aligned with timeline sequencing" | Task Dates | 2 |
| S6 | "The response should identify [DEPENDENCIES/BLOCKERS] with mitigation steps documented" | Dependencies & Blockers | 2 |
| S7 | "The response should link [TASKS/ARTIFACTS] back to original source priorities/files" | Source Traceability | 2 |
| S8 | "The response should specify [COMMUNICATION CHANNELS] (Teams, email, meeting cadence)" | Communication Channels | 1 |
| S9 | "The response should only reference [ENTITIES] verified against source (meta-grounding check)" | Grounding Meta-Check | 2 |
| S10 | "The response should rank [TASKS] by critical path/impact on meeting success" | Priority Assignment | 2 |

#### Extended Patterns (S11–S18) — Additional dimensions for advanced planning

| ID | Template | Dimension | Weight |
|----|----------|-----------|:------:|
| S11 | "The response should include concrete [RISK MITIGATION] strategies with owners" | Risk Mitigation Strategy | 2 |
| S12 | "The response should validate [MILESTONES] are feasible, right-sized, and verifiable" | Milestone Validation | 2 |
| S13 | "The response should state clear [GOALS] and measurable [SUCCESS CRITERIA]" | Goal & Success Criteria | 2 |
| S14 | "The response should specify [RESOURCE ALLOCATION] (people/time/tools/budget)" | Resource Allocation | 2 |
| S15 | "The response should note [COMPLIANCE/GOVERNANCE] requirements (security, privacy, regulatory)" | Compliance & Governance | 1 |
| S16 | "The response should include [REVIEW/FEEDBACK] checkpoints to validate the plan" | Review & Feedback Loops | 1 |
| S17 | "The response should define [ESCALATION PATH] with owners for critical risks" | Escalation Path | 1 |
| S18 | "The response should list [POST-EVENT ACTIONS] (wrap-up, retrospectives, reporting)" | Post-Event Actions | 1 |

---

### Strategy 2: Dimension Consolidation

**Objective:** Consolidate legacy 232 dimensions into S1-S19 canonical framework

**New Taxonomy (S1-S19 + G1-G8):**

#### Core Structural Dimensions (S1–S10)

| ID | New Dimension | Merged From | Weight |
|----|---------------|-------------|:------:|
| S1 | **Meeting Details** | Meeting Objective & Scope, Meeting Context | 3 |
| S2 | **Timeline Alignment** | Timeline & Buffers, Timeline, Backward scheduling | 3 |
| S3 | **Ownership Assignment** | Ownership clarity, Ownership Clarity, Task Ownership | 3 |
| S4 | **Deliverables & Artifacts** | Artifact readiness, Artifact Readiness | 2 |
| S5 | **Task Dates** | Due dates, Task scheduling | 2 |
| S6 | **Dependencies & Blockers** | Dependencies & sequencing, Dependencies, Blockers | 2 |
| S7 | **Source Traceability** | Grounding & traceability, Source references | 2 |
| S8 | **Communication Channels** | Communication Quality, Coordination | 1 |
| S9 | **Grounding Meta-Check** | Entity grounding, Factual alignment | 2 |
| S10 | **Priority Assignment** | Prioritization, Critical path | 2 |

#### Extended Structural Dimensions (S11–S18)

| ID | New Dimension | Merged From | Weight |
|----|---------------|-------------|:------:|
| S11 | **Risk Mitigation Strategy** | Assumptions & Risks, Risk management | 2 |
| S12 | **Milestone Validation** | Feasibility, Milestone coherence | 2 |
| S13 | **Goal & Success Criteria** | Success metrics, Objectives | 2 |
| S14 | **Resource Allocation** | Resource Allocation, Budget/tools | 2 |
| S15 | **Compliance & Governance** | Regulatory, Security checks | 1 |
| S16 | **Review & Feedback Loops** | Progress Tracking, Review checkpoints | 1 |
| S17 | **Escalation Path** | Escalation procedures, Contact chain | 1 |
| S18 | **Post-Event Actions** | Wrap-up, Retrospectives | 1 |

#### Grounding Dimensions (G1–G6)

| ID | Dimension | Weight |
|----|-----------|:------:|
| G1 | **Hallucination Check** (overall) | 3 |
| G2 | **Attendee Grounding** | 3 |
| G3 | **Date/Time Grounding** | 3 |
| G4 | **Artifact Grounding** | 2 |
| G5 | **Topic Grounding** | 2 |
| G6 | **Task Grounding** | 3 |

**Migration Script:**
```python
# Maps legacy dimension names to S1-S19 canonical IDs
DIMENSION_MAP = {
    # S1: Meeting Details
    "Meeting Objective & Scope": "S1",
    "Meeting Context": "S1",
    
    # S2: Timeline Alignment
    "Timeline & Buffers": "S2",
    "Timeline": "S2",
    "Backward scheduling": "S2",
    
    # S3: Ownership Assignment
    "Ownership clarity": "S3",
    "Ownership Clarity": "S3",
    "Ownership": "S3",
    "Task Ownership": "S3",
    
    # S4: Deliverables & Artifacts
    "Artifact readiness": "S4",
    "Artifact Readiness": "S4",
    
    # S5: Task Dates
    "Due dates": "S5",
    "Task scheduling": "S5",
    
    # S6: Dependencies & Blockers
    "Dependencies & sequencing": "S6",
    "Dependencies & Sequencing": "S6",
    "Dependencies": "S6",
    "Blockers": "S6",
    
    # S7: Source Traceability
    "Grounding & traceability": "S7",
    "Source references": "S7",
    
    # S8: Communication Channels
    "Communication Quality": "S8",
    "Coordination": "S8",
    
    # S9: Grounding Meta-Check
    "Entity grounding": "S9",
    "Factual alignment": "S9",
    
    # S10: Priority Assignment
    "Prioritization": "S10",
    "Critical path": "S10",
    
    # S11: Risk Mitigation Strategy
    "Assumptions & Risks": "S11",
    "Disclosure of missing info and assumptions": "S11",
    "Disclosure of assumptions": "S11",
    "Risk management": "S11",
    
    # S12: Milestone Validation
    "Feasibility": "S12",
    "Milestone coherence": "S12",
    
    # S13: Goal & Success Criteria
    "Success metrics": "S13",
    "Objectives": "S13",
    
    # S14: Resource Allocation
    "Resource Allocation": "S14",
    "Budget/tools": "S14",
    
    # S15: Compliance & Governance
    "Regulatory": "S15",
    "Security checks": "S15",
    
    # S16: Review & Feedback Loops
    "Progress Tracking": "S16",
    "Review checkpoints": "S16",
    
    # S17: Escalation Path
    "Escalation procedures": "S17",
    "Contact chain": "S17",
    
    # S18: Post-Event Actions
    "Wrap-up": "S18",
    "Retrospectives": "S18",
}
```

---

### Strategy 3: Level Rebalancing

**Objective:** Achieve a more appropriate distribution of assertion levels

**Target Distribution:**
| Level | Current | Target | Rationale |
|-------|---------|--------|-----------|
| Critical | 55.6% | 30-35% | Only truly essential requirements |
| Expected | 36.4% | 45-50% | Standard quality bar |
| Aspirational | 8.1% | 15-25% | Excellence indicators |

**Level Assignment Criteria:**

**CRITICAL (Must Pass):**
- Factual accuracy (dates, times, attendees)
- Safety and compliance requirements
- Core functionality (provides a timeline)

**EXPECTED (Should Pass):**
- Task ownership assignments
- Artifact identification
- Dependency sequencing
- Reasonable buffer times

**ASPIRATIONAL (Excellence):**
- Proactive risk identification
- Stakeholder alignment suggestions
- Assumption transparency
- Communication quality

**Rebalancing Algorithm:**
```python
def rebalance_level(assertion, current_level):
    # Downgrade over-marked criticals
    if current_level == "critical":
        if is_preference_based(assertion):
            return "expected"
        if is_excellence_indicator(assertion):
            return "aspirational"
    
    # Upgrade under-marked aspirationals
    if current_level == "expected":
        if is_proactive_quality(assertion):
            return "aspirational"
    
    return current_level
```

---

### Strategy 4: Generalization Pipeline

**Objective:** Systematically convert specific assertions to generalizable ones

**Step 1: Entity Extraction**
```python
# Identify specific entities in assertion text
entities = extract_entities(assertion_text)
# Returns: {"PERSON": ["John Smith"], "DATE": ["July 26"], "FILE": ["report.pptx"]}
```

**Step 2: Parameterization**
```python
# Replace specific values with placeholders
generalized = parameterize(assertion_text, entities)
# "John Smith should..." → "[MEETING_ORGANIZER] should..."
# "by July 26" → "by [MEETING_DATE - N days]"
```

**Step 3: Context Binding**
```python
# Create evaluation function that binds to context at runtime
def evaluate(assertion_template, context):
    bound_assertion = bind_parameters(assertion_template, context)
    return check_response_against(bound_assertion)
```

---

### Strategy 5: Robustness Testing Framework

**Objective:** Ensure assertions work across diverse meeting types

**Test Matrix:**

| Meeting Type | Timeline | Ownership | Artifacts | Dependencies |
|--------------|----------|-----------|-----------|--------------|
| 1:1 Meeting | ✓ | ✓ | ✓ | ✓ |
| Team Standup | ✓ | ✓ | ~ | ~ |
| All-Hands | ✓ | ✓ | ✓ | ✓ |
| Project Review | ✓ | ✓ | ✓ | ✓ |
| Client Meeting | ✓ | ✓ | ✓ | ✓ |
| Training Session | ✓ | ✓ | ✓ | ~ |

**Robustness Score Calculation:**
```
Robustness = (Passing Test Cases / Total Test Cases) × 100

Target: >80% for Critical, >70% for Expected, >60% for Aspirational
```

---

### Strategy 6: Human Judge Evaluation Framework

**Objective:** Provide clear, consistent guidelines for human evaluators

**Evaluation Workflow:**

```
┌─────────────────────────────────────────────────────────────┐
│                    EVALUATION WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│  PHASE 1: FACTUAL ACCURACY (Critical)                       │
│  □ Meeting date/time correct?                               │
│  □ Attendees match context?                                 │
│  □ No fabricated information?                               │
├─────────────────────────────────────────────────────────────┤
│  PHASE 2: STRUCTURAL COMPLETENESS (Critical + Expected)     │
│  □ Backward timeline present?                               │
│  □ Tasks have owners?                                       │
│  □ Artifacts identified?                                    │
│  □ Dependencies sequenced?                                  │
├─────────────────────────────────────────────────────────────┤
│  PHASE 3: CLARITY & TRANSPARENCY (Expected)                 │
│  □ Meeting purpose stated?                                  │
│  □ Assumptions disclosed?                                   │
│  □ Instructions clear?                                      │
├─────────────────────────────────────────────────────────────┤
│  PHASE 4: EXCELLENCE INDICATORS (Aspirational)              │
│  □ Risks identified?                                        │
│  □ Stakeholder alignment included?                          │
│  □ Proactive suggestions offered?                           │
└─────────────────────────────────────────────────────────────┘
```

**Scoring Rubric:**

| Score | Label | Criteria |
|-------|-------|----------|
| 5 | Excellent | All critical pass, >90% expected pass, >50% aspirational pass |
| 4 | Good | All critical pass, >80% expected pass |
| 3 | Acceptable | All critical pass, >60% expected pass |
| 2 | Needs Work | 1-2 critical failures, <60% expected pass |
| 1 | Poor | Multiple critical failures |

---

## Part 4: Implementation Roadmap

### Phase 1: Quick Wins (Week 1-2)

| Action | Owner | Effort | Impact |
|--------|-------|--------|--------|
| Normalize dimension casing | Data Team | 2 hours | High |
| Merge duplicate dimensions | Data Team | 4 hours | High |
| Document level criteria | PM | 4 hours | Medium |
| Create evaluation checklist | PM | 2 hours | Medium |

### Phase 2: Systematic Improvements (Week 3-4)

| Action | Owner | Effort | Impact |
|--------|-------|--------|--------|
| Build templatization pipeline | Engineering | 2 days | High |
| Rebalance assertion levels | Data + PM | 1 day | Medium |
| Add missing dimensions | PM | 1 day | Medium |
| Create robustness test suite | QA | 2 days | High |

### Phase 3: Framework Evolution (Month 2)

| Action | Owner | Effort | Impact |
|--------|-------|--------|--------|
| Implement parameterized assertions | Engineering | 1 week | Very High |
| Build human evaluation UI | Engineering | 1 week | High |
| Train evaluators | PM | 2 days | High |
| Pilot with 50 new meetings | All | 1 week | High |

---

## Part 5: Success Metrics

### Quality Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Average assertion quality score | 7.4/10 | 8.5/10 | 4 weeks |
| Specificity issues | 43% | <15% | 4 weeks |
| Applicability issues | 32% | <10% | 4 weeks |
| Unique dimensions | 232 | 12 | 2 weeks |

### Evaluation Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Inter-rater reliability | Unknown | >0.85 | 6 weeks |
| Evaluation time per meeting | Unknown | <10 min | 4 weeks |
| False positive rate | Unknown | <5% | 6 weeks |
| False negative rate | Unknown | <10% | 6 weeks |

---

## Part 6: Appendices

### Appendix A: Low-Quality Assertion Examples with Rewrites

| Original (Score ≤5) | Issue | Rewritten |
|---------------------|-------|-----------|
| "The response should identify Shakia Gencarelli as the meeting organizer" | Specificity | "The response should identify the meeting organizer by name as shown in the calendar event" |
| "The response should reference the file 'FeatureFlagRollout_ComplianceDeepDive.pptx'" | Specificity | "The response should reference relevant files from the meeting context as pre-read materials" |
| "The response should include a step to draft the agenda outline by July 26, 00:00 PST" | Specificity, Applicability | "The response should include a step to draft the agenda outline at least 24 hours before T₀" |

### Appendix B: Pattern-to-Dimension Mapping

| Pattern | Primary Dimension | Secondary Dimensions |
|---------|-------------------|---------------------|
| S1: Explicit Meeting Details | Timeline & Scheduling | Meeting Context |
| S2: Timeline Backward Planning | Timeline & Scheduling | Dependencies |
| S3: Ownership Assignment | Task Ownership | - |
| S4: Artifact Specification | Artifact Readiness | Timeline & Scheduling |
| S5: Dependency Sequencing | Dependencies | Task Ownership |
| S6: Meeting Objective Clarity | Meeting Context | - |
| S7: Assumption Disclosure | Assumptions & Risks | - |
| S8: Stakeholder Alignment | Stakeholder Alignment | Communication Quality |
| S9: Grounding in Context | Meeting Context | - |
| S10: Risk Identification | Assumptions & Risks | - |

### Appendix C: Recommended Tool Enhancements

1. **Assertion Linter** - Automated check for specificity issues
2. **Dimension Normalizer** - Auto-correct dimension naming
3. **Level Suggester** - ML-based level recommendation
4. **Coverage Analyzer** - Gap detection across dimensions
5. **Robustness Tester** - Cross-meeting-type validation

### Appendix D: GPT-5 Simulation & Examples

To validate the two-layer evaluation framework, we created a GPT-5 JJ simulation that generates workback plans at three quality levels (Perfect, Medium, Low) and evaluates them against both **Structural Patterns (S1-S19)** and **Grounding Assertions (G1-G8)**.

**What the simulation demonstrates:**
- How structural assertions check if a plan "has the right shape"
- How grounding assertions verify factual accuracy against source data
- Detection of hallucinations (e.g., fabricated attendees, wrong dates)
- The quality matrix in action: a well-structured plan with hallucinations is **REJECTED**

**Results Summary:**

| Quality | Structural | Grounding | Combined | Verdict |
|---------|-----------|-----------|----------|----------|
| Perfect | 100/100 | 44/50 | 144/150 | EXCELLENT |
| Medium | 49/100 | 45/50 | 94/150 | NEEDS WORK |
| Low | 7/100 | 25/50 | 32/150 | POOR |

**GitHub Resources:**

| Resource | Description | Link |
|----------|-------------|------|
| **GPT-5 Simulation Script** | Python script to generate plans and evaluate with two-layer framework | [generate_plan_examples_gpt5.py](https://github.com/cylin-ms/mira/blob/master/generate_plan_examples_gpt5.py) |
| **Generated Report** | Full evaluation report with Perfect/Medium/Low plan examples | [PLAN_QUALITY_EXAMPLES_GPT5.md](https://github.com/cylin-ms/mira/blob/master/docs/ChinYew/PLAN_QUALITY_EXAMPLES_GPT5.md) |
| **Raw JSON Data** | Structured data including plans, assertions, and evaluations | [plan_examples_gpt5.json](https://github.com/cylin-ms/mira/blob/master/docs/ChinYew/plan_examples_gpt5.json) |
| **Assertion Patterns** | S1-S19 structural patterns with G1-G8 grounding requirements | [assertion_patterns.json](https://github.com/cylin-ms/mira/blob/master/docs/ChinYew/assertion_patterns.json) |

---

## Conclusion

The current assertion framework provides solid coverage of workback plan quality dimensions but suffers from **over-specificity**, **dimension fragmentation**, and **unbalanced severity levels**. 

By implementing the proposed mitigation strategies—**templatization**, **dimension consolidation**, **level rebalancing**, and **robustness testing**—the framework can evolve into a **generalizable, maintainable, and effective** evaluation system.

**Estimated improvement potential:**
- Quality score: 7.4 → 8.5+ (15% improvement)
- Applicability: 68% → 90%+ (32% improvement)
- Evaluation consistency: Unknown → >85% inter-rater reliability

---

*Report generated by GPT-5 JJ Analysis Pipeline*  
*Updated: November 28, 2025 - Added Two-Layer Evaluation Framework*  
*For questions, contact the Mira evaluation team*
