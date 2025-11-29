#!/usr/bin/env python3
"""Analyze Kening's assertions to find grounding patterns not covered by G2-G6."""

import json
import re
from collections import defaultdict

# Load Kening's assertions
data = []
with open('docs/ChinYew/Assertions_genv2_for_LOD1126part1.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

# Look for grounding-related patterns in assertion TEXT
grounding_patterns = {
    'attendee/people': r'attendee|participant|name|person|owner|assigned|stakeholder',
    'date/time': r'date|time|deadline|schedule|by .+ (am|pm|pst|est)|timeline|due',
    'file/artifact': r'file|document|deck|slide|attachment|link|url|artifact',
    'topic/subject': r'topic|subject|agenda|scope|objective|purpose|goal',
    'task/action': r'task|action|step|deliverable|milestone|activity|item|todo',
    'number/quantity': r'budget|\d+%|amount|\$|cost|price|quantity|count|number',
    'location/place': r'location|room|venue|place|site|address|building',
    'email/communication': r'email|message|chat|teams|slack|communication',
    'decision/outcome': r'decision|outcome|result|conclusion|resolution|agreement',
    'constraint/limit': r'constraint|limit|restriction|boundary|requirement|must not',
    'priority/urgency': r'priority|urgent|critical|important|high.?priority|p[0-3]',
    'status/progress': r'status|progress|complete|done|pending|in.?progress|blocked',
    'role/responsibility': r'role|responsibility|accountable|raci|responsible|approver',
}

pattern_counts = {k: 0 for k in grounding_patterns}
pattern_examples = {k: [] for k in grounding_patterns}

for item in data:
    for a in item.get('assertions', []):
        text = a.get('text', '').lower()
        for pattern_name, pattern in grounding_patterns.items():
            if re.search(pattern, text):
                pattern_counts[pattern_name] += 1
                if len(pattern_examples[pattern_name]) < 3:
                    pattern_examples[pattern_name].append(text[:120])

print('=' * 70)
print('GROUNDING ENTITY PATTERNS IN ASSERTIONS')
print('=' * 70)
print()
for pattern_name, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
    print(f'{count:4d} | {pattern_name}')
    
print()
print('=' * 70)
print('PATTERNS NOT IN G2-G6 (potential new Gs)')
print('=' * 70)
# G2=Attendee, G3=DateTime, G4=Artifact, G5=Topic, G6=Task
covered = ['attendee/people', 'date/time', 'file/artifact', 'topic/subject', 'task/action']
for pattern_name, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
    if pattern_name not in covered and count > 10:
        print(f'\n{pattern_name}: {count} occurrences')
        for ex in pattern_examples[pattern_name][:2]:
            print(f'  Example: "{ex}..."')

print()
print('=' * 70)
print('RECOMMENDATION: Potential new G dimensions')
print('=' * 70)
print("""
Based on analysis, consider adding:

G7: Constraint/Limit Grounding
    - "Must not exceed budget/timeline constraints from source"
    - Verifies constraints mentioned are from source, not fabricated

G8: Decision/Outcome Grounding  
    - "Decisions referenced must exist in source meeting/emails"
    - Verifies decisions weren't hallucinated

G9: Priority Grounding
    - "Priority levels must match source context"
    - Verifies P1/P2/Critical tags are accurate

G10: Status Grounding
    - "Status information must reflect source state"
    - Verifies progress/completion status is accurate
""")
