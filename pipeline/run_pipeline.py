"""
Run the complete Two-Layer Assertion Evaluation Pipeline.

Stages:
    1. Scenario Generation - Create meeting scenarios
    2. Assertion Generation - Generate S1-S10 + G1-G5 assertions
    3. Plan Generation - Create perfect/medium/low quality plans
    4. Plan Evaluation - Evaluate plans against assertions
    5. Report Generation - Generate comprehensive report

Usage:
    # Run full pipeline with templates
    python -m pipeline.run_pipeline
    
    # Run full pipeline with custom data
    python -m pipeline.run_pipeline --from-data docs/LOD_1121.WithUserUrl.jsonl
    
    # Run specific stages only
    python -m pipeline.run_pipeline --stages 1,2,3
    
    # Resume from a specific stage
    python -m pipeline.run_pipeline --resume-from 3
"""

import argparse
import time
from datetime import datetime

from .config import (
    PIPELINE_OUTPUT_DIR,
    SCENARIOS_FILE,
    ASSERTIONS_FILE,
    PLANS_FILE,
    EVALUATION_FILE,
    REPORT_FILE,
    file_exists
)

from . import scenario_generation
from . import assertion_generation
from . import plan_generation
from . import plan_evaluation
from . import report_generation


STAGE_INFO = {
    1: {"name": "Scenario Generation", "module": scenario_generation, "output": SCENARIOS_FILE},
    2: {"name": "Assertion Generation", "module": assertion_generation, "output": ASSERTIONS_FILE},
    3: {"name": "Plan Generation", "module": plan_generation, "output": PLANS_FILE},
    4: {"name": "Plan Evaluation", "module": plan_evaluation, "output": EVALUATION_FILE},
    5: {"name": "Report Generation", "module": report_generation, "output": REPORT_FILE},
}


def print_banner():
    """Print pipeline banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║           TWO-LAYER ASSERTION EVALUATION PIPELINE                            ║
║                                                                              ║
║   Framework: Structural (S1-S10) + Grounding (G1-G5)                         ║
║   Version: 1.0.0                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def print_stage_header(stage_num: int, stage_name: str):
    """Print stage header."""
    print(f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│  STAGE {stage_num}: {stage_name.upper():<66} │
└──────────────────────────────────────────────────────────────────────────────┘
""")


def check_prerequisites(stage_num: int) -> bool:
    """Check if prerequisites for a stage exist."""
    if stage_num == 1:
        return True  # No prerequisites
    
    prereqs = {
        2: [SCENARIOS_FILE],
        3: [SCENARIOS_FILE],
        4: [SCENARIOS_FILE, ASSERTIONS_FILE, PLANS_FILE],
        5: [EVALUATION_FILE]
    }
    
    for prereq in prereqs.get(stage_num, []):
        if not file_exists(prereq):
            print(f"  ⚠️ Missing prerequisite: {prereq}")
            return False
    
    return True


def run_stage(stage_num: int, args: argparse.Namespace) -> bool:
    """Run a single stage of the pipeline."""
    info = STAGE_INFO.get(stage_num)
    if not info:
        print(f"  ❌ Unknown stage: {stage_num}")
        return False
    
    print_stage_header(stage_num, info["name"])
    
    # Check prerequisites
    if not check_prerequisites(stage_num):
        print(f"  ❌ Prerequisites not met for stage {stage_num}")
        return False
    
    # Run the stage
    start_time = time.time()
    
    try:
        if stage_num == 1:
            if args.from_data:
                scenario_generation.generate_from_data(args.from_data, args.limit)
            else:
                scenario_generation.generate_from_templates(enrich=args.enrich)
            # Call main to save
            import sys
            original_argv = sys.argv
            sys.argv = ['', '--template'] if not args.from_data else ['', '--from-data', args.from_data, '--limit', str(args.limit)]
            scenario_generation.main()
            sys.argv = original_argv
            
        elif stage_num == 2:
            assertion_generation.main()
            
        elif stage_num == 3:
            plan_generation.main()
            
        elif stage_num == 4:
            plan_evaluation.main()
            
        elif stage_num == 5:
            report_generation.main()
        
        elapsed = time.time() - start_time
        print(f"\n  ⏱️ Stage {stage_num} completed in {elapsed:.1f}s")
        return True
        
    except Exception as e:
        print(f"\n  ❌ Stage {stage_num} failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(description="Two-Layer Assertion Evaluation Pipeline")
    parser.add_argument("--from-data", type=str, help="Load scenarios from JSONL data file")
    parser.add_argument("--limit", type=int, default=3, help="Limit number of scenarios")
    parser.add_argument("--enrich", action="store_true", help="Use GPT-5 to enrich scenarios")
    parser.add_argument("--stages", type=str, help="Comma-separated list of stages to run (e.g., '1,2,3')")
    parser.add_argument("--resume-from", type=int, help="Resume pipeline from this stage")
    parser.add_argument("--skip-existing", action="store_true", help="Skip stages with existing output")
    args = parser.parse_args()
    
    print_banner()
    
    # Determine which stages to run
    if args.stages:
        stages_to_run = [int(s.strip()) for s in args.stages.split(",")]
    elif args.resume_from:
        stages_to_run = list(range(args.resume_from, 6))
    else:
        stages_to_run = [1, 2, 3, 4, 5]
    
    print(f"📋 Pipeline Configuration:")
    print(f"   Stages: {stages_to_run}")
    print(f"   Output Directory: {PIPELINE_OUTPUT_DIR}")
    if args.from_data:
        print(f"   Data Source: {args.from_data}")
    else:
        print(f"   Data Source: Built-in templates")
    print()
    
    # Run stages
    pipeline_start = time.time()
    results = {}
    
    for stage_num in stages_to_run:
        info = STAGE_INFO.get(stage_num)
        
        # Skip if output exists and --skip-existing is set
        if args.skip_existing and file_exists(info["output"]):
            print(f"  ⏭️ Skipping stage {stage_num} (output exists)")
            results[stage_num] = "skipped"
            continue
        
        success = run_stage(stage_num, args)
        results[stage_num] = "success" if success else "failed"
        
        if not success:
            print(f"\n❌ Pipeline stopped at stage {stage_num}")
            break
    
    # Summary
    pipeline_elapsed = time.time() - pipeline_start
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           PIPELINE SUMMARY                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    print(f"⏱️ Total Time: {pipeline_elapsed:.1f}s")
    print()
    
    for stage_num, status in results.items():
        info = STAGE_INFO[stage_num]
        emoji = "✅" if status == "success" else "⏭️" if status == "skipped" else "❌"
        print(f"   {emoji} Stage {stage_num}: {info['name']} - {status}")
    
    print()
    
    # Show output files
    print("📁 Output Files:")
    for stage_num in stages_to_run:
        info = STAGE_INFO[stage_num]
        exists = "✓" if file_exists(info["output"]) else "✗"
        print(f"   [{exists}] {info['output']}")
    
    print()
    
    if all(r == "success" or r == "skipped" for r in results.values()):
        print("✅ Pipeline completed successfully!")
        print(f"\n📈 View the report: {REPORT_FILE}")
    else:
        print("⚠️ Pipeline completed with errors")
    
    return results


if __name__ == "__main__":
    main()
