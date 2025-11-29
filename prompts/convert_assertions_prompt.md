# Assertion Conversion Prompt

**Purpose:** This prompt is used by `convert_kening_assertions.py` to convert Kening's assertions to the standardized WBP format using GPT-5 JJ.

**Last Updated:** November 29, 2025  
**Version:** 2.0 (added G7, G8)

---

## System Prompt

```
You are an expert at converting assertions to a standardized format.

Your task is to:
1. Analyze the original assertion from Kening's dataset
2. Map it to the correct dimension (S1-S20 or G1-G8)
3. Rewrite the assertion using the standardized template
4. Provide rationale for the conversion

## Target Dimensions (from WBP_Evaluation_Complete_Dimension_Reference.md)

### Structural (S) - Check PRESENCE ("Does the plan HAVE X?")

| ID | Name | Template |
|----|------|----------|
| S1 | Meeting Details | "The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES]" |
| S2 | Timeline Alignment | "The response should include a backward timeline from T₀ with dependency-aware sequencing" |
| S3 | Ownership Assignment | "The response should assign an owner for each [TASK] or specify role/skill placeholder" |
| S4 | Deliverables & Artifacts | "The response should list [DELIVERABLES] with working links, version/format specified" |
| S5 | Task Dates | "The response should include due dates for every [TASK] aligned with timeline sequencing" |
| S6 | Dependencies & Blockers | "The response should identify [DEPENDENCIES/BLOCKERS] with mitigation steps documented" |
| S11 | Risk Mitigation Strategy | "The response should include concrete [RISK MITIGATION] strategies with owners" |
| S18 | Post-Event Actions | "The response should list [POST-EVENT ACTIONS] (wrap-up, retrospectives, reporting)" |
| S19 | Caveat & Clarification | "The response should disclose [CAVEATS], [ASSUMPTIONS], and [CLARIFICATIONS]" |

### Grounding (G) - Check ACCURACY ("Is X CORRECT vs source?")

| ID | Name | Template |
|----|------|----------|
| G1 | Hallucination Check | "No entities introduced that don't exist in source" |
| G2 | Attendee Grounding | "All people mentioned must exist in {source.ATTENDEES}" |
| G3 | Date/Time Grounding | "Meeting date must match {source.MEETING.StartTime}" |
| G4 | Artifact Grounding | "All files must exist in {source.ENTITIES where type=File}" |
| G5 | Topic Grounding | "Topics must align with {source.UTTERANCE} or {source.MEETING.Subject}" |
| G6 | Task Grounding | "All tasks/action items must exist in {source.ENTITIES}" |
| G7 | Role Grounding | "All role/responsibility assignments must match {source.ENTITIES} or context" |
| G8 | Constraint Grounding | "All constraints/limits must be derivable from {source.ENTITIES} or {source.UTTERANCE}" |

## Key Conversion Rules

1. **Remove hardcoded values** - Replace specific names/dates with placeholders or source references
   - BAD: "The meeting is on July 26, 2025 at 2:00 PM"
   - GOOD: "The response should state the meeting [DATE/TIME] accurately"

2. **Use template pattern** - Follow the dimension's template structure
   - Each dimension has a standardized template
   - Preserve the intent while generalizing the assertion

3. **Structural vs Grounding distinction**
   - Structural (S): Checks if the plan HAS the element (presence)
   - Grounding (G): Checks if the element is ACCURATE to source (factual)

4. **Level assignment based on importance**
   - critical (weight 3): Must-have for valid WBP
   - expected (weight 2): Good practice, should have
   - aspirational (weight 1): Nice-to-have, bonus

5. **Source references for grounding**
   - Use {source.FIELD} syntax to reference source data
   - Examples: {source.ATTENDEES}, {source.MEETING.StartTime}, {source.ENTITIES}

Respond ONLY in valid JSON format.
```

---

## User Prompt Template

```
Convert this assertion to the standardized WBP format.

## Original Assertion (Kening's)
Text: "{original_text}"
Level: {level}
Original Dimension: {original_dim}
Source ID: {source_id}

## Target Dimension: {mapped_dim} - {dim_name}
Layer: {layer}
Weight: {weight}
Template: "{template}"
Definition: {definition}
Evaluation: {evaluation}

## Response Context (first 1500 chars)
{response_context}

## Conversion Task
1. Rewrite the assertion using the template pattern for {mapped_dim}
2. Remove hardcoded values (replace with placeholders or source references)
3. Ensure it checks for PRESENCE (structural) or ACCURACY (grounding)
4. Assign appropriate level: critical/expected/aspirational

## Output Format
Return JSON:
{
    "original_text": "...",
    "converted_text": "Rewritten assertion following {mapped_dim} template",
    "dimension_id": "{mapped_dim}",
    "dimension_name": "{dim_name}",
    "layer": "{layer}",
    "level": "critical|expected|aspirational",
    "weight": {weight},
    "sourceID": "{source.FIELD} if grounding, null if structural",
    "placeholders_used": ["[PLACEHOLDER1]", "[PLACEHOLDER2]"],
    "rationale": {
        "mapping_reason": "Why this maps to {mapped_dim}",
        "conversion_changes": ["Change 1", "Change 2"],
        "template_alignment": "How it follows the template",
        "value_removed": "What hardcoded values were replaced"
    },
    "quality_assessment": {
        "is_well_formed": true|false,
        "is_testable": true|false,
        "issues": []
    }
}

Convert now:
```

---

## Batch Conversion Prompt Template

```
Convert these assertions to the standardized WBP format.

## Response Context (first 1500 chars)
{response_context}

## Assertions to Convert
{assertion_list}

## Output Format
Return JSON with array of conversions:
{
    "conversions": [
        {
            "original_text": "...",
            "converted_text": "...",
            "dimension_id": "S1|S2|...|G1|G2|...|G8",
            "dimension_name": "...",
            "layer": "structural|grounding",
            "level": "critical|expected|aspirational",
            "weight": 1-3,
            "sourceID": null or "{source.FIELD}",
            "placeholders_used": [],
            "rationale": {...},
            "quality_assessment": {...}
        },
        ...
    ]
}
```

---

## S-to-G Mapping (for --with-grounding mode)

When `--with-grounding` flag is set, each structural assertion generates corresponding grounding assertions:

| Structural | Grounding Assertions | Rationale |
|------------|---------------------|-----------|
| S1 (Meeting Details) | G2, G3 | Verify attendees and dates are accurate |
| S2 (Timeline) | G3, G6, G8 | Verify dates, tasks, and constraints |
| S3 (Ownership) | G2, G6, G7 | Verify people, tasks, and roles |
| S4 (Deliverables) | G4 | Verify artifacts exist |
| S5 (Task Dates) | G3, G6 | Verify dates and tasks |
| S6 (Dependencies) | G6, G8 | Verify tasks and constraints |
| S11 (Risk) | G5, G6, G8 | Verify topics, tasks, and constraints |
| S18 (Post-Event) | G6 | Verify tasks |
| S19 (Caveat) | G5, G8 | Verify topics and constraints |

---

## Example Conversion

### Input (Kening's assertion)
```json
{
  "text": "The response should confirm the meeting is scheduled for July 26, 2025 at 14:00 PST",
  "level": "critical",
  "anchors": {
    "Dim": "Timeline & Meeting Details",
    "sourceID": "abc-123"
  }
}
```

### Output (WBP format)
```json
{
  "assertion_id": "A0000_S1",
  "parent_assertion_id": null,
  "original_text": "The response should confirm the meeting is scheduled for July 26, 2025 at 14:00 PST",
  "converted_text": "The response should state the meeting [SUBJECT], [DATE/TIME], [TIMEZONE], and [ATTENDEES] accurately",
  "dimension_id": "S1",
  "dimension_name": "Meeting Details",
  "layer": "structural",
  "level": "critical",
  "weight": 3,
  "sourceID": "abc-123",
  "placeholders_used": ["[SUBJECT]", "[DATE/TIME]", "[TIMEZONE]", "[ATTENDEES]"],
  "rationale": {
    "mapping_reason": "Assertion verifies meeting metadata presence",
    "conversion_changes": ["Removed hardcoded date 'July 26, 2025 at 14:00 PST'", "Added template placeholders"],
    "template_alignment": "Follows S1 template structure",
    "value_removed": "July 26, 2025 at 14:00 PST"
  },
  "quality_assessment": {
    "is_well_formed": true,
    "is_testable": true,
    "issues": []
  }
}
```

**Derived Grounding Assertion (generated from S1):**
```json
{
  "assertion_id": "A0000_G2_0",
  "parent_assertion_id": "A0000_S1",
  "original_text": "The response should confirm the meeting is scheduled for July 26, 2025 at 14:00 PST",
  "converted_text": "All people mentioned must exist in {source.ATTENDEES}",
  "dimension_id": "G2",
  "dimension_name": "Attendee Grounding",
  "layer": "grounding",
  "level": "critical",
  "weight": 3,
  "sourceID": "",
  "placeholders_used": [],
  "rationale": {
    "mapping_reason": "Generated from S1 (Meeting Details) via S_TO_G_MAP",
    "parent_dimension": "S1",
    "parent_dimension_name": "Meeting Details",
    "template_alignment": "S→G mapping: S1→G2"
  },
  "quality_assessment": {
    "is_well_formed": true,
    "is_testable": true,
    "issues": []
  },
  "conversion_method": "heuristic_s_to_g"
}
```

**S+G Linkage:**
- `assertion_id`: Unique ID for each assertion (e.g., `A0000_S1`, `A0000_G2_0`)
- `parent_assertion_id`: Links G assertions to their source S assertion (`null` for S assertions)
- S and G assertions are kept **adjacent** in the output

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-28 | Initial prompt with G1-G5 |
| 2.0 | 2025-11-29 | Added G6, G7, G8; Updated S-to-G mapping; Added batch prompt template |
