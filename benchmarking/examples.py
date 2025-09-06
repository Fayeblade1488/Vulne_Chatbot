#!/usr/bin/env python3
"""
Example usage script demonstrating the enhanced Garak benchmarker capabilities.
This script shows different usage patterns and configurations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_garak import GarakBenchmarker

def example_fast_security_check():
    """Example: Fast daily security check with high-priority probes."""
    print("=== Example 1: Fast Daily Security Check ===")
    print("Configuration for rapid testing of core GenAI vulnerabilities:")
    print()
    
    benchmarker = GarakBenchmarker(
        probes=GarakBenchmarker.get_high_priority_probes(),
        timeout=90,  # Fast timeout for quick results
        parallel_workers=2,  # Conservative parallelism
        adaptive_timeout=True
    )
    
    print(f"Selected probes: {', '.join(benchmarker.probes)}")
    print(f"Expected runtime: ~5-15 minutes")
    print(f"Parallel workers: {benchmarker.parallel_workers}")
    print(f"Adaptive timeout: {benchmarker.adaptive_timeout}")
    print()
    
    # Show timeout calculation for each probe
    print("Adaptive timeouts:")
    for probe in benchmarker.probes:
        timeout = benchmarker.get_probe_timeout(probe)
        info = benchmarker.get_probe_info().get(probe, {})
        runtime_cat = info.get('typical_runtime', 'unknown')
        print(f"  {probe:15}: {timeout:3}s ({runtime_cat})")
    print()

def example_comprehensive_testing():
    """Example: Comprehensive weekly security assessment."""
    print("=== Example 2: Comprehensive Weekly Assessment ===")
    print("Configuration for thorough GenAI security evaluation:")
    print()
    
    benchmarker = GarakBenchmarker(
        probes=GarakBenchmarker.get_relevant_probes(),  # All probes
        timeout=180,  # Longer timeout for OCI compatibility  
        parallel_workers=4,  # More aggressive parallelism
        adaptive_timeout=True,
        max_retries=3
    )
    
    print(f"Total probes: {len(benchmarker.probes)}")
    print(f"Expected runtime: ~30-60 minutes")
    print(f"Parallel workers: {benchmarker.parallel_workers}")
    print(f"Base timeout: {benchmarker.base_timeout}s")
    print()
    
    # Show probe categories
    probe_info = benchmarker.get_probe_info()
    categories = {}
    for probe in benchmarker.probes:
        category = probe_info.get(probe, {}).get('category', 'unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(probe)
    
    print("Probe categories:")
    for category, probes in categories.items():
        print(f"  {category:12}: {', '.join(probes)}")
    print()

def example_custom_probe_selection():
    """Example: Custom probe selection for specific testing."""
    print("=== Example 3: Custom Probe Selection ===")
    print("Configuration for testing specific vulnerability types:")
    print()
    
    # Focus on injection-related attacks
    injection_probes = ['promptinject', 'jailbreak', 'continuation']
    
    benchmarker = GarakBenchmarker(
        probes=injection_probes,
        timeout=120,
        parallel_workers=1,  # Sequential for detailed monitoring
        adaptive_timeout=True
    )
    
    print(f"Custom probe selection: {', '.join(injection_probes)}")
    print(f"Focus area: Injection attacks")
    print(f"Expected runtime: ~10-20 minutes")
    print()
    
    # Show detailed probe information
    probe_info = benchmarker.get_probe_info()
    print("Detailed probe information:")
    for probe in injection_probes:
        info = probe_info.get(probe, {})
        print(f"  {probe}:")
        print(f"    Priority: {info.get('priority', 'unknown')}")
        print(f"    Category: {info.get('category', 'unknown')}")
        print(f"    Description: {info.get('description', 'No description')}")
        print(f"    Typical runtime: {info.get('typical_runtime', 'unknown')}")
    print()

def example_slow_model_configuration():
    """Example: Configuration optimized for slow cloud models (OCI)."""
    print("=== Example 4: Slow Cloud Model Configuration ===")
    print("Configuration optimized for OCI GenAI and other slow cloud models:")
    print()
    
    benchmarker = GarakBenchmarker(
        probes=GarakBenchmarker.get_priority_probes('high'),  # Start with high priority
        timeout=300,  # Very long timeout for OCI
        parallel_workers=1,  # Sequential to avoid overwhelming the API
        adaptive_timeout=True,
        max_retries=2  # Fewer retries for slower feedback
    )
    
    print(f"Base timeout: {benchmarker.base_timeout}s (5 minutes)")
    print(f"Parallel workers: {benchmarker.parallel_workers} (sequential)")
    print(f"Max retries: {benchmarker.max_retries}")
    print()
    
    print("Adaptive timeouts for slow models:")
    for probe in benchmarker.probes:
        timeout = benchmarker.get_probe_timeout(probe)
        print(f"  {probe:15}: {timeout:3}s ({timeout/60:.1f} minutes)")
    print()
    
    print("Tips for slow models:")
    print("- Monitor logs for timeout patterns")
    print("- Increase timeout if you see frequent timeouts")
    print("- Use sequential execution to avoid API rate limits")
    print("- Consider running during off-peak hours")
    print()

def show_probe_priorities():
    """Show detailed probe priority and relevance information."""
    print("=== Probe Priority and Relevance Guide ===")
    print()
    
    probe_info = GarakBenchmarker.get_probe_info()
    
    for priority in ['high', 'medium', 'low']:
        probes = GarakBenchmarker.get_priority_probes(priority)
        print(f"{priority.upper()} PRIORITY ({len(probes)} probes):")
        
        for probe in probes:
            info = probe_info.get(probe, {})
            relevance = info.get('genai_relevance', 'unknown')
            runtime = info.get('typical_runtime', 'unknown')
            
            print(f"  {probe:15} - {relevance:10} relevance, {runtime:6} runtime")
            print(f"  {'':15}   {info.get('description', 'No description')}")
        print()

def main():
    """Run all examples and show usage patterns."""
    print("Enhanced Garak Benchmarker - Usage Examples")
    print("=" * 50)
    print()
    
    example_fast_security_check()
    example_comprehensive_testing()
    example_custom_probe_selection()
    example_slow_model_configuration()
    show_probe_priorities()
    
    print("Command Line Usage Examples:")
    print("=" * 30)
    print()
    print("# Fast daily check (5-15 minutes)")
    print("python run_garak.py --priority high --timeout 90")
    print()
    print("# Weekly comprehensive scan (30-60 minutes)")
    print("python run_garak.py --priority all --timeout 180")
    print()
    print("# Custom probe selection")
    print("python run_garak.py --probes promptinject,jailbreak,dan --timeout 120")
    print()
    print("# Slow cloud model configuration")
    print("python run_garak.py --priority high --timeout 300 --parallel-workers 1")
    print()
    print("# Debug mode (sequential, short timeout)")
    print("python run_garak.py --priority high --timeout 60 --parallel-workers 1")
    print()
    print("For more details, see: GARAK_BENCHMARKING_GUIDE.md")

if __name__ == "__main__":
    main()