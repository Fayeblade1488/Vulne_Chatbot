import json
import os
import matplotlib.pyplot as plt
from datetime import datetime
import logging
import argparse
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, results_dirs: dict, output_dir: str = None):
        self.results = {}
        for tool, dir_path in results_dirs.items():
            self.results[tool] = self.load_results(dir_path)

        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = f"benchmark_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)

    def load_results(self, dir_path: str) -> Optional[Dict]:
        """Load JSON results from a directory."""
        if not dir_path or not os.path.isdir(dir_path):
            logger.warning(f"Results directory not found or invalid: {dir_path}")
            return None

        results_file = next((f for f in os.listdir(dir_path) if f.endswith('_results.json') or f == 'benchmark_results.json'), None)
        if not results_file:
            logger.warning(f"No results file found in {dir_path}")
            return None

        try:
            with open(os.path.join(dir_path, results_file), 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading results from {results_file}: {e}")
            return None

    def generate_summary_report(self) -> Optional[str]:
        """Generate a markdown summary report."""
        report = "# GenAI Security Benchmarking Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        for tool, data in self.results.items():
            report += f"## {tool.capitalize()} Metrics\n"
            if not data or 'metrics' not in data:
                report += "No data available\n\n"
                continue

            metrics = data['metrics']
            report += f"- **Success/Completion Rate**: {metrics.get('success_rate', metrics.get('block_rate', metrics.get('validation_rate', 0.0))):.2f}%\n"
            report += f"- **Total Runtime**: {metrics.get('runtime_total', 0):.2f}s\n"
            report += f"- **Average Runtime**: {metrics.get('runtime_avg', 0):.2f}s\n"

            if 'vulnerabilities_detected' in metrics:
                report += f"- **Detected Vulnerabilities**: {json.dumps(metrics.get('vulnerabilities_detected', {}), indent=2)}\n\n"
            if 'detected_issues' in metrics:
                report += f"- **Detected Issues**: {json.dumps(metrics.get('detected_issues', {}), indent=2)}\n\n"

        try:
            output_path = os.path.join(self.output_dir, 'summary_report.md')
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"Summary report saved to {output_path}")
            return output_path
        except IOError as e:
            logger.error(f"Error saving summary report: {e}")
            return None

    def generate_visualizations(self):
        """Generate metric visualizations."""
        if not self.results:
            logger.warning("No results to visualize.")
            return

        # Runtime Comparison
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            tools = [k for k, v in self.results.items() if v]
            runtimes = [self.results[t]['metrics'].get('runtime_total', 0) for t in tools]

            ax.bar(tools, runtimes, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            ax.set_title('Benchmark Runtime Comparison', fontsize=16)
            ax.set_ylabel('Total Runtime (Seconds)', fontsize=12)
            ax.set_xlabel('Benchmarking Tools', fontsize=12)

            img_path = os.path.join(self.output_dir, 'runtime_comparison.png')
            plt.savefig(img_path)
            plt.close()
            logger.info(f"Runtime comparison chart saved to {img_path}")
        except Exception as e:
            logger.error(f"Failed to generate runtime visualization: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate benchmark reports.")
    parser.add_argument('results_dirs', type=str, help="A JSON string mapping tools to their results directories.")
    parser.add_argument('--output-dir', type=str, help="Directory to save the report and visualizations.")
    args = parser.parse_args()

    try:
        results_dirs_dict = json.loads(args.results_dirs)
    except json.JSONDecodeError:
        logger.error("Invalid JSON string for results directories.")
        sys.exit(1)

    generator = ReportGenerator(results_dirs_dict, args.output_dir)
    generator.generate_summary_report()
    generator.generate_visualizations()
