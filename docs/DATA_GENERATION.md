# Data Generation Documentation

**Date:** November 22, 2025  
**Author:** Kening Ren  

## Overview
This document outlines the data generation pipeline used to create the workback plan responses and assertions found in this project.

## Data Source
- **Origin:** Test Tenant LOD
- **Generator:** Wei-Wei Cui
- **Generation Date:** November 21, 2025
- **Description:** The dataset contains meeting context data, including user information, utterances, and enterprise grounding data (files, emails, chats, etc.).
- **File Path:** [docs/LOD_1121.jsonl](./LOD_1121.jsonl)

## Generation Process
The responses were generated using a specific prompt designed to act as an expert meeting planner.

1.  **Input:** The raw context data from [docs/LOD_1121.jsonl](./LOD_1121.jsonl).
2.  **Prompt:** The generation logic is defined in [docs/step1_v2.md](./step1_v2.md).
    - **Prompt Author:** Kening Ren
    - **Function:** Takes user context, utterance, and grounding data to produce a detailed workback plan.
    - **Note:** Kening's assertion generation prompt is to be added later.
3.  **Output:** The generated responses and their corresponding assertions are stored in [docs/output_v2.jsonl](./output_v2.jsonl).

## File Relationships
- **Input:** [docs/LOD_1121.jsonl](./LOD_1121.jsonl) (Context Data)
- **Logic:** [docs/step1_v2.md](./step1_v2.md) (Prompt)
- **Output:** [docs/output_v2.jsonl](./output_v2.jsonl) (Generated Plans & Assertions)

## Visualization
A Streamlit application ([visualize_output.py](../visualize_output.py)) is available to inspect the generated outputs and the prompt used.
