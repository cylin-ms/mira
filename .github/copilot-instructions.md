# Copilot Instructions

**Author**: Chin-Yew Lin

**IMPORTANT**: GitHub Copilot, you MUST always check this file (`.github/copilot-instructions.md`) at the beginning of a session or when switching tasks. You must read the instructions herein and update the content (specifically the Scratchpad and Lessons sections) as you progress.

## 1. Core Instructions

- **Continuous Learning**: If you find reusable information (e.g., library versions, model names) or correct a mistake, add it to the **Lessons** section below.
- **Task Management**: Use the **Scratchpad** section to organize your thoughts.
    - Review the Scratchpad when receiving a new task.
    - Clear old tasks if necessary.
    - Plan steps and use todo markers (`[ ]`, `[X]`).
    - Update progress as you finish subtasks.
- **Self-Correction**: Before editing a file, read it. If you make a mistake, record it in Lessons.
- **Daily Summary**: Create a daily summary per date when you have a chance. The daily cycle is defined from 12:01 AM local time to 12:00 AM the next day.
    - **Location**: Store in `daily_summaries/` directory.
    - **Naming**: Use `YYYY-MM-DD.md` format.
    - **Purpose**: To track major achievements for future diaries, automatic newsletters, and performance reviews.

## 2. Project Guidelines

- **Documentation**: Always use Markdown for documentation and README files.
- **README Structure**: Maintain the existing structure of `README.md`.
- **Code Style**:
    - Use descriptive names.
    - Maintain consistency in capitalization and punctuation.
    - Focus on project-specific instructions.
    - Provide context on what you're building, style guidelines, or info on commonly-used methods.
- **Metadata**:
    - **Author**: All documents created must include an author field with the value "Chin-Yew Lin".

## 3. Tools Reference

Note: All tools are in python. You can consult the python files and write your own script for batch processing.

### GPT-5 Q&A Tool
Interactive and batch Q&A with GPT-5, with automatic session logging organized by date.
- **Interactive**: `python tools/gpt5_qa.py` or `.\gpt5.ps1`
- **Single Question**: `python tools/gpt5_qa.py -q "Your question"` or `.\gpt5.ps1 "Your question"`
- **From File**: `python tools/gpt5_qa.py --prompt-file question.txt`
- **List Sessions**: `python tools/gpt5_qa.py --list-sessions`
- **View Session**: `python tools/gpt5_qa.py --view-session 2025-11-29/session_001.json`
- **Storage**: All Q&A sessions saved to `gpt5_prompts/YYYY-MM-DD/session_NNN.json`

### Screenshot Verification
Capture screenshots and verify with LLMs.
- **Capture**: `python tools/screenshot_utils.py URL [--output OUTPUT] [--width WIDTH] [--height HEIGHT]`
- **Verify**: `python tools/llm_api.py --prompt "Question" --provider {openai|anthropic} --image path/to/screenshot.png`

### LLM API
Invoke LLM for tasks.
- **Command**: `python ./tools/llm_api.py --prompt "Prompt" --provider "anthropic"`
- **Providers**: OpenAI (gpt-4o), Azure OpenAI, DeepSeek, Anthropic (claude-3-sonnet), Gemini, Local LLM.

### GPT-5 API (Windows)
Call Substrate GPT-5 JJ API using MSAL broker authentication.
- **Endpoint**: `https://fe-26.qas.bing.net/chat/completions`
- **Model**: `dev-gpt-5-chat-jj`
- **Auth**: MSAL broker with `enable_broker_on_windows=True`
- **Dependencies**: `pip install msal[broker] requests`
- **See**: Full code sample in Lessons section below

### Web Browser
Scrape web pages.
- **Command**: `python ./tools/web_scraper.py --max-concurrent 3 URL1 URL2`

### Search Engine
Search the web.
- **Command**: `python ./tools/search_engine.py "keywords"`

## 4. Lessons

### User Specified Lessons
- You have a python venv in `./venv`. Use it.
- **Python is already installed** - do NOT run `python --version` or check if Python exists. Just use it directly.
- Include info useful for debugging in the program output.
- Read the file before you try to edit it.
- When using `git` and `gh` for multiline messages, write to a file first, then use `git commit -F <filename>`. Include "[Copilot] " in the commit message.
- For ASCII diagrams in markdown, use plain ASCII characters (`+`, `-`, `|`, `v`, `--->`) instead of Unicode box-drawing characters for consistent rendering.

### S/G Dimension Definition Update Checklist

When updating S (Structural) or G (Grounding) dimension definitions, the following files must be updated:

**Primary Definition Files (Update First):**
1. `assertion_analyzer/dimensions.py` - Source of truth for `S_TO_G_MAP`, `G_RATIONALE_FOR_S`, `DIMENSION_NAMES`
2. `assertion_analyzer/prompts.json` - GPT-5 prompts referencing dimensions

**Main Documentation:**
3. `assertion_analyzer/README.md` - S+G Framework, Workflow diagram, S→G Mapping table, examples
4. `README.md` (project root) - Data format section with S+G linkage
5. `.github/copilot-instructions.md` - Lessons section

**ChinYew Documentation Suite:**
6. `docs/ChinYew/WBP_Evaluation_Complete_Dimension_Reference.md` - Canonical dimension reference tables
7. `docs/ChinYew/WBP_Evaluation_Rubric.md` - Scoring tables, Success/Fail examples
8. `docs/ChinYew/Assertion_Framework_Migration_Report.md` - Section 7 (Grounding Layer Design)
9. `docs/ChinYew/ASSERTION_QUALITY_REPORT.md` - Quality assessment criteria
10. `docs/ChinYew/LESSONS_LEARNED_ASSERTION_FRAMEWORK.md` - Framework design decisions
11. `docs/ChinYew/ANNOUNCEMENT_WBP_Assertion_Framework.md` - Public announcement

**Data Files (May need re-generation):**
- `docs/ChinYew/assertions_converted_gpt5_combined.jsonl`
- `docs/ChinYew/assertions_kening_enhanced.jsonl`
- `docs/ChinYew/conversion_report.json`

**Scripts (May need logic updates):**
- `convert_kening_assertions.py`
- `assertion_analyzer/analyzer.py`
- For ASCII art tables/boxes: Always verify all lines have the **same character count** to ensure border alignment. Avoid emojis/Unicode symbols (like `✓`, `→`, `▼`) inside ASCII boxes as they have inconsistent display widths. Use plain ASCII alternatives like `[PASS]`, `-->`, `v` instead.

### GPT-5 API on Windows
To call Substrate GPT-5 JJ API on Windows:

```python
import msal
import ctypes
import requests

# Configuration
SUBSTRATE_ENDPOINT = "https://fe-26.qas.bing.net/chat/completions"
SUBSTRATE_RESOURCE = "https://substrate.office.com"
CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
JJ_MODEL = "dev-gpt-5-chat-jj"

# Authentication (Windows MSAL broker)
app = msal.PublicClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    enable_broker_on_windows=True,
)
scopes = [f"{SUBSTRATE_RESOURCE}/.default"]

# Try silent auth, then interactive
accounts = app.get_accounts()
if accounts:
    result = app.acquire_token_silent(scopes, account=accounts[0])
else:
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    result = app.acquire_token_interactive(scopes, parent_window_handle=hwnd)

token = result["access_token"]

# API Call
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-ModelType": JJ_MODEL
}
payload = {
    "model": JJ_MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Your prompt here"}
    ],
    "temperature": 0.3,
    "max_tokens": 4000
}
response = requests.post(SUBSTRATE_ENDPOINT, headers=headers, json=payload, timeout=120)
result = response.json()["choices"][0]["message"]["content"]
```

**Dependencies**: `pip install msal[broker] requests`

### Learned Lessons
<!-- Add project-specific lessons here as you learn them -->
- Step 4 (S→G mapping) now uses GPT-5 to intelligently select only relevant G dimensions based on assertion text, instead of blindly applying all mapped Gs
- **G assertions are NEVER standalone**: G-level (grounding) assertions are always instantiated through S-level (structural) assertions. S assertions define WHAT structural elements should exist, G assertions define the GROUNDING CONSTRAINTS that validate those elements against the source scenario. The `linked_g_dims` field in each S assertion specifies which G checks apply.
- **G9 Planner-Generated Consistency**: Added G9 to validate planner-created content (assumptions, blockers, mitigations, open questions). Enables GOOD PLANNING while preventing HALLUCINATION (contradicting scenario facts).
- **Dimension Status Classifications**: REQUIRED, ASPIRATIONAL, CONDITIONAL, N/A (operational), MERGED. Use these to determine penalty/scoring.
- **Slot Type Grounding**: GROUNDED (must match scenario), DERIVED (inferable), CONDITIONAL (if provided), PLANNER-GEN (G9 checks consistency), N/A (structural, no grounding).
- **S+G Dimensions are ATOMIC**: Each S or G dimension tests exactly ONE thing. Free-form assertions (like Kening's) can combine multiple requirements in one sentence. The conversion task is to DECOMPOSE one free-form assertion into multiple atomic S+G units. Example: "meeting '1:1 Review' scheduled July 26" → S1 (Title) + G5 (slot: '1:1 Review') AND S5 (Task Dates) + G3 (slot: 'July 26').
- **Multi-label Classification**: Use `decomposition_prompt.json` to break down free-form assertions. One assertion can trigger multiple S dimensions, each with linked G dimensions and extracted slot values.
- **Optimized Prompts via GPT-5**: When designing prompts for classification/IE tasks, run GPT-5 3 times and synthesize. Store optimized prompts in `assertion_analyzer/prompts/` as JSON files with version, system_prompt, user_prompt_template, output_schema, temperature, and notes.

### S→G→M Three-Layer Framework (2025-11-30 Design Discussion)

**Key Insight**: Hallucination prevention is fundamentally different from S and G assertions.

**Layer Definitions**:
| Layer | What it checks | Dependencies | Verification |
|-------|----------------|--------------|--------------|
| **S (Structural)** | Does X exist? (have/have not) | Independent | LLM reads response, answers yes/no |
| **G (Grounding)** | If X exists, is the value correct? | Independent (each G checks one thing) | Compare response value to source |
| **M (Meta)** | Are there any unsupported facts? | DEPENDENT on ALL Gs | Aggregates all G results |

**Why G1 (Hallucination Prevention) was removed**:
- S assertions: Check presence of specific elements (directly observable)
- G assertions (G2-G10): Check one value matches source (directly observable)
- Hallucination: Checks ABSENCE of unsupported content - requires exhaustively checking ALL G dimensions
- Hallucination is a **derived property** (M1), not a directly observable assertion

**G10 Independence**: G10 (Relation Grounding) checks if RELATION(X, Y) exists in source. It does NOT depend on whether X or Y are correct (that's G2/G6's job). Each G assertion is self-contained - it only verifies its own claim given the arguments. If arguments are wrong, that's a separate error counted by other G assertions.

**Final Framework**:
```
S Layer: S1-S20 (Existence checks - independent, check first)
G Layer: G2-G10 (Grounding checks - independent, each checks one value)
M Layer: M1 (No Hallucination - derived from all G results, computed last)
```

## 5. Scratchpad

### Current Task: Completed - assertion_analyzer v2.1 packaged and pushed

#### Completed Today (2025-11-30):
[X] 1. Added Haidong Zhang as coauthor to WBP_Framework_Design_Summary.md and WBP_Evaluation_Complete_Dimension_Reference.md
[X] 2. Added Foundation Documents section to README.md with version numbers
[X] 3. Updated assertion_analyzer/dimensions.py:
    - Added G9 (Planner-Generated Consistency) dimension
    - Updated S_TO_G_MAP with new G9 mappings
    - Updated G_RATIONALE_FOR_S with detailed rationale
    - Added dimension status comments (REQUIRED, ASPIRATIONAL, CONDITIONAL, N/A, MERGED)
    - Updated SLOT_TYPES with grounding classifications
    - Updated DIMENSION_NAMES (28→29 dimensions)
    - Updated GROUNDING_PRIORITY_ORDER to include G9
[X] 4. Updated assertion_analyzer/README.md:
    - Updated dimension counts (28→29, G1-G8→G1-G9)
    - Updated S→G Mapping table with status legend
    - Added G9 description to Grounding section
    - Added version and coauthors
[X] 5. Updated assertion_analyzer/prompts.json:
    - Updated all 4 prompts (system, scenario_generation, wbp_generation, wbp_verification)
    - Added G9 verification criteria
    - Version bumped to 2.1
[X] 6. Tested single assertion and batch mode - ALL PASSED (8/8 + 5/5 assertions)
[X] 7. Cleaned up assertion_analyzer/ directory (removed temp files, one-off scripts)
[X] 8. Copied example outputs to examples/ with dedicated subdirectories
[X] 9. Updated examples documentation in README.md
[X] 10. Created QUICKSTART.md for easy onboarding
[X] 11. Created assertion_analyzer_v2.1.zip (211 KB) for sharing
[X] 12. Committed and pushed to GitHub (commit 0958f20, 100 files, 17,051 insertions)

#### Previously Completed (2025-11-29):
[X] All S dimensions reviewed (S1-S20)
[X] All G dimensions finalized (G1-G9)
[X] Dimension status classifications assigned
[X] Slot types reference with grounding classifications
[X] S6 merged S11 (Risk) and S13 (Escalation)
[X] S12 merged into S17
[X] S7, S14, S15 marked N/A (operational)
[X] S10, S17 marked CONDITIONAL
[X] S8, S9, S16, S18, S19 marked ASPIRATIONAL
[X] Created WBP_Framework_Design_Summary.md with 7 design principles

#### Completed (2025-11-30 continued):
[X] 13. Identified key insight: S+G dimensions are ATOMIC, free-form assertions need DECOMPOSITION
[X] 14. Asked GPT-5 3x to optimize decomposition prompt (sessions 018-020)
[X] 15. Created `assertion_analyzer/prompts/decomposition_prompt.json` v3.0
[X] 16. Tested decomposition on 4 assertions - all correctly decomposed into atomic S+G units
[X] 17. Created `assertion_analyzer/prompts/classification_prompt.json` v2.0 (optimized)
[X] 18. Created `assertion_analyzer/prompts/ie_slot_extraction_prompt.json` v2.0 (optimized)
[X] 19. Implemented staged processing (STAGE_SIZE=50) with token refresh between stages
[X] 20. Updated output format to unified S+G units with nested g_slots
[X] 21. Added separate S/G counting for independent success rate reporting
[X] 22. Updated decomposition_prompt.json to v4.0 with s_template + s_literal forms
[X] 23. Added sub_category field to output format for dimension specialization
    - s_dimension_name: Canonical from DIMENSION_NAMES (e.g., "Meeting Details")
    - sub_category: Specialized from GPT-5 (e.g., "Title") or null if same
[X] 24. Ran full Kening conversion v2.3 with G10 support (2,318 input → 5,600 S+G units)
[X] 25. Investigated anomalies: 253 "Unknown" (pure G), 2 G18 (hallucinated dimension)
[X] 26. GPT-5 consultation (3 runs) on hallucination placement - consensus: M layer
[X] 27. Established S→G→M three-layer framework design:
    - S (Structural, S1-S20): Check IF something exists - INDEPENDENT
    - G (Grounding, G2-G10): Check if VALUE matches source - INDEPENDENT
    - M (Meta, M1): No Hallucination - DERIVED from all G results
[X] 28. Updated decomposition_prompt.json to v6.0 (every G must have S parent)
[X] 29. Updated dimensions.py with S→G→M framework documentation
    - G1 deprecated ("DEPRECATED - See M1")
    - M1 added ("No Hallucination")
    - GROUNDING_PRIORITY_ORDER updated (G1 removed, G10 added)
    - META_LAYER_ORDER added ["M1"]
    - SLOT_TYPES updated (G1 references → M1)
[X] 30. Updated copilot-instructions.md with S→G→M framework lesson

#### Plan:
[X] 1. Update convert_kening_assertions_v2.py to use decomposition prompt - DONE
[X] 2. Add staged processing with token refresh - DONE
[X] 3. Add sub_category for dimension specialization - DONE
[X] 4. Added G10 (Relation Grounding) dimension - DONE
    - Added RELATION_TYPES to dimensions.py
    - Added G10 to DIMENSION_NAMES, S_TO_G_MAP, G_RATIONALE_FOR_S
    - Updated WBP_Evaluation_Complete_Dimension_Reference.md with G10 section
    - Updated prompts.json to v2.3 with G10 guidance
    - Added G9/G10 to analyzer.py DIMENSION_SPEC
    - Tested: G10 now being selected for dependency assertions!
[X] 5. Commit and push G10 changes - DONE (commit c2be918)
[X] 6. Run full conversion on all 224 meetings - DONE (v2.3, 5,600 S+G units)
[X] 7. Establish S→G→M three-layer framework - DONE (GPT-5 consultation, design finalized)
[ ] 8. Commit S→G→M framework documentation updates
[ ] 9. Repackage assertion_analyzer_v2.4.zip (with S→G→M framework)
