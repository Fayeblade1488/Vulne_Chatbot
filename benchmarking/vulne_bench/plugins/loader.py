"""
Plugin loader for the Vulne_Chatbot benchmarking suite.
This module provides functionality to dynamically load plugins from a plugins directory.
"""

import os
import sys
import importlib.util
from typing import List, Dict, Any, Optional
import logging

from .plugin_interface import plugin_manager, BenchmarkPlugin, ProbePlugin, ReporterPlugin

logger = logging.getLogger(__name__)

def load_plugins_from_directory(plugin_dir: str) -> Dict[str, List[str]]:
    """
    Load plugins from a directory.
    
    Args:
        plugin_dir: Directory containing plugin modules
        
    Returns:
        Dictionary mapping plugin types to lists of loaded plugin names
    """
    if not os.path.exists(plugin_dir):
        logger.warning(f"Plugin directory does not exist: {plugin_dir}")
        return {}
    
    loaded_plugins = {
        'benchmark': [],
        'probe': [],
        'reporter': []
    }
    
    # Add plugin directory to Python path
    if plugin_dir not in sys.path:
        sys.path.insert(0, plugin_dir)
    
    # Iterate through Python files in the plugin directory
    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove .py extension
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(plugin_dir, filename))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for plugin classes in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type):
                        # Check if it's a benchmark plugin
                        if issubclass(attr, BenchmarkPlugin) and attr != BenchmarkPlugin:
                            plugin_manager.register_benchmark_plugin(attr)
                            loaded_plugins['benchmark'].append(attr_name)
                            logger.info(f"Loaded benchmark plugin: {attr_name}")
                        
                        # Check if it's a probe plugin instance
                        elif isinstance(attr, ProbePlugin):
                            plugin_manager.register_probe_plugin(attr)
                            loaded_plugins['probe'].append(attr_name)
                            logger.info(f"Loaded probe plugin: {attr_name}")
                        
                        # Check if it's a reporter plugin instance
                        elif isinstance(attr, ReporterPlugin):
                            plugin_manager.register_reporter_plugin(attr)
                            loaded_plugins['reporter'].append(attr_name)
                            logger.info(f"Loaded reporter plugin: {attr_name}")
                            
            except Exception as e:
                logger.error(f"Failed to load plugin from {filename}: {e}")
    
    return loaded_plugins

def load_plugins(config: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Load plugins based on configuration.
    
    Args:
        config: Configuration dictionary containing plugin settings
        
    Returns:
        Dictionary mapping plugin types to lists of loaded plugin names
    """
    loaded_plugins = {
        'benchmark': [],
        'probe': [],
        'reporter': []
    }
    
    # Load plugins from the default plugins directory
    default_plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    default_plugins = load_plugins_from_directory(default_plugin_dir)
    for plugin_type, plugins in default_plugins.items():
        loaded_plugins[plugin_type].extend(plugins)
    
    # Load plugins from additional directories specified in config
    if 'plugin_directories' in config.get('general', {}):
        for plugin_dir in config['general']['plugin_directories']:
            additional_plugins = load_plugins_from_directory(plugin_dir)
            for plugin_type, plugins in additional_plugins.items():
                loaded_plugins[plugin_type].extend(plugins)
    
    return loaded_plugins

def create_benchmark_plugin(plugin_name: str, config: Dict[str, Any], output_dir: Optional[str] = None) -> Optional[BenchmarkPlugin]:
    """
    Create an instance of a benchmark plugin.
    
    Args:
        plugin_name: Name of the plugin to create
        config: Configuration for the plugin
        output_dir: Directory to save results
        
    Returns:
        Plugin instance or None if not found
    """
    plugin_class = plugin_manager.get_benchmark_plugin(plugin_name)
    if plugin_class:
        try:
            return plugin_class(config, output_dir)
        except Exception as e:
            logger.error(f"Failed to create benchmark plugin {plugin_name}: {e}")
    return None

def get_available_plugins() -> Dict[str, List[str]]:
    """
    Get lists of available plugins by type.
    
    Returns:
        Dictionary mapping plugin types to lists of available plugin names
    """
    return {
        'benchmark': plugin_manager.list_benchmark_plugins(),
        'probe': plugin_manager.list_probe_plugins(),
        'reporter': plugin_manager.list_reporter_plugins()
    }

# Example plugin implementation
class ExampleBenchmarkPlugin(BenchmarkPlugin):
    """Example benchmark plugin implementation."""
    
    def run_benchmark(self) -> Dict[str, Any]:
        """Run the example benchmark."""
        # Simulate some work
        import time
        time.sleep(1)
        
        # Return example results
        self.results = [
            {'test': 'example1', 'passed': True, 'time': 0.5},
            {'test': 'example2', 'passed': False, 'time': 0.3}
        ]
        
        self.metrics = {
            'total_tests': 2,
            'passed_tests': 1,
            'failed_tests': 1,
            'success_rate': 50.0
        }
        
        self.save_results(self.results)
        return {'metrics': self.metrics, 'results': self.results}
    
    def get_name(self) -> str:
        """Get the plugin name."""
        return "ExampleBenchmark"
    
    def get_description(self) -> str:
        """Get the plugin description."""
        return "An example benchmark plugin for demonstration purposes"

# Register the example plugin
plugin_manager.register_benchmark_plugin(ExampleBenchmarkPlugin)

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Show available plugins
    print("Available plugins:")
    plugins = get_available_plugins()
    for plugin_type, plugin_list in plugins.items():
        print(f"  {plugin_type}: {plugin_list}")