# Vulne_Chatbot - GenAI Security Evaluation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A deliberately vulnerable chatbot application designed for testing AI security tools and benchmarking guardrail effectiveness.

## Quick Start

```bash
# Clone and setup
git clone <repository>
cd Vulne_Chatbot
make setup

# Run the vulnerable chatbot
make run

# Run benchmarks
make benchmark
```

See [docs/guides/QUICKSTART.md](docs/guides/QUICKSTART.md) for detailed instructions.

## Features

- **Vulnerable Target App:** Flask-based chatbot with intentional vulnerabilities (Data Leakage, SQLi, RCE, IDOR)
- **Multi-Model Support:** Local Ollama models and cloud-based OCI GenAI models
- **Automated Benchmarking:** Extensible suite for Garak, NeMo Guardrails, and GuardrailsAI
- **Custom Probes:** SSRF, IDOR, and more security test probes
- **Comprehensive Reporting:** Detailed metrics and visualizations
- **Containerized:** Docker and docker-compose support

## Project Structure

```
Vulne_Chatbot/
├── app/              # Flask application
├── benchmarking/     # Security benchmarking suite
├── configs/          # Configuration files
├── scripts/          # Utility scripts
├── tests/            # Test suite
├── docs/             # Documentation
└── data/             # Results and examples
```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Benchmarking Guide](docs/guides/BENCHMARKING.md)
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Security Policy](docs/legal/SECURITY.md)

## License

MIT - see [LICENSE](docs/legal/LICENSE)

## Disclaimer

This application contains deliberate security vulnerabilities for testing purposes. 
See [DISCLAIMER](docs/legal/DISCLAIMER.md) for important usage guidelines.
