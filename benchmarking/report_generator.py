import json
import os
import matplotlib.pyplot as plt
from datetime import datetime
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, results_dirs: dict):
        self.results = {}
        for tool, dir_path in results_dirs.items():
            if dir_path and os.path.isdir(dir_path):
                self.results[tool] = self.load_results(dir_path)
            else:
                logger.warning(f"Directory not found for {tool}: {dir_path}")
                self.results[tool] = {}

        self.output_dir = f"benchmark_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)

    def load_results(self, dir_path: str) -> dict:
        """Load JSON results from directory."""
        results_file = next((f for f in os.listdir(dir_path) if f.endswith('_results.json')), None)
        if not results_file:
            logger.warning(f"No results file found in {dir_path}")
            return {}

        with open(os.path.join(dir_path, results_file), 'r') as f:
            return json.load(f)

    def generate_summary_report(self) -> str:
        """Generate markdown summary report."""
        report = "# GenAI Security Benchmarking Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        for tool, data in self.results.items():
            report += f"## {tool.capitalize()} Metrics\n"
            if not data:
                report += "No data available\n"
                continue

            metrics = data.get('metrics', {})
            report += f"- Success Rate: {metrics.get('success_rate', 0):.2f}%\n"
            report += f"- Coverage: {metrics.get('coverage', 0):.2f}%\n"
            report += f"- Total Runtime: {metrics.get('runtime_total', 0):.2f}s\n"
            report += f"- Detected Vulnerabilities: {json.dumps(metrics.get('vulnerabilities_detected', {}), indent=2)}\n\n"

        output_path = os.path.join(self.output_dir, 'summary_report.md')
        with open(output_path, 'w') as f:
            f.write(report)

        logger.info(f"Summary report saved to {output_path}")
        return output_path

    def generate_visualizations(self):
        """Generate metric visualizations."""
        fig, ax = plt.subplots(figsize=(10, 6))

        tools = [tool for tool, data in self.results.items() if data]
        runtimes = [self.results[t].get('metrics', {}).get('runtime_total', 0) for t in tools]

        if not runtimes:
            logger.warning("No data available to generate runtime comparison chart.")
            return

        ax.bar(tools, runtimes)
        ax.set_title('Benchmark Runtime Comparison')
        ax.set_ylabel('Seconds')
        ax.set_xlabel('Tools')

        path = os.path.join(self.output_dir, 'runtime_comparison.png')
        plt.savefig(path)
        plt.close()

        logger.info(f"Visualizations generated at {path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate benchmark reports.")
    parser.add_argument(
        '--results',
        nargs=2,
        action='append',
        metavar=('TOOL_NAME', 'DIRECTORY_PATH'),
        help='The tool name and the path to its results directory. Can be specified multiple times.'
    )

    args = parser.parse_args()

    results_dirs = {tool: path for tool, path in args.results} if args.results else {}

    if not results_dirs:
        logger.error("No result directories provided. Use the --results argument.")
    else:
        generator = ReportGenerator(results_dirs)
        generator.generate_summary_report()
        generator.generate_visualizations()
