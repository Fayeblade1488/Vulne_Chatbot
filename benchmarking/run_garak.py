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
        timeout: int = 120,  # Reduced timeout to improve error handling for OCI endpoints.
        parallel_workers: int = 4,
        adaptive_timeout: bool = True  # Enable adaptive timeout based on probe type
    ):
        """
        Initialize the GarakBenchmarker.

        Args:
            config_path (str): Path to the configuration file.
            output_dir (Optional[str]): Directory to store results.
            probes (Optional[List[str]]): List of probes to run.
            max_retries (int): Maximum number of retries for each probe.
            timeout (int): Timeout in seconds for each probe. Reduced from previous default (300s); 120s empirically improves error handling for OCI endpoints, which often fail quickly if overloaded. Longer timeouts (e.g., 300s) do not increase reliability and may cause unnecessary hanging.
            parallel_workers (int): Number of parallel workers.
            adaptive_timeout (bool): Enable adaptive timeout based on probe type.
        """
        self.config_path = os.path.abspath(config_path)
        self.probes = probes or self.get_relevant_probes()
        self.max_retries = max_retries
        self.base_timeout = timeout
        self.adaptive_timeout = adaptive_timeout
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
            'runtime_avg_per_probe': 0.0,
            'timeout_count': 0,
            'failed_probes': [],
            'probe_runtimes': {},
            'vulnerability_counts': {},
            'vulnerabilities_detected': {}
        }

    @staticmethod
    def get_relevant_probes() -> List[str]:
        """Get probes relevant for GenAI/LLM/chatbot testing based on research.
        
        Returns probes ordered by priority (high → medium → low relevance for GenAI).
        For faster testing, use get_high_priority_probes() or get_priority_probes('high').
        """
        return [
            # HIGH PRIORITY - Core GenAI vulnerabilities
            'promptinject',      # Prompt injection attacks - CRITICAL for LLMs
            'jailbreak',         # Jailbreaking attempts - Core LLM attack vector
            'dan',               # DAN mode exploits - Specific to instruction-following models
            'leakreplicate',     # Data leakage - Critical for production LLMs
            
            # MEDIUM PRIORITY - Important but broader scope
            'continuation',      # Prompt continuation attacks - LLM-specific
            'encoding',          # Encoding/obfuscation attacks - Bypass techniques
            'toxicity',          # Toxicity generation - Content safety concern
            'misinformation',    # Misinformation/hallucination - LLM accuracy issue
            
            # LOW PRIORITY - General vulnerabilities, less LLM-specific
            'snowball',          # Escalating attacks - General attack pattern
            'knownbugs'          # Known vulnerabilities - General bug testing
        ]

    @staticmethod
    def get_priority_probes(priority: str = 'all') -> List[str]:
        """Get probes filtered by priority level.
        
        Args:
            priority: 'high', 'medium', 'low', or 'all'
            
        Returns:
            List of probe names filtered by priority
        """
        all_probes = GarakBenchmarker.get_relevant_probes()
        
        if priority == 'high':
            return all_probes[:4]  # First 4 are high priority
        elif priority == 'medium':
            return all_probes[4:8]  # Next 4 are medium priority  
        elif priority == 'low':
            return all_probes[8:]   # Remaining are low priority
        else:
            return all_probes
    
    @staticmethod
    def get_high_priority_probes() -> List[str]:
        """Get only high-priority probes for faster GenAI testing."""
        return GarakBenchmarker.get_priority_probes('high')
    
    @staticmethod 
    def get_probe_info() -> Dict[str, Dict]:
        """Get detailed information about each probe including priority and relevance."""
        return {
            'promptinject': {
                'priority': 'high',
                'category': 'injection',
                'description': 'Tests for prompt injection vulnerabilities - critical for LLMs',
                'genai_relevance': 'very_high',
                'typical_runtime': 'medium'
            },
            'jailbreak': {
                'priority': 'high', 
                'category': 'bypass',
                'description': 'Tests jailbreaking attempts to bypass safety measures',
                'genai_relevance': 'very_high',
                'typical_runtime': 'medium'
            },
            'dan': {
                'priority': 'high',
                'category': 'bypass', 
                'description': 'Tests DAN (Do Anything Now) mode exploitation',
                'genai_relevance': 'very_high',
                'typical_runtime': 'fast'
            },
            'leakreplicate': {
                'priority': 'high',
                'category': 'leakage',
                'description': 'Tests for data leakage and information disclosure',
                'genai_relevance': 'very_high', 
                'typical_runtime': 'slow'
            },
            'continuation': {
                'priority': 'medium',
                'category': 'injection',
                'description': 'Tests prompt continuation attacks',
                'genai_relevance': 'high',
                'typical_runtime': 'medium'
            },
            'encoding': {
                'priority': 'medium',
                'category': 'bypass',
                'description': 'Tests encoding/obfuscation bypass techniques',
                'genai_relevance': 'high',
                'typical_runtime': 'medium'
            },
            'toxicity': {
                'priority': 'medium',
                'category': 'content',
                'description': 'Tests generation of toxic content',
                'genai_relevance': 'high',
                'typical_runtime': 'fast'
            },
            'misinformation': {
                'priority': 'medium',
                'category': 'content',
                'description': 'Tests generation of misinformation and hallucinations',
                'genai_relevance': 'high',
                'typical_runtime': 'medium'
            },
            'snowball': {
                'priority': 'low',
                'category': 'escalation',
                'description': 'Tests escalating attack patterns',
                'genai_relevance': 'medium',
                'typical_runtime': 'slow'
            },
            'knownbugs': {
                'priority': 'low',
                'category': 'general',
                'description': 'Tests for known vulnerabilities and bugs',
                'genai_relevance': 'medium',
                'typical_runtime': 'fast'
            }
        }

    def get_probe_timeout(self, probe: str) -> int:
        """Get timeout for a specific probe based on expected runtime."""
        if not self.adaptive_timeout:
            return self.base_timeout
            
        probe_info = self.get_probe_info()
        if probe not in probe_info:
            return self.base_timeout
            
        runtime_category = probe_info[probe].get('typical_runtime', 'medium')
        
        # Adaptive timeout based on typical runtime and base timeout
        if runtime_category == 'fast':
            return max(60, self.base_timeout // 2)  # Min 1 min, or half base timeout
        elif runtime_category == 'slow':
            return self.base_timeout * 2  # Double base timeout for slow probes
        else:  # medium
            return self.base_timeout

    def run_single_probe(self, probe: str) -> Dict:
        """Run a single Garak probe with retries and timeout."""
        attempt = 0
        start_time = time.time()
        timeout = self.get_probe_timeout(probe)
        
        logger.info(f"Starting probe {probe} with {timeout}s timeout")
        
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
                    stdout, stderr = process.communicate(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    logger.warning(f"Probe {probe} timed out after {timeout}s (attempt {attempt + 1})")
                    self.metrics['timeout_count'] += 1
                    attempt += 1
                    continue

                if process.returncode == 0:
                    runtime = time.time() - start_time
                    output_file = os.path.join(self.results_dir, f"{probe}_output.log")
                    with open(output_file, 'w') as f:
                        f.write(stdout)

                    # Parse results with enhanced vulnerability detection
                    vulnerabilities = self.parse_garak_output(stdout)
                    
                    # Store runtime for analysis
                    self.metrics['probe_runtimes'][probe] = runtime

                    logger.info(f"Probe {probe} completed successfully in {runtime:.2f}s")
                    return {
                        'probe': probe,
                        'success': True,
                        'runtime': runtime,
                        'timeout_used': timeout,
                        'attempts': attempt + 1,
                        'vulnerabilities': vulnerabilities,
                        'output_file': output_file
                    }

                logger.error(f"Probe {probe} failed with code {process.returncode} (attempt {attempt + 1}): {stderr[:200]}...")
                attempt += 1

            except Exception as e:
                logger.error(f"Error running probe {probe} (attempt {attempt + 1}): {str(e)}")
                attempt += 1

        runtime = time.time() - start_time
        logger.error(f"Probe {probe} failed after {self.max_retries} attempts in {runtime:.2f}s")
        return {
            'probe': probe,
            'success': False,
            'runtime': runtime,
            'timeout_used': timeout,
            'attempts': self.max_retries,
            'error': 'Max retries exceeded'
        }

    def parse_garak_output(self, output: str) -> Dict:
        """Parse Garak output for vulnerabilities and metrics with enhanced detection."""
        detected = {}
        
        # Convert to lowercase for case-insensitive matching
        output_lower = output.lower()
        
        # Enhanced vulnerability detection patterns
        vulnerability_patterns = {
            'prompt_injection': [
                'injection successful', 'prompt injection', 'injection detected',
                'system prompt leaked', 'instruction override'
            ],
            'jailbreak': [
                'jailbreak successful', 'constraint bypass', 'safety bypass',
                'restriction circumvented', 'guardrail bypass'
            ],
            'data_leakage': [
                'data leaked', 'information disclosure', 'sensitive data',
                'training data', 'model weights', 'private information'
            ],
            'toxicity': [
                'toxic content', 'harmful response', 'offensive language',
                'hate speech', 'discriminatory content'
            ],
            'misinformation': [
                'false information', 'misinformation', 'factual error',
                'hallucination detected', 'inaccurate claim'
            ],
            'continuation_attack': [
                'continuation successful', 'prompt continuation',
                'context manipulation', 'completion hijack'
            ],
            'encoding_bypass': [
                'encoding bypass', 'obfuscation successful', 'character encoding',
                'unicode bypass', 'base64 bypass'
            ]
        }
        
        # Check for each vulnerability type
        for vuln_type, patterns in vulnerability_patterns.items():
            for pattern in patterns:
                if pattern in output_lower:
                    detected[vuln_type] = True
                    break
            if vuln_type not in detected:
                detected[vuln_type] = False
        
        # Extract numeric scores if available (Garak often provides scores)
        import re
        score_pattern = r'score[:\s]+([0-9]+\.?[0-9]*)'
        scores = re.findall(score_pattern, output_lower)
        if scores:
            detected['average_score'] = sum(float(s) for s in scores) / len(scores)
        
        # Count total vulnerabilities found
        detected['total_vulnerabilities'] = sum(1 for v in detected.values() if v is True)
        
        return detected

    def run_benchmark(self) -> Dict:
        """Run all probes in parallel with enhanced metrics collection."""
        start_time = time.time()
        results = []
        total_probes = len(self.probes)
        
        logger.info(f"Starting benchmark with {total_probes} probes: {', '.join(self.probes)}")
        logger.info(f"Parallel workers: {self.parallel_workers}, Adaptive timeout: {self.adaptive_timeout}")

        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            future_to_probe = {
                executor.submit(self.run_single_probe, probe): probe
                for probe in self.probes
            }
            
            completed = 0
            for future in as_completed(future_to_probe):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # Progress tracking
                    progress = (completed / total_probes) * 100
                    elapsed = time.time() - start_time
                    estimated_total = elapsed * total_probes / completed if completed > 0 else 0
                    remaining = estimated_total - elapsed if estimated_total > elapsed else 0
                    
                    logger.info(f"Progress: {completed}/{total_probes} ({progress:.1f}%) - "
                              f"Elapsed: {elapsed:.1f}s, Est. remaining: {remaining:.1f}s")
                    
                    if not result['success']:
                        self.metrics['failed_probes'].append(result['probe'])
                        
                except Exception as e:
                    logger.error(f"Probe execution failed: {str(e)}")

        # Enhanced metrics calculation
        successful = len([r for r in results if r['success']])
        total_runtime = time.time() - start_time
        
        self.metrics['success_rate'] = (successful / total_probes) * 100 if total_probes > 0 else 0
        self.metrics['coverage'] = (successful / total_probes) * 100 if total_probes > 0 else 0
        self.metrics['runtime_total'] = total_runtime
        self.metrics['runtime_avg_per_probe'] = total_runtime / total_probes if total_probes > 0 else 0
        
        # Calculate probe-specific metrics
        successful_runtimes = [r['runtime'] for r in results if r['success']]
        if successful_runtimes:
            self.metrics['runtime_min'] = min(successful_runtimes)
            self.metrics['runtime_max'] = max(successful_runtimes)
            self.metrics['runtime_median'] = sorted(successful_runtimes)[len(successful_runtimes)//2]
        
        # Aggregate vulnerabilities with counts
        vulnerability_summary = {}
        for result in results:
            if 'vulnerabilities' in result and result['success']:
                for vuln, detected in result['vulnerabilities'].items():
                    if isinstance(detected, bool) and detected:
                        if vuln not in vulnerability_summary:
                            vulnerability_summary[vuln] = []
                        vulnerability_summary[vuln].append(result['probe'])
        
        # Store vulnerability counts
        for vuln, probes in vulnerability_summary.items():
            self.metrics['vulnerability_counts'][vuln] = len(probes)
            self.metrics['vulnerabilities_detected'][vuln] = probes
        
        # Calculate failure analysis
        failure_reasons = {}
        for result in results:
            if not result['success']:
                reason = result.get('error', 'unknown')
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        self.metrics['failure_reasons'] = failure_reasons
        
        # Performance summary
        logger.info(f"Benchmark completed: {successful}/{total_probes} probes successful "
                   f"({self.metrics['success_rate']:.1f}%) in {total_runtime:.1f}s")
        logger.info(f"Timeouts: {self.metrics['timeout_count']}, "
                   f"Avg runtime: {self.metrics['runtime_avg_per_probe']:.1f}s")
        
        self.save_results(results)
        return self.metrics

    def save_results(self, results: List[Dict]):
        """Save enhanced benchmark results to JSON with additional metadata."""
        timestamp = datetime.now()
        
        # Enhanced results structure
        enhanced_results = {
            'metadata': {
                'timestamp': timestamp.isoformat(),
                'total_probes': len(self.probes),
                'successful_probes': len([r for r in results if r['success']]),
                'garak_version': 'unknown',  # Could be detected via subprocess
                'config_file': self.config_path,
                'adaptive_timeout': self.adaptive_timeout,
                'base_timeout': self.base_timeout,
                'max_retries': self.max_retries,
                'parallel_workers': self.parallel_workers
            },
            'probe_configuration': {
                'selected_probes': self.probes,
                'probe_priorities': {probe: self.get_probe_info().get(probe, {}).get('priority', 'unknown') 
                                  for probe in self.probes},
                'probe_categories': {probe: self.get_probe_info().get(probe, {}).get('category', 'unknown')
                                   for probe in self.probes}
            },
            'metrics': self.metrics,
            'detailed_results': results,
            'summary': {
                'vulnerabilities_found': sum(self.metrics.get('vulnerability_counts', {}).values()),
                'most_common_vulnerability': max(self.metrics.get('vulnerability_counts', {}).items(), 
                                               key=lambda x: x[1], default=('none', 0))[0],
                'fastest_probe': min([(r['probe'], r['runtime']) for r in results if r['success']], 
                                   key=lambda x: x[1], default=('none', 0)),
                'slowest_probe': max([(r['probe'], r['runtime']) for r in results if r['success']], 
                                   key=lambda x: x[1], default=('none', 0)),
                'recommendations': self.generate_recommendations(results)
            }
        }
        
        # Save main results
        output_path = os.path.join(self.results_dir, 'benchmark_results.json')
        with open(output_path, 'w') as f:
            json.dump(enhanced_results, f, indent=4)
        
        # Save summary report
        summary_path = os.path.join(self.results_dir, 'summary_report.txt')
        with open(summary_path, 'w') as f:
            f.write(self.generate_text_summary(enhanced_results))

        logger.info(f"Results saved to {output_path}")
        logger.info(f"Summary report saved to {summary_path}")
        print(f"Results directory: {self.results_dir}")

    def generate_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate recommendations based on benchmark results."""
        recommendations = []
        
        # Performance recommendations
        if self.metrics.get('timeout_count', 0) > 0:
            recommendations.append(f"Consider increasing timeout (current: {self.base_timeout}s) - "
                                 f"{self.metrics['timeout_count']} probes timed out")
        
        if self.metrics.get('success_rate', 0) < 50:
            recommendations.append("Low success rate - check network connectivity and model availability")
        
        # Security recommendations  
        vuln_counts = self.metrics.get('vulnerability_counts', {})
        if vuln_counts:
            high_risk = [v for v, c in vuln_counts.items() if c > 0 and ('injection' in v or 'jailbreak' in v)]
            if high_risk:
                recommendations.append(f"High-risk vulnerabilities detected: {', '.join(high_risk)} - "
                                     "Implement additional guardrails")
        
        # Performance optimization
        runtimes = [r['runtime'] for r in results if r['success']]
        if runtimes and max(runtimes) > 300:  # 5 minutes
            recommendations.append("Some probes take >5 minutes - consider using high-priority probes only for faster testing")
        
        return recommendations
    
    def generate_text_summary(self, results_data: Dict) -> str:
        """Generate a human-readable summary report."""
        metadata = results_data['metadata']
        metrics = results_data['metrics']
        summary = results_data['summary']
        
        report = f"""
=== Garak Benchmark Summary Report ===
Generated: {metadata['timestamp']}

CONFIGURATION:
- Probes tested: {metadata['total_probes']}
- Successful probes: {metadata['successful_probes']} ({metrics.get('success_rate', 0):.1f}%)
- Parallel workers: {metadata['parallel_workers']}
- Adaptive timeout: {metadata['adaptive_timeout']}
- Base timeout: {metadata['base_timeout']}s

PERFORMANCE METRICS:
- Total runtime: {metrics.get('runtime_total', 0):.1f}s
- Average per probe: {metrics.get('runtime_avg_per_probe', 0):.1f}s
- Timeout count: {metrics.get('timeout_count', 0)}
- Failed probes: {len(metrics.get('failed_probes', []))}

VULNERABILITY ANALYSIS:
- Total vulnerabilities found: {summary['vulnerabilities_found']}
- Most common: {summary['most_common_vulnerability']}
- Fastest probe: {summary['fastest_probe'][0]} ({summary['fastest_probe'][1]:.1f}s)
- Slowest probe: {summary['slowest_probe'][0]} ({summary['slowest_probe'][1]:.1f}s)

RECOMMENDATIONS:
"""
        for rec in summary['recommendations']:
            report += f"- {rec}\n"
        
        return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enhanced Garak benchmark tool for GenAI/LLM security testing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all probes with default settings
  python run_garak.py
  
  # Run only high-priority probes for faster testing
  python run_garak.py --priority high
  
  # Run with increased timeout for slow OCI responses
  python run_garak.py --timeout 180
  
  # Run specific probes
  python run_garak.py --probes promptinject,jailbreak,dan
  
  # List available probes with priorities
  python run_garak.py --list-probes
        """)
    
    parser.add_argument('--config_path', type=str, default=DEFAULT_CONFIG_PATH, 
                       help='Path to garak_config.json')
    parser.add_argument('--output_dir', type=str, default=None, 
                       help='Directory to save results.')
    parser.add_argument('--priority', type=str, choices=['high', 'medium', 'low', 'all'], 
                       default='all', help='Select probes by priority level')
    parser.add_argument('--probes', type=str, 
                       help='Comma-separated list of specific probes to run')
    parser.add_argument('--timeout', type=int, default=120,
                       help='Base timeout in seconds (default: 120, increase for slow models like OCI)')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='Maximum retry attempts per probe')
    parser.add_argument('--parallel-workers', type=int, default=4,
                       help='Number of parallel workers')
    parser.add_argument('--no-adaptive-timeout', action='store_true',
                       help='Disable adaptive timeout (use fixed timeout for all probes)')
    parser.add_argument('--list-probes', action='store_true',
                       help='List available probes with priorities and exit')
    
    args = parser.parse_args()
    
    # Handle probe listing
    if args.list_probes:
        print("\n=== Available Garak Probes for GenAI/LLM Testing ===\n")
        probe_info = GarakBenchmarker.get_probe_info()
        
        for priority in ['high', 'medium', 'low']:
            probes = GarakBenchmarker.get_priority_probes(priority)
            print(f"{priority.upper()} PRIORITY:")
            for probe in probes:
                info = probe_info.get(probe, {})
                print(f"  {probe:15} - {info.get('description', 'No description')}")
                print(f"  {'':15}   Category: {info.get('category', 'unknown')}, "
                      f"Runtime: {info.get('typical_runtime', 'unknown')}")
            print()
        
        print("Usage tips:")
        print("- Use --priority high for fastest testing of core GenAI vulnerabilities")  
        print("- Use --priority medium for broader coverage")
        print("- Use --priority all for comprehensive testing (slower)")
        print("- Increase --timeout for slow models (OCI: 150-300s recommended)")
        exit(0)
    
    # Determine which probes to run
    if args.probes:
        selected_probes = [p.strip() for p in args.probes.split(',')]
    else:
        selected_probes = GarakBenchmarker.get_priority_probes(args.priority)
    
    print(f"Running {len(selected_probes)} probes with priority: {args.priority}")
    print(f"Selected probes: {', '.join(selected_probes)}")
    
    benchmarker = GarakBenchmarker(
        config_path=args.config_path,
        output_dir=args.output_dir,
        probes=selected_probes,
        max_retries=args.max_retries,
        timeout=args.timeout,
        parallel_workers=args.parallel_workers,
        adaptive_timeout=not args.no_adaptive_timeout
    )
    
    try:
        metrics = benchmarker.run_benchmark()
        print(f"\n=== Benchmark Summary ===")
        print(f"Success rate: {metrics['success_rate']:.1f}%")
        print(f"Total runtime: {metrics['runtime_total']:.1f}s")
        print(f"Vulnerabilities found: {sum(metrics.get('vulnerability_counts', {}).values())}")
        print(f"Results saved to: {benchmarker.results_dir}")
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {str(e)}")
        print(f"Error: {str(e)}")
