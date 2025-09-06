#!/usr/bin/env python3
"""
Improved Garak Probe Runner
Handles ANSI codes, implements retry logic, and generates comprehensive reports
"""

import subprocess
import json
import re
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('garak_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GarakProbeRunner:
    """Enhanced Garak probe runner with retry logic and reporting"""
    
    def __init__(self, config_path: str = "configs/garak/garak_config.json"):
        self.config_path = Path(config_path)
        self.results_dir = Path("data/results/garak_probes")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def clean_ansi_codes(self, text: str) -> str:
        """Remove ANSI escape codes from text"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
        
    def get_probe_list(self) -> List[str]:
        """Get list of available probes, handling ANSI codes"""
        try:
            logger.info("Fetching available Garak probes...")
            result = subprocess.run(
                ['garak', '--list_probes'],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            # Clean ANSI codes
            clean_output = self.clean_ansi_codes(result.stdout)
            
            # Parse probe names - adjust pattern based on actual output format
            probes = []
            lines = clean_output.split('\n')
            
            for line in lines:
                line = line.strip()
                # Skip empty lines and headers
                if not line or line.startswith(('Available', 'Probes:', '=', '-')):
                    continue
                    
                # Extract probe names (format: probe.name or just probename)
                # Adjust this pattern based on your Garak version's output
                if '.' in line:
                    probe_name = line.split()[0] if line else ''
                    if probe_name and not probe_name.startswith('#'):
                        probes.append(probe_name)
                        
            logger.info(f"Found {len(probes)} probes")
            return probes
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout while fetching probe list")
            return []
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get probe list: {e}")
            logger.error(f"stderr: {e.stderr}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting probe list: {e}")
            return []
    
    def run_single_probe(self, probe: str, retry: bool = True) -> Dict:
        """Run a single probe with optional retry"""
        logger.info(f"Running probe: {probe}")
        
        cmd = [
            'garak',
            '--model_type', 'rest',
            '--model_name', 'vulnerable_chatbot',
            '--generator_option_file', str(self.config_path),
            '--probes', probe,
            '--verbose'
        ]
        
        max_attempts = 2 if retry else 1
        
        for attempt in range(max_attempts):
            try:
                start_time = time.time()
                
                # Run the probe
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per probe
                )
                
                runtime = time.time() - start_time
                
                # Check if successful
                if result.returncode == 0:
                    logger.info(f"✓ Probe {probe} completed in {runtime:.2f}s")
                    
                    # Save output
                    output_file = self.results_dir / f"{probe.replace('.', '_')}_{self.timestamp}.txt"
                    with open(output_file, 'w') as f:
                        f.write(f"=== STDOUT ===\n{result.stdout}\n")
                        f.write(f"\n=== STDERR ===\n{result.stderr}\n")
                    
                    return {
                        'probe': probe,
                        'success': True,
                        'runtime': runtime,
                        'attempt': attempt + 1,
                        'output_file': str(output_file),
                        'returncode': result.returncode
                    }
                else:
                    logger.warning(f"✗ Probe {probe} failed with code {result.returncode} (attempt {attempt + 1}/{max_attempts})")
                    
                    if attempt < max_attempts - 1:
                        logger.info(f"  Retrying {probe} in 5 seconds...")
                        time.sleep(5)
                    
            except subprocess.TimeoutExpired:
                logger.error(f"✗ Probe {probe} timed out (attempt {attempt + 1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    logger.info(f"  Retrying {probe}...")
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"✗ Probe {probe} error: {e}")
                
        # If we get here, all attempts failed
        return {
            'probe': probe,
            'success': False,
            'error': 'Failed after all retry attempts',
            'attempts': max_attempts
        }
    
    def run_all_probes(self, probes: Optional[List[str]] = None, skip_list: Optional[List[str]] = None):
        """Run all probes or a specific list"""
        if probes is None:
            probes = self.get_probe_list()
            
        if not probes:
            logger.error("No probes to run")
            return None
            
        # Apply skip list if provided
        if skip_list:
            probes = [p for p in probes if p not in skip_list]
            logger.info(f"Skipping {len(skip_list)} probes")
            
        logger.info(f"Starting to run {len(probes)} probes")
        logger.info("=" * 60)
        
        results = []
        successful = 0
        failed = 0
        
        for i, probe in enumerate(probes, 1):
            logger.info(f"\n[{i}/{len(probes)}] Processing: {probe}")
            result = self.run_single_probe(probe)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
                
            # Show progress
            logger.info(f"Progress: {i}/{len(probes)} | Success: {successful} | Failed: {failed}")
            
        # Generate and save summary
        summary = self.generate_summary(results)
        self.save_results(results, summary)
        
        return summary
    
    def generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics"""
        total = len(results)
        successful = len([r for r in results if r['success']])
        failed = total - successful
        
        total_runtime = sum(r.get('runtime', 0) for r in results if r.get('runtime'))
        avg_runtime = total_runtime / successful if successful > 0 else 0
        
        failed_probes = [r['probe'] for r in results if not r['success']]
        
        summary = {
            'timestamp': self.timestamp,
            'total_probes': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'total_runtime': total_runtime,
            'average_runtime': avg_runtime,
            'failed_probes': failed_probes
        }
        
        return summary
    
    def save_results(self, results: List[Dict], summary: Dict):
        """Save results and summary to JSON files"""
        # Save detailed results
        results_file = self.results_dir / f'results_{self.timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump({
                'summary': summary,
                'results': results
            }, f, indent=2)
            
        # Save summary separately for quick access
        summary_file = self.results_dir / f'summary_{self.timestamp}.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Update latest summary link
        latest_file = self.results_dir / 'latest_summary.json'
        with open(latest_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        logger.info(f"\nResults saved to: {results_file}")
        logger.info(f"Summary saved to: {summary_file}")
        
        # Print summary to console
        self.print_summary(summary)
    
    def print_summary(self, summary: Dict):
        """Print formatted summary to console"""
        logger.info("\n" + "=" * 60)
        logger.info("BENCHMARK SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Probes:    {summary['total_probes']}")
        logger.info(f"Successful:      {summary['successful']}")
        logger.info(f"Failed:          {summary['failed']}")
        logger.info(f"Success Rate:    {summary['success_rate']:.1f}%")
        logger.info(f"Total Runtime:   {summary['total_runtime']:.2f}s")
        logger.info(f"Average Runtime: {summary['average_runtime']:.2f}s")
        
        if summary['failed_probes']:
            logger.warning("\nFailed Probes:")
            for probe in summary['failed_probes']:
                logger.warning(f"  - {probe}")
        
        logger.info("=" * 60)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Garak security probes')
    parser.add_argument('--config', default='configs/garak/garak_config.json',
                        help='Path to Garak config file')
    parser.add_argument('--probes', nargs='+', help='Specific probes to run')
    parser.add_argument('--skip', nargs='+', help='Probes to skip')
    parser.add_argument('--list', action='store_true', help='List available probes and exit')
    
    args = parser.parse_args()
    
    runner = GarakProbeRunner(config_path=args.config)
    
    if args.list:
        probes = runner.get_probe_list()
        print("\nAvailable Probes:")
        for probe in probes:
            print(f"  - {probe}")
        sys.exit(0)
    
    # Run probes
    runner.run_all_probes(probes=args.probes, skip_list=args.skip)

if __name__ == "__main__":
    main()
