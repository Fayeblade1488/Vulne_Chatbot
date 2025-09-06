# Troubleshooting Guide

This document provides solutions to common issues encountered when using the Vulne_Chatbot platform.

## 1. Installation Issues

### Missing Dependencies
**Problem**: ImportError when running benchmarking scripts

**Solution**:
```bash
# Install all required dependencies
pip install -r benchmarking/vulne_bench/requirements.txt

# Install the benchmarking package in development mode
pip install -e benchmarking/
```

### Permission Errors
**Problem**: Permission denied when installing packages

**Solution**:
```bash
# Use --user flag to install in user directory
pip install --user -r benchmarking/vulne_bench/requirements.txt

# Or use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r benchmarking/vulne_bench/requirements.txt
```

## 2. Connection Issues

### Connection Refused Error
**Problem**: Cannot connect to the Vulne_Chatbot application

**Solution**:
1. Verify the application is running:
   ```bash
   # Check if the service is listening on port 7000
   netstat -an | grep 7000
   # or on macOS/Linux:
   lsof -i :7000
   ```

2. Start the Vulne_Chatbot application:
   ```bash
   # Using Docker (recommended)
   docker build -t vulne-chatbot .
   docker run -p 7000:7000 -it vulne-chatbot
   
   # Or directly with Flask
   python vulne_chat.py
   ```

3. Check the configuration in `garak_config.json`:
   ```json
   {
      "rest": {
         "RestGenerator": {
            "uri": "http://127.0.0.1:7000/chat",
            // ... other settings
         }
      }
   }
   ```

### SSL Certificate Errors
**Problem**: SSL verification fails when connecting to HTTPS endpoints

**Solution**:
1. For testing environments, disable SSL verification:
   ```json
   {
      "rest": {
         "RestGenerator": {
            "verify": false,
            "session_kwargs": {
               "verify": false
            },
            "request_kwargs": {
               "verify": false
            }
         }
      }
   }
   ```

2. For production, use proper certificates:
   ```bash
   # Install certificates
   pip install --upgrade certifi
   ```

## 3. Garak-Specific Issues

### Unknown Probes Error
**Problem**: Garak reports "Unknown probes" error

**Solution**:
1. Clean probe names to remove ANSI formatting:
   ```bash
   # List probes and clean formatting
   python -m garak --list_probes | sed 's/\x1B\[[0-9;]*[JKmsu]//g'
   ```

2. Verify probe names in configuration:
   ```json
   {
      "garak": {
         "probes": [
            "promptinject",  // Correct
            "garak.probes.promptinject.PromptInject"  // Also correct, but more verbose
         ]
      }
   }
   ```

### Timeout Errors
**Problem**: Probes timeout during execution

**Solution**:
1. Increase timeout values in configuration:
   ```json
   {
      "garak": {
         "timeout": 600,  // Increase from default 300 seconds
         "max_retries": 5  // Increase retry attempts
      }
   }
   ```

2. For cloud models, use adaptive timeouts:
   The benchmarking suite now includes adaptive timeout functionality that adjusts based on historical response times.

## 4. Model-Specific Issues

### Local Model Not Found
**Problem**: Ollama models not available

**Solution**:
1. Verify Ollama is running:
   ```bash
   # Start Ollama service
   ollama serve
   
   # In another terminal, check available models
   ollama list
   ```

2. Pull required models:
   ```bash
   # Pull commonly used models
   ollama pull mistral
   ollama pull llama3
   ollama pull codellama
   ```

### OCI Authentication Errors
**Problem**: Cannot authenticate with Oracle Cloud Infrastructure

**Solution**:
1. Verify OCI configuration:
   ```bash
   # Check OCI configuration
   oci setup config
   
   # Verify configuration file exists
   ls ~/.oci/config
   ```

2. Set environment variables:
   ```bash
   export OCI_CONFIG_FILE=~/.oci/config
   export OCI_CONFIG_PROFILE=DEFAULT
   ```

3. Check compartment ID in `.env.real`:
   ```ini
   OCI_COMPARTMENT_ID=ocid1.compartment.oc1..your-compartment-id
   ```

## 5. Performance Issues

### High Memory Usage
**Problem**: Benchmarking consumes excessive memory

**Solution**:
1. Reduce parallel workers:
   ```json
   {
      "garak": {
         "parallel_workers": 2  // Reduce from default 4
      }
   }
   ```

2. Monitor resource usage:
   The enhanced benchmarking suite now includes resource monitoring that tracks CPU and memory usage.

### Slow Execution
**Problem**: Tests take too long to complete

**Solution**:
1. Use selective probing:
   ```json
   {
      "garak": {
         "probes": [
            "promptinject",
            "leakreplicate",
            // Only include most relevant probes
         ]
      }
   }
   ```

2. Enable caching:
   The benchmarking suite now includes caching to avoid redundant test executions.

## 6. Reporting Issues

### Missing Visualization Libraries
**Problem**: Cannot generate charts and graphs

**Solution**:
```bash
# Install visualization dependencies
pip install matplotlib numpy
```

### Report Generation Failures
**Problem**: Reports fail to generate or are incomplete

**Solution**:
1. Check output directories:
   ```bash
   # Ensure output directory exists and is writable
   mkdir -p results
   chmod 755 results
   ```

2. Verify JSON parsing:
   Check that result files are properly formatted JSON.

## 7. Docker Issues

### Container Won't Start
**Problem**: Docker container fails to start

**Solution**:
1. Check Docker build logs:
   ```bash
   docker build -t vulne-chatbot . 2>&1 | tee build.log
   ```

2. Verify dependencies in Dockerfile:
   ```dockerfile
   # Ensure all required packages are installed
   RUN pip install --no-cache-dir -r requirements.txt
   RUN pip install -e benchmarking/
   ```

### Port Conflicts
**Problem**: Port 7000 already in use

**Solution**:
```bash
# Use a different port
docker run -p 8000:7000 -it vulne-chatbot

# Update configuration to use new port
# In garak_config.json:
{
   "rest": {
      "RestGenerator": {
         "uri": "http://127.0.0.1:8000/chat"
      }
   }
}
```

## 8. Debugging Commands

### Enable Verbose Logging
```bash
# Set logging level to DEBUG
export PYTHON_LOG_LEVEL=DEBUG

# Run with verbose output
python -m benchmarking.vulne_bench.run_garak --config config.json --verbose
```

### Check Resource Usage
```bash
# Monitor system resources during testing
htop
# or
top -p $(pgrep -f vulne_chat.py)
```

### Test Individual Components
```bash
# Test connection to Vulne_Chatbot
curl -X POST http://127.0.0.1:7000/health

# Test Garak installation
python -m garak --help

# Test benchmarking package
python -c "import vulne_bench; print('Package imported successfully')"
```

## 9. Common Configuration Issues

### Incorrect File Paths
**Problem**: File not found errors

**Solution**:
1. Use absolute paths in configuration:
   ```json
   {
      "garak": {
         "config_path": "/full/path/to/garak_config.json"
      }
   }
   ```

2. Verify file existence:
   ```bash
   ls -la /path/to/garak_config.json
   ```

### JSON Formatting Errors
**Problem**: Invalid JSON in configuration files

**Solution**:
1. Validate JSON syntax:
   ```bash
   # Use Python to validate JSON
   python -m json.tool config.json
   ```

2. Use online JSON validators for complex configurations

## 10. Getting Help

If you encounter issues not covered in this guide:

1. Check the GitHub issues for similar problems
2. Review the application logs for detailed error messages
3. Enable debug logging for more verbose output
4. Contact the development team with:
   - Error messages
   - Steps to reproduce
   - System information (OS, Python version, etc.)
   - Relevant configuration files (with sensitive data removed)

This troubleshooting guide will be updated as new issues are encountered and resolved.