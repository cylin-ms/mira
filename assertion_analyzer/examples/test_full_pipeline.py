"""
Test FULL assertion analyzer pipeline:
1. Classification: Input → S/G dimension
2. S+G Assertion Generation: Generate S assertion + linked G assertions
3. Scenario Generation: Create meeting scenario as ground truth
4. WBP Generation: Generate workback plan satisfying assertions
5. Verification: Verify WBP against scenario

This test uses the main analyzer functions directly.
"""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assertion_analyzer.analyzer import (
    analyze_assertion,
    generate_sg_assertions,
)


def main():
    # Test assertion
    test_assertion = "The response should state that the meeting '1:1 Action Items Review' is scheduled for July 26, 2025 at 14:00 PST."
    
    print("=" * 70)
    print("FULL PIPELINE TEST")
    print("=" * 70)
    print(f"Input: {test_assertion}")
    print()
    
    # =========================================================================
    # STEP 1: Classification
    # =========================================================================
    print(f"{'='*70}")
    print("STEP 1: CLASSIFICATION (GPT-5)")
    print("=" * 70)
    
    gpt5_result = analyze_assertion(test_assertion)
    
    print(f"  Dimension: {gpt5_result.get('dimension_id')} - {gpt5_result.get('dimension_name')}")
    print(f"  Layer: {gpt5_result.get('layer')}")
    print(f"  Level: {gpt5_result.get('level')}")
    print(f"  Rationale: {gpt5_result.get('rationale', '')[:100]}...")
    
    # =========================================================================
    # STEPS 2-5: S+G Generation → Scenario → WBP → Verification
    # =========================================================================
    print(f"\n{'='*70}")
    print("STEPS 2-5: S+G GENERATION → SCENARIO → WBP → VERIFICATION")
    print("=" * 70)
    
    # This single call does:
    # 2. Generate S assertion + G assertions
    # 3. Generate scenario
    # 4. Generate WBP
    # 5. Verify WBP
    assertions = generate_sg_assertions(
        gpt5_result=gpt5_result,
        assertion_text=test_assertion,
        assertion_index=0,
        generate_examples=True,  # This triggers steps 3-5
        verbose=True
    )
    
    # =========================================================================
    # Display Results
    # =========================================================================
    print(f"\n{'='*70}")
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nGenerated {len(assertions)} assertions:")
    
    # Primary S assertion
    primary = assertions[0] if assertions else None
    if primary:
        print(f"\n  PRIMARY S ASSERTION:")
        print(f"    ID: {primary.get('assertion_id')}")
        print(f"    Dimension: {primary.get('dimension_id')} - {primary.get('dimension_name')}")
        print(f"    Text: {primary.get('text')}")
        print(f"    Linked G dims: {primary.get('linked_g_dims', [])}")
        
        # Show scenario if generated
        success_example = primary.get('success_example', {})
        if success_example:
            scenario = success_example.get('scenario', {})
            print(f"\n  SCENARIO (Ground Truth):")
            print(f"    Title: {scenario.get('title', 'N/A')}")
            print(f"    Date: {scenario.get('date', 'N/A')} at {scenario.get('time', 'N/A')}")
            print(f"    Attendees: {', '.join(scenario.get('attendees', []))}")
            
            wbp = success_example.get('workback_plan', '')
            print(f"\n  WBP Generated: {len(wbp)} chars")
            if wbp:
                preview = wbp[:300] + "..." if len(wbp) > 300 else wbp
                print(f"    Preview: {preview[:200]}...")
            
            print(f"\n  VERIFICATION:")
            print(f"    Overall: {'PASS' if success_example.get('overall_verified') else 'FAIL'}")
            for ar in success_example.get('assertion_results', []):
                status = "✓" if ar.get('passes', False) else "✗"
                print(f"      {status} {ar.get('assertion_id', 'N/A')}: {ar.get('explanation', '')[:50]}...")
    
    # G assertions
    g_assertions = assertions[1:] if len(assertions) > 1 else []
    if g_assertions:
        print(f"\n  GENERATED G ASSERTIONS ({len(g_assertions)}):")
        for g in g_assertions:
            print(f"    - {g.get('assertion_id')}: {g.get('dimension_id')} ({g.get('dimension_name')})")
            print(f"      Text: {g.get('text', '')[:80]}...")
    
    # =========================================================================
    # Save Results
    # =========================================================================
    output_file = os.path.join(os.path.dirname(__file__), 'full_pipeline_output.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_name": "Full Pipeline Test",
            "input_assertion": test_assertion,
            "classification": gpt5_result,
            "assertions": assertions
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("=" * 70)
    print(f"  Classification: {gpt5_result.get('dimension_id')} - {gpt5_result.get('dimension_name')}")
    print(f"  S assertions: 1")
    print(f"  G assertions: {len(g_assertions)}")
    print(f"  Scenario: Generated")
    print(f"  WBP: Generated")
    print(f"  Verification: {'PASS' if primary and primary.get('success_example', {}).get('overall_verified') else 'FAIL'}")
    print(f"\n  Results saved to: {output_file}")


if __name__ == '__main__':
    main()
