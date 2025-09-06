# GenAI Security Benchmarking Metrics Guide

## Key Metrics for GenAI/LLM Testing

### 1. Primary Metrics (Must-Have)

#### Attack Success Rate (ASR)
- **Definition**: Percentage of attacks that successfully exploit the vulnerability
- **Formula**: `(Successful Attacks / Total Attempts) × 100`
- **Target**: Lower is better for defended systems
- **Use Case**: Core metric for evaluating model vulnerability

#### Defense Bypass Rate (DBR)
- **Definition**: Rate at which attacks bypass active guardrails
- **Formula**: `(Bypassed Defenses / Total Defended Attempts) × 100`
- **Relevance**: Critical when comparing NeMo vs GuardrailsAI effectiveness

#### Time to First Exploit (TTFE)
- **Definition**: Time taken to find the first successful vulnerability
- **Measurement**: Seconds/minutes from start
- **Use Case**: Indicates how quickly an attacker could compromise the system

### 2. Performance Metrics

#### Response Time Impact
- **Baseline**: Average response time without guardrails
- **With Defense**: Response time with guardrails active
- **Overhead**: `(Defended Time - Baseline Time) / Baseline Time × 100`
- **Acceptable Range**: <50% overhead for production

#### Throughput Metrics
- **Requests Per Minute (RPM)**: How many prompts processed
- **Tokens Per Second (TPS)**: For token-level analysis
- **Concurrency Handling**: Max parallel requests without failure

### 3. Coverage Metrics

#### Vulnerability Coverage
```python
coverage_score = {
    "prompt_injection": 0.85,  # 85% of known patterns tested
    "data_leakage": 0.75,
    "ssrf": 0.90,
    "idor": 0.80,
    "encoding_bypass": 0.70
}
```

#### Probe Completion Rate
- **Formula**: `(Completed Probes / Total Probes) × 100`
- **Target**: >95% for reliable results
- **Note**: Track why probes fail (timeout, error, skip)

### 4. Comparative Metrics (Garak vs NeMo vs GuardrailsAI)

| Metric | Garak | NeMo Guardrails | GuardrailsAI |
|--------|-------|-----------------|--------------|
| Setup Complexity | High | Medium | Low |
| Runtime Overhead | High (hours) | Low (ms) | Medium (seconds) |
| False Positive Rate | Low | Medium | Medium |
| Vulnerability Coverage | Comprehensive | Targeted | Configurable |
| Custom Probe Support | Excellent | Limited | Good |

### 5. Resource Utilization

#### Memory Usage
- Peak memory consumption during testing
- Memory leaks detection
- GPU utilization (if applicable)

#### API Cost Metrics (for OCI/Cloud Models)
- Tokens consumed per test
- Cost per vulnerability found
- Efficiency score: `Vulnerabilities Found / Dollar Spent`

## Recommended Reporting Format

### Executive Summary
```markdown
## Security Assessment Summary
- **Total Vulnerabilities Found**: 15
- **Critical**: 5 (Prompt Injection, Data Leakage)
- **High**: 7 (SSRF, IDOR)
- **Medium**: 3 (Encoding bypasses)
- **Defense Effectiveness**: 65% (GuardrailsAI blocked 65% of attacks)
- **Performance Impact**: +35ms average latency
- **Test Duration**: 2.5 hours
```

### Detailed Metrics Table
```python
metrics = {
    "test_execution": {
        "total_probes": 10,
        "successful_probes": 9,
        "failed_probes": 1,
        "total_attempts": 450,
        "total_runtime_hours": 2.5
    },
    "vulnerability_metrics": {
        "attack_success_rate": 33.5,
        "unique_vulnerabilities": 15,
        "false_positives": 2,
        "false_negatives": 1
    },
    "performance_metrics": {
        "avg_response_time_ms": 850,
        "p95_response_time_ms": 2100,
        "timeout_rate": 0.02
    },
    "defense_comparison": {
        "nemo_block_rate": 72,
        "guardrailsai_block_rate": 65,
        "combined_block_rate": 84
    }
}
```

## Optimization Tips for Faster Testing

### 1. Probe Selection Strategy
```python
# Progressive testing approach
quick_test = ["promptinject.basic", "jailbreak", "custom_probes.SsrfCustomProbe"]
standard_test = quick_test + ["leakreplicate", "encoding", "dan"]
comprehensive_test = standard_test + ["malwaregen", "continuation", "toxicity"]
```

### 2. Timeout Configuration
```python
timeout_config = {
    "local_models": 30,      # Ollama models
    "oci_models": 120,       # OCI can be slow
    "probe_timeout": 300,    # Overall probe timeout
    "retry_delay": 5         # Between retries
}
```

### 3. Parallel Execution (When Possible)
- Run different probe categories in parallel
- Use separate endpoints for each guardrail system
- Batch similar probes together

## Documenting Limitations

### Known Limitations Template
```markdown
## Testing Limitations

### 1. Runtime Constraints
- Full Garak suite requires 35-40 hours for comprehensive testing
- OCI models have 20+ second response times
- Rate limiting may affect results

### 2. Probe Relevance
- Some probes designed for classifiers (not applicable)
- TextAttack probes are pre-LLM era
- Custom probes may not cover all edge cases

### 3. Environmental Factors
- Network latency affects timing metrics
- Model temperature settings impact reproducibility
- Guardrail configurations may vary

### 4. Measurement Accuracy
- False positive rate: ~5-10%
- Some attacks may succeed due to model variance, not vulnerability
- Timing metrics include network overhead
```

## Quick Benchmark Script

```bash
#!/bin/bash
# Quick 30-minute benchmark

PROBES="promptinject jailbreak leakreplicate encoding custom_probes.SsrfCustomProbe"

for probe in $PROBES; do
    echo "Running probe: $probe"
    timeout 360 garak \
        --model_type rest \
        --model_name vulnerable_chatbot \
        --generator_option_file configs/garak/optimized_config.json \
        --probes "$probe" \
        --report_path "results/${probe}_$(date +%Y%m%d_%H%M%S).json" \
        || echo "Probe $probe failed or timed out"
done
```

## Recommended Metrics for Your Use Case

Given your setup with OCI models and 20+ second response times:

1. **Focus on High-Impact Probes**: Use the `recommended_probe_list` (10 probes, ~2-4 hours)
2. **Key Metrics to Track**:
   - Attack Success Rate (primary)
   - Defense Bypass Rate (for guardrail comparison)
   - Time per probe (for optimization)
   - Cost per test (OCI API costs)

3. **Reporting Priority**:
   - Executive summary with vulnerability counts
   - Comparative table (Garak vs NeMo vs GuardrailsAI)
   - Specific examples of successful attacks
   - Recommendations for remediation

4. **Documentation Focus**:
   - Why certain probes were selected/skipped
   - Environmental constraints (OCI latency)
   - Reproducibility instructions
   - Cost-benefit analysis
