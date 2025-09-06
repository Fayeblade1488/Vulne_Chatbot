import os
import subprocess
import logging
from datetime import datetime
import json
import argparse

# Import the configuration validator
from .config_validator import load_and_validate_config, ConfigValidationError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_benchmark(tool_script: str, config_path: str, output_dir: str) -> str:
    """Run a single benchmark script as a module."""
    module_name = f'vulne_bench.{tool_script.replace(".py", "")}'
    cmd = ['python', '-m', module_name, '--config', config_path, '--output_dir', output_dir]
    logger.info(f"Executing command: {' '.join(cmd)}")

    try:
        # We don't capture output here to see the progress bars (tqdm) in real-time
        subprocess.run(cmd, check=True, text=True)
        logger.info(f"Successfully completed benchmark for: {module_name}")
        return output_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run {module_name}. Return code: {e.returncode}")
        return None
    except FileNotFoundError:
        # This error is less likely with `python -m` but good to keep
        logger.error(f"Module not found: {module_name}. Make sure the package is installed correctly.")
        return None

def run_report_generator(results_dirs: dict, output_dir: str):
    """Run the report generator script as a module."""
    module_name = 'vulne_bench.report_generator'
    results_json = json.dumps(results_dirs)
    cmd = ['python', '-m', module_name, '--results_dirs', results_json, '--output_dir', output_dir]
    logger.info(f"Executing command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        logger.info("Report generation complete.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate report: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run all benchmarks for Vulne_Chatbot.")
    parser.add_argument('--config', type=str, default=os.path.join(os.path.dirname(__file__), 'config.json'), help='Path to the main configuration file.')
    args = parser.parse_args()

    # Load and validate configuration
    try:
        config = load_and_validate_config(args.config)
    except ConfigValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        return
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse configuration file as JSON: {e}")
        return

    # --- 1. Create a master directory for this entire run ---
    master_run_dir = os.path.join(os.getcwd(), f"master_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(master_run_dir, exist_ok=True)
    logger.info(f"Created master results directory: {master_run_dir}")

    results_dirs = {}

    # --- 2. Define tools to run ---
    benchmark_scripts = {
        'garak': 'run_garak.py',
        'nemo': 'run_nemo.py',
        'guardrailsai': 'run_guardrailsai.py'
    }

    # --- 3. Run each benchmark ---
    for tool, script in benchmark_scripts.items():
        if tool in config:
            logger.info(f"----- Running {tool.capitalize()} Benchmark -----")
            tool_output_dir = os.path.join(master_run_dir, f"{tool}_results")
            os.makedirs(tool_output_dir, exist_ok=True)

            result_dir = run_benchmark(script, args.config, tool_output_dir)
            if result_dir:
                results_dirs[tool] = result_dir
        else:
            logger.warning(f"No configuration found for '{tool}'. Skipping.")

    # --- 4. Generate the final report ---
    if results_dirs:
        logger.info("----- Generating Final Report -----")
        report_output_dir = os.path.join(master_run_dir, "final_report")
        os.makedirs(report_output_dir, exist_ok=True)
        run_report_generator(results_dirs, report_output_dir)
    else:
        logger.warning("No benchmark results were generated. Skipping report generation.")

    logger.info(f"All benchmarks completed. Results are in: {master_run_dir}")

if __name__ == "__main__":
    main()