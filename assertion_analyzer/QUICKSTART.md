# Assertion Analyzer - Quick Start

**Analyze WBP (Workback Plan) assertions using GPT-5.**

## Requirements

- **Windows** (required for MSAL broker authentication)
- **Python 3.10+** - Download from https://www.python.org/downloads/
- **Microsoft account** with GPT-5 API access

## Setup (One-time)

### Option 1: Using run script (Recommended)
```powershell
cd assertion_analyzer
.\run.ps1   # Auto-creates .venv and installs dependencies
```

### Option 2: Manual setup
```powershell
cd assertion_analyzer

# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Single Assertion
```powershell
.\run.ps1 "The plan includes task deadlines"
```

### Batch Mode
```powershell
.\run.ps1 -Batch "examples/sample_input.txt" -OutputDir "./results"
```

### Options
| Flag | Description |
|------|-------------|
| `-Json` | Output JSON only |
| `-NoExamples` | Quick classification (no WBP generation) |
| `-OutputDir` | Specify output directory |
| `-Context` | Add meeting context |

## Output

Each assertion generates:
- `A000N_analysis.json` - Full analysis with S+G linkage
- `A000N_analysis.md` - Human-readable report

## What It Does

1. **Classifies** assertion into 29 dimensions (S1-S20 structural + G1-G9 grounding)
2. **Generates** a meeting scenario as ground truth
3. **Creates** a workback plan (WBP) satisfying the assertion
4. **Verifies** the WBP against all S+G assertions

## Examples

See `examples/` for sample inputs and outputs.

## Documentation

- `README.md` - Full documentation
- `WBP_Framework_Design_Summary.md` - Design principles
- `WBP_Evaluation_Complete_Dimension_Reference.md` - Dimension reference
