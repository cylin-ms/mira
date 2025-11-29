#!/usr/bin/env python3
"""
Command-line interface for the Assertion Analyzer package.

Usage:
    python -m assertion_analyzer "Your assertion text here"
    python -m assertion_analyzer --batch input.txt --output-dir ./results
    python -m assertion_analyzer --help
"""

import sys
import os
import json
import argparse
import time
from datetime import datetime

from .analyzer import (
    analyze_assertion,
    generate_sg_assertions,
    generate_report,
    AssertionAnalyzer,
)
from .config import get_substrate_token


def print_results(assertions: list):
    """Pretty print the assertion results."""
    print("\n" + "=" * 70)
    print("CONVERSION RESULTS")
    print("=" * 70)
    
    for i, a in enumerate(assertions):
        is_primary = a.get('parent_assertion_id') is None
        prefix = "[P]" if is_primary else "  +-"
        dim = a.get('dimension_id', 'UNMAPPED')
        layer = a.get('layer', 'unknown')
        level = a.get('level', 'unknown')
        
        print(f"\n{prefix} [{a.get('assertion_id')}] {dim} ({layer}/{level})")
        print(f"   {a.get('dimension_name')}")
        print(f"   Text: {a.get('text', '')[:80]}...")
        
        if is_primary:
            rationale = a.get('rationale', {}).get('mapping_reason', '')
            if rationale:
                print(f"   Rationale: {rationale[:80]}...")
    
    print("\n" + "-" * 70)
    s_count = sum(1 for a in assertions if a.get('dimension_id', '').startswith('S'))
    g_count = sum(1 for a in assertions if a.get('dimension_id', '').startswith('G'))
    print(f"Total: {len(assertions)} assertions ({s_count} S + {g_count} G)")


def process_single_assertion(assertion: str, index: int, context: str = None, 
                             output_dir: str = None, no_examples: bool = False,
                             quiet: bool = False, json_output: bool = False,
                             no_report: bool = False, assertion_id: str = None) -> dict:
    """
    Process a single assertion and return results.
    
    Args:
        assertion: The assertion text to analyze
        index: Index for ID generation
        context: Optional context
        output_dir: Directory to save results
        no_examples: Skip WBP example generation
        quiet: Reduce verbosity
        json_output: Output as JSON
        no_report: Skip report generation
        assertion_id: Custom assertion ID (e.g., "A0001")
    
    Returns:
        dict with 'success', 'assertions', 'error', 'file_path', 'assertion_id' keys
    """
    # Generate assertion ID if not provided
    if assertion_id is None:
        assertion_id = f"A{index:04d}"
    
    result = {
        'success': False,
        'assertion': assertion,
        'index': index,
        'assertion_id': assertion_id,
        'assertions': [],
        'error': None,
        'file_path': None
    }
    
    try:
        # Step 1: GPT-5 classification
        gpt5_result = analyze_assertion(assertion, context)
        
        if "error" in gpt5_result:
            result['error'] = gpt5_result.get('error')
            return result
        
        if not quiet:
            print(f"   ID: {assertion_id}")
            print(f"   Dimension: {gpt5_result.get('dimension_id')} - {gpt5_result.get('dimension_name')}")
        
        # Step 2: Generate S+G assertions with linkage
        assertions = generate_sg_assertions(
            gpt5_result, 
            assertion, 
            index,
            generate_examples=not no_examples,
            verbose=not quiet
        )
        
        result['assertions'] = assertions
        
        # Step 3: Generate report and save
        if not no_report:
            report_result = generate_report(assertions, assertion, output_dir, assertion_id)
            result['file_path'] = report_result.get('json_file_path')
            if not quiet and not json_output:
                print(report_result['summary_table'])
        elif json_output:
            print(json.dumps(assertions, indent=2, ensure_ascii=False))
        else:
            print_results(assertions)
        
        result['success'] = True
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def run_batch_mode(input_file: str, output_dir: str = None, context: str = None,
                   no_examples: bool = False, quiet: bool = False) -> int:
    """
    Process multiple assertions from a file.
    
    Args:
        input_file: Path to text file with one assertion per line
        output_dir: Directory to save results (default: ./batch_results_YYYYMMDD_HHMMSS)
        context: Optional context for all assertions
        no_examples: Skip WBP example generation
        quiet: Reduce verbosity
        
    Returns:
        Exit code (0 = success, 1 = some failures, 2 = all failures)
    """
    # Read assertions from file
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return 2
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Filter empty lines and comments
    assertions = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            assertions.append(line)
    
    if not assertions:
        print("Error: No assertions found in input file")
        return 2
    
    total = len(assertions)
    
    # Setup output directory
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"./batch_results_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 70)
    print("WBP Assertion Analyzer - BATCH MODE")
    print("=" * 70)
    print(f"Input file:  {input_file}")
    print(f"Output dir:  {output_dir}")
    print(f"Assertions:  {total}")
    if context:
        print(f"Context:     {context}")
    print("=" * 70)
    
    # Pre-load resources for efficiency (prompts are loaded at module import time)
    print("\nInitializing...")
    print("  [OK] Prompts loaded from prompts.json")
    
    # Pre-authenticate to avoid auth popup during batch processing
    try:
        get_substrate_token()
        print("  [OK] Authentication token acquired")
    except Exception as e:
        print(f"  [FAIL] Authentication failed: {e}")
        return 2
    
    # Create assertion index file (ID -> assertion mapping)
    assertion_index = {
        "input_file": input_file,
        "total": total,
        "assertions": {
            f"A{i:04d}": assertion for i, assertion in enumerate(assertions)
        }
    }
    index_path = os.path.join(output_dir, "_assertions_index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(assertion_index, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Assertion index saved to: _assertions_index.json")
    
    print()
    
    # Process each assertion
    results = []
    success_count = 0
    fail_count = 0
    start_time = time.time()
    
    for i, assertion in enumerate(assertions):
        # Generate assertion ID
        assertion_id = f"A{i:04d}"
        
        # Progress indicator
        progress = f"[{i+1}/{total}]"
        elapsed = time.time() - start_time
        if i > 0:
            eta = (elapsed / i) * (total - i)
            eta_str = f" | ETA: {int(eta)}s"
        else:
            eta_str = ""
        
        # Truncate assertion for display
        display_text = assertion[:45] + "..." if len(assertion) > 45 else assertion
        print(f"\n{progress} {assertion_id}: \"{display_text}\"{eta_str}")
        print("-" * 70)
        
        # Process
        result = process_single_assertion(
            assertion=assertion,
            index=i,
            context=context,
            output_dir=output_dir,
            no_examples=no_examples,
            quiet=quiet,
            json_output=False,
            no_report=False,
            assertion_id=assertion_id
        )
        
        results.append(result)
        
        if result['success']:
            success_count += 1
            print(f"   [OK] Saved to: {result['file_path']}")
        else:
            fail_count += 1
            print(f"   [FAIL] {result['error']}")
    
    # Summary
    total_time = time.time() - start_time
    print()
    print("=" * 70)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Total:     {total} assertions")
    print(f"Success:   {success_count}")
    print(f"Failed:    {fail_count}")
    print(f"Time:      {total_time:.1f}s ({total_time/total:.1f}s per assertion)")
    print(f"Output:    {output_dir}")
    print("=" * 70)
    
    # Save batch summary
    summary_path = os.path.join(output_dir, "_batch_summary.json")
    summary = {
        "input_file": input_file,
        "output_dir": output_dir,
        "total": total,
        "success": success_count,
        "failed": fail_count,
        "time_seconds": round(total_time, 2),
        "results": [
            {
                "assertion_id": r['assertion_id'],
                "index": r['index'],
                "assertion": r['assertion'],
                "success": r['success'],
                "error": r['error'],
                "file": r['file_path']
            }
            for r in results
        ]
    }
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Summary:   {summary_path}")
    
    # Generate batch markdown report
    md_report_path = os.path.join(output_dir, "_batch_summary.md")
    md_content = _generate_batch_markdown_report(summary, results, output_dir)
    with open(md_report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Report:    {md_report_path}")
    
    # Return code
    if fail_count == 0:
        return 0
    elif success_count == 0:
        return 2
    else:
        return 1


def _generate_batch_markdown_report(summary: dict, results: list, output_dir: str) -> str:
    """
    Generate a comprehensive markdown report for batch processing results.
    Includes aggregated statistics, dimension distribution, and insights.
    """
    lines = []
    
    # Header
    lines.append("# Batch Analysis Report")
    lines.append("")
    lines.append("**Author**: TimeBerry Assertion Analyzer  ")
    lines.append(f"**Generated**: {datetime.now().isoformat()}  ")
    lines.append(f"**Input File**: `{summary.get('input_file', 'N/A')}`")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Executive Summary
    total = summary.get('total', 0)
    success = summary.get('success', 0)
    failed = summary.get('failed', 0)
    time_sec = summary.get('time_seconds', 0)
    
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| **Total Assertions** | {total} |")
    lines.append(f"| **Successful** | {success} ✅ |")
    lines.append(f"| **Failed** | {failed} {'❌' if failed > 0 else ''} |")
    lines.append(f"| **Success Rate** | {(success/total*100):.1f}% |")
    lines.append(f"| **Total Time** | {time_sec:.1f}s |")
    lines.append(f"| **Avg Time/Assertion** | {time_sec/total:.1f}s |")
    lines.append("")
    
    # Aggregate dimension statistics
    dimension_counts = {}
    layer_counts = {"structural": 0, "grounding": 0}
    level_counts = {"critical": 0, "expected": 0, "aspirational": 0}
    g_selection_stats = {"total_possible": 0, "total_selected": 0}
    
    for r in results:
        if not r.get('success') or not r.get('assertions'):
            continue
        
        for a in r['assertions']:
            dim_id = a.get('dimension_id', 'UNKNOWN')
            dimension_counts[dim_id] = dimension_counts.get(dim_id, 0) + 1
            
            layer = a.get('layer', 'unknown')
            if layer in layer_counts:
                layer_counts[layer] += 1
            
            level = a.get('level', 'unknown')
            if level in level_counts:
                level_counts[level] += 1
    
    # Dimension Distribution
    lines.append("## Dimension Distribution")
    lines.append("")
    
    # Separate S and G dimensions
    s_dims = {k: v for k, v in dimension_counts.items() if k.startswith('S')}
    g_dims = {k: v for k, v in dimension_counts.items() if k.startswith('G')}
    
    if s_dims:
        lines.append("### Structural Dimensions (S)")
        lines.append("")
        lines.append("| Dimension | Count | Percentage |")
        lines.append("|-----------|-------|------------|")
        total_s = sum(s_dims.values())
        for dim, count in sorted(s_dims.items()):
            pct = (count / total_s * 100) if total_s > 0 else 0
            bar = "█" * int(pct / 5)  # Visual bar
            lines.append(f"| {dim} | {count} | {pct:.1f}% {bar} |")
        lines.append("")
    
    if g_dims:
        lines.append("### Grounding Dimensions (G)")
        lines.append("")
        lines.append("| Dimension | Count | Percentage |")
        lines.append("|-----------|-------|------------|")
        total_g = sum(g_dims.values())
        for dim, count in sorted(g_dims.items()):
            pct = (count / total_g * 100) if total_g > 0 else 0
            bar = "█" * int(pct / 5)
            lines.append(f"| {dim} | {count} | {pct:.1f}% {bar} |")
        lines.append("")
    
    # Layer and Level breakdown
    lines.append("## Layer & Level Breakdown")
    lines.append("")
    lines.append("| Layer | Count |")
    lines.append("|-------|-------|")
    for layer, count in layer_counts.items():
        lines.append(f"| {layer.capitalize()} | {count} |")
    lines.append("")
    
    lines.append("| Level | Count |")
    lines.append("|-------|-------|")
    for level, count in level_counts.items():
        lines.append(f"| {level.capitalize()} | {count} |")
    lines.append("")
    
    # G Selection Efficiency (comparing GPT-5 selection vs static mapping)
    lines.append("## Intelligent G Selection Analysis")
    lines.append("")
    lines.append("GPT-5 selects only relevant G dimensions for each assertion,")
    lines.append("rather than blindly using all mapped Gs.")
    lines.append("")
    
    # Calculate avg Gs per S assertion
    s_count = sum(s_dims.values())
    g_count = sum(g_dims.values())
    if s_count > 0:
        avg_g_per_s = g_count / s_count
        lines.append(f"**Average G dimensions per S assertion**: {avg_g_per_s:.2f}")
        lines.append("")
    
    # Individual Results Table
    lines.append("## Assertion Results")
    lines.append("")
    lines.append("| ID | Assertion | S Dim | G Dims | Status |")
    lines.append("|-----|-----------|-------|--------|--------|")
    
    for r in results:
        aid = r.get('assertion_id', 'N/A')
        assertion_text = r.get('assertion', '')[:40]
        if len(r.get('assertion', '')) > 40:
            assertion_text += "..."
        
        if r.get('success') and r.get('assertions'):
            s_dims_result = [a.get('dimension_id') for a in r['assertions'] if a.get('dimension_id', '').startswith('S')]
            g_dims_result = [a.get('dimension_id') for a in r['assertions'] if a.get('dimension_id', '').startswith('G')]
            s_dim = s_dims_result[0] if s_dims_result else '-'
            g_dim_str = ', '.join(g_dims_result) if g_dims_result else '-'
            status = "✅"
        else:
            s_dim = '-'
            g_dim_str = '-'
            status = f"❌ {r.get('error', 'Error')[:20]}"
        
        lines.append(f"| {aid} | {assertion_text} | {s_dim} | {g_dim_str} | {status} |")
    lines.append("")
    
    # Insights Section
    lines.append("## Insights")
    lines.append("")
    
    if s_dims:
        most_common_s = max(s_dims.items(), key=lambda x: x[1])
        lines.append(f"- **Most common structural dimension**: {most_common_s[0]} ({most_common_s[1]} occurrences)")
    
    if g_dims:
        most_common_g = max(g_dims.items(), key=lambda x: x[1])
        lines.append(f"- **Most common grounding dimension**: {most_common_g[0]} ({most_common_g[1]} occurrences)")
    
    if failed > 0:
        lines.append(f"- **⚠️ {failed} assertion(s) failed processing** - review errors in individual reports")
    
    if s_count > 0 and g_count > 0:
        g_reduction = "efficient" if avg_g_per_s < 2 else "moderate"
        lines.append(f"- **G selection efficiency**: {g_reduction} (avg {avg_g_per_s:.1f} Gs per S)")
    
    lines.append("")
    
    # Output Files
    lines.append("## Output Files")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    lines.append("| `_assertions_index.json` | ID to assertion text mapping |")
    lines.append("| `_batch_summary.json` | Full batch results in JSON |")
    lines.append("| `_batch_summary.md` | This report |")
    lines.append("| `A0000_analysis.json` | Individual JSON reports |")
    lines.append("| `A0000_analysis.md` | Individual markdown reports |")
    lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Generated by WBP Assertion Analyzer using GPT-5*")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and convert assertions using GPT-5 and the WBP framework",
        prog="python -m assertion_analyzer"
    )
    parser.add_argument(
        "assertion",
        nargs="?",
        default=None,
        help="The assertion text to analyze"
    )
    parser.add_argument(
        "-b", "--batch",
        type=str,
        metavar="FILE",
        help="Batch mode: process assertions from a text file (one per line)"
    )
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="Optional context about the meeting/response"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text"
    )
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Assertion index for ID generation (default: 0)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=None,
        help="Directory to save results (default: current dir or auto-generated for batch)"
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip final report generation"
    )
    parser.add_argument(
        "--no-examples",
        action="store_true",
        help="Skip WBP example generation (faster, classify only)"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    args = parser.parse_args()
    
    # Batch mode
    if args.batch:
        return run_batch_mode(
            input_file=args.batch,
            output_dir=args.output_dir,
            context=args.context,
            no_examples=args.no_examples,
            quiet=args.quiet
        )
    
    # Single assertion mode
    assertion = args.assertion
    if assertion is None:
        assertion = "The response arranges the draft slides task before review slides task in the plan"
    
    if not args.quiet:
        print("=" * 70)
        print("WBP Assertion Analyzer")
        print("=" * 70)
        print(f"Input: \"{assertion}\"")
        if args.context:
            print(f"Context: {args.context}")
        print()
    
    result = process_single_assertion(
        assertion=assertion,
        index=args.index,
        context=args.context,
        output_dir=args.output_dir,
        no_examples=args.no_examples,
        quiet=args.quiet,
        json_output=args.json,
        no_report=args.no_report
    )
    
    if not result['success']:
        print(f"Error: {result['error']}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
