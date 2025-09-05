import json
import os
import time
import subprocess
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Path Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, 'garak_config.json')
LOG_FILE = os.path.join(SCRIPT_DIR, 'garak_benchmark.log')

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GarakBenchmarker:
    def __init__(
        self,
        config_path: str = DEFAULT_CONFIG_PATH,
        output_dir: Optional[str] = None,
        probes: Optional[List[str]] = None,
        max_retries: int = 3,
        timeout: int = 300,
        parallel_workers: int = 4
    ):
        self.config_path = os.path.abspath(config_path)
        self.probes = probes or self.get_relevant_probes()
        self.max_retries = max_retries
        self.timeout = timeout
        self.parallel_workers = parallel_workers
        if output_dir:
            self.results_dir = os.path.abspath(output_dir)
        else:
            self.results_dir = os.path.join(SCRIPT_DIR, f"garak_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(self.results_dir, exist_ok=True)
        self.metrics = {
            'success_rate': 0.0,
            'coverage': 0.0,
            'runtime_total': 0.0,
            'failed_probes': [],
            'vulnerabilities_detected': {}
        }

    @staticmethod
    def get_relevant_probes() -> List[str]:
        """Relevant probes for GenAI/LLM/chatbot testing based on research."""
        return [
            'promptinject',      # Prompt injection attacks
            'leakreplicate',     # Data leakage
            'knownbugs',         # Known vulnerabilities
            'toxicity',          # Toxicity generation
            'misinformation',    # Misinformation/hallucination
            'encoding',          # Encoding/obfuscation attacks
            'jailbreak',         # Jailbreaking attempts
            'dan',               # DAN mode exploits
            'continuation',      # Prompt continuation attacks
            'snowball'           # Escalating attacks
        ]

    def run_single_probe(self, probe: str) -> Dict:
        """Run a single Garak probe with retries and timeout."""
        attempt = 0
        start_time = time.time()
        while attempt < self.max_retries:
            try:
                cmd = [
                    'garak',
                    '--model_type', 'rest',
                    '--model_name', 'vulnerable_chatbot',
                    '--generator_option_file', self.config_path,
                    '--probes', probe,
                    '--verbose'
                ]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                try:
                    stdout, stderr = process.communicate(timeout=self.timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    logger.warning(f"Probe {probe} timed out after {self.timeout}s")
                    attempt += 1
                    continue

                if process.returncode == 0:
                    runtime = time.time() - start_time
                    output_file = os.path.join(self.results_dir, f"{probe}_output.log")
                    with open(output_file, 'w') as f:
                        f.write(stdout)

                    # Parse results (simplified; extend with actual parsing)
                    vulnerabilities = self.parse_garak_output(stdout)

                    logger.info(f"Probe {probe} completed in {runtime:.2f}s")
                    return {
                        'probe': probe,
                        'success': True,
                        'runtime': runtime,
                        'vulnerabilities': vulnerabilities,
                        'output_file': output_file
                    }

                logger.error(f"Probe {probe} failed with code {process.returncode}: {stderr}")
                attempt += 1

            except Exception as e:
                logger.error(f"Error running probe {probe}: {str(e)}")
                attempt += 1

        return {
            'probe': probe,
            'success': False,
            'error': 'Max retries exceeded'
        }

    def parse_garak_output(self, output: str) -> Dict:
        """Parse Garak output for vulnerabilities and metrics."""
        # Implement parsing logic here (regex or JSON if available)
        # Example: Count detected vulnerabilities
        detected = {}
        if 'injection successful' in output.lower():
            detected['prompt_injection'] = True
        # Add more parsers...
        return detected

    def run_benchmark(self) -> Dict:
        """Run all probes in parallel with metrics collection."""
        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            future_to_probe = {
                executor.submit(self.run_single_probe, probe): probe
                for probe in self.probes
            }

            for future in as_completed(future_to_probe):
                try:
                    result = future.result()
                    results.append(result)
                    if not result['success']:
                        self.metrics['failed_probes'].append(result['probe'])
                except Exception as e:
                    logger.error(f"Probe execution failed: {str(e)}")

        # Calculate metrics
        total_probes = len(self.probes)
        successful = len([r for r in results if r['success']])
        self.metrics['success_rate'] = (successful / total_probes) * 100 if total_probes > 0 else 0
        self.metrics['coverage'] = (successful / total_probes) * 100 if total_probes > 0 else 0
        self.metrics['runtime_total'] = time.time() - start_time

        # Aggregate vulnerabilities
        for result in results:
            if 'vulnerabilities' in result:
                for vuln, detected in result['vulnerabilities'].items():
                    if detected:
                        self.metrics['vulnerabilities_detected'][vuln] = self.metrics['vulnerabilities_detected'].get(vuln, 0) + 1

        self.save_results(results)
        return self.metrics

    def save_results(self, results: List[Dict]):
        """Save benchmark results to JSON."""
        output_path = os.path.join(self.results_dir, 'benchmark_results.json')
        with open(output_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'probes': self.probes,
                'metrics': self.metrics,
                'detailed_results': results
            }, f, indent=4)

        logger.info(f"Results saved to {output_path}")
        print(self.results_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Garak benchmark.")
    parser.add_argument('--config_path', type=str, default=DEFAULT_CONFIG_PATH, help='Path to garak_config.json')
    parser.add_argument('--output_dir', type=str, default=None, help='Directory to save results.')
    args = parser.parse_args()

    benchmarker = GarakBenchmarker(
        config_path=args.config_path,
        output_dir=args.output_dir
    )
    benchmarker.run_benchmark()
