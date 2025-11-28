"""
Stage 1: Scenario Generation

Generates meeting scenarios for workback plan evaluation.
Each scenario includes:
- Meeting details (title, date, time, attendees)
- Context and background
- Available artifacts (files, documents)
- Dependencies and blockers
- Source entities for grounding verification

Usage:
    python -m pipeline.scenario_generation
    python -m pipeline.scenario_generation --from-data docs/LOD_1121.WithUserUrl.jsonl
    python -m pipeline.scenario_generation --template
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict
import uuid

from .config import (
    Scenario, 
    SCENARIOS_FILE, 
    save_json, 
    load_json,
    call_gpt5_api,
    extract_json_from_response,
    DELAY_BETWEEN_CALLS
)
import time


# ═══════════════════════════════════════════════════════════════════════════════
# Template Scenarios
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATE_SCENARIOS = [
    {
        "id": "scenario_001",
        "title": "Q1 Product Launch Readiness Review",
        "date": "January 15, 2025",
        "time": "2:00 PM",
        "timezone": "PST",
        "duration_minutes": 90,
        "organizer": "Sarah Chen",
        "attendees": ["Sarah Chen", "Mike Johnson", "Lisa Park", "Tom Wilson"],
        "context": """The team is preparing for a major product launch scheduled for February 1, 2025. 
This meeting is to review all readiness items, identify blockers, and finalize the launch checklist.
Engineering has completed 90% of features, but there are concerns about QA timeline.""",
        "artifacts": [
            "Product_Launch_Checklist_v3.xlsx",
            "Engineering_Status_Report.pdf",
            "Design_Assets_Summary.docx",
            "QA_Test_Results_Dec.pdf"
        ],
        "dependencies": [
            "Engineering sign-off required before QA final approval",
            "Design assets must be finalized before marketing materials",
            "Legal review pending on Terms of Service updates"
        ],
        "user_prompt": "Help me create a workback plan for the upcoming meeting 'Q1 Product Launch Readiness Review'"
    },
    {
        "id": "scenario_002",
        "title": "Budget Planning FY26 Kickoff",
        "date": "December 5, 2024",
        "time": "10:00 AM",
        "timezone": "EST",
        "duration_minutes": 120,
        "organizer": "James Miller",
        "attendees": ["James Miller", "Emily Davis", "Robert Brown", "Amanda Lee", "Chris Taylor"],
        "context": """Annual budget planning kickoff for FY26. Finance team needs to consolidate 
departmental requests, review historical spending, and align with strategic priorities.
CFO has requested 5% overall cost reduction target.""",
        "artifacts": [
            "FY25_Actual_Spending.xlsx",
            "Department_Budget_Requests.xlsx",
            "Strategic_Priorities_FY26.pptx",
            "Cost_Reduction_Guidelines.pdf"
        ],
        "dependencies": [
            "Department heads must submit requests before consolidation",
            "Strategic priorities document from CEO required",
            "HR headcount projections needed for salary planning"
        ],
        "user_prompt": "Create a workback plan to prepare for the FY26 Budget Planning Kickoff meeting"
    },
    {
        "id": "scenario_003",
        "title": "Customer Escalation Review - Acme Corp",
        "date": "November 20, 2024",
        "time": "3:30 PM",
        "timezone": "PST",
        "duration_minutes": 60,
        "organizer": "Jennifer White",
        "attendees": ["Jennifer White", "David Kim", "Rachel Green", "Mark Thompson"],
        "context": """Critical customer escalation from Acme Corp regarding service outages. 
Customer is threatening contract termination unless issues are resolved.
Three major incidents in the past month need root cause analysis.""",
        "artifacts": [
            "Acme_Incident_Report_Nov.pdf",
            "Service_Level_Agreement.pdf",
            "System_Architecture_Diagram.png",
            "Previous_Meeting_Notes.docx"
        ],
        "dependencies": [
            "Engineering post-mortem reports due before meeting",
            "Account manager to provide customer sentiment update",
            "Legal to review SLA breach implications"
        ],
        "user_prompt": "Help me prepare a workback plan for the Acme Corp escalation review meeting"
    }
]


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario Generation from Data
# ═══════════════════════════════════════════════════════════════════════════════

def extract_scenario_from_lod(item: Dict, index: int) -> Scenario:
    """Extract a scenario from LOD (List of Documents) format data."""
    
    # Extract meeting info
    meeting = item.get("MEETING", {})
    utterance = item.get("UTTERANCE", {})
    attendees = item.get("ATTENDEES", [])
    entities = item.get("ENTITIES_TO_USE", [])
    
    # Parse meeting time
    start_time = meeting.get("StartTime", "")
    if "T" in start_time:
        date_part = start_time.split("T")[0]
        time_part = start_time.split("T")[1].split("-")[0] if "-" in start_time else start_time.split("T")[1]
    else:
        date_part = "TBD"
        time_part = "TBD"
    
    # Extract files from entities
    files = []
    for entity in entities:
        if entity.get("type") == "File":
            files.append(entity.get("Name", entity.get("name", "Unknown File")))
    
    # Build source entities for grounding
    source_entities = {
        "attendees": attendees,
        "organizer": meeting.get("Organizer", attendees[0] if attendees else "Unknown"),
        "meeting_date": date_part,
        "meeting_time": time_part,
        "timezone": "UTC",  # Default
        "files": files,
        "topics": [meeting.get("Subject", "")],
        "dependencies": []
    }
    
    return Scenario(
        id=f"lod_{index:03d}",
        title=meeting.get("Subject", f"Meeting {index}"),
        date=date_part,
        time=time_part,
        timezone="UTC",
        duration_minutes=int(meeting.get("Duration", 60)),
        organizer=source_entities["organizer"],
        attendees=attendees,
        context=utterance.get("text", ""),
        artifacts=files,
        dependencies=[],
        user_prompt=utterance.get("text", f"Help me prepare for: {meeting.get('Subject', 'this meeting')}"),
        source_entities=source_entities
    )


def generate_scenario_with_gpt5(base_scenario: Dict) -> Scenario:
    """Use GPT-5 to enrich a scenario with realistic details."""
    
    prompt = f"""Given this meeting scenario, generate realistic enriched details.

Base Scenario:
- Title: {base_scenario.get('title', 'Unknown')}
- Date: {base_scenario.get('date', 'TBD')}
- Attendees: {', '.join(base_scenario.get('attendees', []))}
- Context: {base_scenario.get('context', '')[:500]}

Generate a JSON response with these fields:
{{
    "enriched_context": "Detailed meeting context (2-3 sentences)",
    "key_topics": ["topic1", "topic2", "topic3"],
    "potential_blockers": ["blocker1", "blocker2"],
    "expected_outcomes": ["outcome1", "outcome2"],
    "preparation_needed": ["prep1", "prep2"]
}}

Return ONLY valid JSON."""

    try:
        response = call_gpt5_api(prompt, temperature=0.5, max_tokens=1000)
        enrichment = extract_json_from_response(response)
        
        # Merge enrichment into scenario
        return Scenario(
            id=base_scenario.get('id', str(uuid.uuid4())[:8]),
            title=base_scenario.get('title', 'Unknown'),
            date=base_scenario.get('date', 'TBD'),
            time=base_scenario.get('time', 'TBD'),
            timezone=base_scenario.get('timezone', 'UTC'),
            duration_minutes=base_scenario.get('duration_minutes', 60),
            organizer=base_scenario.get('organizer', 'Unknown'),
            attendees=base_scenario.get('attendees', []),
            context=enrichment.get('enriched_context', base_scenario.get('context', '')),
            artifacts=base_scenario.get('artifacts', []),
            dependencies=enrichment.get('potential_blockers', base_scenario.get('dependencies', [])),
            user_prompt=base_scenario.get('user_prompt', ''),
            source_entities=base_scenario.get('source_entities', {})
        )
    except Exception as e:
        print(f"  ⚠️ GPT-5 enrichment failed: {e}")
        # Return basic scenario without enrichment
        return Scenario(**base_scenario)


# ═══════════════════════════════════════════════════════════════════════════════
# Main Functions
# ═══════════════════════════════════════════════════════════════════════════════

def generate_from_templates(enrich: bool = False) -> List[Scenario]:
    """Generate scenarios from built-in templates."""
    print("\n📋 Stage 1: Scenario Generation (from templates)")
    print("=" * 60)
    
    scenarios = []
    for template in TEMPLATE_SCENARIOS:
        # Build source entities
        template["source_entities"] = {
            "attendees": template["attendees"],
            "organizer": template["organizer"],
            "meeting_date": template["date"],
            "meeting_time": template["time"],
            "timezone": template["timezone"],
            "files": template["artifacts"],
            "topics": [template["title"]],
            "dependencies": template["dependencies"]
        }
        
        if enrich:
            print(f"  🔄 Enriching: {template['title']}...")
            scenario = generate_scenario_with_gpt5(template)
            time.sleep(DELAY_BETWEEN_CALLS)
        else:
            scenario = Scenario(**template)
        
        scenarios.append(scenario)
        print(f"  ✅ Generated: {scenario.title}")
    
    return scenarios


def generate_from_data(data_file: str, limit: int = 5) -> List[Scenario]:
    """Generate scenarios from LOD JSONL data file."""
    print(f"\n📋 Stage 1: Scenario Generation (from {data_file})")
    print("=" * 60)
    
    scenarios = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            item = json.loads(line)
            scenario = extract_scenario_from_lod(item, i)
            scenarios.append(scenario)
            print(f"  ✅ Extracted: {scenario.title[:50]}...")
    
    return scenarios


def main():
    """Main entry point for scenario generation."""
    parser = argparse.ArgumentParser(description="Stage 1: Scenario Generation")
    parser.add_argument("--from-data", type=str, help="Load scenarios from JSONL data file")
    parser.add_argument("--template", action="store_true", help="Use built-in template scenarios")
    parser.add_argument("--enrich", action="store_true", help="Use GPT-5 to enrich scenarios")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of scenarios from data")
    parser.add_argument("--output", type=str, default=SCENARIOS_FILE, help="Output file path")
    args = parser.parse_args()
    
    if args.from_data:
        scenarios = generate_from_data(args.from_data, args.limit)
    else:
        scenarios = generate_from_templates(enrich=args.enrich)
    
    # Save scenarios
    output = {
        "generated_at": datetime.now().isoformat(),
        "source": args.from_data if args.from_data else "templates",
        "count": len(scenarios),
        "scenarios": [s.to_dict() for s in scenarios]
    }
    
    save_json(output, args.output)
    
    print(f"\n✅ Stage 1 Complete: {len(scenarios)} scenarios generated")
    print(f"   Output: {args.output}")
    
    return scenarios


if __name__ == "__main__":
    main()
