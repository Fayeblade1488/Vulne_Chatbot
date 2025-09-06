"""
Configuration management utility for the Vulne_Chatbot benchmarking suite.
This script provides command-line tools for managing configuration files.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any
from .config_validator import (
    load_and_validate_config, 
    create_default_config, 
    validate_config_schema,
    update_config
)

def validate_config_command(args: argparse.Namespace) -> None:
    """Validate a configuration file."""
    try:
        config = load_and_validate_config(args.config_path)
        print(f"✓ Configuration file '{args.config_path}' is valid")
        
        # Print summary
        print("\nConfiguration Summary:")
        print(f"  Garak probes: {len(config.get('garak', {}).get('probes', []))}")
        print(f"  NeMo test cases: {len(config.get('nemo', {}).get('test_cases', []))}")
        print(f"  GuardrailsAI test cases: {len(config.get('guardrailsai', {}).get('test_cases', []))}")
        print(f"  Target models: {len(config.get('general', {}).get('models', []))}")
        
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        sys.exit(1)

def create_config_command(args: argparse.Namespace) -> None:
    """Create a default configuration file."""
    try:
        config = create_default_config(args.output_path)
        print(f"✓ Default configuration created at '{args.output_path}'")
    except Exception as e:
        print(f"✗ Failed to create configuration: {e}")
        sys.exit(1)

def update_config_command(args: argparse.Namespace) -> None:
    """Update a configuration file with new values."""
    try:
        # Load existing configuration
        config = load_and_validate_config(args.config_path)
        
        # Parse updates from JSON string
        updates = json.loads(args.updates)
        
        # Apply updates
        updated_config = update_config(config, updates)
        
        # Validate updated configuration
        errors = validate_config_schema(updated_config)
        if errors:
            print("✗ Updated configuration is invalid:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        
        # Save updated configuration
        with open(args.config_path, 'w') as f:
            json.dump(updated_config, f, indent=2)
        
        print(f"✓ Configuration updated successfully")
        
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in updates: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Failed to update configuration: {e}")
        sys.exit(1)

def show_config_command(args: argparse.Namespace) -> None:
    """Show the contents of a configuration file."""
    try:
        config = load_and_validate_config(args.config_path)
        
        if args.section:
            if args.section in config:
                print(json.dumps(config[args.section], indent=2))
            else:
                print(f"Section '{args.section}' not found in configuration")
                sys.exit(1)
        else:
            print(json.dumps(config, indent=2))
            
    except Exception as e:
        print(f"✗ Failed to show configuration: {e}")
        sys.exit(1)

def compare_configs_command(args: argparse.Namespace) -> None:
    """Compare two configuration files."""
    try:
        config1 = load_and_validate_config(args.config1)
        config2 = load_and_validate_config(args.config2)
        
        print("Configuration Comparison:")
        print(f"File 1: {args.config1}")
        print(f"File 2: {args.config2}")
        print()
        
        # Compare top-level sections
        all_sections = set(config1.keys()) | set(config2.keys())
        for section in sorted(all_sections):
            if section in config1 and section in config2:
                if config1[section] == config2[section]:
                    print(f"  {section}: ✓ Identical")
                else:
                    print(f"  {section}: ⚠ Different")
            elif section in config1:
                print(f"  {section}: ➕ Only in file 1")
            else:
                print(f"  {section}: ➖ Only in file 2")
                
    except Exception as e:
        print(f"✗ Failed to compare configurations: {e}")
        sys.exit(1)

def main() -> None:
    """Main entry point for the configuration management utility."""
    parser = argparse.ArgumentParser(
        description="Configuration management utility for Vulne_Chatbot benchmarking suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
  validate    Validate a configuration file
  create      Create a default configuration file
  update      Update a configuration file with new values
  show        Show the contents of a configuration file
  compare     Compare two configuration files

Examples:
  config-tool validate config.json
  config-tool create my_config.json
  config-tool update config.json '{"garak":{"timeout":600}}'
  config-tool show config.json --section garak
  config-tool compare config1.json config2.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a configuration file')
    validate_parser.add_argument('config_path', help='Path to the configuration file')
    validate_parser.set_defaults(func=validate_config_command)
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a default configuration file')
    create_parser.add_argument('output_path', help='Path where the configuration file should be created')
    create_parser.set_defaults(func=create_config_command)
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a configuration file with new values')
    update_parser.add_argument('config_path', help='Path to the configuration file')
    update_parser.add_argument('updates', help='JSON string with updates to apply')
    update_parser.set_defaults(func=update_config_command)
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show the contents of a configuration file')
    show_parser.add_argument('config_path', help='Path to the configuration file')
    show_parser.add_argument('--section', help='Show only a specific section')
    show_parser.set_defaults(func=show_config_command)
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two configuration files')
    compare_parser.add_argument('config1', help='Path to the first configuration file')
    compare_parser.add_argument('config2', help='Path to the second configuration file')
    compare_parser.set_defaults(func=compare_configs_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the appropriate command
    try:
        args.func(args)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()