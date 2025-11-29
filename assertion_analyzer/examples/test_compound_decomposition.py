"""
Test compound assertion decomposition into atomic S+G units.
Uses the optimized decomposition_prompt.json (v3.0).
"""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assertion_analyzer.config import call_gpt5_api, extract_json_from_response

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
    print("COMPOUND ASSERTION DECOMPOSITION TEST")
    print("=" * 70)
    print(f"Input: {len(assertions)} compound assertions")
    print()
    
    # Load prompt config
    config = load_decomposition_prompt()
    
    # Process each assertion
    all_results = []
    total_s_units = 0
    total_g_slots = 0
    
    for i, assertion in enumerate(assertions):
        print(f"\n{'='*70}")
        print(f"TEST {i+1}: {assertion[:60]}...")
        print("=" * 70)
        
        units = decompose_assertion(assertion, config)
        all_results.append({
            "original_assertion": assertion,
            "atomic_units": units
        })
        
        for unit in units:
            s_dim = unit.get('s_dimension', 'null')
            s_name = unit.get('s_name', '')
            s_assertion = unit.get('s_assertion', '')
            linked_g = unit.get('linked_g', [])
            
            if s_dim:
                total_s_units += 1
            total_g_slots += len(linked_g)
            
            print(f"\n  {s_dim}: {s_name}")
            print(f"    → {s_assertion}")
            for g in linked_g:
                g_dim = g.get('g_dimension', '')
                slot = g.get('slot_value', '')
                if isinstance(slot, list):
                    slot = ', '.join(str(s) for s in slot)
                print(f"      └─ {g_dim}: {slot}")
    
    # Save results
    output_file = os.path.join(os.path.dirname(__file__), 'compound_assertions_output.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_name": "Compound Assertion Decomposition",
            "prompt_version": config.get('version', 'unknown'),
            "input_count": len(assertions),
            "total_s_units": total_s_units,
            "total_g_slots": total_g_slots,
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("=" * 70)
    print(f"Input assertions:    {len(assertions)}")
    print(f"Output S units:      {total_s_units}")
    print(f"Output G slots:      {total_g_slots}")
    print(f"Avg S units/assert:  {total_s_units/len(assertions):.1f}")
    print(f"\nResults saved to: {output_file}")

if __name__ == '__main__':
    main()
