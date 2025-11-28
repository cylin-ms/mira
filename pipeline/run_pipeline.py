"""
Run the complete Two-Layer Assertion Evaluation Pipeline.

Stages:
    1. Scenario Generation - Create meeting scenarios
    2. Assertion Generation - Generate S1-S10 + G1-G5 assertions
    3. Plan Generation - Create perfect/medium/low quality plans
    4. Plan Evaluation - Evaluate plans against assertions
    5. Report Generation - Generate comprehensive report

Each run creates a unique run ID and subdirectory for tracking.

Usage:
    # Run full pipeline (creates new run ID)
    python -m pipeline.run_pipeline
    
    # Run with custom run ID
    python -m pipeline.run_pipeline --run-id my_experiment_01
    
    # Resume/continue an existing run
    python -m pipeline.run_pipeline --continue-run run_20251128_151500_abc12345
    
    # List all previous runs
    python -m pipeline.run_pipeline --list-runs
    
    # Run specific stages only
    python -m pipeline.run_pipeline --stages 1,2,3
    
    # Resume from a specific stage
    python -m pipeline.run_pipeline --resume-from 3
"""

import argparse
import time
import os
from datetime import datetime

from .config import (
    initialize_run,
    load_run,
    get_current_run_id,
    get_current_run_dir,
    get_run_file,
    list_runs,
    file_exists,
    SCENARIOS_FILENAME,
    ASSERTIONS_FILENAME,
    PLANS_FILENAME,
    EVALUATION_FILENAME,
    REPORT_FILENAME,
)

from . import scenario_generation
from . import assertion_generation
from . import plan_generation
from . import plan_evaluation
from . import report_generation


def get_stage_info():
    """Get stage info with current run paths."""
    return {
        1: {"name": "Scenario Generation", "module": scenario_generation, "file": SCENARIOS_FILENAME},
        2: {"name": "Assertion Generation", "module": assertion_generation, "file": ASSERTIONS_FILENAME},
        3: {"name": "Plan Generation", "module": plan_generation, "file": PLANS_FILENAME},
        4: {"name": "Plan Evaluation", "module": plan_evaluation, "file": EVALUATION_FILENAME},
        5: {"name": "Report Generation", "module": report_generation, "file": REPORT_FILENAME},
    }


def print_banner(run_id: str):
    """Print pipeline banner with run ID."""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           TWO-LAYER ASSERTION EVALUATION PIPELINE                            ║
║                                                                              ║
║   Framework: Structural (S1-S10) + Grounding (G1-G5)                         ║
║   Run ID: {run_id:<64} ║
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
        2: [SCENARIOS_FILENAME],
        3: [SCENARIOS_FILENAME],
        4: [SCENARIOS_FILENAME, ASSERTIONS_FILENAME, PLANS_FILENAME],
        5: [EVALUATION_FILENAME]
    }
    
    for prereq_file in prereqs.get(stage_num, []):
        prereq_path = get_run_file(prereq_file)
        if not file_exists(prereq_path):
            print(f"  ⚠️ Missing prerequisite: {prereq_path}")
            return False
    
    return True


def run_stage(stage_num: int, args: argparse.Namespace) -> bool:
    """Run a single stage of the pipeline."""
    stage_info = get_stage_info()
    info = stage_info.get(stage_num)
    if not info:
        print(f"  ❌ Unknown stage: {stage_num}")
        return False
    
    print_stage_header(stage_num, info["name"])
    
    # Check prerequisites
    if not check_prerequisites(stage_num):
        print(f"  ❌ Prerequisites not met for stage {stage_num}")
        return False
    
    # Run the stage with current run directory
    start_time = time.time()
    run_dir = get_current_run_dir()
    
    try:
        if stage_num == 1:
            # Scenario generation
            import sys
            original_argv = sys.argv
            output_file = get_run_file(SCENARIOS_FILENAME)
            if args.from_data:
                sys.argv = ['', '--from-data', args.from_data, '--limit', str(args.limit), '--output', output_file]
            else:
                sys.argv = ['', '--template', '--output', output_file]
                if args.enrich:
                    sys.argv.append('--enrich')
            scenario_generation.main()
            sys.argv = original_argv
            
        elif stage_num == 2:
            import sys
            original_argv = sys.argv
            sys.argv = ['', 
                       '--scenarios', get_run_file(SCENARIOS_FILENAME),
                       '--output', get_run_file(ASSERTIONS_FILENAME)]
            assertion_generation.main()
            sys.argv = original_argv
            
        elif stage_num == 3:
            import sys
            original_argv = sys.argv
            sys.argv = ['',
                       '--scenarios', get_run_file(SCENARIOS_FILENAME),
                       '--output', get_run_file(PLANS_FILENAME)]
            plan_generation.main()
            sys.argv = original_argv
            
        elif stage_num == 4:
            import sys
            original_argv = sys.argv
            sys.argv = ['',
                       '--scenarios', get_run_file(SCENARIOS_FILENAME),
                       '--assertions', get_run_file(ASSERTIONS_FILENAME),
                       '--plans', get_run_file(PLANS_FILENAME),
                       '--output', get_run_file(EVALUATION_FILENAME)]
            plan_evaluation.main()
            sys.argv = original_argv
            
        elif stage_num == 5:
            import sys
            original_argv = sys.argv
            sys.argv = ['',
                       '--scenarios', get_run_file(SCENARIOS_FILENAME),
                       '--assertions', get_run_file(ASSERTIONS_FILENAME),
                       '--plans', get_run_file(PLANS_FILENAME),
                       '--evaluation', get_run_file(EVALUATION_FILENAME),
                       '--output', get_run_file(REPORT_FILENAME)]
            report_generation.main()
            sys.argv = original_argv
        
        elapsed = time.time() - start_time
        print(f"\n  ⏱️ Stage {stage_num} completed in {elapsed:.1f}s")
        return True
        
    except Exception as e:
        print(f"\n  ❌ Stage {stage_num} failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_runs():
    """Show all available runs."""
    runs = list_runs()
    
    if not runs:
        print("No pipeline runs found.")
        return
    
    print(f"\n📁 Available Pipeline Runs ({len(runs)} total):")
    print("=" * 80)
    print(f"{'Run ID':<45} {'Created':<20} {'Status':<10}")
    print("-" * 80)
    
    for run in runs:
        run_id = run.get("run_id", "unknown")
        created = run.get("created_at", "unknown")
        if created and created != "unknown":
            # Parse ISO format and format nicely
            try:
                dt = datetime.fromisoformat(created)
                created = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        status = run.get("status", "unknown")
        print(f"{run_id:<45} {created:<20} {status:<10}")
    
    print()
    print("To continue a run: python -m pipeline.run_pipeline --continue-run <run_id>")


def update_run_status(status: str):
    """Update the current run's status in metadata."""
    import json
    run_dir = get_current_run_dir()
    metadata_file = os.path.join(run_dir, "run_metadata.json")
    
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        metadata["status"] = status
        metadata["updated_at"] = datetime.now().isoformat()
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    except Exception:
        pass


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(description="Two-Layer Assertion Evaluation Pipeline")
    parser.add_argument("--run-id", type=str, help="Custom run ID (auto-generated if not specified)")
    parser.add_argument("--continue-run", type=str, help="Continue/resume an existing run by ID")
    parser.add_argument("--list-runs", action="store_true", help="List all previous pipeline runs")
    parser.add_argument("--from-data", type=str, help="Load scenarios from JSONL data file")
    parser.add_argument("--limit", type=int, default=3, help="Limit number of scenarios")
    parser.add_argument("--enrich", action="store_true", help="Use GPT-5 to enrich scenarios")
    parser.add_argument("--stages", type=str, help="Comma-separated list of stages to run (e.g., '1,2,3')")
    parser.add_argument("--resume-from", type=int, help="Resume pipeline from this stage")
    parser.add_argument("--skip-existing", action="store_true", help="Skip stages with existing output")
    args = parser.parse_args()
    
    # Handle --list-runs
    if args.list_runs:
        show_runs()
        return {}
    
    # Initialize or load run
    if args.continue_run:
        try:
            run_id = load_run(args.continue_run)
            print(f"📂 Continuing run: {run_id}")
        except ValueError as e:
            print(f"❌ {e}")
            return {}
    else:
        run_id = initialize_run(args.run_id)
        print(f"📂 New run created: {run_id}")
    
    print_banner(run_id)
    
    # Determine which stages to run
    if args.stages:
        stages_to_run = [int(s.strip()) for s in args.stages.split(",")]
    elif args.resume_from:
        stages_to_run = list(range(args.resume_from, 6))
    else:
        stages_to_run = [1, 2, 3, 4, 5]
    
    run_dir = get_current_run_dir()
    
    print(f"📋 Pipeline Configuration:")
    print(f"   Run ID: {run_id}")
    print(f"   Stages: {stages_to_run}")
    print(f"   Output Directory: {run_dir}")
    if args.from_data:
        print(f"   Data Source: {args.from_data}")
    else:
        print(f"   Data Source: Built-in templates")
    print()
    
    # Run stages
    pipeline_start = time.time()
    results = {}
    stage_info = get_stage_info()
    
    update_run_status("running")
    
    for stage_num in stages_to_run:
        info = stage_info.get(stage_num)
        
        # Skip if output exists and --skip-existing is set
        output_path = get_run_file(info["file"])
        if args.skip_existing and file_exists(output_path):
            print(f"  ⏭️ Skipping stage {stage_num} (output exists)")
            results[stage_num] = "skipped"
            continue
        
        success = run_stage(stage_num, args)
        results[stage_num] = "success" if success else "failed"
        
        if not success:
            print(f"\n❌ Pipeline stopped at stage {stage_num}")
            update_run_status("failed")
            break
    
    # Summary
    pipeline_elapsed = time.time() - pipeline_start
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           PIPELINE SUMMARY                                    ║
║   Run ID: {run_id:<65} ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    print(f"⏱️ Total Time: {pipeline_elapsed:.1f}s")
    print()
    
    for stage_num, status in results.items():
        info = stage_info[stage_num]
        emoji = "✅" if status == "success" else "⏭️" if status == "skipped" else "❌"
        print(f"   {emoji} Stage {stage_num}: {info['name']} - {status}")
    
    print()
    
    # Show output files
    print("📁 Output Files:")
    for stage_num in stages_to_run:
        info = stage_info[stage_num]
        output_path = get_run_file(info["file"])
        exists = "✓" if file_exists(output_path) else "✗"
        print(f"   [{exists}] {output_path}")
    
    print()
    
    if all(r == "success" or r == "skipped" for r in results.values()):
        update_run_status("completed")
        print("✅ Pipeline completed successfully!")
        report_path = get_run_file(REPORT_FILENAME)
        print(f"\n📈 View the report: {report_path}")
    else:
        print("⚠️ Pipeline completed with errors")
    
    print(f"\n💡 To view this run later: python -m pipeline.run_pipeline --continue-run {run_id}")
    
    return results


if __name__ == "__main__":
    main()
