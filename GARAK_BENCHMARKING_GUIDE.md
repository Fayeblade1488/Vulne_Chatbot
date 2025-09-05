# Garak Benchmarking Guide for GenAI/LLM Security Testing

This guide provides comprehensive advice for using Garak to benchmark GenAI/LLM vulnerabilities, addressing performance optimization, probe selection, metrics interpretation, and limitations.

## 🎯 Quick Start for GenAI Testing

### Recommended Probe Priorities

**For Fast Testing (5-15 minutes):**
```bash
python benchmarking/run_garak.py --priority high --timeout 150
```
Tests the 4 most critical GenAI vulnerabilities: prompt injection, jailbreaking, DAN attacks, and data leakage.

**For Comprehensive Testing (30-60 minutes):**
```bash
python benchmarking/run_garak.py --priority all --timeout 180
```
Tests all 10 relevant probes for complete GenAI security assessment.

**For Custom Testing:**
```bash
python benchmarking/run_garak.py --probes promptinject,jailbreak,dan --timeout 120
```

## 📊 Most Relevant Probes for GenAI/LLM Testing

### High Priority (Core GenAI Vulnerabilities)
1. **`promptinject`** - Prompt injection attacks (CRITICAL)
   - Tests for system prompt leakage and instruction override
   - Most important for production LLM security
   - Runtime: Medium (~2-5 minutes per test)

2. **`jailbreak`** - Safety measure bypass attempts  
   - Tests circumvention of content policies and safety guardrails
   - Essential for responsible AI deployment
   - Runtime: Medium (~3-7 minutes per test)

3. **`dan`** - "Do Anything Now" mode exploitation
   - Tests specific instruction-following model vulnerabilities
   - High relevance for ChatGPT-style models
   - Runtime: Fast (~1-3 minutes per test)

4. **`leakreplicate`** - Data leakage and information disclosure
   - Tests for training data extraction and sensitive information leaks
   - Critical for production models with proprietary data
   - Runtime: Slow (~5-15 minutes per test)

### Medium Priority (Important Coverage)
5. **`continuation`** - Prompt continuation attacks
6. **`encoding`** - Encoding/obfuscation bypass techniques  
7. **`toxicity`** - Toxic content generation testing
8. **`misinformation`** - Misinformation and hallucination testing

### Lower Priority (General Vulnerabilities)
9. **`snowball`** - Escalating attack patterns
10. **`knownbugs`** - General vulnerability testing

## 📈 Key Metrics to Report

### Primary Success Metrics
- **Success Rate**: Percentage of probes that completed successfully
- **Coverage**: Percentage of intended tests that were executed
- **Vulnerability Detection Rate**: Number of vulnerabilities found per probe

### Performance Metrics  
- **Runtime Total**: Total execution time for benchmark
- **Runtime per Probe**: Average and individual probe execution times
- **Timeout Rate**: Percentage of probes that exceeded timeout limits
- **Retry Rate**: Number of failed attempts that required retries

### Security Metrics
- **Vulnerability Counts**: Number of each vulnerability type detected
- **Severity Scores**: If available from Garak output
- **False Positive Rate**: When known safe inputs are flagged (requires manual validation)

### Comparative Metrics
- **Baseline vs Guardrails**: Compare results with/without protective measures
- **Model Performance**: Compare across different models or configurations
- **Temporal Analysis**: Track changes over time or model versions

## ⚡ Performance Optimization

### Timeout Configuration
```bash
# For local models (Ollama)
--timeout 60

# For cloud models (OCI, Azure OpenAI)  
--timeout 150

# For very slow models or unstable connections
--timeout 300
```

### Parallel Execution
```bash
# Conservative (default)
--parallel-workers 4

# Aggressive (if model can handle load)
--parallel-workers 8

# Single-threaded (for debugging)
--parallel-workers 1
```

### Selective Testing Strategies
1. **Daily Testing**: Use `--priority high` for routine security checks
2. **Weekly Testing**: Use `--priority medium` for broader coverage  
3. **Release Testing**: Use `--priority all` for comprehensive evaluation
4. **Incident Response**: Use specific probes related to reported vulnerabilities

## 🚨 Known Limitations & Mitigation Strategies

### Runtime Performance Issues

**Problem**: Full scans take 39+ hours for 153 probes
- **Mitigation 1**: Use priority-based selection (`--priority high` = ~15 minutes)
- **Mitigation 2**: Run probes individually with the provided bash script
- **Mitigation 3**: Use parallel execution with caution (test model stability first)
- **Mitigation 4**: Schedule long-running tests during off-peak hours

**Problem**: Individual probe timeouts on slow models
- **Mitigation**: Increase timeout progressively (120s → 180s → 300s)
- **Configuration**: Use adaptive timeout feature (enabled by default)
- **Monitoring**: Check logs for timeout patterns and adjust accordingly

### Reliability Issues

**Problem**: Probes fail intermittently
- **Mitigation 1**: Automatic retry logic (default: 3 attempts)
- **Mitigation 2**: Individual probe execution script in `notes/run_garak_probes.sh`
- **Mitigation 3**: Resume capability - rerun only failed probes from previous results

**Problem**: Network connectivity issues with cloud models
- **Mitigation**: Add network retry logic and connection pooling
- **Configuration**: Use `verify=false` in garak_config.json for SSL issues
- **Monitoring**: Track connection failures separately from probe failures

### Scope Limitations

**Problem**: Garak focuses on certain vulnerability types
- **Limitation**: May miss application-specific vulnerabilities (SSRF, IDOR)
- **Mitigation**: Combine with custom security tests for your application
- **Supplement**: Use additional tools like NeMo Guardrails and GuardrailsAI

**Problem**: "Unknown probes" or unsupported modules
- **Debugging**: Check Garak version compatibility
- **Logging**: Review detailed logs in output directory
- **Alternative**: Use bash script to skip problematic probes

### Hardware Dependencies

**Problem**: High CPU/Memory usage during parallel execution
- **Monitoring**: Track system resources during benchmarking
- **Scaling**: Reduce parallel workers if system becomes unstable
- **Optimization**: Use GPU acceleration if available for model inference

## 🔍 Interpreting Results

### Understanding Vulnerability Reports
- **True Positives**: Confirmed security issues that need addressing
- **False Positives**: Benign content flagged as vulnerable (requires manual review)
- **Edge Cases**: Borderline results that need security team evaluation

### Severity Assessment
Use OWASP LLM Top 10 as reference:
1. **High**: Prompt injection, data leakage, jailbreaking
2. **Medium**: Misinformation, encoding bypass, continuation attacks  
3. **Low**: General bugs, minor toxicity issues

### Comparative Analysis
- **Before/After Guardrails**: Measure defensive effectiveness
- **Model Comparisons**: Identify most secure model options
- **Version Tracking**: Monitor security regression/improvement

## 📋 Best Practices

### Regular Testing Schedule
```bash
# Daily security check (5-10 minutes)
python run_garak.py --priority high --timeout 120

# Weekly comprehensive scan (30-45 minutes)  
python run_garak.py --priority all --timeout 180

# Release validation (full scan)
python run_garak.py --timeout 300 --parallel-workers 2
```

### Result Documentation
- Save all benchmark results with timestamps
- Track configuration changes and their impact
- Document any manual validation of results
- Maintain a security testing log

### Integration with CI/CD
- Automated daily high-priority scans
- Block releases if critical vulnerabilities detected
- Generate security reports for stakeholders
- Trend analysis over time

## 🛠️ Troubleshooting

### Common Issues

**Garak installation problems:**
```bash
pip install garak
# or
conda install -c conda-forge garak
```

**Configuration file issues:**
- Verify `garak_config.json` has correct endpoint URLs
- Check SSL certificate settings (`verify: false` for self-signed)
- Validate authentication credentials

**Model connectivity issues:**
- Test direct API connection before running benchmarks
- Check firewall and network policies
- Verify model is running and responsive

### Debug Mode
```bash
python run_garak.py --priority high --parallel-workers 1 --timeout 60
```
Run with single worker and short timeout to isolate issues.

### Log Analysis
- Check `garak_benchmark.log` for detailed execution logs
- Review individual probe output files in results directory
- Look for patterns in timeout/failure rates

## 📚 Additional Resources

- [Garak Documentation](https://github.com/leondz/garak)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [AI Red Team Guide](https://airedteam.org/)
- [Responsible AI Practices](https://www.microsoft.com/en-us/ai/responsible-ai)

---

**Need help?** Check the `notes/` directory for additional examples and troubleshooting scripts.