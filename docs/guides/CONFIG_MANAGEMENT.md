# Configuration Management Tools

This directory contains tools for managing configuration files for the Vulne_Chatbot benchmarking suite.

## Available Tools

### 1. Configuration Validator (`config_validator.py`)
A Python module that provides functions for validating configuration files against a schema.

### 2. Configuration Tool (`config_tool.py`)
A command-line utility for managing configuration files with the following commands:

#### validate
Validate a configuration file against the required schema.

```bash
vulne-config validate config.json
```

#### create
Create a default configuration file.

```bash
vulne-config create my_config.json
```

#### update
Update a configuration file with new values.

```bash
vulne-config update config.json '{"garak":{"timeout":600}}'
```

#### show
Show the contents of a configuration file.

```bash
# Show entire configuration
vulne-config show config.json

# Show only a specific section
vulne-config show config.json --section garak
```

#### compare
Compare two configuration files.

```bash
vulne-config compare config1.json config2.json
```

## Configuration Schema

The configuration file must follow this schema:

```json
{
    "garak": {
        "config_path": "path/to/garak_config.json",
        "probes": ["probe1", "probe2", "..."],
        "max_retries": 3,
        "timeout": 300,
        "parallel_workers": 4
    },
    "nemo": {
        "config_path": "path/to/nemo_config",
        "test_cases": [
            {
                "input": "test input",
                "expected_block": true,
                "type": "vulnerability_type"
            }
        ],
        "max_retries": 3,
        "timeout": 60,
        "parallel_workers": 4
    },
    "guardrailsai": {
        "test_cases": [
            {
                "input": "test input",
                "expected_fail": true,
                "type": "vulnerability_type"
            }
        ],
        "max_retries": 3,
        "timeout": 60,
        "parallel_workers": 4
    },
    "general": {
        "target_url": "http://127.0.0.1:7000/chat",
        "models": ["model1", "model2"],
        "output_dir": "results",
        "email_notify": false,
        "email_to": "admin@example.com"
    }
}
```

## Usage Examples

### Validating a Configuration
```bash
vulne-config validate benchmarking/vulne_bench/config.json
```

### Creating a New Configuration
```bash
vulne-config create my_custom_config.json
```

### Updating Timeout Values
```bash
vulne-config update config.json '{"garak":{"timeout":600},"nemo":{"timeout":120}}'
```

### Comparing Configurations
```bash
vulne-config compare config_original.json config_modified.json
```

## Error Handling

The tools provide detailed error messages for common issues:

- **Schema Validation Errors**: Missing required fields, incorrect data types
- **File Not Found Errors**: Configuration files that don't exist
- **JSON Parsing Errors**: Invalid JSON syntax in configuration files
- **Permission Errors**: Insufficient permissions to read/write files

## Best Practices

1. **Always Validate**: Validate configuration files before running benchmarks
2. **Backup Configurations**: Keep backups of working configurations
3. **Version Control**: Track configuration changes in version control
4. **Environment-Specific Configs**: Use different configurations for development, testing, and production
5. **Documentation**: Document custom configurations and their purposes

## Contributing

To extend the configuration management tools:

1. Add new validation rules to `config_validator.py`
2. Extend the command-line interface in `config_tool.py`
3. Update this documentation with new features
4. Add unit tests for new functionality