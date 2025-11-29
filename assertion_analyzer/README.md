# Assertion Analyzer

A self-contained Python package for WBP (Workback Plan) assertion analysis using GPT-5.

**Authors:** Chin-Yew Lin, Haidong Zhang  
**Version:** 2.1 (November 2025)  
**Prompts:** v3.0 (with atomic decomposition support)

> **⚠️ Windows Only**: This package requires Windows due to the MSAL broker authentication for GPT-5 API access. Linux and macOS are not supported.

## Features

- **GPT-5 Classification**: Classifies assertions into 29 dimensions (S1-S20 structural + G1-G9 grounding)
- **S+G Linkage**: Automatically generates related grounding assertions for structural dimensions
- **Scenario Generation**: Creates realistic meeting scenarios as ground truth
- **WBP Generation**: Generates workback plans that satisfy assertions
- **Verification**: Verifies WBPs against scenarios and assertions
- **Customizable Prompts**: Prompts stored in `prompts.json` for easy fine-tuning
- **Self-contained venv**: Runs in its own virtual environment

## Quick Start (Recommended)

The easiest way to run the analyzer is using the provided run script, which automatically sets up a virtual environment:

### Windows (PowerShell)

```powershell
cd assertion_analyzer
.\run.ps1 "The plan includes task deadlines"
```

The script will automatically:
1. Create a `.venv` virtual environment (if not exists)
2. Install all dependencies
3. Run the analyzer

## Manual Setup

If you prefer to set up the environment manually:

### Option 1: Using setup script

```bash
cd assertion_analyzer
python setup_env.py        # Create venv and install deps
python setup_env.py --clean  # Clean install (removes existing venv)
```

### Option 2: Manual venv creation

```bash
cd assertion_analyzer

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Single Assertion Mode

```powershell
# Analyze with default example
.\run.ps1

# Analyze custom assertion
.\run.ps1 "The response should list tasks in chronological order"

# With context
.\run.ps1 "Tasks have clear owners" -Context "Team meeting about Q1 planning"

# Output as JSON
.\run.ps1 "Timeline is clear" -Json

# Quick classification (no WBP generation)
.\run.ps1 "Has deadlines" -NoExamples

# Save to specific directory
.\run.ps1 "Tasks ordered" -OutputDir ./reports
```

### Batch Mode

Process multiple assertions from a text file (one assertion per line):

```powershell
# Basic batch processing (auto-generates output directory)
.\run.ps1 -Batch "assertions.txt"

# Specify output directory
.\run.ps1 -Batch "assertions.txt" -OutputDir "./results"

# Batch with context and faster processing
.\run.ps1 -Batch "assertions.txt" -OutputDir "./results" -Context "Q1 planning" -NoExamples
```

**Input file format** (`assertions.txt`):
```
# Lines starting with # are ignored
The plan includes clear deadlines
Tasks are assigned to specific owners
The timeline shows dependencies between tasks
```

**Output**:
- Individual JSON files for each assertion in the output directory
- `_batch_summary.json` with overall results and statistics
- Progress indicator showing `[3/10] Processing...` with ETA

### Python API

```python
from assertion_analyzer import AssertionAnalyzer, analyze_assertion

# High-level interface
analyzer = AssertionAnalyzer(output_dir="./reports")
result = analyzer.analyze("The response should arrange tasks before the deadline")

print(result['summary_table'])
print(f"JSON saved to: {result['json_file_path']}")

# Low-level classification only
classification = analyze_assertion("Tasks have owners assigned")
print(f"Dimension: {classification['dimension_id']}")
print(f"Layer: {classification['layer']}")
```

---

# Deep Dive: Design & Architecture

This section explains the core design principles and workflow of the Assertion Analyzer.

## The Problem: Evaluating AI-Generated Plans

When an AI generates a Workback Plan (WBP) for a meeting, how do we verify it's correct? We need to check two fundamentally different things:

1. **Structure**: Does the plan HAVE the right elements? (timeline, owners, deliverables)
2. **Grounding**: Are the facts CORRECT? (real attendees, accurate dates, existing files)

These two concerns are orthogonal but interconnected. A plan can have perfect structure but wrong facts, or vice versa.

## The Solution: S+G Framework with Linkage

The Assertion Analyzer implements a **29-dimension framework** split into:
- **20 Structural dimensions (S1-S20)**: Check plan shape and completeness
- **9 Grounding dimensions (G1-G9)**: Check factual accuracy (G9 validates planner-generated content)

### Key Concept: G Assertions Are Instantiated Through S Assertions

**G-level (grounding) assertions are never standalone.** They are always instantiated in the context of validating elements identified by S-level (structural) assertions.

The relationship works as follows:

1. **S-level assertions** define **what** structural elements should exist (tasks, dates, owners, deliverables, etc.)
2. **G-level assertions** define **grounding constraints** that validate those elements against the source scenario
3. The `linked_g_dims` field in each S assertion specifies which G checks apply

**Example:**
```
S2 assertion: "Each [TASK] must have a [DUE_DATE]..."
    └── linked_g_dims: ["G3", "G6"]
        ├── G3: Validate that [DUE_DATE] is consistent with meeting date
        └── G6: Validate that [TASK] traces to scenario's action_items
```

When evaluating an S assertion like "Task 'finalize slides' has due date March 10":
- **S2** checks the structural requirement (task has a due date)
- **G3** grounds the date (is March 10 valid relative to March 15 meeting?)
- **G6** grounds the task (is "finalize slides" in the scenario's action items?)

The standalone G assertion definitions serve as a **reference library** that S assertions link to. This is why Step 4 uses GPT-5 to intelligently select relevant G dimensions based on each S assertion's content.

### Key Concept: S+G Dimensions Are ATOMIC

**Each S or G dimension tests exactly ONE thing.** However, free-form assertions (like those written by humans) can combine multiple requirements in one sentence.

The conversion task is to **DECOMPOSE** one free-form assertion into **multiple atomic S+G units**:

```
Free-form assertion:
"The response should state that the meeting '1:1 Action Items Review' 
 is scheduled for July 26, 2025 at 14:00 PST."
                    |
                    v DECOMPOSE
+---------------------------------------------------------------+
| S1: Title - "State the meeting title"                         |
|   +-- G5: slot_value = "1:1 Action Items Review"              |
+---------------------------------------------------------------+
| S5: Task Dates - "State the meeting date/time"                |
|   +-- G3: slot_value = "July 26, 2025 at 14:00 PST"           |
+---------------------------------------------------------------+
```

This decomposition is handled by the **decomposition prompt** (`prompts/decomposition_prompt.json`), which:
1. Identifies ALL S dimensions present in the assertion
2. Extracts slot values for linked G dimensions
3. Returns an array of atomic S+G units

**Why atomic matters:**
- Single-responsibility: Each assertion tests one thing
- Precise scoring: Pass/fail at granular level
- Clear traceability: S→G linkage is explicit
- Composable: Complex assertions = multiple atomic units

The key insight is that **structural assertions imply grounding requirements**:

```
┌─────────────────────────────────────────────────────────────────┐
│  User Input: "The plan arranges draft slides before review"     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  GPT-5 Classification                                           │
│  → S2: Timeline Alignment (structural, critical)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  S → G Selection (GPT-5 intelligent selection)                  │
│                                                                 │
│  S2 (Timeline) available Gs: [G3, G6]                           │
│                                                                 │
│  GPT-5 analyzes the assertion to select ONLY relevant Gs:       │
│    └── G6: Action Item Grounding  (SELECTED)                    │
│        "Task ordering must trace to actual action items"        │
│                                                                 │
│    (G3: Date/Time skipped - no dates in original assertion)     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Output: 1 S assertion + 2 G assertions (linked)                │
│                                                                 │
│  A0001_S2 (parent)                                              │
│    ├── A0001_G3_0 (child, parent_id = A0001_S2)                 │
│    └── A0001_G6_1 (child, parent_id = A0001_S2)                 │
└─────────────────────────────────────────────────────────────────┘
```

## The 5-Step Workflow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        ASSERTION ANALYZER WORKFLOW                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Step 1: INPUT                                                           │
│  ════════════                                                            │
│  User provides an assertion text:                                        │
│  "The response arranges draft slides task before review slides task"     │
│                                                                          │
│                              │                                           │
│                              ▼                                           │
│  Step 2: SCENARIO GENERATION (GPT-5)                                     │
│  ═══════════════════════════════════                                     │
│  Generate a realistic meeting scenario as "ground truth":                │
│                                                                          │
│  {                                                                       │
│    "title": "Q1 Marketing Presentation Planning",                        │
│    "date": "2025-12-15",                                                 │
│    "attendees": ["Alice Chen", "Bob Smith", "Carol Davis"],              │
│    "artifacts": ["Q1_slides_draft.pptx", "marketing_data.xlsx"],         │
│    "action_items_discussed": [                                           │
│      "Draft slides first, then review",                                  │
│      "Alice to create initial draft by Dec 10"                           │
│    ]                                                                     │
│  }                                                                       │
│                                                                          │
│  WHY? The scenario provides verifiable facts for grounding checks.       │
│                                                                          │
│                              │                                           │
│                              ▼                                           │
│  Step 3: ASSERTION CLASSIFICATION (GPT-5)                                │
│  ═════════════════════════════════════════                               │
│  Classify into one of 28 dimensions:                                     │
│                                                                          │
│  {                                                                       │
│    "dimension_id": "S2",                                                 │
│    "dimension_name": "Timeline Alignment",                               │
│    "layer": "structural",                                                │
│    "level": "critical",                                                  │
│    "rationale": "The assertion is about task sequencing..."              │
│  }                                                                       │
│                                                                          │
│                              │                                           │
│                              ▼                                           │
│  Step 4: INTELLIGENT G SELECTION (GPT-5)                                 │
│  ════════════════════════════════════════                                │
│  Select RELEVANT grounding dimensions for THIS specific assertion:       │
│                                                                          │
│  GPT-5 analyzes the assertion text to determine which G dimensions       │
│  are actually needed (not just blindly using the static S→G map).        │
│                                                                          │
│  Input: "The plan arranges draft slides before review slides"            │
│  S2 available Gs: [G3, G6]                                               │
│                                                                          │
│  GPT-5 reasoning:                                                        │
│  - G3 (Dates): NOT needed - no specific dates mentioned                  │
│  - G6 (Actions): NEEDED - assertion references specific tasks            │
│                                                                          │
│  Result (only relevant Gs):                                              │
│  • A0000_S2 (structural): "Timeline has correct sequencing"              │
│  • A0000_G6_0 (grounding): "Task ordering matches discussion"            │
│                                                                          │
│                              │                                           │
│                              ▼                                           │
│  Step 5: WBP GENERATION & VERIFICATION (GPT-5)                           │
│  ═════════════════════════════════════════════                           │
│  Generate a WBP that satisfies ALL assertions, then verify:              │
│                                                                          │
│  WBP includes:                                                           │
│  | T-n  | Date   | Task               | Owner       | Deliverable  |     │
│  |------|--------|--------------------|-------------|--------------|     │
│  | T-10 | Dec 05 | Draft slides       | Alice Chen  | Draft deck   |     │
│  | T-5  | Dec 10 | Review slides      | Bob Smith   | Feedback doc |     │
│  | T-0  | Dec 15 | Final presentation | Carol Davis | Final deck   |     │
│                                                                          │
│  Verification checks:                                                    │
│  [PASS] S2: Draft (T-10) before Review (T-5)                             │
│  [PASS] G3: Dates consistent with Dec 15 meeting                         │
│  [PASS] G6: Tasks trace to action_items_discussed                        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Why Scenario Generation?

The scenario serves as **synthetic ground truth** for grounding verification:

| Without Scenario           | With Scenario                                            |
|----------------------------|----------------------------------------------------------|
| "Names should be correct"  | "Names must be Alice, Bob, or Carol"                     |
| "Dates should be valid"    | "Dates must be before Dec 15, 2025"                      |
| "Files should exist"       | "Only Q1_slides_draft.pptx and marketing_data.xlsx exist"|

This allows us to **definitively verify** grounding assertions against concrete facts.

## S → G Mapping Rationale

Each mapping has a specific reason. For example:

| S Dimension    | G Dimension       | Rationale                                                      |
|----------------|-------------------|----------------------------------------------------------------|
| S2 (Timeline)  | G3 (Date/Time)    | Timeline dates must be consistent with the actual meeting date |
| S2 (Timeline)  | G6 (Action Items) | Task ordering must trace to action items actually discussed    |
| S3 (Ownership) | G2 (Attendee)     | Task owners must be actual attendees who can be accountable    |
| S3 (Ownership) | G6 (Action Items) | Ownership assignments must correspond to agreed-upon actions   |

The full mapping is in `dimensions.py`.

## Data Flow

```
Input Assertion
      |
      v
+-------------+    +--------------+
| GPT-5 Call  |--->|   Scenario   | (Ground Truth)
| #1          |    |   JSON       |
+-------------+    +------+-------+
      |                   |
      v                   |
+-------------+           |
| GPT-5 Call  |---> Classification (S2, structural, critical)
| #2          |           |
+-------------+           |
      |                   |
      v                   |
+-------------+    +------+-------+
| S->G Mapping|--->|  Assertions  |
| (Local)     |    |  [S2,G3,G6]  |
+-------------+    +------+-------+
      |                   |
      v                   v
+-------------+    +--------------+
| GPT-5 Call  |--->|     WBP      | (Satisfies S+G)
| #3          |    |   Markdown   |
+-------------+    +------+-------+
      |                   |
      v                   v
+-------------+    +--------------+
| GPT-5 Call  |--->| Verification | (Pass/Fail per assertion)
| #4          |    |   Results    |
+-------------+    +--------------+
      |
      v
Final Report (Console + JSON)
```

## Assertion Linkage Structure

The new **Hybrid Assertion Format** uses templates with slot placeholders:

```json
{
  "assertions": [
    {
      "assertion_id": "S2_A1",
      "dimension_id": "S2",
      "layer": "structural",
      "template": "All [TASK] entries must be scheduled using T-minus notation relative to [MEETING_DATE].",
      "instantiated": "All task entries must be scheduled using T-minus notation relative to March 15, 2025.",
      "slot_types": ["TASK", "MEETING_DATE"],
      "sub_aspect": "T-minus scheduling notation",
      "linked_g_dims": ["G3"]
    },
    {
      "assertion_id": "S2_A1_G3",
      "parent_assertion_id": "S2_A1",
      "dimension_id": "G3",
      "layer": "grounding",
      "template": "The [MEETING_DATE] must match the actual meeting date specified in the scenario.",
      "instantiated": "The March 15, 2025 must match the actual meeting date specified in the scenario.",
      "slot_types": ["MEETING_DATE"],
      "sub_aspect": "Meeting date accuracy",
      "rationale": {
        "mapping_reason": "Timeline dates must be consistent with meeting date",
        "parent_dimension": "S2"
      }
    }
  ]
}
```

### Assertion Format Fields

| Field | Description |
|-------|-------------|
| `assertion_id` | Unique ID (e.g., `S2_A1`, `G3_A1`) |
| `template` | Assertion with `[SLOT_TYPE]` placeholders |
| `instantiated` | Concrete example with actual values from reference scenario |
| `slot_types` | List of slot types used in the template |
| `sub_aspect` | Specific aspect of the dimension being tested |
| `linked_g_dims` | G dimensions that apply when evaluating this S assertion |
| `parent_assertion_id` | For G assertions, links back to the parent S assertion |

### Slot Types Reference

| Slot Type | Description | Example |
|-----------|-------------|---------|
| `[ATTENDEE]` | Person from attendee list | Alice Chen, Bob Smith |
| `[MEETING_DATE]` | The meeting date | March 15, 2025 |
| `[DUE_DATE]` | A task due date | March 10, 2025 |
| `[TASK]` | A task name/description | finalize slides |
| `[OWNER]` | Task owner (same as ATTENDEE) | Carol Davis |
| `[ARTIFACT]` | File/document reference | Q1_slides.pptx |
| `[TOPIC]` | Agenda topic | budget allocation |
| `[ACTION_ITEM]` | Action item from scenario | review budget |
| `[DELIVERABLE]` | Output/deliverable | Final deck v2.0 |
| `[MEETING_TITLE]` | Meeting title | Q1 Marketing Strategy Review |
| `[ENTITY]` | Any named entity | (used for hallucination checks) |
```

---

## Framework Dimensions

> **Note**: The assertions below use the **Hybrid Format** with template placeholders and instantiated examples. Generated by GPT-5.

### Reference Scenario

| Field | Value |
|-------|-------|
| Meeting | Q1 Marketing Strategy Review |
| Date | March 15, 2025 |
| Attendees | Alice Chen (PM), Bob Smith (Designer), Carol Davis (Engineer), David Lee (Marketing Lead) |
| Artifacts | Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx |
| Topics | Q1 priorities, budget allocation, campaign timeline |
| Action Items | finalize slides, review budget, launch campaign |

### Structural (S1-S20) - Hybrid Format Examples

Each S assertion uses the hybrid format with `linked_g_dims` specifying which G assertions apply:

#### S1: Meeting Details

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S1_A1 | The meeting title must be explicitly stated as [MEETING_TITLE]. | ...Q1 Marketing Strategy Review. | MEETING_TITLE | Meeting title clarity | - |
| S1_A2 | The meeting date must be clearly stated as [MEETING_DATE] and include time/timezone. | ...March 15, 2025... | MEETING_DATE | Date/time specification | G3 |
| S1_A3 | The attendee list must include all required attendees: [ATTENDEE]+. | ...Alice Chen, Bob Smith, Carol Davis, David Lee. | ATTENDEE | Attendee completeness | G2 |

#### S2: Timeline Alignment

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S2_A1 | All [TASK] entries must use T-minus notation relative to [MEETING_DATE]. | ...relative to March 15, 2025. | TASK, MEETING_DATE | T-minus notation | G3 |
| S2_A2 | Each [TASK] must have a [DUE_DATE] before [MEETING_DATE]. | ...'finalize slides' before March 15, 2025. | TASK, DUE_DATE, MEETING_DATE | Deadline alignment | G3, G6 |
| S2_A3 | Tasks must be ordered by dependency. | ...'finalize slides' before 'launch campaign'. | TASK | Dependency sequencing | G6 |

#### S3: Ownership Assignment

| ID | Template | Instantiated | Slot Types | Sub-aspect | Linked G |
|----|----------|--------------|------------|------------|----------|
| S3_A1 | Each [TASK] must have a named [OWNER] assigned. | ...'finalize slides' assigned to Alice Chen. | TASK, OWNER | Owner presence | G2, G6 |
| S3_A2 | If [OWNER] unavailable, provide role/skill placeholder for [TASK]. | ...'Designer' for 'review slides'. | OWNER, TASK | Role placeholder | G6 |
| S3_A3 | Every [OWNER] must be from the scenario attendee list. | ...Alice Chen, Bob Smith, Carol Davis, David Lee. | OWNER, TASK | Owner validity | G2 |

### Grounding (G1-G9) - Reference Library

G assertions serve as a **reference library** that S assertions link to via `linked_g_dims`. They are never standalone.

> **G9 (Planner-Generated Consistency)**: NEW - Validates that planner-created content (assumptions, blockers, mitigations, open questions) doesn't contradict scenario facts. Enables creative planning while preventing hallucination.

#### G1: Hallucination Check

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G1_A1 | Every mentioned [ATTENDEE] must exist in scenario attendee list. | ...one of: Alice Chen, Bob Smith, Carol Davis, David Lee. | ATTENDEE | No fabricated names |
| G1_A2 | Every referenced [ARTIFACT] must match an artifact from scenario. | ...one of: Q1_slides.pptx, budget_2025.xlsx, marketing_plan.docx. | ARTIFACT | No fabricated artifacts |
| G1_A3 | All mentioned [TOPIC] must correspond to scenario topics. | ...Q1 priorities, budget allocation, campaign timeline. | TOPIC | No fabricated topics |

#### G2: Attendee Grounding

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G2_A1 | Every [OWNER] assigned to [TASK] must be from scenario attendee list. | ...Alice Chen, Bob Smith, Carol Davis, David Lee. | OWNER, TASK | Task owner validity |
| G2_A2 | Any [ATTENDEE] in descriptions must exist in scenario. | ...scenario attendee list. | ATTENDEE | Incidental mention validity |
| G2_A3 | No [ENTITY] outside scenario attendee list should appear. | ...no names outside Alice, Bob, Carol, David. | ENTITY | No hallucinated people |

#### G3: Date/Time Grounding

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G3_A1 | The [MEETING_DATE] must match scenario meeting date. | ...March 15, 2025... | MEETING_DATE | Meeting date accuracy |
| G3_A2 | No [DUE_DATE] should occur after [MEETING_DATE] for pre-meeting tasks. | ...before March 15, 2025. | DUE_DATE, MEETING_DATE | Due date consistency |

#### G6: Action Item Grounding

| ID | Template | Instantiated | Slot Types | Sub-aspect |
|----|----------|--------------|------------|------------|
| G6_A1 | Every [TASK] must correspond to an [ACTION_ITEM] from scenario. | ...finalize slides, review budget, launch campaign. | TASK, ACTION_ITEM | Task traceability |
| G6_A2 | WBP must include [TASK] for each scenario [ACTION_ITEM]. | ...all action items covered. | ACTION_ITEM, TASK | Coverage completeness |

### Complete S → G Mapping

> **Status Legend**: REQUIRED, ASPIRATIONAL, CONDITIONAL, N/A (not applicable), MERGED

```
S1  (Meeting Details)          → G2, G3, G5        [REQUIRED]
S2  (Timeline)                 → G3, G6            [REQUIRED]
S3  (Ownership)                → G2, G6            [REQUIRED]
S4  (Deliverables)             → G4, G5            [REQUIRED]
S5  (Task Dates)               → G3                [REQUIRED]
S6  (Dependencies & Blockers)  → G2, G6, G7, G9    [REQUIRED + ASPIRATIONAL] (merged S11, S13)
S7  (Meeting Outcomes)         → (none)            [N/A - not applicable to WBP]
S8  (Parallel Workstreams)     → G2, G6            [ASPIRATIONAL]
S9  (Checkpoints)              → G2, G3, G6        [ASPIRATIONAL]
S10 (Resource-Aware Planning)  → G2, G3, G4, G6    [CONDITIONAL]
S11 (Risk Mitigation)          → (none)            [MERGED into S6]
S12 (Communication Plan)       → (none)            [MERGED into S17]
S13 (Escalation Protocol)      → (none)            [MERGED into S6]
S14 (Feedback Integration)     → (none)            [N/A - operational]
S15 (Progress Tracking)        → (none)            [N/A - operational]
S16 (Assumptions)              → G5, G6, G9        [ASPIRATIONAL]
S17 (Cross-team Coordination)  → G2, G3, G6        [CONDITIONAL]
S18 (Post-Event Actions)       → G2, G3, G6        [ASPIRATIONAL]
S19 (Open Questions)           → G2, G3, G6, G9    [ASPIRATIONAL]
S20 (Clarity & First Impression) → G2, G3, G5, G7  [REQUIRED]
```

---

## Examples

See the `examples/` directory for sample inputs and outputs:

### Input Files
- `sample_input.txt` - 8 example assertions covering different dimensions (S1-S9)
- `sample_batch_input.txt` - 5 simpler assertions for quick batch testing

### Output Directories
- `sample_input_output/` - Batch run results from `sample_input.txt` (8 assertions)
- `sample_batch_input_output/` - Batch run results from `sample_batch_input.txt` (5 assertions)

Each output directory contains:
- `A000N_analysis.json` - Full JSON output with S+G linkage for each assertion
- `A000N_analysis.md` - Markdown report for each assertion
- `_batch_summary.json` - Summary of all results in JSON format
- `_batch_summary.md` - Human-readable batch summary
- `_assertions_index.json` - Index mapping assertion IDs to input text

### Running the Examples

```powershell
# Run single assertion
.\run.ps1 "The response arranges the draft slides task before review slides task"

# Run batch on sample_input.txt
.\run.ps1 -Batch "examples/sample_input.txt" -OutputDir "examples/sample_input_output"

# Run batch on sample_batch_input.txt  
.\run.ps1 -Batch "examples/sample_batch_input.txt" -OutputDir "examples/sample_batch_input_output"
```

---

## Customizing Prompts

Edit `prompts.json` to customize the GPT-5 prompts:

```json
{
  "system_prompt": "Your custom system prompt...",
  "scenario_generation_prompt": "Your scenario prompt...",
  "wbp_generation_prompt": "Your WBP generation prompt...",
  "wbp_verification_prompt": "Your verification prompt..."
}
```

## Authentication

The package uses Microsoft MSAL broker authentication to access the Substrate GPT-5 API. This requires Windows because the MSAL broker (`enable_broker_on_windows=True`) is a Windows-specific feature. On first run, a browser window may open for authentication.

## Package Structure

```
assertion_analyzer/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point
├── analyzer.py          # Core analysis functions
├── config.py            # API configuration
├── dimensions.py        # Dimension definitions & S→G mapping
├── prompts.json         # Legacy GPT-5 prompts (v2.1)
├── prompts/             # Optimized prompt files (v3.0)
│   ├── classification_prompt.json      # Single assertion → dimension(s)
│   ├── ie_slot_extraction_prompt.json  # Extract slot values for G dims
│   └── decomposition_prompt.json       # Free-form → atomic S+G units
├── requirements.txt     # Python dependencies
├── setup_env.py         # Environment setup script
├── run.ps1              # Windows run script
├── examples/            # Sample inputs and outputs
│   ├── sample_input.txt              # 8 assertions for batch testing
│   ├── sample_batch_input.txt        # 5 assertions for quick testing
│   ├── sample_input_output/          # Results from sample_input.txt
│   └── sample_batch_input_output/    # Results from sample_batch_input.txt
├── .venv/               # Virtual environment (created on first run)
└── README.md            # This file
```

### Prompt Files (v3.0)

The `prompts/` directory contains optimized JSON prompt files designed through GPT-5 iteration:

| File | Purpose | Version |
|------|---------|---------|
| `classification_prompt.json` | Classify assertions into S/G dimensions with all definitions inline | 2.0 |
| `ie_slot_extraction_prompt.json` | Extract slot values (names, dates, files) for G dimensions | 2.0 |
| `decomposition_prompt.json` | Decompose free-form assertions into atomic S+G units | 3.0 |

Each prompt file contains:
- `system_prompt`: Role and task description
- `user_prompt_template`: Template with `{assertion_text}` placeholder
- `output_schema`: Expected JSON structure
- `temperature`: Recommended temperature setting
- `notes`: Design decisions and usage tips

## Dependencies

- `msal[broker]>=1.24.0` - Microsoft authentication (Windows only)
- `requests>=2.28.0` - HTTP client
