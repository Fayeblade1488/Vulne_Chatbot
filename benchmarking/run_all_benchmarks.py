import os
import subprocess
import logging
from datetime import datetime
import argparse
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_benchmark(tool_script: str, output_dir: str, dry_run: bool, args: list = None) -> str:
    """Run a benchmarking script."""
    cmd = ['python', tool_script, '--output-dir', output_dir]
    if args:
        cmd.extend(args)
    if dry_run:
        cmd.append('--dry-run')
        logger.info(f"DRY RUN: Would execute: {' '.join(cmd)}")
        return output_dir

    try:
        subprocess.check_call(cmd)
        return output_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run {tool_script}: {e}")
        return None

def run_report_generator(results_dirs: dict, dry_run: bool):
    """Run the report generator script."""
    cmd = ['python', 'report_generator.py', json.dumps(results_dirs)]
    if dry_run:
        logger.info(f"DRY RUN: Would execute: {' '.join(cmd)}")
        return

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run report_generator.py: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all benchmarks.")
    parser.add_argument('--target-url', type=str, default="http://127.0.0.1:7000/chat", help="Target URL for the chatbot.")
    parser.add_argument('--models', type=str, default="mistral:latest,oci:cohere.command-r-plus", help="Comma-separated list of models to test.")
    parser.add_argument('--output-dir', type=str, default="benchmark_results", help="Main directory to store all benchmark results.")
    parser.add_argument('--dry-run', action='store_true', help="Print commands without executing them.")
    args = parser.parse_args()

    # Create a timestamped main results directory
    main_output_dir = os.path.join(args.output_dir, datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(main_output_dir, exist_ok=True)
    logger.info(f"Results will be stored in: {main_output_dir}")

    # Define tool-specific output directories
    garak_dir = os.path.join(main_output_dir, 'garak')
    nemo_dir = os.path.join(main_output_dir, 'nemo')
    guardrailsai_dir = os.path.join(main_output_dir, 'guardrailsai')

    # Run Garak
    logger.info("----- Running Garak Benchmark -----")
    actual_garak_dir = run_benchmark('run_garak.py', garak_dir, args.dry_run)

    # Run NeMo
    logger.info("----- Running NeMo Benchmark -----")
    actual_nemo_dir = run_benchmark('run_nemo.py', nemo_dir, args.dry_run)

    # Run GuardrailsAI
    logger.info("----- Running GuardrailsAI Benchmark -----")
    actual_guardrailsai_dir = run_benchmark('run_guardrailsai.py', guardrailsai_dir, args.dry_run)

    # Generate report
    logger.info("----- Generating Report -----")
    results_dirs = {
        'garak': actual_garak_dir,
        'nemo': actual_nemo_dir,
        'guardrailsai': actual_guardrailsai_dir
    }
    # Filter out None values in case of failures
    results_dirs = {k: v for k, v in results_dirs.items() if v is not None}

    if results_dirs:
        run_report_generator(results_dirs, args.dry_run)
    else:
        logger.warning("No benchmark results to report.")

    logger.info("All benchmarks completed.")
