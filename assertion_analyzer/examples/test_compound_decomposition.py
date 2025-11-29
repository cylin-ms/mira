"""
Test compound assertion decomposition into atomic S+G units.
Uses the optimized decomposition_prompt.json (v4.0).
Outputs s_template, s_literal, sub_category format.

Full Process Test:
1. Decomposition: Free-form → atomic S+G units
2. Outputs: s_template, s_literal, sub_category, g_slots
"""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assertion_analyzer.config import call_gpt5_api, extract_json_from_response
from assertion_analyzer.dimensions import DIMENSION_NAMES, G_RATIONALE_FOR_S

def load_decomposition_prompt():
    """Load the decomposition prompt configuration."""
    prompt_file = os.path.join(
        os.path.dirname(__file__), 
        '..', 'prompts', 'decomposition_prompt.json'
    )
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def decompose_assertion(assertion_text: str, config: dict) -> list:
    """Decompose a free-form assertion into atomic S+G units."""
    prompt = config['user_prompt_template'].replace('{assertion_text}', assertion_text)
    result_text = call_gpt5_api(
        prompt, 
        system_prompt=config['system_prompt'], 
        temperature=config.get('temperature', 0.2)
    )
    return extract_json_from_response(result_text)


def build_sg_units(units: list, original_assertion: str, assertion_idx: int) -> list:
    """
    Convert decomposed units into full S+G unit format.
    
    Output format matches convert_kening_assertions_v2.py:
    - assertion_id: M0000_A{idx}_S{seq}_{s_dim}
    - s_dimension, s_dimension_name, sub_category
    - s_template, s_literal
    - g_slots: [{g_dimension, g_dimension_name, slot_name, slot_value, rationale}]
    """
    results = []
    
    for seq, unit in enumerate(units):
        s_dim = unit.get('s_dimension')
        s_name = unit.get('s_name', '')
        s_template = unit.get('s_template', '')
        s_literal = unit.get('s_literal', '')
        linked_g = unit.get('linked_g', [])
        
        # Handle null S dimension (pure grounding)
        if not s_dim:
            s_dim = "G1"  # Default to G1 for pure grounding assertions
        
        # Compute canonical name and sub_category
        canonical_name = DIMENSION_NAMES.get(s_dim, s_dim)
        sub_category = s_name if s_name and s_name != canonical_name else None
        
        # Build g_slots with full info
        g_slots = []
        for g in linked_g:
            g_dim = g.get('g_dimension', '')
            g_name = DIMENSION_NAMES.get(g_dim, g_dim)
            slot_name = g.get('slot_name', '')
            slot_value = g.get('slot_value')
            
            # Get rationale from G_RATIONALE_FOR_S
            rationale = G_RATIONALE_FOR_S.get(s_dim, {}).get(g_dim, f"Generated from {s_dim} decomposition")
            
            g_slots.append({
                "g_dimension": g_dim,
                "g_dimension_name": g_name,
                "slot_name": slot_name,
                "slot_value": slot_value,
                "rationale": rationale
            })
        
        # Determine level based on S dimension
        if s_dim in ['S1', 'S2', 'S3', 'S4', 'S5']:
            level = 'critical'
        elif s_dim in ['S8', 'S9', 'S16', 'S18', 'S19']:
            level = 'aspirational'
        else:
            level = 'expected'
        
        # Build assertion ID
        assertion_id = f"M0000_A{assertion_idx:03d}_S{seq}_{s_dim}"
        
        sg_unit = {
            "assertion_id": assertion_id,
            "original_assertion": original_assertion,
            "s_dimension": s_dim,
            "s_dimension_name": canonical_name,
            "sub_category": sub_category,
            "s_template": s_template,
            "s_literal": s_literal,
            "level": level,
            "g_slots": g_slots,
            "rationale": {
                "mapping_reason": f"Decomposed from: {original_assertion[:80]}...",
                "conversion_method": "decomposition"
            }
        }
        results.append(sg_unit)
    
    return results


def main():
    # Load assertions
    input_file = os.path.join(os.path.dirname(__file__), 'compound_assertions.txt')
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse assertions (skip comments and empty lines)
    assertions = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            assertions.append(line)
    
    print("=" * 70)
    print("COMPOUND ASSERTION DECOMPOSITION TEST (Full Process)")
    print("=" * 70)
    print(f"Input: {len(assertions)} compound assertions")
    print()
    
    # Load prompt config
    config = load_decomposition_prompt()
    print(f"Prompt version: {config.get('version', 'unknown')}")
    
    # Process each assertion
    all_sg_units = []
    total_s_units = 0
    total_g_slots = 0
    by_s_dimension = {}
    by_g_dimension = {}
    
    for i, assertion in enumerate(assertions):
        print(f"\n{'='*70}")
        print(f"TEST {i+1}: {assertion[:60]}...")
        print("=" * 70)
        
        # Step 1: Decompose
        units = decompose_assertion(assertion, config)
        
        # Step 2: Build full S+G units
        sg_units = build_sg_units(units, assertion, i)
        all_sg_units.extend(sg_units)
        
        # Step 3: Display and count
        for sg_unit in sg_units:
            s_dim = sg_unit['s_dimension']
            s_name = sg_unit['s_dimension_name']
            sub_cat = sg_unit['sub_category']
            s_template = sg_unit['s_template']
            s_literal = sg_unit['s_literal']
            g_slots = sg_unit['g_slots']
            
            total_s_units += 1
            total_g_slots += len(g_slots)
            by_s_dimension[s_dim] = by_s_dimension.get(s_dim, 0) + 1
            
            print(f"\n  [{sg_unit['assertion_id']}]")
            print(f"  {s_dim}: {s_name}")
            if sub_cat:
                print(f"    Sub-category: {sub_cat}")
            print(f"    Template: {s_template}")
            print(f"    Literal:  {s_literal}")
            print(f"    Level:    {sg_unit['level']}")
            
            for g in g_slots:
                g_dim = g['g_dimension']
                g_name = g['g_dimension_name']
                slot_name = g['slot_name']
                slot_value = g['slot_value']
                if isinstance(slot_value, list):
                    slot_value = ', '.join(str(s) for s in slot_value)
                print(f"      └─ {g_dim} ({g_name}) [{slot_name}]: {slot_value}")
                by_g_dimension[g_dim] = by_g_dimension.get(g_dim, 0) + 1
    
    # Save results as JSONL (same format as convert_kening_assertions_v2.py)
    output_file = os.path.join(os.path.dirname(__file__), 'compound_assertions_output.jsonl')
    with open(output_file, 'w', encoding='utf-8') as f:
        for sg_unit in all_sg_units:
            f.write(json.dumps(sg_unit, ensure_ascii=False) + '\n')
    
    # Also save as single JSON with summary
    summary_file = os.path.join(os.path.dirname(__file__), 'compound_assertions_output.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_name": "Compound Assertion Decomposition (Full Process)",
            "prompt_version": config.get('version', 'unknown'),
            "input_count": len(assertions),
            "total_s_units": total_s_units,
            "total_g_slots": total_g_slots,
            "by_s_dimension": by_s_dimension,
            "by_g_dimension": by_g_dimension,
            "sg_units": all_sg_units
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("=" * 70)
    print(f"Input assertions:    {len(assertions)}")
    print(f"Output S units:      {total_s_units}")
    print(f"Output G slots:      {total_g_slots}")
    print(f"Avg S units/assert:  {total_s_units/len(assertions):.1f}")
    print(f"\nBy S Dimension:")
    for s_dim, count in sorted(by_s_dimension.items()):
        name = DIMENSION_NAMES.get(s_dim, s_dim)
        print(f"  {s_dim}: {name} ({count})")
    print(f"\nBy G Dimension:")
    for g_dim, count in sorted(by_g_dimension.items()):
        name = DIMENSION_NAMES.get(g_dim, g_dim)
        print(f"  {g_dim}: {name} ({count})")
    print(f"\nResults saved to:")
    print(f"  JSONL: {output_file}")
    print(f"  JSON:  {summary_file}")

if __name__ == '__main__':
    main()
