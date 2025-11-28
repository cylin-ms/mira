# WBP Evaluation Pipeline

## User Guide

This guide explains how to use the Workback Plan (WBP) Evaluation Pipeline based on **Chin-Yew's WBP Evaluation Rubric** to simulate and evaluate workback plan generation quality.

---

## Table of Contents

1. [Overview](#overview)
2. [What Does It Do?](#what-does-it-do)
3. [Quick Start](#quick-start)
4. [Pipeline Stages](#pipeline-stages)
5. [Command Reference](#command-reference)
6. [Understanding the Output](#understanding-the-output)
7. [Managing Runs](#managing-runs)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The pipeline simulates the full lifecycle of workback plan generation and evaluation:

1. **Creates realistic meeting scenarios** with attendees, dates, artifacts, and context
2. **Generates two-layer assertions** (Structural S1-S18 + Grounding G1-G5) to evaluate plan quality
3. **Produces plans at three quality levels** (perfect, medium, low) for testing
4. **Evaluates plans** against assertions using GPT-5 JJ with weighted scoring
5. **Generates comprehensive reports** with metrics, strengths, weaknesses, and next actions

### Why Use This Pipeline?

- **Validate assertion frameworks** before deploying to production
- **Test evaluation logic** with controlled quality variations
- **Generate training data** for ML models
- **Benchmark different prompting strategies**
- **Document and reproduce experiments** with unique run IDs

---

## What Does It Do?

### Chin-Yew's WBP Evaluation Rubric

The pipeline implements **Chin-Yew's WBP Evaluation Rubric** (see `docs/ChinYew/WBP_Evaluation_Rubric.md`) with:

- **Scoring Model:** 0 = Missing, 1 = Partial, 2 = Fully Met
- **Weighted Quality Score:** Σ(score × weight) / max_possible
- **Weights:** Critical = 3, Moderate = 2, Light = 1

#### Layer 1: Structural Assertions (S1-S18)
*Question: "Does the plan HAVE X?"*

These check for **presence** of required elements:

| ID | Pattern | Weight | What It Checks |
|----|---------|:------:|----------------|
| **S1** | Meeting Details | 3 | Subject, date, time, timezone, attendee list |
| **S2** | Timeline Alignment | 3 | Backward scheduling (T-minus) with dependency-aware sequencing |
| **S3** | Ownership Assignment | 3 | Named owners OR role/skill placeholders |
| S12 | Milestone Validation | 2 | Feasible, right-sized, coherent milestones |
| S4 | Deliverables & Artifacts | 2 | Outputs with links, version/format |
| S5 | Task Dates | 2 | Due dates aligned with timeline |
| S6 | Dependencies & Blockers | 2 | Predecessors, risks, mitigation steps |
| S7 | Source Traceability | 2 | Tasks/artifacts link to source |
| S9 | Grounding Meta-Check | 2 | All G1-G5 pass; no factual drift |
| S10 | Priority Assignment | 2 | Tasks ranked by critical path |
| S11 | Risk Mitigation Strategy | 2 | Concrete contingencies with owners |
| S13 | Goal & Success Criteria | 2 | Clear objectives and measurable indicators |
| S14 | Resource Allocation | 2 | People/time/tools/budget visibility |
| S8 | Communication Channels | 1 | Teams, email, meeting cadence |
| S15 | Compliance & Governance | 1 | Security, privacy, regulatory checks |
| S16 | Review & Feedback Loops | 1 | Scheduled checkpoints |
| S17 | Escalation Path | 1 | Escalation owners and steps |
| S18 | Post-Event Actions | 1 | Wrap-up tasks, retrospectives |

#### Layer 2: Grounding Assertions (G1-G5)
*Question: "Is X CORRECT vs source?"*

These check for **factual accuracy** against source data:

| ID | Pattern | Weight | Source Field |
|----|---------|:------:|--------------|
| **G1** | Attendee Grounding | 3 | source.attendees |
| **G2** | Date/Time Grounding | 3 | source.meeting_date/time |
| **G5** | Hallucination Check | 3 | All source fields |
| G3 | Artifact Grounding | 2 | source.files |
| G4 | Topic Grounding | 2 | source.topics |

### Quality Levels

The pipeline generates plans at three quality levels to test detection:

| Quality | Target Structural | Target Grounding | Deliberate Issues |
|---------|------------------|------------------|-------------------|
| **Perfect** | 100% | 100% | None - fully compliant |
| **Medium** | 80% | 60% | Missing priorities, fabricated attendees |
| **Low** | 40% | 20% | Generic owners, wrong dates, hallucinated files |

---

## Quick Start

### Run the Full Pipeline

```powershell
# Run with default template scenarios
python -m pipeline.run_pipeline

# Run with custom scenarios from data file
python -m pipeline.run_pipeline --from-data docs/LOD_1121.WithUserUrl.jsonl --limit 5
```

### View Results

After the pipeline completes, you'll see:
- A unique **Run ID** (e.g., `run_20251128_152644_fdcff2d3`)
- All outputs saved to `docs/pipeline_runs/<run_id>/`
- A comprehensive **evaluation report** in Markdown format

```powershell
# List all previous runs
python -m pipeline.run_pipeline --list-runs

# Open the report
code docs/pipeline_runs/<run_id>/evaluation_report.md
```

---

## Pipeline Stages

### Stage 1: Scenario Generation

**Purpose:** Create realistic meeting scenarios with ground truth data.

**Inputs:** 
- Built-in templates OR
- External JSONL data file

**Outputs:** `scenarios.json`

Each scenario includes:
- Meeting details (title, date, time, timezone, duration)
- Organizer and attendees
- Context and objectives
- Artifacts (files, documents)
- Dependencies and blockers
- User prompt (what triggered the workback plan request)

**Example scenario:**
```json
{
  "id": "scenario_001",
  "title": "Q1 Product Launch Readiness Review",
  "date": "January 15, 2025",
  "time": "2:00 PM",
  "timezone": "PST",
  "organizer": "Sarah Chen",
  "attendees": ["Sarah Chen", "Mike Johnson", "Lisa Park"],
  "artifacts": ["Product_Launch_Checklist_v3.xlsx", "Engineering_Status_Report.pdf"],
  "context": "The team is preparing for a major product launch..."
}
```

---

### Stage 2: Assertion Generation

**Purpose:** Generate two-layer assertions (S1-S10 + G1-G5) for each scenario.

**Inputs:** `scenarios.json`

**Outputs:** `assertions.json`

**What happens:**
1. For each scenario, GPT-5 generates 10 structural assertions
2. Then generates 5 grounding assertions with source field references
3. Each assertion is tagged with pattern ID, level, and layer

**Example structural assertion:**
```json
{
  "id": "A1",
  "pattern_id": "S1",
  "text": "The workback plan includes explicit meeting details (date, time, timezone, attendees)",
  "level": "critical",
  "checks_for": "presence of meeting metadata",
  "layer": "structural"
}
```

**Example grounding assertion:**
```json
{
  "id": "G1",
  "pattern_id": "G1",
  "text": "All people mentioned in the plan exist in source.attendees",
  "level": "critical",
  "source_field": "source.attendees",
  "layer": "grounding"
}
```

---

### Stage 3: Plan Generation

**Purpose:** Generate workback plans at three quality levels for each scenario.

**Inputs:** `scenarios.json`

**Outputs:** `plans.json`

**What happens:**
1. For each scenario, generates a **perfect** plan (100% compliant)
2. Generates a **medium** plan (deliberate minor issues)
3. Generates a **low** plan (significant issues and hallucinations)

**Deliberate issues in medium plans:**
- Missing priority assignments
- One fabricated attendee name
- One non-existent file reference

**Deliberate issues in low plans:**
- No explicit meeting date/time
- Generic owners ("someone", "the team", "TBD")
- Multiple fabricated files
- Wrong dates and timelines
- Hallucinated topics

---

### Stage 4: Plan Evaluation

**Purpose:** Evaluate each plan against its assertions using GPT-5 JJ.

**Inputs:** `scenarios.json`, `assertions.json`, `plans.json`

**Outputs:** `evaluation_results.json`

**What happens:**
1. For each plan, evaluates all structural assertions (pass/fail)
2. Evaluates all grounding assertions against source data
3. Calculates structural score (% passed) and grounding score (% passed)
4. Assigns verdict: `pass`, `fail_structure`, `fail_grounding`, or `fail_both`

**Verdict logic:**
- **pass**: Structural ≥ 75% AND Grounding ≥ 75%
- **fail_structure**: Structural < 75% AND Grounding ≥ 75%
- **fail_grounding**: Structural ≥ 75% AND Grounding < 75%
- **fail_both**: Structural < 75% AND Grounding < 75%

---

### Stage 5: Report Generation

**Purpose:** Generate a comprehensive Markdown report with all results.

**Inputs:** All previous stage outputs

**Outputs:** `evaluation_report.md`

**Report sections:**
1. Executive Summary
2. Key Metrics
3. Scenarios (full details)
4. Assertions (tables by scenario)
5. Plans (collapsible content)
6. Evaluation Results by Quality Level
7. Two-Layer Framework Analysis
8. Verdict Distribution
9. Detailed Results (per plan)
10. Insights & Recommendations
11. Appendix: Framework Reference

---

## Command Reference

### Basic Commands

```powershell
# Run full pipeline (creates new run ID)
python -m pipeline.run_pipeline

# Run with custom run ID
python -m pipeline.run_pipeline --run-id experiment_01

# Use external data source
python -m pipeline.run_pipeline --from-data path/to/data.jsonl --limit 5

# Enrich scenarios with GPT-5
python -m pipeline.run_pipeline --enrich
```

### Run Management

```powershell
# List all previous runs
python -m pipeline.run_pipeline --list-runs

# Continue/examine an existing run
python -m pipeline.run_pipeline --continue-run run_20251128_152644_fdcff2d3

# Resume from a specific stage
python -m pipeline.run_pipeline --continue-run <run_id> --resume-from 4
```

### Selective Execution

```powershell
# Run only specific stages
python -m pipeline.run_pipeline --stages 1,2,3

# Skip stages with existing output
python -m pipeline.run_pipeline --skip-existing

# Resume from stage 3
python -m pipeline.run_pipeline --resume-from 3
```

### Run Individual Stages

```powershell
# Stage 1: Generate scenarios
python -m pipeline.scenario_generation --template

# Stage 2: Generate assertions
python -m pipeline.assertion_generation --scenarios docs/pipeline_runs/<run_id>/scenarios.json

# Stage 3: Generate plans
python -m pipeline.plan_generation --scenarios docs/pipeline_runs/<run_id>/scenarios.json

# Stage 4: Evaluate plans
python -m pipeline.plan_evaluation --scenarios ... --assertions ... --plans ...

# Stage 5: Generate report
python -m pipeline.report_generation --evaluation docs/pipeline_runs/<run_id>/evaluation_results.json
```

---

## Understanding the Output

### Run Directory Structure

Each run creates a directory under `docs/pipeline_runs/<run_id>/`:

```
docs/pipeline_runs/run_20251128_152644_fdcff2d3/
├── run_metadata.json        # Run ID, status, timestamps
├── scenarios.json           # Stage 1 output
├── assertions.json          # Stage 2 output
├── plans.json               # Stage 3 output
├── evaluation_results.json  # Stage 4 output
└── evaluation_report.md     # Stage 5 output (final report)
```

### Run Metadata

```json
{
  "run_id": "run_20251128_152644_fdcff2d3",
  "created_at": "2025-11-28T15:26:44.123456",
  "status": "completed",
  "updated_at": "2025-11-28T15:33:18.654321"
}
```

Status values: `initialized`, `running`, `completed`, `failed`

### Key Metrics to Watch

1. **Quality Differentiation:** Perfect > Medium > Low scores
2. **Structural vs Grounding Gap:** Large gaps indicate hallucination issues
3. **Pass Rate by Quality:** Perfect should pass, Low should fail
4. **Per-Assertion Pass Rates:** Identify weak assertion patterns

### Expected Results

| Quality | Expected Structural | Expected Grounding | Expected Verdict |
|---------|--------------------|--------------------|------------------|
| Perfect | 80-100% | 80-100% | pass |
| Medium | 60-80% | 30-60% | fail_both or fail_grounding |
| Low | 20-40% | 0-20% | fail_both |

---

## Managing Runs

### Listing Runs

```powershell
python -m pipeline.run_pipeline --list-runs
```

Output:
```
📁 Available Pipeline Runs (3 total):
================================================================================
Run ID                                        Created              Status
--------------------------------------------------------------------------------
run_20251128_152644_fdcff2d3                  2025-11-28 15:26     completed
run_20251128_140000_abc12345                  2025-11-28 14:00     completed
run_20251127_093000_xyz98765                  2025-11-27 09:30     failed
```

### Comparing Runs

To compare results across runs:

```powershell
# View reports side by side
code docs/pipeline_runs/run_A/evaluation_report.md docs/pipeline_runs/run_B/evaluation_report.md

# Compare metrics programmatically
python -c "
import json
run_a = json.load(open('docs/pipeline_runs/run_A/evaluation_results.json'))
run_b = json.load(open('docs/pipeline_runs/run_B/evaluation_results.json'))
print('Run A pass rate:', run_a['summary']['by_verdict'].get('pass', 0))
print('Run B pass rate:', run_b['summary']['by_verdict'].get('pass', 0))
"
```

### Cleaning Up Old Runs

```powershell
# Remove a specific run
Remove-Item -Recurse -Force docs/pipeline_runs/run_20251127_093000_xyz98765

# Keep only last 5 runs
Get-ChildItem docs/pipeline_runs | Sort-Object Name -Descending | Select-Object -Skip 5 | Remove-Item -Recurse -Force
```

---

## Advanced Usage

### Custom Scenarios

Create your own scenarios JSON:

```json
{
  "generated_at": "2025-11-28T12:00:00",
  "source": "custom",
  "scenarios": [
    {
      "id": "custom_001",
      "title": "My Custom Meeting",
      "date": "December 1, 2025",
      "time": "10:00 AM",
      "timezone": "EST",
      "duration_minutes": 60,
      "organizer": "Jane Doe",
      "attendees": ["Jane Doe", "John Smith"],
      "context": "Quarterly review meeting...",
      "artifacts": ["Q4_Report.xlsx"],
      "dependencies": ["Budget approval"],
      "user_prompt": "Create a workback plan for the quarterly review",
      "source_entities": {
        "attendees": ["Jane Doe", "John Smith"],
        "organizer": "Jane Doe",
        "meeting_date": "December 1, 2025",
        "meeting_time": "10:00 AM",
        "timezone": "EST",
        "files": ["Q4_Report.xlsx"],
        "topics": ["Quarterly review", "Budget"],
        "dependencies": ["Budget approval"]
      }
    }
  ]
}
```

Then run:
```powershell
python -m pipeline.assertion_generation --scenarios my_scenarios.json --output my_assertions.json
```

### Modifying Quality Thresholds

Edit `pipeline/plan_evaluation.py` to adjust pass/fail thresholds:

```python
# Current thresholds (75%)
STRUCTURAL_THRESHOLD = 0.75
GROUNDING_THRESHOLD = 0.75
```

### Adding Custom Assertion Patterns

Edit `pipeline/assertion_generation.py` to add new patterns:

```python
STRUCTURAL_PATTERNS = {
    # ... existing patterns ...
    "S11": {
        "name": "Risk Assessment",
        "description": "Plan includes risk assessment section",
        "checks_for": "presence of risk analysis"
    }
}
```

---

## Troubleshooting

### Authentication Issues

**Error:** "Failed to authenticate with Microsoft"

**Solution:**
1. Make sure you're on the corporate network or VPN
2. Clear token cache: `Remove-Item ~/.msal_token_cache.bin -ErrorAction SilentlyContinue`
3. Try again - browser will open for authentication

### Rate Limiting

**Error:** "429 Too Many Requests"

**Solution:**
- The pipeline has built-in delays (2 seconds between calls)
- If you still hit limits, increase `DELAY_BETWEEN_CALLS` in `pipeline/config.py`

### Missing Prerequisites

**Error:** "Missing prerequisite: scenarios.json"

**Solution:**
- Run stages in order, or use `--resume-from` to start from the right stage
- Or run the full pipeline: `python -m pipeline.run_pipeline`

### Incomplete Runs

**Error:** Pipeline stopped mid-way

**Solution:**
1. Find your run ID: `python -m pipeline.run_pipeline --list-runs`
2. Resume: `python -m pipeline.run_pipeline --continue-run <run_id> --resume-from <stage>`

---

## Example Workflow

### 1. Initial Experiment

```powershell
# Run full pipeline with templates
python -m pipeline.run_pipeline --run-id baseline_v1

# View results
code docs/pipeline_runs/baseline_v1/evaluation_report.md
```

### 2. Test with Real Data

```powershell
# Run with production-like data
python -m pipeline.run_pipeline --run-id real_data_test --from-data docs/LOD_1121.WithUserUrl.jsonl --limit 10
```

### 3. Compare Results

```powershell
# List runs
python -m pipeline.run_pipeline --list-runs

# Compare pass rates
python -c "
import json
for run_id in ['baseline_v1', 'real_data_test']:
    data = json.load(open(f'docs/pipeline_runs/{run_id}/evaluation_results.json'))
    pass_rate = data['summary']['by_verdict'].get('pass', 0) / len(data['results']) * 100
    print(f'{run_id}: {pass_rate:.1f}% pass rate')
"
```

---

## Support

For questions or issues:
1. Check the [README.md](../README.md) for project overview
2. Review [LESSONS_LEARNED_ASSERTION_FRAMEWORK.md](LESSONS_LEARNED_ASSERTION_FRAMEWORK.md) for framework details
3. Open an issue in the repository

---

*Last updated: November 28, 2025*
