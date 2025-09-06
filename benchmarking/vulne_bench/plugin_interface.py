"""
Plugin interface for the Vulne_Chatbot benchmarking suite.
This module defines the base classes and interfaces for extending the benchmarking suite.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class BenchmarkPlugin(ABC):
    """Abstract base class for benchmarking plugins."""
    
    def __init__(self, config: Dict[str, Any], output_dir: Optional[str] = None):
        """
        Initialize the plugin.
        
        Args:
            config: Configuration dictionary for this plugin
            output_dir: Directory to save results
        """
        self.config = config
        self.output_dir = output_dir
        self.metrics = {}
        self.results = []
    
    @abstractmethod
    def run_benchmark(self) -> Dict[str, Any]:
        """
        Run the benchmark and return results.
        
        Returns:
            Dictionary containing benchmark results and metrics
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this plugin.
        
        Returns:
            Plugin name
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the description of this plugin.
        
        Returns:
            Plugin description
        """
        pass
    
    def save_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Save benchmark results to file.
        
        Args:
            results: List of result dictionaries
        """
        import json
        import os
        
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, f'{self.get_name().lower()}_results.json')
            with open(output_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'plugin': self.get_name(),
                    'metrics': self.metrics,
                    'results': results
                }, f, indent=4)
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Update the metrics dictionary.
        
        Args:
            metrics: Metrics to update
        """
        self.metrics.update(metrics)

class ProbePlugin(ABC):
    """Abstract base class for custom probe plugins."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the probe plugin.
        
        Args:
            name: Name of the probe
            description: Description of what the probe tests
        """
        self.name = name
        self.description = description
        self.prompts = []
        self.tags = []
    
    @abstractmethod
    def generate_prompts(self) -> List[str]:
        """
        Generate prompts for this probe.
        
        Returns:
            List of prompt strings
        """
        pass
    
    @abstractmethod
    def detect_vulnerability(self, response: str) -> Dict[str, Any]:
        """
        Detect vulnerabilities in a response.
        
        Args:
            response: AI response to analyze
            
        Returns:
            Dictionary containing detection results
        """
        pass
    
    def get_name(self) -> str:
        """Get the name of this probe."""
        return self.name
    
    def get_description(self) -> str:
        """Get the description of this probe."""
        return self.description

class ReporterPlugin(ABC):
    """Abstract base class for reporting plugins."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the reporter plugin.
        
        Args:
            name: Name of the reporter
            description: Description of what the reporter does
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def generate_report(self, results: Dict[str, Any], output_dir: str) -> str:
        """
        Generate a report from benchmark results.
        
        Args:
            results: Benchmark results dictionary
            output_dir: Directory to save the report
            
        Returns:
            Path to the generated report
        """
        pass
    
    def get_name(self) -> str:
        """Get the name of this reporter."""
        return self.name
    
    def get_description(self) -> str:
        """Get the description of this reporter."""
        return self.description

class PluginManager:
    """Manager for loading and running plugins."""
    
    def __init__(self):
        """Initialize the plugin manager."""
        self.benchmark_plugins = {}
        self.probe_plugins = {}
        self.reporter_plugins = {}
    
    def register_benchmark_plugin(self, plugin_class: type) -> None:
        """
        Register a benchmark plugin.
        
        Args:
            plugin_class: Plugin class to register
        """
        plugin = plugin_class({}, None)
        self.benchmark_plugins[plugin.get_name()] = plugin_class
    
    def register_probe_plugin(self, plugin: ProbePlugin) -> None:
        """
        Register a probe plugin.
        
        Args:
            plugin: Probe plugin instance to register
        """
        self.probe_plugins[plugin.get_name()] = plugin
    
    def register_reporter_plugin(self, plugin: ReporterPlugin) -> None:
        """
        Register a reporter plugin.
        
        Args:
            plugin: Reporter plugin instance to register
        """
        self.reporter_plugins[plugin.get_name()] = plugin
    
    def get_benchmark_plugin(self, name: str) -> Optional[type]:
        """
        Get a registered benchmark plugin.
        
        Args:
            name: Name of the plugin
            
        Returns:
            Plugin class or None if not found
        """
        return self.benchmark_plugins.get(name)
    
    def get_probe_plugin(self, name: str) -> Optional[ProbePlugin]:
        """
        Get a registered probe plugin.
        
        Args:
            name: Name of the plugin
            
        Returns:
            Plugin instance or None if not found
        """
        return self.probe_plugins.get(name)
    
    def get_reporter_plugin(self, name: str) -> Optional[ReporterPlugin]:
        """
        Get a registered reporter plugin.
        
        Args:
            name: Name of the plugin
            
        Returns:
            Plugin instance or None if not found
        """
        return self.reporter_plugins.get(name)
    
    def list_benchmark_plugins(self) -> List[str]:
        """
        List all registered benchmark plugins.
        
        Returns:
            List of plugin names
        """
        return list(self.benchmark_plugins.keys())
    
    def list_probe_plugins(self) -> List[str]:
        """
        List all registered probe plugins.
        
        Returns:
            List of plugin names
        """
        return list(self.probe_plugins.keys())
    
    def list_reporter_plugins(self) -> List[str]:
        """
        List all registered reporter plugins.
        
        Returns:
            List of plugin names
        """
        return list(self.reporter_plugins.keys())

# Global plugin manager instance
plugin_manager = PluginManager()

def register_plugin(plugin_type: str, plugin: Any) -> None:
    """
    Register a plugin with the global plugin manager.
    
    Args:
        plugin_type: Type of plugin ('benchmark', 'probe', 'reporter')
        plugin: Plugin to register
    """
    if plugin_type == 'benchmark':
        plugin_manager.register_benchmark_plugin(plugin)
    elif plugin_type == 'probe':
        plugin_manager.register_probe_plugin(plugin)
    elif plugin_type == 'reporter':
        plugin_manager.register_reporter_plugin(plugin)
    else:
        raise ValueError(f"Unknown plugin type: {plugin_type}")

def get_plugin_manager() -> PluginManager:
    """
    Get the global plugin manager.
    
    Returns:
        PluginManager instance
    """
    return plugin_manager