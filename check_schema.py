import json

with open('docs/ChinYew/assertions_converted_gpt5_enhanced.jsonl', 'r', encoding='utf-8') as f:
    d = json.loads(f.readline())

print('First 5 assertions:')
for i, a in enumerate(d['assertions'][:5]):
    print(f"  {i}: id={a.get('assertion_id')}, parent={a.get('parent_assertion_id')}, dim={a.get('dimension_id')}")
