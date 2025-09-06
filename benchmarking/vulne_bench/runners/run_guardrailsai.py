import json
import os
import time
import logging
import argparse
import bleach
from datetime import datetime
from typing import List, Dict, Optional
from guardrails import Guard
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential
import tqdm
import bandit.core.manager as bandit_manager

# Import the configuration validator
from .config_validator import load_and_validate_config, ConfigValidationError

# Import your Guard configuration from config.py
# Assuming config.py defines 'guard' object
from config import guard

# --- Logging Setup ---
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('guardrailsai_benchmark.log', maxBytes=10**6, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[handler, logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class GuardrailsAIBenchmarker:
    def __init__(
        self,
        config: Dict,
        output_dir: Optional[str] = None,
    ):
        self.guard = guard  # From config.py
        self.test_cases = config['test_cases']
        self.max_retries = config['max_retries']
        self.timeout = config['timeout']
        self.parallel_workers = config['parallel_workers']
        if output_dir:
            self.results_dir = os.path.abspath(output_dir)
        else:
            self.results_dir = os.path.join(os.path.dirname(__file__), f"guardrailsai_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(self.results_dir, exist_ok=True)
        self.metrics = {
            'validation_rate': 0.0,
            'failure_rate': 0.0,
            'runtime_avg': 0.0,
            'failed_tests': [],
            'detected_issues': {}
        }

    def security_scan(self):
        """Run Bandit security scan on this script."""
        try:
            b_manager = bandit_manager.BanditManager()
            b_manager.discover_files([__file__])
            b_manager.run_tests()
            issues = b_manager.get_issue_list()
            if issues:
                logger.warning(f"Security issues found: {len(issues)}")
                for issue in issues:
                    logger.warning(issue)
            else:
                logger.info("Security scan passed")
        except Exception as e:
            logger.error(f"Security scan failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def run_single_test(self, test_case: Dict) -> Dict:
        """Run a single test case with retries and sanitization."""
        user_input = bleach.clean(test_case['input'])
        start_time = time.time()

        try:
            # Note: Guard.validate does not have a native timeout.
            # For long-running validators, consider wrapping in a thread with a timeout.
            result = self.guard.validate(user_input)
            runtime = time.time() - start_time

            was_valid = result.validation_passed
            issues = []
            if not was_valid and hasattr(result, 'validations'):
                for v in result.validations:
                    if v.fail_reason:
                        issues.append({
                            'validator': v.validator.rail_alias,
                            'fail_reason': v.fail_reason
                        })

            logger.info(f"Test '{user_input[:20]}...' {'valid' if was_valid else 'invalid'} in {runtime:.2f}s")
            return {
                'input': user_input,
                'valid': was_valid,
                'expected_fail': test_case['expected_fail'],
                'type': test_case['type'],
                'issues': issues,
                'runtime': runtime,
                'success': True
            }
        except Exception as e:
            logger.error(f"Test failed for input '{user_input[:20]}...': {str(e)}")
            raise # Reraise to trigger tenacity retry

    def run_benchmark(self) -> Dict:
        """Run all tests in parallel with progress bar."""
        self.security_scan()
        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            futures = [executor.submit(self.run_single_test, test) for test in self.test_cases]
            for future in tqdm.tqdm(as_completed(futures), total=len(self.test_cases), desc="Running GuardrailsAI Tests"):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"A test case failed after all retries: {e}")
                    results.append({'success': False, 'error': str(e)})

        # Calculate metrics
        successful_results = [r for r in results if r['success']]
        total_tests = len(self.test_cases)
        successful_count = len(successful_results)
        valid_count = len([r for r in successful_results if r.get('valid', False)])
        false_negatives = len([r for r in successful_results if r.get('valid', False) and r['expected_fail']])

        self.metrics['validation_rate'] = (valid_count / total_tests) * 100 if total_tests > 0 else 0
        self.metrics['failure_rate'] = (false_negatives / total_tests) * 100 if total_tests > 0 else 0
        self.metrics['runtime_avg'] = sum(r.get('runtime', 0) for r in successful_results) / successful_count if successful_count > 0 else 0
        self.metrics['failed_tests'] = [r['input'] for r in results if not r['success']]

        # Aggregate issues
        for result in successful_results:
            if result.get('issues'):
                for issue in result['issues']:
                    reason = issue.get('fail_reason', 'unknown')
                    self.metrics['detected_issues'][reason] = self.metrics['detected_issues'].get(reason, 0) + 1

        self.save_results(results)
        self.metrics['runtime_total'] = time.time() - start_time
        return self.metrics

    def save_results(self, results: List[Dict]):
        output_path = os.path.join(self.results_dir, 'guardrailsai_results.json')
        with open(output_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'test_cases': len(self.test_cases),
                'metrics': self.metrics,
                'detailed_results': results
            }, f, indent=4)
        logger.info(f"Results saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Run GuardrailsAI benchmark.")
    parser.add_argument('--config', type=str, required=True, help='Path to the configuration file.')
    parser.add_argument('--output_dir', type=str, default=None, help='Directory to save results.')
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

    benchmarker = GuardrailsAIBenchmarker(
        config=config['guardrailsai'],
        output_dir=args.output_dir
    )
    benchmarker.run_benchmark()

if __name__ == "__main__":
    main()
