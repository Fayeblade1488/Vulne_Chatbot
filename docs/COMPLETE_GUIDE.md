# 📚 Complete Vulne_Chatbot Testing Suite Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Installation & Setup](#installation--setup)
3. [Core Features](#core-features)
4. [Advanced Testing](#advanced-testing)
5. [Monitoring & Observability](#monitoring--observability)
6. [CI/CD Integration](#cicd-integration)
7. [API Reference](#api-reference)
8. [Best Practices](#best-practices)

---

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# Clone the repository
git clone https://github.com/yourusername/Vulne_Chatbot.git
cd Vulne_Chatbot

# Use the Makefile for quick setup
make setup-dev
make run
# In another terminal
make frontend
```

Visit http://localhost:3000 for the UI or http://localhost:7000 for the API.

---

## 📦 Installation & Setup

### Prerequisites

- **Python 3.9+** (3.11 recommended)
- **Node.js 18+** and npm
- **Docker** (optional but recommended)
- **Ollama** for local model testing
- **Redis** for distributed testing (optional)
- **PostgreSQL** for persistent storage (optional)

### Step-by-Step Installation

#### 1. Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e benchmarking/

# Install frontend dependencies
cd frontend
npm install
cd ..
```

#### 2. Configuration

Create `.env.real` from the template:

```bash
cp .env.example .env.real
```

Edit `.env.real`:

```env
# Model Configuration
OLLAMA_HOST=http://localhost:11434
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
COHERE_API_KEY=your-key-here

# OCI Configuration (if using Oracle Cloud)
OCI_GENAI_ENDPOINT=https://inference.generativeai.us-chicago-1.oci.oraclecloud.com
OCI_COMPARTMENT_ID=your-compartment-id

# Security Settings
FLASK_SECRET_KEY=your-secret-key-here
GUARDRAILS_MODE=nemo  # Options: none, nemo, guardrails-ai

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost:5432/vulne_db
REDIS_URL=redis://localhost:6379

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### 3. Install Ollama Models

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull models for testing
ollama pull mistral:latest
ollama pull llama2:latest
ollama pull codellama:latest
```

#### 4. Database Setup (Optional)

```bash
# Using Docker
docker run -d \
  --name vulne-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=vulne_db \
  -p 5432:5432 \
  postgres:14

# Using Docker for Redis
docker run -d \
  --name vulne-redis \
  -p 6379:6379 \
  redis:alpine
```

---

## 🎯 Core Features

### 1. Vulnerable Chatbot Application

The main application (`app/vulne_chat.py`) includes deliberate vulnerabilities:

```python
# Start the vulnerable app
python app/vulne_chat.py

# Test endpoints
curl http://localhost:7000/health
curl -X POST http://localhost:7000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "mistral:latest"}'
```

**Built-in Vulnerabilities:**
- Prompt injection
- Data leakage
- SQL injection
- Remote code execution
- IDOR (Insecure Direct Object Reference)
- XSS (Cross-Site Scripting)

### 2. Frontend Dashboard

```bash
# Start the React frontend
cd frontend
npm start
```

**Features:**
- Real-time vulnerability monitoring
- Interactive benchmarking controls
- Visual analytics and reporting
- Test configuration management

### 3. Benchmarking Suite

Run comprehensive security tests:

```bash
# Run all benchmarks
python benchmarking/run_all_benchmarks.py \
  --target-url http://localhost:7000/chat \
  --models mistral:latest,llama2:latest \
  --output-dir results

# Run specific benchmark
python benchmarking/run_garak.py \
  --target-url http://localhost:7000/chat \
  --model mistral:latest
```

### 4. Security Monitoring

Start real-time security monitoring:

```bash
# Start the security monitor
python scripts/security_monitor.py

# Monitor will detect:
# - Anomalies in metrics
# - Attack patterns
# - Threshold violations
# - Coordinated attacks
```

### 5. AI-Powered Probe Generation

Generate custom attack probes:

```bash
# Generate probes using AI
python scripts/ai_probe_generator.py

# Use generated probes in testing
python benchmarking/run_garak.py \
  --probes generated_probes.json
```

### 6. Multi-Model Comparison

Compare vulnerabilities across models:

```bash
# Run comparative analysis
python scripts/multi_model_tester.py

# Generates:
# - model_comparison_report.html
# - model_comparison_charts.png
# - Statistical analysis
```

---

## 🔬 Advanced Testing

### Distributed Testing with Celery

```python
# celery_config.py
from celery import Celery

app = Celery('vulne_bench',
             broker='redis://localhost:6379',
             backend='redis://localhost:6379')

@app.task
def test_probe(model, probe):
    # Test implementation
    pass

# Start workers
celery -A celery_config worker --loglevel=info --concurrency=4
```

### Custom Probe Development

Create custom probes in `benchmarking/vulne_bench/custom_probes.py`:

```python
from garak.probes.base import Probe

class CustomVulnerabilityProbe(Probe):
    """Custom probe for specific vulnerability"""
    
    name = "custom_vulnerability"
    description = "Tests for custom vulnerability pattern"
    tags = ["custom", "security"]
    
    prompts = [
        "Your custom attack prompt here",
        "Another attack variant"
    ]
    
    def check(self, response):
        # Custom detection logic
        return "vulnerability_indicator" in response.lower()
```

### Defense Mechanism Testing

Test guardrail effectiveness:

```python
# defense_tester.py
import asyncio
from scripts.defense_tester import DefenseTester

async def test_defenses():
    tester = DefenseTester()
    
    # Test bypass rates
    bypass_rate = await tester.test_bypass_rate(
        guardrail="nemo",
        probes=["prompt_injection", "jailbreak"]
    )
    
    # Test false positive rates
    fp_rate = await tester.test_false_positives(
        guardrail="guardrails-ai",
        benign_inputs=["normal conversation"]
    )
    
    print(f"Bypass Rate: {bypass_rate:.2%}")
    print(f"False Positive Rate: {fp_rate:.2%}")

asyncio.run(test_defenses())
```

### API Security Testing

```bash
# GraphQL testing
python scripts/api_security_tester.py \
  --type graphql \
  --endpoint http://localhost:7000/graphql

# REST API fuzzing
python scripts/api_security_tester.py \
  --type rest \
  --fuzz \
  --endpoint http://localhost:7000/api

# WebSocket testing
python scripts/api_security_tester.py \
  --type websocket \
  --endpoint ws://localhost:7000/ws
```

---

## 📊 Monitoring & Observability

### Prometheus Setup

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'vulne_chatbot'
    static_configs:
      - targets: ['localhost:7000']
    metrics_path: '/metrics'
  
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
```

Start Prometheus:

```bash
docker run -d \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Grafana Dashboard

```bash
# Start Grafana
docker run -d \
  -p 3001:3000 \
  --name grafana \
  grafana/grafana

# Import dashboard
# 1. Navigate to http://localhost:3001
# 2. Login (admin/admin)
# 3. Import dashboard from `monitoring/grafana-dashboard.json`
```

### Logging with ELK Stack

```yaml
# docker-compose.elk.yml
version: '3'
services:
  elasticsearch:
    image: elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  
  logstash:
    image: logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
  
  kibana:
    image: kibana:7.14.0
    ports:
      - "5601:5601"
```

### Custom Metrics

Add custom metrics to your application:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
vulnerability_detected = Counter(
    'vulnerabilities_detected_total',
    'Total vulnerabilities detected',
    ['model', 'type']
)

response_time = Histogram(
    'model_response_duration_seconds',
    'Model response time',
    ['model']
)

active_tests = Gauge(
    'active_tests',
    'Number of active tests running'
)

# Use in code
vulnerability_detected.labels(model='gpt-4', type='prompt_injection').inc()
response_time.labels(model='gpt-4').observe(1.23)
active_tests.set(5)
```

---

## 🔄 CI/CD Integration

### GitHub Actions

The repository includes a comprehensive GitHub Actions workflow:

```yaml
# .github/workflows/security-testing.yml
name: Security Testing Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
```

### Manual Trigger

```bash
# Trigger workflow manually
gh workflow run security-testing.yml \
  --field test_level=comprehensive
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - security
  - benchmark
  - deploy

security-scan:
  stage: security
  script:
    - pip install bandit safety
    - bandit -r app/ benchmarking/
    - safety check
  artifacts:
    reports:
      junit: security-report.xml
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        
        stage('Security Scan') {
            steps {
                sh 'make security-scan'
            }
        }
        
        stage('Benchmark') {
            when {
                branch 'main'
            }
            steps {
                sh 'make benchmark'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'results/**/*'
            publishHTML([
                reportDir: 'results',
                reportFiles: 'benchmark-report.html',
                reportName: 'Benchmark Report'
            ])
        }
    }
}
```

---

## 📡 API Reference

### REST API Endpoints

#### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "message": "Your prompt here",
  "model": "mistral:latest",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

#### Metrics Endpoint
```http
GET /api/metrics

Response:
{
  "total_tests": 1234,
  "vulnerabilities_found": 56,
  "success_rate": 0.95,
  "avg_response_time": 1.23
}
```

#### Benchmark Control
```http
POST /api/benchmarks/run
Content-Type: application/json

{
  "models": ["mistral:latest", "llama2:latest"],
  "probes": ["prompt_injection", "data_leakage"],
  "parallel": true,
  "timeout": 300
}
```

### WebSocket API

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:7000/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'metrics'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Metrics update:', data);
};
```

### GraphQL API

```graphql
# Query vulnerabilities
query GetVulnerabilities($model: String!) {
  vulnerabilities(model: $model) {
    id
    type
    severity
    description
    detectedAt
    probe
    response
  }
}

# Mutation to run test
mutation RunTest($input: TestInput!) {
  runTest(input: $input) {
    success
    results {
      model
      vulnerabilityDetected
      responseTime
    }
  }
}
```

---

## 🎯 Best Practices

### Security Testing

1. **Always test in isolated environments**
   - Use Docker containers
   - Separate test databases
   - Network isolation

2. **Rate limiting and timeouts**
   ```python
   # Add rate limiting
   from flask_limiter import Limiter
   
   limiter = Limiter(
       app,
       key_func=lambda: get_remote_address(),
       default_limits=["100 per hour"]
   )
   
   @app.route('/chat')
   @limiter.limit("10 per minute")
   def chat():
       pass
   ```

3. **Sanitize all inputs**
   ```python
   import bleach
   
   def sanitize_input(text):
       return bleach.clean(text, tags=[], strip=True)
   ```

### Performance Optimization

1. **Use caching**
   ```python
   from functools import lru_cache
   import redis
   
   cache = redis.Redis()
   
   @lru_cache(maxsize=1000)
   def expensive_operation(param):
       # Cached operation
       pass
   ```

2. **Parallel processing**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   import asyncio
   
   async def parallel_tests(probes):
       with ThreadPoolExecutor(max_workers=10) as executor:
           futures = [executor.submit(test_probe, p) for p in probes]
           results = [f.result() for f in futures]
       return results
   ```

3. **Database optimization**
   ```sql
   -- Add indexes for common queries
   CREATE INDEX idx_vulnerabilities_model ON vulnerabilities(model);
   CREATE INDEX idx_test_results_timestamp ON test_results(timestamp);
   ```

### Monitoring Best Practices

1. **Set up alerts**
   ```yaml
   # alerting-rules.yml
   groups:
     - name: vulnerability_alerts
       rules:
         - alert: HighVulnerabilityRate
           expr: rate(vulnerabilities_detected_total[5m]) > 0.1
           for: 5m
           annotations:
             summary: "High vulnerability detection rate"
   ```

2. **Log aggregation**
   ```python
   import structlog
   
   logger = structlog.get_logger()
   
   logger.info("test_completed",
               model="gpt-4",
               vulnerability_detected=True,
               response_time=1.23)
   ```

3. **Distributed tracing**
   ```python
   from opentelemetry import trace
   
   tracer = trace.get_tracer(__name__)
   
   with tracer.start_as_current_span("test_probe"):
       # Your test code
       pass
   ```

### Development Workflow

1. **Use pre-commit hooks**
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 22.3.0
       hooks:
         - id: black
     
     - repo: https://github.com/PyCQA/flake8
       rev: 4.0.1
       hooks:
         - id: flake8
     
     - repo: https://github.com/PyCQA/bandit
       rev: 1.7.4
       hooks:
         - id: bandit
   ```

2. **Version control best practices**
   ```bash
   # Feature branch workflow
   git checkout -b feature/new-probe
   git add .
   git commit -m "feat: add custom probe for XSS detection"
   git push origin feature/new-probe
   # Create pull request
   ```

3. **Documentation standards**
   ```python
   def test_vulnerability(model: str, probe: str) -> TestResult:
       """
       Test a specific vulnerability on a model.
       
       Args:
           model: Name of the model to test
           probe: The attack probe to use
       
       Returns:
           TestResult containing success status and details
       
       Raises:
           ModelNotFoundError: If the model doesn't exist
           TimeoutError: If the test times out
       
       Example:
           >>> result = test_vulnerability("gpt-4", "ignore instructions")
           >>> print(result.vulnerability_detected)
           True
       """
       pass
   ```

---

## 🔗 Additional Resources

- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [AI Security Best Practices](https://github.com/securing-ai/ai-security-best-practices)
- [Garak Documentation](https://github.com/leondz/garak)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)

---

## 📧 Support

For issues and questions:
1. Check the [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
2. Search [existing issues](https://github.com/yourusername/Vulne_Chatbot/issues)
3. Create a new issue with detailed information
4. Join our [Discord community](https://discord.gg/vulnechat)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
