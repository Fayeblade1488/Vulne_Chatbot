import os
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_benchmark(tool_script: str, output_dir: str):
    """Run a single benchmark script, directing its output to a specific directory."""
    cmd = ['python', f'benchmarking/{tool_script}', '--output_dir', output_dir]
    logger.info(f"Executing command: {' '.join(cmd)}")
    
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True, # Still capture to check stderr
            text=True
        )
        logger.info(f"Successfully completed benchmark for: {tool_script}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run {tool_script}. Return code: {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error(f"Script not found: {tool_script}. Make sure you are in the correct directory.")
        return False

if __name__ == "__main__":
    # --- 1. Create a master directory for this entire run ---
    master_run_dir = f"master_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(master_run_dir, exist_ok=True)
    logger.info(f"Created master results directory: {master_run_dir}")

    results_dirs = {}
    
    # --- 2. Define tools and their result subdirectories ---
    benchmark_scripts = {
        'garak': 'run_garak.py',
        'nemo': 'run_nemo.py',
        'guardrailsai': 'run_guardrailsai.py'
    }

    # --- 3. Run each benchmark, passing its dedicated output directory ---
    for tool, script in benchmark_scripts.items():
        tool_output_dir = os.path.join(master_run_dir, f"{tool}_results")
        os.makedirs(tool_output_dir, exist_ok=True)
        
        success = run_benchmark(script, tool_output_dir)
        if success:
            results_dirs[tool] = tool_output_dir

    # --- 4. Generate the final report if there were any successful runs ---
    if results_dirs:
        logger.info("Generating final report from collected results...")
        report_cmd = ['python', 'benchmarking/report_generator.py']
        for tool, path in results_dirs.items():
            report_cmd.extend(['--results', tool, path])
        
        try:
            subprocess.run(report_cmd, check=True)
            logger.info("Report generation complete.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate report: {e}")
    else:
        logger.warning("No benchmark results were generated. Skipping report generation.")

    logger.info("All benchmarks completed.")
