"""
Dimension definitions for the Mira 2.0 WBP framework.

Three-Layer Framework: S → G → M
================================
- S (Structural, S1-S20): Check IF something exists (have/have not) - INDEPENDENT
- G (Grounding, G2-G10): Check if VALUE matches source - INDEPENDENT  
- M (Meta, M1): Check for unsupported facts (hallucination) - DEPENDENT on all Gs

Key Design Insight (2025-11-30):
- S and G assertions are INDEPENDENT - each can be verified on its own
- M1 (Hallucination) is DERIVED - cannot be computed without ALL G results
- G1 was REMOVED - hallucination prevention moved to M layer (M1)

Dimension Status Classifications:
- REQUIRED: Core structural elements, penalized if missing
- ASPIRATIONAL: Nice-to-have, not penalized if missing, bonus if present
- CONDITIONAL: Requires additional scenario input to be evaluable
- N/A: Not applicable to WBP evaluation (operational, not planning)
- MERGED: Consolidated into another dimension

Key Concept: G Assertions Are Instantiated Through S Assertions
==============================================================
G-level (grounding) assertions are NEVER standalone. They are always
instantiated in the context of validating elements identified by S-level
(structural) assertions.

Relationship:
1. S-level assertions define WHAT structural elements should exist
   (tasks, dates, owners, deliverables, etc.)
2. G-level assertions define GROUNDING CONSTRAINTS that validate those
   elements against the source scenario
3. The S_TO_G_MAP below specifies which G checks apply to each S dimension

G Assertion Independence:
========================
Each G assertion is SELF-CONTAINED. For example:
- G10 checks if RELATION(X, Y) exists in source
- It does NOT depend on whether X or Y are correct (that's G2/G6's job)
- If arguments are wrong, that's a separate error counted by other G assertions

Assertion Format (Hybrid):
==========================
Each assertion now uses a hybrid format with:
- template: Contains [SLOT_TYPE] placeholders (e.g., [ATTENDEE], [TASK])
- instantiated: Concrete example with actual values from reference scenario
- slot_types: List of slot types used in the template
- sub_aspect: Specific aspect of the dimension being checked
- linked_g_dims: G dimensions that apply when this S assertion is evaluated

Example:
    {
        "assertion_id": "S2_A1",
        "template": "Each [TASK] must have a [DUE_DATE] before the [MEETING_DATE].",
        "instantiated": "Each task like 'finalize slides' must have a due date before March 15, 2025.",
        "slot_types": ["TASK", "DUE_DATE", "MEETING_DATE"],
        "sub_aspect": "Task deadline alignment",
        "linked_g_dims": ["G3", "G6"]
    }

Slot Types Reference:
====================
- [ATTENDEE]: Person from the attendee list (e.g., Alice Chen, Bob Smith)
- [DATE]: An absolute date (e.g., March 15, 2025)
- [MEETING_DATE]: The meeting date from the scenario
- [DUE_DATE]: A task due date
- [ARTIFACT]: A file or document reference (e.g., Q1_slides.pptx)
- [TOPIC]: An agenda topic (e.g., budget allocation)
- [ACTION_ITEM]: An action item from the scenario (e.g., finalize slides)
- [TASK]: A task name or description
- [OWNER]: A task owner (same as ATTENDEE but in ownership context)
- [DELIVERABLE]: An output or deliverable
- [MEETING_TITLE]: The title of the meeting
- [ENTITY]: Any named entity that could be hallucinated

The G definitions serve as a REFERENCE LIBRARY that S assertions link to.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# S → G MAPPING (which grounding dimensions apply to each structural dimension)
# ═══════════════════════════════════════════════════════════════════════════════

# Dimension Status:
#   REQUIRED: S1-S5, S20
#   REQUIRED+ASPIRATIONAL: S6 (dependencies required, blockers aspirational)
#   ASPIRATIONAL: S8, S9, S16, S18, S19
#   CONDITIONAL: S10, S17
#   N/A: S7, S11 (merged→S6), S12 (merged→S17), S13 (merged→S6), S14, S15

S_TO_G_MAP = {
    "S1": ["G2", "G3", "G5"],      # Meeting Details → Attendee, Date/Time, Topic (REQUIRED)
    "S2": ["G3", "G6", "G10"],     # Timeline → Date/Time, Action Items, Relations (REQUIRED) - G10 for dependency ordering
    "S3": ["G2", "G6", "G10"],     # Ownership → Attendee, Action Items, Relations (REQUIRED) - G10 for OWNS relation
    "S4": ["G4", "G5"],             # Deliverables → Artifact, Topic (REQUIRED)
    "S5": ["G3"],                   # Task Dates → Date/Time (REQUIRED)
    "S6": ["G2", "G6", "G7", "G9", "G10"], # Dependencies & Blockers → Attendee, Action Items, Context, Consistency, Relations (REQUIRED+ASPIRATIONAL) - G10 for DEPENDS_ON, BLOCKS
    "S7": [],                        # Meeting Outcomes → N/A (not applicable to WBP)
    "S8": ["G2", "G6"],             # Parallel Workstreams → Attendee, Action Items (ASPIRATIONAL)
    "S9": ["G2", "G3", "G6"],       # Checkpoints → Attendee, Date/Time, Action Items (ASPIRATIONAL)
    "S10": ["G2", "G3", "G4", "G6"],# Resource-Aware Planning → Attendee, Date/Time, Artifact, Action Items (CONDITIONAL)
    "S11": [],                       # Risk Mitigation → MERGED into S6
    "S12": [],                       # Communication Plan → MERGED into S17
    "S13": [],                       # Escalation Protocol → MERGED into S6
    "S14": [],                       # Feedback Integration → N/A (operational)
    "S15": [],                       # Progress Tracking → N/A (operational)
    "S16": ["G5", "G6", "G9"],      # Assumptions → Topic, Action Items, Consistency (ASPIRATIONAL)
    "S17": ["G2", "G3", "G6", "G10"], # Cross-team Coordination → Attendee, Date/Time, Action Items, Relations (CONDITIONAL) - G10 for cross-team dependencies
    "S18": ["G2", "G3", "G6"],      # Post-Event Actions → Attendee, Date/Time, Action Items (ASPIRATIONAL)
    "S19": ["G2", "G3", "G6", "G9"],# Open Questions → Attendee, Date/Time, Action Items, Consistency (ASPIRATIONAL)
    "S20": ["G2", "G3", "G5", "G7"],# Clarity → Attendee, Date/Time, Topic, Context (REQUIRED)
}

# ═══════════════════════════════════════════════════════════════════════════════
# G RATIONALE FOR S - Why each G dimension applies to its parent S dimension
# ═══════════════════════════════════════════════════════════════════════════════

G_RATIONALE_FOR_S = {
    # S1: Meeting Details (REQUIRED)
    ("S1", "G2"): "Meeting details must reference actual attendees from the meeting context to verify participant accuracy",
    ("S1", "G3"): "Meeting details must match the actual meeting date/time to ensure schedule accuracy",
    ("S1", "G5"): "Meeting subject/agenda must align with actual topics from the meeting context",
    
    # S2: Timeline Alignment (REQUIRED)
    ("S2", "G3"): "Timeline sequencing requires verifying that scheduled dates are consistent with the actual meeting date and don't conflict",
    ("S2", "G6"): "Task ordering in the timeline must be traceable to actual action items discussed in the meeting",
    
    # S3: Ownership Assignment (REQUIRED)
    ("S3", "G2"): "Task owners must be actual attendees who can be held accountable for the work",
    ("S3", "G6"): "Ownership assignments must correspond to action items that were actually agreed upon",
    
    # S4: Deliverables & Artifacts (REQUIRED)
    ("S4", "G4"): "Referenced deliverables/documents must actually exist or be creatable from available artifacts",
    ("S4", "G5"): "Deliverables must align with topics actually discussed, not fabricated requirements",
    
    # S5: Task Dates (REQUIRED)
    ("S5", "G3"): "Task start/end dates must be consistent with the meeting date and realistic timeframes",
    
    # S6: Dependencies, Blockers & Mitigation (REQUIRED + ASPIRATIONAL) - merged S11, S13
    ("S6", "G2"): "Mitigation owners and escalation contacts must be actual attendees",
    ("S6", "G6"): "Dependencies and blockers should be traceable to action items or issues raised in the discussion",
    ("S6", "G7"): "Plan-level blockers affecting goals must preserve original scenario context",
    ("S6", "G9"): "Planner-identified blockers, mitigations, and escalation triggers must not contradict scenario facts",
    
    # S7: Meeting Outcomes (N/A - not applicable to WBP evaluation)
    # No rationale needed - dimension is N/A
    
    # S8: Parallel Workstreams (ASPIRATIONAL)
    ("S8", "G2"): "Parallel task owners must be actual attendees",
    ("S8", "G6"): "Parallel workstreams must be traceable to action items that can actually run concurrently",
    
    # S9: Checkpoints (ASPIRATIONAL)
    ("S9", "G2"): "Checkpoint task owners must be actual attendees",
    ("S9", "G3"): "Checkpoint dates must be consistent with the meeting date and task timeline",
    ("S9", "G6"): "Checkpoints should verify progress on actual action items from the meeting",
    
    # S10: Resource-Aware Planning (CONDITIONAL - requires resource constraints input)
    ("S10", "G2"): "Resources must be allocated to actual attendees or their teams",
    ("S10", "G3"): "Task dates must respect owner unavailability periods if provided",
    ("S10", "G4"): "Resource dependencies (budget, equipment) must match scenario if provided",
    ("S10", "G6"): "Skill requirements must be traceable to tasks discussed",
    
    # S11: Risk Mitigation Strategy (MERGED into S6)
    # No rationale needed - dimension is merged
    
    # S12: Communication Plan (MERGED into S17)
    # No rationale needed - dimension is merged
    
    # S13: Escalation Protocol (MERGED into S6)
    # No rationale needed - dimension is merged
    
    # S14: Feedback Integration (N/A - operational, not planning)
    # No rationale needed - dimension is N/A
    
    # S15: Progress Tracking (N/A - operational, not planning)
    # No rationale needed - dimension is N/A
    
    # S16: Assumptions & Prerequisites (ASPIRATIONAL)
    ("S16", "G5"): "Stated assumptions must relate to actual topics discussed",
    ("S16", "G6"): "Assumptions affecting task prerequisites must be traceable to action items",
    ("S16", "G9"): "Planner-stated assumptions must not contradict scenario facts",
    
    # S17: Cross-team Coordination (CONDITIONAL - requires cross-team dependency input)
    ("S17", "G2"): "Cross-team contacts must be actual attendees or verified stakeholders",
    ("S17", "G3"): "Cross-team handoff dates must be consistent with timeline",
    ("S17", "G6"): "Cross-team tasks must be traceable to discussed action items",
    ("S17", "G10"): "Cross-team dependency relations must be grounded in scenario discussions",
    
    # S18: Post-Event Actions (ASPIRATIONAL)
    ("S18", "G2"): "Post-event task owners must be actual attendees",
    ("S18", "G3"): "Follow-up dates must be after T-0 and realistic",
    ("S18", "G6"): "Follow-up actions must trace to actual discussion outcomes",
    
    # S19: Open Questions & Decision Points (ASPIRATIONAL)
    ("S19", "G2"): "Question owners must be actual attendees",
    ("S19", "G3"): "Question resolution dates must be consistent with dependent task timelines",
    ("S19", "G6"): "Questions must relate to actual action items or tasks",
    ("S19", "G9"): "Open questions must not ask about information already in the scenario",
    
    # S20: Clarity & First Impression (REQUIRED)
    ("S20", "G2"): "Owner names must match attendee list for consistency",
    ("S20", "G3"): "Date formats must be consistent and valid",
    ("S20", "G5"): "Goal statement must align with meeting topics",
    ("S20", "G7"): "Title and context must preserve original scenario meaning",
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # G10: Relation Grounding - rationales for each S dimension that uses G10
    # ═══════════════════════════════════════════════════════════════════════════════
    # G10 verifies that RELATIONSHIPS between entities are grounded in the scenario,
    # not just that the entities themselves exist. Relation types:
    #   DEPENDS_ON(TaskA, TaskB): TaskA depends on TaskB (prerequisite)
    #   BLOCKS(Blocker, Task): Blocker prevents Task from proceeding
    #   OWNS(Attendee, Task): Person is responsible for Task
    #   PRODUCES(Task, Deliverable): Task produces Deliverable
    #   REQUIRES_INPUT(Task, Artifact): Task needs Artifact as input
    
    ("S2", "G10"): "Dependency ordering (prerequisite before dependent) must be grounded in scenario-stated or logically-derived DEPENDS_ON relations",
    ("S3", "G10"): "Ownership assignments must be grounded in scenario-stated or role-derived OWNS relations",
    ("S6", "G10"): "Dependencies and blockers must be grounded in scenario-stated DEPENDS_ON and BLOCKS relations",
    ("S17", "G10"): "Cross-team dependencies must be grounded in scenario-stated DEPENDS_ON relations across teams",
}

# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION NAMES
# ═══════════════════════════════════════════════════════════════════════════════

DIMENSION_NAMES = {
    # Structural (S1-S20) with status
    "S1": "Meeting Details",                      # REQUIRED
    "S2": "Timeline Alignment",                   # REQUIRED
    "S3": "Ownership Assignment",                 # REQUIRED
    "S4": "Deliverables & Artifacts",             # REQUIRED
    "S5": "Task Dates",                           # REQUIRED
    "S6": "Dependencies, Blockers & Mitigation", # REQUIRED + ASPIRATIONAL (merged S11, S13)
    "S7": "Meeting Outcomes",                     # N/A (not applicable to WBP)
    "S8": "Parallel Workstreams",                 # ASPIRATIONAL
    "S9": "Checkpoints",                          # ASPIRATIONAL
    "S10": "Resource-Aware Planning",             # CONDITIONAL
    "S11": "Risk Mitigation Strategy",            # MERGED into S6
    "S12": "Communication Plan",                  # MERGED into S17
    "S13": "Escalation Protocol",                 # MERGED into S6
    "S14": "Feedback Integration",                # N/A (operational)
    "S15": "Progress Tracking",                   # N/A (operational)
    "S16": "Assumptions & Prerequisites",         # ASPIRATIONAL
    "S17": "Cross-team Coordination",             # CONDITIONAL
    "S18": "Post-Event Actions",                  # ASPIRATIONAL
    "S19": "Open Questions & Decision Points",   # ASPIRATIONAL (renamed from Caveat)
    "S20": "Clarity & First Impression",          # REQUIRED
    # Grounding (G2-G10) - G1 moved to M layer as M1
    # NOTE: G1 (Hallucination Check) was REMOVED from G layer.
    # Hallucination is now M1 in Meta layer because it's DERIVED from all G results.
    "G1": "DEPRECATED - See M1",                  # MOVED to M layer (was Hallucination Check)
    "G2": "Attendee Grounding",
    "G3": "Date/Time Grounding",
    "G4": "Artifact Grounding",
    "G5": "Topic Grounding",
    "G6": "Action Item Grounding",
    "G7": "Context Preservation",
    "G8": "Instruction Adherence",
    "G9": "Planner-Generated Consistency",        # checks assumptions, blockers, mitigations, open questions
    "G10": "Relation Grounding",                  # verifies relationships between entities (DEPENDS_ON, OWNS, etc.)
    # Meta Layer (M1) - DEPENDENT on all G results
    "M1": "No Hallucination",                     # DERIVED from all G2-G10 results
}

# ═══════════════════════════════════════════════════════════════════════════════
# SLOT TYPES REFERENCE
# ═══════════════════════════════════════════════════════════════════════════════

# Slot Type Grounding Legend:
#   GROUNDED: Must come from scenario (hard requirement, penalized if violated)
#   DERIVED: Can be reasonably inferred from scenario context
#   CONDITIONAL: Only grounded if scenario provides the information
#   PLANNER-GEN: Planner can create reasonable values (checked by G9 for consistency)
#   N/A: Structural element, no grounding needed

SLOT_TYPES = {
    # GROUNDED slot types (must match scenario)
    "ATTENDEE": "Person from the attendee list (e.g., Alice Chen, Bob Smith)",           # GROUNDED → G2
    "OWNER": "A task owner (subset of attendees)",                                       # GROUNDED → G2
    "DATE": "An absolute date (e.g., March 15, 2025)",                                   # GROUNDED → G3
    "MEETING_DATE": "The meeting date from the scenario",                                # GROUNDED → G3, G7
    "DUE_DATE": "A task due date",                                                       # GROUNDED → G3
    "ARTIFACT": "A file or document reference (input, exists now)",                      # GROUNDED → G4
    "DELIVERABLE": "Planned output of a task (future)",                                  # GROUNDED → G4
    "TOPIC": "An agenda topic (e.g., budget allocation)",                                # GROUNDED → G5
    "ACTION_ITEM": "An action item from the scenario (e.g., finalize slides)",           # GROUNDED → G6, G8
    "TASK": "A task name or description",                                                # GROUNDED → G6
    "MEETING_TITLE": "The title of the meeting",                                         # GROUNDED → G5 (topic)
    "ENTITY": "Any named entity (person, file, date, topic) that could be hallucinated",# GROUNDED → M1 (meta)
    # DERIVED slot types (inferable from scenario)
    "GOAL_STATEMENT": "Meeting objective summary",                                       # DERIVED → G5, G7
    "SKILL": "Expertise/capability required for a task",                                 # DERIVED → G2
    # CONDITIONAL slot types (only grounded if scenario provides)
    "GOAL": "The plan's objective/target outcome",                                       # CONDITIONAL → G7
    "ESCALATION_CONTACT": "Person with authority for escalation",                        # CONDITIONAL → G2
    "RESOURCE": "Non-people resource (budget, equipment)",                               # CONDITIONAL → G4
    "UNAVAILABLE_PERIOD": "Time window when OWNER unavailable",                          # CONDITIONAL → G3
    # PLANNER-GEN slot types (checked by G9 for consistency)
    "ASSUMPTION": "Condition believed true at planning time",                            # PLANNER-GEN → G9
    "BLOCKER": "Obstacle (task-level or plan-level)",                                    # PLANNER-GEN → G9
    "MITIGATION": "Action/plan to address a blocker",                                    # PLANNER-GEN → G9
    "OPEN_QUESTION": "Known unknown needing resolution for plan success",                # PLANNER-GEN → G9
    "ESCALATION_TRIGGER": "Condition that initiates escalation",                         # PLANNER-GEN → G9
    # N/A slot types (structural, no grounding)
    "STATUS": "Task status value (Done, In Progress, Blocked)",                          # N/A
    "HEADER_ROW": "Table column headers (Task, Owner, Deadline, Status)",                # N/A
    "MEETING_TIME": "Time of the meeting",                                               # GROUNDED → G3
    "TIMEZONE": "Timezone for the meeting",                                              # GROUNDED → G3
}

# ═══════════════════════════════════════════════════════════════════════════════
# RELATION TYPES (for dependency/prerequisite grounding)
# ═══════════════════════════════════════════════════════════════════════════════
# Relations are binary predicates between entities. They must be grounded from
# the scenario - either explicitly stated or logically derivable.
#
# Format: RELATION(entity1, entity2) = True if the relation holds
#
# Grounding Types for Relations:
#   EXPLICIT: Directly stated in scenario (e.g., "Alice needs the slides before she can present")
#   DERIVED: Logically implied by scenario context (e.g., "review" implies reading before feedback)
#   TEMPORAL: Implied by time constraints (e.g., T-3 task must precede T-1 task)

RELATION_TYPES = {
    # Dependency Relations (GROUNDED or DERIVED)
    "DEPENDS_ON": {
        "description": "Task A depends on Task B (B is prerequisite for A)",
        "signature": "(TASK, TASK)",
        "grounding": "EXPLICIT or DERIVED",
        "examples": [
            "DEPENDS_ON('launch campaign', 'finalize slides') - campaign needs slides",
            "DEPENDS_ON('QA testing', 'development complete') - can't test unbuilt code",
            "DEPENDS_ON('present demo', 'prepare demo') - can't present unprepared demo",
        ],
        "detection_signals": [
            "Explicit: 'X depends on Y', 'X requires Y', 'X needs Y first', 'X blocked by Y'",
            "Derived: 'X after Y', 'Y before X', 'once Y is done, X can start'",
            "Temporal: Task X scheduled after Task Y with logical connection",
        ],
        "linked_g": ["G6"],  # Action Item Grounding verifies the tasks exist
    },
    "BLOCKS": {
        "description": "Blocker B prevents Task T from proceeding",
        "signature": "(BLOCKER, TASK)",
        "grounding": "EXPLICIT or PLANNER-GEN",
        "examples": [
            "BLOCKS('designer unavailable', 'create mockups') - no designer, no mockups",
            "BLOCKS('budget not approved', 'hire vendor') - need budget to hire",
        ],
        "detection_signals": [
            "Explicit: 'X is blocking Y', 'can't do Y until X resolved'",
            "Planner-Gen: Reasonable blocker inferred from task requirements",
        ],
        "linked_g": ["G6", "G9"],  # G6 verifies task, G9 checks blocker consistency
    },
    "OWNS": {
        "description": "Person P is responsible for Task T",
        "signature": "(ATTENDEE, TASK)",
        "grounding": "EXPLICIT or DERIVED",
        "examples": [
            "OWNS('Alice Chen', 'finalize slides') - Alice assigned to slides",
            "OWNS('Bob Smith', 'design review') - Bob doing design work",
        ],
        "detection_signals": [
            "Explicit: 'Alice will do X', 'X assigned to Alice', 'Alice owns X'",
            "Derived: Role implies ownership (designer owns design tasks)",
        ],
        "linked_g": ["G2", "G6"],  # G2 verifies attendee, G6 verifies task
    },
    "PRODUCES": {
        "description": "Task T produces Deliverable D",
        "signature": "(TASK, DELIVERABLE)",
        "grounding": "EXPLICIT or DERIVED",
        "examples": [
            "PRODUCES('finalize slides', 'Q1_slides.pptx') - task creates artifact",
            "PRODUCES('write report', 'status_report.docx') - writing produces doc",
        ],
        "detection_signals": [
            "Explicit: 'Task X will produce Y', 'output of X is Y'",
            "Derived: Task name implies output (e.g., 'create slides' → slides)",
        ],
        "linked_g": ["G4", "G6"],  # G4 verifies artifact, G6 verifies task
    },
    "REQUIRES_INPUT": {
        "description": "Task T requires Artifact A as input",
        "signature": "(TASK, ARTIFACT)",
        "grounding": "EXPLICIT or DERIVED",
        "examples": [
            "REQUIRES_INPUT('review budget', 'budget_2025.xlsx') - need file to review",
            "REQUIRES_INPUT('present slides', 'Q1_slides.pptx') - need slides to present",
        ],
        "detection_signals": [
            "Explicit: 'Task X needs Y', 'X requires access to Y'",
            "Derived: Task implies input (e.g., 'review X' requires X)",
        ],
        "linked_g": ["G4", "G6"],  # G4 verifies artifact, G6 verifies task
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# REFERENCE SCENARIO (for examples)
# ═══════════════════════════════════════════════════════════════════════════════

REFERENCE_SCENARIO = {
    "meeting_title": "Q1 Marketing Strategy Review",
    "date": "March 15, 2025",
    "attendees": ["Alice Chen (PM)", "Bob Smith (Designer)", "Carol Davis (Engineer)", "David Lee (Marketing Lead)"],
    "artifacts": ["Q1_slides.pptx", "budget_2025.xlsx", "marketing_plan.docx"],
    "topics": ["Q1 priorities", "budget allocation", "campaign timeline"],
    "action_items": ["finalize slides", "review budget", "launch campaign"]
}

# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURAL DIMENSIONS (S1-S20) - NEW HYBRID ASSERTION FORMAT
# ═══════════════════════════════════════════════════════════════════════════════

STRUCTURAL_DIMENSIONS = {
    # Core (S1-S10)
    "S1": {
        "name": "Meeting Details",
        "weight": 3,
        "definition": "Subject, date, time, timezone, attendee list clearly stated.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S1_A1",
                "template": "The meeting title must be explicitly stated as [MEETING_TITLE].",
                "instantiated": "The meeting title must be explicitly stated as Q1 Marketing Strategy Review.",
                "slot_types": ["MEETING_TITLE"],
                "sub_aspect": "Meeting title clarity",
                "linked_g_dims": []
            },
            {
                "assertion_id": "S1_A2",
                "template": "The meeting date must be clearly stated as [MEETING_DATE] and include a valid time and timezone.",
                "instantiated": "The meeting date must be clearly stated as March 15, 2025 and include a valid time and timezone.",
                "slot_types": ["MEETING_DATE"],
                "sub_aspect": "Meeting date, time, and timezone specification",
                "linked_g_dims": ["G3"]
            },
            {
                "assertion_id": "S1_A3",
                "template": "The attendee list must include all required attendees: [ATTENDEE]+.",
                "instantiated": "The attendee list must include all required attendees: Alice Chen (PM), Bob Smith (Designer), Carol Davis (Engineer), David Lee (Marketing Lead).",
                "slot_types": ["ATTENDEE"],
                "sub_aspect": "Attendee list completeness and accuracy",
                "linked_g_dims": ["G2"]
            }
        ]
    },
    "S2": {
        "name": "Timeline Alignment",
        "weight": 3,
        "definition": "Backward scheduling (T-minus) with dependency-aware sequencing from meeting date.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S2_A1",
                "template": "All [TASK] entries must be scheduled using T-minus notation relative to [MEETING_DATE].",
                "instantiated": "All task entries must be scheduled using T-minus notation relative to March 15, 2025.",
                "slot_types": ["TASK", "MEETING_DATE"],
                "sub_aspect": "T-minus scheduling notation",
                "linked_g_dims": ["G3"]
            },
            {
                "assertion_id": "S2_A2",
                "template": "Each [TASK] must have a [DUE_DATE] that occurs before [MEETING_DATE].",
                "instantiated": "Each task such as 'finalize slides' must have a due date that occurs before March 15, 2025.",
                "slot_types": ["TASK", "DUE_DATE", "MEETING_DATE"],
                "sub_aspect": "Task deadline alignment",
                "linked_g_dims": ["G3", "G6"]
            },
            {
                "assertion_id": "S2_A3",
                "template": "Tasks must be ordered by dependency, with prerequisite [TASK] scheduled before dependent [TASK].",
                "instantiated": "Tasks must be ordered by dependency, with 'finalize slides' scheduled before 'launch campaign'.",
                "slot_types": ["TASK"],
                "sub_aspect": "Dependency-aware sequencing",
                "linked_g_dims": ["G6"]
            },
            {
                "assertion_id": "S2_A4",
                "template": "The timeline must include buffer/contingency time between the last [TASK] and [MEETING_DATE].",
                "instantiated": "The timeline must include buffer/contingency time between the last task and March 15, 2025.",
                "slot_types": ["TASK", "MEETING_DATE"],
                "sub_aspect": "Buffer time inclusion",
                "linked_g_dims": ["G3"]
            }
        ]
    },
    "S3": {
        "name": "Ownership Assignment",
        "weight": 3,
        "definition": "Named owners per task OR role/skill placeholder if names unavailable.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S3_A1",
                "template": "Each [TASK] must have a named [OWNER] assigned.",
                "instantiated": "Each task such as 'finalize slides' must have a named owner like Alice Chen assigned.",
                "slot_types": ["TASK", "OWNER"],
                "sub_aspect": "Owner assignment presence",
                "linked_g_dims": ["G2", "G6"]
            },
            {
                "assertion_id": "S3_A2",
                "template": "If a specific [OWNER] name is unavailable, a role/skill placeholder must be provided for [TASK].",
                "instantiated": "If a specific owner name is unavailable, a role/skill placeholder like 'Designer' must be provided for 'review slides'.",
                "slot_types": ["OWNER", "TASK"],
                "sub_aspect": "Role placeholder when name unavailable",
                "linked_g_dims": ["G6"]
            },
            {
                "assertion_id": "S3_A3",
                "template": "Every [OWNER] assigned to a [TASK] must be from the scenario attendee list.",
                "instantiated": "Every owner assigned must be from: Alice Chen, Bob Smith, Carol Davis, or David Lee.",
                "slot_types": ["OWNER", "TASK"],
                "sub_aspect": "Owner validity check",
                "linked_g_dims": ["G2"]
            }
        ]
    },
    "S4": {
        "name": "Deliverables & Artifacts",
        "weight": 2,
        "definition": "All outputs listed with working links, version/format specified.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S4_A1",
                "template": "Every [TASK] with an output must specify a [DELIVERABLE] with format/version.",
                "instantiated": "Every task with an output must specify a deliverable like 'Q1_slides.pptx v2.0'.",
                "slot_types": ["TASK", "DELIVERABLE"],
                "sub_aspect": "Deliverable specification",
                "linked_g_dims": ["G4"]
            },
            {
                "assertion_id": "S4_A2",
                "template": "Every referenced [ARTIFACT] must exist in the scenario artifact list.",
                "instantiated": "Every referenced artifact must be from: Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx.",
                "slot_types": ["ARTIFACT"],
                "sub_aspect": "Artifact validity",
                "linked_g_dims": ["G4"]
            }
        ]
    },
    "S5": {
        "name": "Task Dates",
        "weight": 2,
        "definition": "Due dates for every task aligned with S2/S12 sequencing.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S5_A1",
                "template": "Every [TASK] must have a [DUE_DATE] explicitly specified.",
                "instantiated": "Every task like 'review budget' must have a due date explicitly specified.",
                "slot_types": ["TASK", "DUE_DATE"],
                "sub_aspect": "Due date presence",
                "linked_g_dims": ["G3"]
            },
            {
                "assertion_id": "S5_A2",
                "template": "All [DUE_DATE] values must be before or on [MEETING_DATE].",
                "instantiated": "All due dates must be before or on March 15, 2025.",
                "slot_types": ["DUE_DATE", "MEETING_DATE"],
                "sub_aspect": "Date consistency",
                "linked_g_dims": ["G3"]
            }
        ]
    },
    "S6": {
        "name": "Dependencies & Blockers",
        "weight": 2,
        "definition": "Predecessors and risks identified; mitigation steps documented.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S6_A1",
                "template": "Each [TASK] with prerequisites must list its dependencies on other [TASK] items.",
                "instantiated": "Task 'launch campaign' must list its dependency on 'finalize slides' and 'review budget'.",
                "slot_types": ["TASK"],
                "sub_aspect": "Dependency listing",
                "linked_g_dims": ["G6"]
            },
            {
                "assertion_id": "S6_A2",
                "template": "Identified blockers must have mitigation steps with an [OWNER] responsible.",
                "instantiated": "Identified blockers must have mitigation steps with an owner like Alice Chen responsible.",
                "slot_types": ["OWNER"],
                "sub_aspect": "Blocker mitigation",
                "linked_g_dims": ["G2"]
            }
        ]
    },
    "S7": {
        "name": "Meeting Outcomes",
        "weight": 2,
        "definition": "Expected outcomes and success criteria for the meeting.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S7_A1",
                "template": "The plan must state expected outcomes aligned with [TOPIC].",
                "instantiated": "The plan must state expected outcomes aligned with Q1 priorities, budget allocation, campaign timeline.",
                "slot_types": ["TOPIC"],
                "sub_aspect": "Outcome alignment with topics",
                "linked_g_dims": ["G5"]
            }
        ]
    },
    "S8": {
        "name": "Parallel Workstreams",
        "weight": 1,
        "definition": "Concurrent tasks identified with resource allocation.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S8_A1",
                "template": "Tasks that can run in parallel must be identified with separate [OWNER] assignments.",
                "instantiated": "Tasks that can run in parallel like 'finalize slides' and 'review budget' must have separate owners.",
                "slot_types": ["OWNER"],
                "sub_aspect": "Parallel task identification",
                "linked_g_dims": ["G2", "G6"]
            }
        ]
    },
    "S9": {
        "name": "Checkpoints",
        "weight": 2,
        "definition": "Verification points to validate progress before meeting.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S9_A1",
                "template": "The plan must include checkpoint dates before [MEETING_DATE] to verify [TASK] completion.",
                "instantiated": "The plan must include checkpoint dates before March 15, 2025 to verify task completion.",
                "slot_types": ["MEETING_DATE", "TASK"],
                "sub_aspect": "Checkpoint presence",
                "linked_g_dims": ["G3", "G6"]
            }
        ]
    },
    "S10": {
        "name": "Resource Allocation",
        "weight": 2,
        "definition": "People/time/tools/budget availability and constraints visible.",
        "group": "core",
        "assertions": [
            {
                "assertion_id": "S10_A1",
                "template": "Resource allocation must map [OWNER] availability to [TASK] assignments.",
                "instantiated": "Resource allocation must map owner availability (Alice Chen, Bob Smith, etc.) to task assignments.",
                "slot_types": ["OWNER", "TASK"],
                "sub_aspect": "Resource-task mapping",
                "linked_g_dims": ["G2"]
            }
        ]
    },
    # Extended (S11-S19)
    "S11": {
        "name": "Risk Mitigation Strategy",
        "weight": 2,
        "definition": "Concrete contingencies for top risks with owners.",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S11_A1",
                "template": "Each identified risk must have a mitigation strategy with an [OWNER] assigned.",
                "instantiated": "Each identified risk must have a mitigation strategy with an owner like Alice Chen assigned.",
                "slot_types": ["OWNER"],
                "sub_aspect": "Risk mitigation ownership",
                "linked_g_dims": ["G2"]
            },
            {
                "assertion_id": "S11_A2",
                "template": "Risks related to [TASK] delays must specify contingency actions.",
                "instantiated": "Risks related to 'finalize slides' delays must specify contingency actions.",
                "slot_types": ["TASK"],
                "sub_aspect": "Task-specific contingency",
                "linked_g_dims": ["G6"]
            }
        ]
    },
    "S12": {
        "name": "Communication Plan",
        "weight": 1,
        "definition": "Collaboration methods specified (Teams, email, meeting cadence).",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S12_A1",
                "template": "Communication channels must be specified for [OWNER] coordination on [TASK].",
                "instantiated": "Communication channels must be specified for Alice Chen coordination on 'finalize slides'.",
                "slot_types": ["OWNER", "TASK"],
                "sub_aspect": "Communication channel specification",
                "linked_g_dims": ["G2"]
            }
        ]
    },
    "S13": {
        "name": "Escalation Protocol",
        "weight": 1,
        "definition": "Escalation owners and steps for critical risks defined.",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S13_A1",
                "template": "Escalation contacts must be from the scenario attendee list: [ATTENDEE].",
                "instantiated": "Escalation contacts must be from: Alice Chen, Bob Smith, Carol Davis, or David Lee.",
                "slot_types": ["ATTENDEE"],
                "sub_aspect": "Escalation contact validity",
                "linked_g_dims": ["G2"]
            }
        ]
    },
    "S14": {
        "name": "Feedback Integration",
        "weight": 1,
        "definition": "Scheduled checkpoints to validate and iterate the plan.",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S14_A1",
                "template": "Feedback loops must be tied to [TOPIC] discussions.",
                "instantiated": "Feedback loops must be tied to Q1 priorities, budget allocation, or campaign timeline discussions.",
                "slot_types": ["TOPIC"],
                "sub_aspect": "Feedback-topic alignment",
                "linked_g_dims": ["G5", "G7"]
            }
        ]
    },
    "S15": {
        "name": "Progress Tracking",
        "weight": 2,
        "definition": "Metrics and methods for tracking task completion.",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S15_A1",
                "template": "Progress tracking must measure completion of each [TASK] and [ACTION_ITEM].",
                "instantiated": "Progress tracking must measure completion of tasks like finalize slides, review budget, launch campaign.",
                "slot_types": ["TASK", "ACTION_ITEM"],
                "sub_aspect": "Task completion tracking",
                "linked_g_dims": ["G6"]
            }
        ]
    },
    "S16": {
        "name": "Assumptions & Prerequisites",
        "weight": 2,
        "definition": "Stated assumptions and conditions that must be true.",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S16_A1",
                "template": "Assumptions must be explicitly stated and relate to [TOPIC] or [TASK] prerequisites.",
                "instantiated": "Assumptions must be explicitly stated and relate to budget approval or campaign launch prerequisites.",
                "slot_types": ["TOPIC", "TASK"],
                "sub_aspect": "Assumption documentation",
                "linked_g_dims": ["G5", "G7"]
            }
        ]
    },
    "S17": {
        "name": "Cross-team Coordination",
        "weight": 1,
        "definition": "Dependencies on other teams identified with contacts.",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S17_A1",
                "template": "Cross-team contacts must be from the attendee list: [ATTENDEE].",
                "instantiated": "Cross-team contacts must be from: Alice Chen, Bob Smith, Carol Davis, or David Lee.",
                "slot_types": ["ATTENDEE"],
                "sub_aspect": "Cross-team contact validity",
                "linked_g_dims": ["G2"]
            }
        ]
    },
    "S18": {
        "name": "Post-Event Actions",
        "weight": 1,
        "definition": "Wrap-up tasks, retrospectives, and reporting.",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S18_A1",
                "template": "Post-event actions must have [OWNER] and [DUE_DATE] after [MEETING_DATE].",
                "instantiated": "Post-event actions must have an owner like Alice Chen and a due date after March 15, 2025.",
                "slot_types": ["OWNER", "DUE_DATE", "MEETING_DATE"],
                "sub_aspect": "Post-event task specification",
                "linked_g_dims": ["G2", "G3"]
            }
        ]
    },
    "S19": {
        "name": "Caveat & Clarification",
        "weight": 2,
        "definition": "Open questions, decision points, and items needing clarification.",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S19_A1",
                "template": "Open questions must be documented and relate to [TOPIC] or [TASK].",
                "instantiated": "Open questions must be documented and relate to budget allocation or campaign timeline.",
                "slot_types": ["TOPIC", "TASK"],
                "sub_aspect": "Open question documentation",
                "linked_g_dims": ["G5"]
            },
            {
                "assertion_id": "S19_A2",
                "template": "Assumptions must be explicitly disclosed without presenting them as facts.",
                "instantiated": "Assumptions about budget approval must be explicitly disclosed without presenting them as facts.",
                "slot_types": [],
                "sub_aspect": "Assumption transparency",
                "linked_g_dims": ["G7", "G8"]
            }
        ]
    },
    # S20: Clarity & First Impression - UX/Presentation Layer
    # Note: No linked_g_dims as this is a presentation quality check, not grounding
    "S20": {
        "name": "Clarity & First Impression",
        "weight": 2,
        "definition": "WBP is instantly recognizable, intuitive to use, and professionally formatted.",
        "group": "extended",
        "assertions": [
            {
                "assertion_id": "S20_A1",
                "template": "The WBP must include a structured table with columns: Task, Owner, Deadline, Status.",
                "instantiated": "The WBP must include a structured table with columns: Task, Owner, Deadline, Status.",
                "slot_types": [],
                "sub_aspect": "Required columns present",
                "linked_g_dims": [],
                "test_method": "automated",
                "pass_criteria": "All four columns exist with headers spelled correctly",
                "good_example": "| Task | Owner | Deadline | Status |\n|------|-------|----------|--------|\n| Draft report | Alice | 2024-07-15 | In Progress |",
                "poor_example": "| Activity | Person | Due Date | Progress |"
            },
            {
                "assertion_id": "S20_A2",
                "template": "A goal or mission statement must appear within the first 3 lines of the WBP.",
                "instantiated": "A goal statement like 'Goal: Deliver marketing assets by launch date' must appear within the first 3 lines.",
                "slot_types": [],
                "sub_aspect": "Goal statement at top",
                "linked_g_dims": [],
                "test_method": "automated",
                "pass_criteria": "Text containing 'Goal', 'Objective', or 'Purpose' appears before the task table",
                "good_example": "**Goal:** Deliver marketing campaign assets by Aug 30 to support product launch.",
                "poor_example": "(No goal stated, jumps straight to task table)"
            },
            {
                "assertion_id": "S20_A3",
                "template": "Each task description must be concise (≤12 words).",
                "instantiated": "Each task description like 'Create initial wireframes for homepage' must be ≤12 words.",
                "slot_types": [],
                "sub_aspect": "Task description brevity",
                "linked_g_dims": [],
                "test_method": "automated",
                "pass_criteria": "No task description exceeds 12 words",
                "good_example": "Create initial wireframes for homepage.",
                "poor_example": "Create initial wireframes for homepage including all responsive breakpoints and accessibility adjustments."
            },
            {
                "assertion_id": "S20_A4",
                "template": "All deadlines must use consistent date format: YYYY-MM-DD.",
                "instantiated": "All deadlines must use format like 2025-03-15, not 'March 15' or '3/15/25'.",
                "slot_types": [],
                "sub_aspect": "Consistent date format",
                "linked_g_dims": [],
                "test_method": "automated",
                "pass_criteria": "Every entry in Deadline column matches regex \\d{4}-\\d{2}-\\d{2}",
                "good_example": "2024-07-15",
                "poor_example": "07/15/24 or July 15th, 2024"
            },
            {
                "assertion_id": "S20_A5",
                "template": "Tasks must be sorted by Deadline in ascending (chronological) order.",
                "instantiated": "Tasks must be sorted chronologically: 2025-03-01 → 2025-03-10 → 2025-03-15.",
                "slot_types": [],
                "sub_aspect": "Chronological task ordering",
                "linked_g_dims": [],
                "test_method": "automated",
                "pass_criteria": "Each deadline is equal to or later than the previous one",
                "good_example": "2024-07-01 → 2024-07-10 → 2024-07-15",
                "poor_example": "2024-07-15 → 2024-07-01 → 2024-07-10"
            },
            {
                "assertion_id": "S20_A6",
                "template": "No blank cells in required columns (Task, Owner, Deadline, Status).",
                "instantiated": "Every row must have values in Task, Owner, Deadline, and Status columns.",
                "slot_types": [],
                "sub_aspect": "No empty required fields",
                "linked_g_dims": [],
                "test_method": "automated",
                "pass_criteria": "All required fields are populated in every row",
                "good_example": "All rows have complete information",
                "poor_example": "Some tasks missing owners or deadlines"
            },
            {
                "assertion_id": "S20_A7",
                "template": "Owner names must be consistent (no spelling variations for the same person).",
                "instantiated": "Owner names must be consistent: always 'Alice Chen', not 'Alice', 'alice', or 'A. Chen'.",
                "slot_types": [],
                "sub_aspect": "Owner name consistency",
                "linked_g_dims": [],
                "test_method": "automated",
                "pass_criteria": "No variation in case or spelling for the same person across the WBP",
                "good_example": "'Alice Chen' used everywhere",
                "poor_example": "'Alice Chen', 'alice chen', 'A. Chen' used interchangeably"
            },
            {
                "assertion_id": "S20_A8",
                "template": "If custom status terms are used, a legend must be provided.",
                "instantiated": "If using 'NS', 'IP', 'Done' as status, include: 'Legend: NS=Not Started, IP=In Progress'.",
                "slot_types": [],
                "sub_aspect": "Status legend presence",
                "linked_g_dims": [],
                "test_method": "automated",
                "pass_criteria": "Legend exists if any status is not in standard set {Not Started, In Progress, Complete, Done, Completed, Pending, Blocked}",
                "good_example": "Status Legend: NS = Not Started, IP = In Progress, C = Complete",
                "poor_example": "Uses 'P', 'BLK', 'TBD' without explanation"
            }
        ]
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# GROUNDING DIMENSIONS (G1-G8) - NEW HYBRID ASSERTION FORMAT
# G assertions are REFERENCE DEFINITIONS that S assertions link to via linked_g_dims.
# They are instantiated only when validating elements from S assertions.
# ═══════════════════════════════════════════════════════════════════════════════

GROUNDING_DIMENSIONS = {
    "G1": {
        "name": "Hallucination Check",
        "weight": 3,
        "definition": "No extraneous entities or fabricated details not in source.",
        "verification": "Check for any names, dates, artifacts not present in scenario",
        "assertions": [
            {
                "assertion_id": "G1_A1",
                "template": "Every mentioned [ATTENDEE] in the WBP must exist in the scenario attendee list.",
                "instantiated": "Every mentioned attendee in the WBP must be one of: Alice Chen, Bob Smith, Carol Davis, or David Lee.",
                "slot_types": ["ATTENDEE"],
                "sub_aspect": "No fabricated attendee names"
            },
            {
                "assertion_id": "G1_A2",
                "template": "Every referenced [ARTIFACT] in the WBP must match an artifact from the scenario.",
                "instantiated": "Every referenced artifact in the WBP must be one of: Q1_slides.pptx, budget_2025.xlsx, or marketing_plan.docx.",
                "slot_types": ["ARTIFACT"],
                "sub_aspect": "No extra or fabricated artifacts"
            },
            {
                "assertion_id": "G1_A3",
                "template": "All mentioned [TOPIC] in the WBP must correspond to a known topic from the scenario.",
                "instantiated": "All mentioned topics in the WBP must correspond to one of: Q1 priorities, budget allocation, campaign timeline.",
                "slot_types": ["TOPIC"],
                "sub_aspect": "Agenda topic accuracy"
            }
        ]
    },
    "G2": {
        "name": "Attendee Grounding",
        "weight": 3,
        "definition": "All people mentioned must be from scenario's attendee list.",
        "verification": "Compare all names in WBP against scenario.attendees",
        "assertions": [
            {
                "assertion_id": "G2_A1",
                "template": "Every [OWNER] assigned to a [TASK] in the WBP must be from the scenario attendee list.",
                "instantiated": "Every task owner assigned to a task in the WBP must be one of: Alice Chen, Bob Smith, Carol Davis, or David Lee.",
                "slot_types": ["OWNER", "TASK", "ATTENDEE"],
                "sub_aspect": "Task owner validity"
            },
            {
                "assertion_id": "G2_A2",
                "template": "Any [ATTENDEE] mentioned in WBP descriptions, notes, or communications must exist in the scenario.",
                "instantiated": "Any attendee mentioned in WBP notes or descriptions, such as collaboration contacts, must be from the scenario attendee list.",
                "slot_types": ["ATTENDEE"],
                "sub_aspect": "Incidental attendee mention validity"
            },
            {
                "assertion_id": "G2_A3",
                "template": "No [ENTITY] representing a person outside the scenario attendee list should appear.",
                "instantiated": "No person name outside Alice Chen, Bob Smith, Carol Davis, or David Lee should appear in the WBP.",
                "slot_types": ["ENTITY"],
                "sub_aspect": "No hallucinated people"
            }
        ]
    },
    "G3": {
        "name": "Date/Time Grounding",
        "weight": 3,
        "definition": "All dates/times must be consistent with scenario's meeting date.",
        "verification": "Verify dates are realistic relative to scenario.date",
        "assertions": [
            {
                "assertion_id": "G3_A1",
                "template": "The [MEETING_DATE] must match the actual meeting date specified in the scenario.",
                "instantiated": "The March 15, 2025 must match the actual meeting date specified in the scenario.",
                "slot_types": ["MEETING_DATE"],
                "sub_aspect": "Meeting date accuracy"
            },
            {
                "assertion_id": "G3_A2",
                "template": "No [DUE_DATE] should occur after the [MEETING_DATE] for pre-meeting tasks.",
                "instantiated": "No task due date for pre-meeting work should occur after March 15, 2025.",
                "slot_types": ["DUE_DATE", "MEETING_DATE"],
                "sub_aspect": "Due date consistency"
            }
        ]
    },
    "G4": {
        "name": "Artifact Grounding",
        "weight": 2,
        "definition": "All referenced files/documents must exist in scenario's artifacts.",
        "verification": "Compare file references against scenario.artifacts",
        "assertions": [
            {
                "assertion_id": "G4_A1",
                "template": "Every referenced [ARTIFACT] in the work-back plan must exist in the scenario artifact list.",
                "instantiated": "Every referenced artifact such as Q1_slides.pptx in the work-back plan must exist in the scenario artifact list.",
                "slot_types": ["ARTIFACT"],
                "sub_aspect": "Artifact existence check"
            },
            {
                "assertion_id": "G4_A2",
                "template": "If a task specifies a deliverable file [ARTIFACT], it must be from the scenario artifact list.",
                "instantiated": "If a task specifies a deliverable file marketing_plan.docx, it must be from the scenario artifact list.",
                "slot_types": ["ARTIFACT"],
                "sub_aspect": "Deliverable artifact validity"
            }
        ]
    },
    "G5": {
        "name": "Topic Grounding",
        "weight": 2,
        "definition": "All topics/agenda items must align with scenario's discussion_points.",
        "verification": "Check topics against scenario.discussion_points",
        "assertions": [
            {
                "assertion_id": "G5_A1",
                "template": "Each agenda topic [TOPIC] in the work-back plan must exist in the scenario discussion points.",
                "instantiated": "Each agenda topic (e.g., Q1 priorities, budget allocation, campaign timeline) in the work-back plan must exist in the scenario discussion points.",
                "slot_types": ["TOPIC"],
                "sub_aspect": "Topic alignment"
            },
            {
                "assertion_id": "G5_A2",
                "template": "No agenda topic [TOPIC] should introduce content not present in the scenario.",
                "instantiated": "No agenda topic (e.g., introducing new product launch) should introduce content not present in the scenario discussion points.",
                "slot_types": ["TOPIC"],
                "sub_aspect": "No hallucinated topics"
            }
        ]
    },
    "G6": {
        "name": "Action Item Grounding",
        "weight": 2,
        "definition": "All action items must be traceable to scenario's action_items_discussed.",
        "verification": "Compare action items against scenario.action_items_discussed",
        "assertions": [
            {
                "assertion_id": "G6_A1",
                "template": "Every [TASK] in the work-back plan must correspond to an [ACTION_ITEM] from the scenario.",
                "instantiated": "Every task in the work-back plan must correspond to an action item from: finalize slides, review budget, launch campaign.",
                "slot_types": ["TASK", "ACTION_ITEM"],
                "sub_aspect": "Task-to-action-item traceability"
            },
            {
                "assertion_id": "G6_A2",
                "template": "The work-back plan must include a corresponding [TASK] for each scenario [ACTION_ITEM].",
                "instantiated": "The work-back plan must include a corresponding task for each action item: finalize slides, review budget, launch campaign.",
                "slot_types": ["ACTION_ITEM", "TASK"],
                "sub_aspect": "Action item coverage completeness"
            }
        ]
    },
    "G7": {
        "name": "Context Preservation",
        "weight": 2,
        "definition": "Original context and constraints from scenario are maintained.",
        "verification": "Verify WBP preserves scenario.context meaning",
        "assertions": [
            {
                "assertion_id": "G7_A1",
                "template": "The Work-Back Plan includes the original meeting date [MEETING_DATE] without modification.",
                "instantiated": "The Work-Back Plan includes the original meeting date March 15, 2025 without modification.",
                "slot_types": ["MEETING_DATE"],
                "sub_aspect": "Meeting date preservation"
            },
            {
                "assertion_id": "G7_A2",
                "template": "The Work-Back Plan includes only attendees from the original scenario: [ATTENDEE]+.",
                "instantiated": "The Work-Back Plan includes only attendees from the original scenario: Alice Chen, Bob Smith, Carol Davis, David Lee.",
                "slot_types": ["ATTENDEE"],
                "sub_aspect": "Attendee list preservation"
            },
            {
                "assertion_id": "G7_A3",
                "template": "The Work-Back Plan references only original scenario artifacts: [ARTIFACT]+.",
                "instantiated": "The Work-Back Plan references only original scenario artifacts: Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx.",
                "slot_types": ["ARTIFACT"],
                "sub_aspect": "Artifact reference preservation"
            }
        ]
    },
    "G8": {
        "name": "Instruction Adherence",
        "weight": 2,
        "definition": "Any specific instructions from the meeting are followed.",
        "verification": "Check compliance with any instructions in scenario",
        "assertions": [
            {
                "assertion_id": "G8_A1",
                "template": "The WBP includes a task for each [ACTION_ITEM] mentioned in the scenario instructions.",
                "instantiated": "The WBP includes a task for each action item: finalize slides, review budget, launch campaign.",
                "slot_types": ["ACTION_ITEM"],
                "sub_aspect": "Instruction coverage"
            },
            {
                "assertion_id": "G8_A2",
                "template": "Each task for an [ACTION_ITEM] is assigned to an [ATTENDEE] from the scenario.",
                "instantiated": "Each task for an action item like review budget is assigned to an attendee from the scenario.",
                "slot_types": ["ACTION_ITEM", "ATTENDEE"],
                "sub_aspect": "Instruction-task-owner alignment"
            },
            {
                "assertion_id": "G8_A3",
                "template": "The WBP references each [ARTIFACT] mentioned in the scenario instructions.",
                "instantiated": "The WBP references each artifact such as Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx mentioned in the scenario.",
                "slot_types": ["ARTIFACT"],
                "sub_aspect": "Artifact instruction adherence"
            }
        ]
    },
    # G9: NEW - Consistency Check for Planner-Generated Elements
    "G9": {
        "name": "Planner-Generated Consistency",
        "weight": 2,
        "definition": "Planner-generated elements (assumptions, blockers, mitigations, open questions) must not contradict scenario facts.",
        "verification": "Check that planner-added content is consistent with scenario; allows creative planning but prevents contradictions.",
        "purpose": "Enables GOOD PLANNING (identifying reasonable risks/assumptions/questions) while preventing HALLUCINATION (contradicting scenario facts).",
        "applies_to": ["ASSUMPTION", "BLOCKER", "MITIGATION", "OPEN_QUESTION", "ESCALATION_TRIGGER"],
        "assertions": [
            {
                "assertion_id": "G9_A1",
                "template": "No [ASSUMPTION] may contradict facts stated in the scenario.",
                "instantiated": "Assumption 'budget will be approved by April 10' must not contradict scenario (e.g., if scenario says 'budget already rejected').",
                "slot_types": ["ASSUMPTION"],
                "sub_aspect": "Assumption consistency"
            },
            {
                "assertion_id": "G9_A2",
                "template": "No [BLOCKER] may contradict facts stated in the scenario.",
                "instantiated": "Blocker 'designer unavailable' must not contradict scenario (e.g., if scenario says 'Bob Smith (Designer) confirmed available').",
                "slot_types": ["BLOCKER"],
                "sub_aspect": "Blocker consistency"
            },
            {
                "assertion_id": "G9_A3",
                "template": "[MITIGATION] must be logically related to its [BLOCKER] and not contradict scenario constraints.",
                "instantiated": "Mitigation 'use backup designer Carol' must be logically related to blocker 'designer unavailable' and Carol must be in attendee list.",
                "slot_types": ["MITIGATION", "BLOCKER"],
                "sub_aspect": "Mitigation consistency"
            },
            {
                "assertion_id": "G9_A4",
                "template": "Planner-generated [ASSUMPTION], [BLOCKER], and [MITIGATION] should be plausible given scenario context.",
                "instantiated": "Assumption 'legal review will pass' is plausible if scenario mentions legal tasks; blocker 'server outage' is implausible if scenario is about marketing slides.",
                "slot_types": ["ASSUMPTION", "BLOCKER", "MITIGATION"],
                "sub_aspect": "Contextual plausibility"
            },
            {
                "assertion_id": "G9_A5",
                "template": "[OPEN_QUESTION] must be relevant to plan success and not contradict known scenario facts.",
                "instantiated": "Open question 'Who approves budgets over $50K?' is relevant if scenario mentions budget approval; question 'What color should the logo be?' is irrelevant if scenario is about budget planning.",
                "slot_types": ["OPEN_QUESTION"],
                "sub_aspect": "Open question relevance"
            },
            {
                "assertion_id": "G9_A6",
                "template": "[OPEN_QUESTION] should identify genuine gaps in knowledge, not ask about information already provided in the scenario.",
                "instantiated": "Open question 'Who is the project manager?' is invalid if scenario already states 'Alice Chen (PM)'.",
                "slot_types": ["OPEN_QUESTION"],
                "sub_aspect": "No redundant questions"
            }
        ]
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# PRIORITY ORDERS
# ═══════════════════════════════════════════════════════════════════════════════

STRUCTURAL_CORE_ORDER = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10"]
STRUCTURAL_EXTENDED_ORDER = ["S11", "S12", "S13", "S14", "S15", "S16", "S17", "S18", "S19", "S20"]
STRUCTURAL_PRIORITY_ORDER = STRUCTURAL_CORE_ORDER + STRUCTURAL_EXTENDED_ORDER

# G1 removed from grounding layer - it's now M1 in meta layer
GROUNDING_PRIORITY_ORDER = ["G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10"]

# Meta layer - computed AFTER all G assertions are evaluated
# M1 (No Hallucination) is DERIVED from the aggregate of all G2-G10 results
META_LAYER_ORDER = ["M1"]


def get_dimension_weight(dim_id: str) -> int:
    """Get the weight for a dimension ID."""
    if dim_id in STRUCTURAL_DIMENSIONS:
        return STRUCTURAL_DIMENSIONS[dim_id]["weight"]
    elif dim_id in GROUNDING_DIMENSIONS:
        return GROUNDING_DIMENSIONS[dim_id]["weight"]
    return 1  # Default weight


def get_dimension_name(dim_id: str) -> str:
    """Get the human-readable name for a dimension ID."""
    return DIMENSION_NAMES.get(dim_id, dim_id)


def get_grounding_for_structural(s_dim: str) -> list:
    """Get the list of grounding dimensions that apply to a structural dimension."""
    return S_TO_G_MAP.get(s_dim, [])


def get_rationale(s_dim: str, g_dim: str) -> str:
    """Get the rationale for why a grounding dimension applies to a structural dimension."""
    return G_RATIONALE_FOR_S.get((s_dim, g_dim), "")
