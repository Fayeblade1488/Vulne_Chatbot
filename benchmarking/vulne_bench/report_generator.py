import json
import os
import matplotlib.pyplot as plt
from datetime import datetime
import logging
import argparse

# For trend analysis
import numpy as np
from typing import Dict, List, Any

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

    def load_results(self, dir_path: str) -> dict:
        """Load JSON results from a directory."""
        if not dir_path or not os.path.isdir(dir_path):
            logger.warning(f"Results directory not found or invalid: {dir_path}")
            return {}
            
        results_file = next((f for f in os.listdir(dir_path) if f.endswith('_results.json') or f == 'benchmark_results.json'), None)
        if not results_file:
            logger.warning(f"No results file found in {dir_path}")
            return {}
        
        try:
            with open(os.path.join(dir_path, results_file), 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading results from {results_file}: {e}")
            return {}

    def calculate_trends(self) -> Dict[str, Any]:
        """Calculate trends across tools and metrics."""
        trends = {}
        
        # For now, we'll just return basic trend information
        # In a more advanced implementation, this would analyze historical data
        trends['tools_compared'] = list(self.results.keys())
        
        # Calculate performance trends
        performance_trends = {}
        for tool, data in self.results.items():
            if data and 'metrics' in data:
                metrics = data['metrics']
                performance_trends[tool] = {
                    'success_rate': metrics.get('success_rate', 0),
                    'runtime_total': metrics.get('runtime_total', 0),
                    'precision': metrics.get('precision', 0),
                    'recall': metrics.get('recall', 0)
                }
        
        trends['performance'] = performance_trends
        return trends

    def estimate_costs(self) -> Dict[str, Any]:
        """Estimate costs for cloud-based model usage."""
        costs = {}
        
        # Basic cost estimation - in a real implementation, this would be more sophisticated
        # and based on actual model pricing
        for tool, data in self.results.items():
            if data and 'detailed_results' in data:
                # Estimate based on number of probes/tests run
                num_tests = len(data['detailed_results'])
                # Rough estimate: $0.001 per test (this would be model-specific)
                estimated_cost = num_tests * 0.001
                costs[tool] = {
                    'estimated_cost': round(estimated_cost, 4),
                    'num_tests': num_tests,
                    'cost_per_test': 0.001
                }
        
        return costs

    def generate_summary_report(self) -> str:
        """Generate a detailed markdown summary report."""
        report = "# GenAI Security Benchmarking Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"
        
        # Add trend analysis
        trends = self.calculate_trends()
        report += "## Trend Analysis\n\n"
        report += "This report compares the performance of different security tools against the Vulne_Chatbot platform.\n\n"
        
        # Add cost estimation
        costs = self.estimate_costs()
        if costs:
            report += "## Cost Estimation\n\n"
            report += "| Tool | Estimated Cost (USD) | Number of Tests | Cost per Test |\n"
            report += "|------|---------------------|----------------|---------------|\n"
            for tool, cost_data in costs.items():
                report += f"| {tool.capitalize()} | ${cost_data['estimated_cost']:.4f} | {cost_data['num_tests']} | ${cost_data['cost_per_test']:.4f} |\n"
            report += "\n\n"
        
        report += "## Overall Summary\n\n"
        report += "| Tool | Success/Block Rate | Avg Runtime (s) | Total Runtime (s) | Vulnerabilities Detected |\n"
        report += "|------|--------------------|-----------------|-------------------|--------------------------|\n"

        for tool, data in self.results.items():
            if not data or 'metrics' not in data:
                continue
            metrics = data['metrics']
            rate = metrics.get('success_rate', metrics.get('block_rate', metrics.get('validation_rate', 0.0)))
            avg_runtime = metrics.get('runtime_avg', 0.0)
            total_runtime = metrics.get('runtime_total', 0.0)
            vulns = len(metrics.get('vulnerabilities_detected', metrics.get('detected_issues', {})))
            report += f"| {tool.capitalize()} | {rate:.2f}% | {avg_runtime:.2f} | {total_runtime:.2f} | {vulns} |\n"
        
        report += "\n\n---\n"

        for tool, data in self.results.items():
            report += f"## {tool.capitalize()} Detailed Metrics\n"
            if not data or 'metrics' not in data:
                report += "No data available\n\n"
                continue
                
            metrics = data['metrics']
            report += f"- **Total Runtime**: {metrics.get('runtime_total', 0):.2f}s\n"
            report += f"- **Average Runtime**: {metrics.get('runtime_avg', 0):.2f}s per test\n"
            
            if 'success_rate' in metrics:
                report += f"- **Success Rate**: {metrics.get('success_rate', 0):.2f}%\n"
            if 'block_rate' in metrics:
                report += f"- **Block Rate**: {metrics.get('block_rate', 0):.2f}%\n"
            if 'validation_rate' in metrics:
                report += f"- **Validation Rate**: {metrics.get('validation_rate', 0):.2f}%\n"
            if 'false_positive_rate' in metrics:
                report += f"- **False Positive Rate**: {metrics.get('false_positive_rate', 0):.2f}%\n"
            if 'precision' in metrics:
                report += f"- **Precision**: {metrics.get('precision', 0):.2f}\n"
            if 'recall' in metrics:
                report += f"- **Recall**: {metrics.get('recall', 0):.2f}\n"
            
            # Add resource usage if available
            if 'resource_usage' in metrics:
                resource_usage = metrics['resource_usage']
                report += f"- **Average CPU Usage**: {resource_usage.get('avg_cpu_percent', 0):.2f}%\n"
                report += f"- **Peak CPU Usage**: {resource_usage.get('max_cpu_percent', 0):.2f}%\n"
                report += f"- **Average Memory Usage**: {resource_usage.get('avg_memory_percent', 0):.2f}%\n"
                report += f"- **Peak Memory Usage**: {resource_usage.get('max_memory_percent', 0):.2f}%\n"
            
            # Add cache statistics if available
            if 'cache_hits' in metrics and 'cache_misses' in metrics:
                total = metrics['cache_hits'] + metrics['cache_misses']
                hit_rate = (metrics['cache_hits'] / total) * 100 if total > 0 else 0
                report += f"- **Cache Hit Rate**: {hit_rate:.2f}% ({metrics['cache_hits']}/{total})\n"

            vulns = metrics.get('vulnerabilities_detected', metrics.get('detected_issues', {}))
            if vulns:
                report += "\n**Detected Vulnerabilities/Issues:**\n"
                report += "```json\n" + json.dumps(vulns, indent=2) + "\n```\n"

            failed = metrics.get('failed_probes', metrics.get('failed_tests', []))
            if failed:
                report += "\n**Failed Probes/Tests:**\n"
                for f in failed:
                    report += f"- `{f}`\n"
            report += "\n"

        output_path = os.path.join(self.output_dir, 'summary_report.md')
        with open(output_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Summary report saved to {output_path}")
        return output_path

    def generate_visualizations(self):
        """Generate metric visualizations."""
        if not self.results:
            logger.warning("No results to visualize.")
            return

        # Runtime Comparison Chart
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

        # Vulnerability Detection Chart
        try:
            all_vulns = {}
            for tool, data in self.results.items():
                if data and 'metrics' in data:
                    vulns = data['metrics'].get('vulnerabilities_detected', data['metrics'].get('detected_issues', {}))
                    for vuln, count in vulns.items():
                        if vuln not in all_vulns:
                            all_vulns[vuln] = {t: 0 for t in self.results.keys()}
                        all_vulns[vuln][tool] = count
            
            if all_vulns:
                vuln_names = list(all_vulns.keys())
                tool_names = list(self.results.keys())
                data = [[all_vulns[v][t] for t in tool_names] for v in vuln_names]

                fig, ax = plt.subplots(figsize=(12, 8))
                bar_width = 0.2
                index = range(len(tool_names))

                for i, vuln_name in enumerate(vuln_names):
                    ax.bar([x + i * bar_width for x in index], [d[i] for d in data], bar_width, label=vuln_name)

                ax.set_xlabel('Tools', fontsize=12)
                ax.set_ylabel('Count', fontsize=12)
                ax.set_title('Detected Vulnerabilities by Tool', fontsize=16)
                ax.set_xticks([i + bar_width for i in index])
                ax.set_xticklabels(tool_names)
                ax.legend()

                img_path = os.path.join(self.output_dir, 'vulnerability_comparison.png')
                plt.savefig(img_path)
                plt.close()
                logger.info(f"Vulnerability comparison chart saved to {img_path}")

        except Exception as e:
            logger.error(f"Failed to generate vulnerability visualization: {e}")

        # Performance Metrics Radar Chart
        try:
            tools = [k for k, v in self.results.items() if v and 'metrics' in v]
            if tools:
                # Prepare data for radar chart
                metrics_data = {}
                for tool in tools:
                    metrics = self.results[tool]['metrics']
                    metrics_data[tool] = {
                        'success_rate': metrics.get('success_rate', 0),
                        'precision': metrics.get('precision', 0) * 100,  # Scale to 0-100
                        'recall': metrics.get('recall', 0) * 100,      # Scale to 0-100
                        'efficiency': 100 - min(metrics.get('runtime_total', 0) / 10, 100)  # Inverse of runtime
                    }

                # Create radar chart
                fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
                
                # Define angles for radar chart
                angles = [n / float(len(metrics_data[tools[0]].keys())) * 2 * np.pi for n in range(len(metrics_data[tools[0]].keys()))]
                angles += angles[:1]  # Complete the circle

                # Plot data for each tool
                for tool in tools:
                    values = list(metrics_data[tool].values())
                    values += values[:1]  # Complete the circle
                    ax.plot(angles, values, 'o-', linewidth=2, label=tool)
                    ax.fill(angles, values, alpha=0.25)

                # Add labels
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(list(metrics_data[tools[0]].keys()))
                ax.set_ylim(0, 100)
                ax.set_title('Performance Metrics Comparison', size=16, pad=20)
                ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

                img_path = os.path.join(self.output_dir, 'performance_radar.png')
                plt.savefig(img_path, bbox_inches='tight')
                plt.close()
                logger.info(f"Performance radar chart saved to {img_path}")

        except Exception as e:
            logger.error(f"Failed to generate performance radar chart: {e}")

    def generate_pdf_report(self):
        """Placeholder for PDF report generation."""
        logger.info("PDF report generation is not yet implemented.")
        # Implementation would use a library like reportlab
        # from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        # from reportlab.lib.styles import getSampleStyleSheet
        # ... build PDF document ...

def main():
    parser = argparse.ArgumentParser(description="Generate benchmark reports.")
    parser.add_argument('--results_dirs', type=str, required=True, help='A JSON string mapping tools to their results directories.')
    parser.add_argument('--output_dir', type=str, help="Directory to save the report and visualizations.")
    args = parser.parse_args()

    try:
        results_dirs_dict = json.loads(args.results_dirs)
    except json.JSONDecodeError:
        logger.error("Invalid JSON string for results directories.")
        return
        
    generator = ReportGenerator(results_dirs_dict, args.output_dir)
    generator.generate_summary_report()
    generator.generate_visualizations()
    generator.generate_pdf_report()

if __name__ == "__main__":
    main()
