#!/usr/bin/env python3
"""
Quick validation script for the enhanced Garak benchmarker.
Tests the functionality without actually running Garak probes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_garak import GarakBenchmarker

def test_probe_selection():
    """Test probe selection and priority functionality."""
    print("=== Testing Probe Selection ===")
    
    # Test all priority levels
    all_probes = GarakBenchmarker.get_relevant_probes()
    high_probes = GarakBenchmarker.get_priority_probes('high')
    medium_probes = GarakBenchmarker.get_priority_probes('medium')
    low_probes = GarakBenchmarker.get_priority_probes('low')
    
    print(f"All probes ({len(all_probes)}): {', '.join(all_probes)}")
    print(f"High priority ({len(high_probes)}): {', '.join(high_probes)}")
    print(f"Medium priority ({len(medium_probes)}): {', '.join(medium_probes)}")
    print(f"Low priority ({len(low_probes)}): {', '.join(low_probes)}")
    
    # Validate no duplicates and complete coverage
    all_priority_probes = high_probes + medium_probes + low_probes
    assert len(all_priority_probes) == len(all_probes), "Priority probes don't match all probes"
    assert len(set(all_priority_probes)) == len(all_priority_probes), "Duplicate probes in priorities"
    
    print("✓ Probe selection working correctly")

def test_probe_info():
    """Test probe information functionality."""
    print("\n=== Testing Probe Information ===")
    
    probe_info = GarakBenchmarker.get_probe_info()
    all_probes = GarakBenchmarker.get_relevant_probes()
    
    # Validate all probes have info
    for probe in all_probes:
        assert probe in probe_info, f"No info for probe: {probe}"
        info = probe_info[probe]
        assert 'priority' in info, f"No priority for probe: {probe}"
        assert 'category' in info, f"No category for probe: {probe}"
        assert 'description' in info, f"No description for probe: {probe}"
        
    print(f"✓ All {len(all_probes)} probes have complete information")

def test_timeout_calculation():
    """Test adaptive timeout calculation."""
    print("\n=== Testing Timeout Calculation ===")
    
    # Test with adaptive timeout enabled
    benchmarker = GarakBenchmarker(
        config_path='../garak_config.json',
        timeout=120,
        adaptive_timeout=True
    )
    
    # Test different probe types
    test_cases = [
        ('dan', 'fast'),  # Should get shorter timeout
        ('promptinject', 'medium'),  # Should get base timeout
        ('leakreplicate', 'slow'),  # Should get longer timeout
    ]
    
    for probe, expected_speed in test_cases:
        timeout = benchmarker.get_probe_timeout(probe)
        print(f"  {probe} ({expected_speed}): {timeout}s")
        
        if expected_speed == 'fast':
            assert timeout <= benchmarker.base_timeout, f"Fast probe timeout too high: {timeout}"
        elif expected_speed == 'slow':
            assert timeout >= benchmarker.base_timeout, f"Slow probe timeout too low: {timeout}"
    
    # Test with adaptive timeout disabled
    benchmarker_fixed = GarakBenchmarker(
        config_path='../garak_config.json',
        timeout=120,
        adaptive_timeout=False
    )
    
    for probe, _ in test_cases:
        timeout = benchmarker_fixed.get_probe_timeout(probe)
        assert timeout == 120, f"Fixed timeout not working: {timeout}"
    
    print("✓ Adaptive timeout calculation working correctly")

def test_metrics_initialization():
    """Test metrics initialization."""
    print("\n=== Testing Metrics Initialization ===")
    
    benchmarker = GarakBenchmarker(
        config_path='../garak_config.json',
        output_dir='/tmp/test_garak_output'
    )
    
    required_metrics = [
        'success_rate', 'coverage', 'runtime_total', 'runtime_avg_per_probe',
        'timeout_count', 'failed_probes', 'probe_runtimes', 'vulnerability_counts',
        'vulnerabilities_detected'
    ]
    
    for metric in required_metrics:
        assert metric in benchmarker.metrics, f"Missing metric: {metric}"
    
    print("✓ All required metrics initialized")

def main():
    """Run all validation tests."""
    print("Running enhanced Garak benchmarker validation...\n")
    
    try:
        test_probe_selection()
        test_probe_info()
        test_timeout_calculation()
        test_metrics_initialization()
        
        print("\n" + "="*50)
        print("✅ All validation tests passed!")
        print("The enhanced Garak benchmarker is ready to use.")
        print("\nNext steps:")
        print("1. Test with: python run_garak.py --list-probes")
        print("2. Run fast test: python run_garak.py --priority high --timeout 60")
        print("3. Check the GARAK_BENCHMARKING_GUIDE.md for detailed usage")
        
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()