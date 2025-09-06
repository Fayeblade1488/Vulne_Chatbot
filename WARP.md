# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

---

## Architecture Overview

This repository comprises a deliberately vulnerable Flask-based chatbot plus a modular, extensible benchmarking suite for evaluating LLM security posture. The platform includes:

- **Vulnerable Chatbot App (`vulne_chat.py`)**: Flask app with built-in prompt, data leakage, SQLi, RCE, and IDOR vulnerabilities, used as the live test target for attack/defense tooling.
- **Benchmarking Suite (`benchmarking/`, `vulne_bench`)**: Runs configurable scenarios using Garak, NeMo Guardrails, and GuardrailsAI. It supports parallel execution, custom probes, and generates metrics and reports.
- **Extensibility**: Add new security probes as Python classes or extend the NeMo action set for additional model behaviors.

```
Probes/Plugins → Benchmark Runner (run_all_benchmarks.py) → HTTP requests → Flask App → Model (Ollama/OCI) & Guardrails → Response/Detection → Reports
```

- Probes: `benchmarking/vulne_bench/custom_probes.py`
- Plugins: `benchmarking/vulne_bench/plugin_interface.py`
- NeMo Actions: `config_NeMo/actions.py`

---

## Setup and Install

**Python 3.11+ is required.**

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install core and benchmarking dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e benchmarking/
```

If you plan to use OCI, also install and configure the OCI CLI.

---

## Configuration: Minimum Viable .env

Example: `.env.real` (see `.env.example`)

- `OCI_GENAI_ENDPOINT`   # (if using OCI GenAI models)
- `OCI_COMPARTMENT_ID`   # (if using OCI GenAI models)
- `FLASK_SECRET_KEY`     # (optional, fallback key if not set)
- `GUARDRAILS_MODE`      # (options: none, nemo, guardrails-ai; default from env, CLI, or config file)
- `NEMO_LOG_LEVEL`       # (optional)

Sensitive API keys for actual model invocation must be present (see `config.py`). Precedence: environment variables > config file defaults.

---

## Run (Native)

### Start Vulnerable Chatbot (Flask, native)

```bash
# (ensure Ollama is running for local models)
ollama serve

# With the venv active and .env.real present:
python vulne_chat.py
```

- By default, listens on port 7000.
- Health check: `http://localhost:7000/health`
- Web UI: `http://localhost:7000/`

---

## Run (Docker)

### Build and Run the Entire Stack

```bash
docker build -t vulne-chatbot .
docker run -p 7000:7000 --env-file .env.real -it vulne-chatbot
```

- App will be available on `http://localhost:7000/`

---

## Benchmarking: Commands and Workflow

All benchmarking tools are in `benchmarking/`. The three orchestrated tools (Garak, NeMo Guardrails, GuardrailsAI) are run via one canonical workflow:

### 1. Validate or Create Benchmark Config

Validate an existing config:
```bash
vulne-config validate benchmarking/vulne_bench/config.json
```

Or create a new config:
```bash
vulne-config create benchmarking/vulne_bench/config.json
```

Show section or compare configs:
```bash
vulne-config show benchmarking/vulne_bench/config.json --section garak
vulne-config compare old.json new.json
```

### 2. Run All Benchmarks and Generate Report

```bash
python benchmarking/run_all_benchmarks.py --target-url http://localhost:7000/chat --models mistral:latest,oci:cohere.command-r-plus --output-dir results
```

- Per-tool raw and summary results appear in the output directory (timestamped):
  - `garak/`, `nemo/`, `guardrailsai/`
  - Final report: `summary_report.md` and visualizations

---

## Configuration Management

- All benchmarking config ops are rooted in `benchmarking/vulne_bench/config_tool.py`:
  - `validate`, `create`, `update`, `show`, `compare`
- Schema enforcement (required keys, error reporting) is in `config_validator.py`.
- CLI provides help/long descriptions. Example:

```bash
vulne-config validate benchmarking/vulne_bench/config.json
```

See CLI for subcommands and usage.

---

## Extensibility

### Probes (Benchmarking)
- Add new probe classes to `benchmarking/vulne_bench/custom_probes.py` or use the `probe_template.py` scaffold.
- Required: subclass `garak.probes.base.Probe`, define `prompts`, `tags`, and `detector_name`.
- Register probe by adding its key to the config file’s `probes` list.

### Actions (NeMo Guardrails)
- Add new actions in `config_NeMo/actions.py` and register using `app.register_action("name", func)` in `init()`.
- Reference from NeMo config YAML as needed.

---

## Command Palette (Quick Reference)

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -e benchmarking/

# Run Flask app natively
ollama serve        # local model inference
python vulne_chat.py

# Run with Docker
docker build -t vulne-chatbot .
docker run -p 7000:7000 --env-file .env.real -it vulne-chatbot

# Benchmark lifecycle
vulne-config validate benchmarking/vulne_bench/config.json
python benchmarking/run_all_benchmarks.py --target-url http://localhost:7000/chat --models mistral:latest,oci:cohere.command-r-plus --output-dir results

# Results
# See results in output/summary_report.md and output visualizations
```

---

## References

- `README.md` — Quickstart, architecture, and run instructions
- `requirements.txt`, `benchmarking/requirements.txt` — All dependencies (core and for benchmarking)
- `.env.example`, `config.py` — Environment/configuration settings
- `Dockerfile` — Canonical Docker build/run
- `vulne_chat.py` — Main application entrypoint (Flask API/UI)
- `benchmarking/README.md`, `benchmarking/vulne_bench/README.md` — Benchmark suite overview/setup
- `benchmarking/vulne_bench/config_tool.py` — Benchmark config validation/generation/updating commands
- `benchmarking/vulne_bench/custom_probes.py`, `probe_template.py` — Add or extend benchmarking probes
- `config_NeMo/actions.py` — Add/extend NeMo Guardrails actions

---

## Troubleshooting (From Codebase)

- Config validation errors will print detailed schema failures to the console with an ✗ prefix, e.g.:
  `✗ Configuration validation failed: Missing required section: garak`
- If the Flask app doesn’t start, check `.env.real` for required fields or port conflicts on 7000.
- Always check benchmarking logs in output directories (`garak_benchmark.log`, `nemo_benchmark.log`, etc.) for details.

---

This WARP.md is maintained as the canonical, code-backed reference for setting up, running, testing, and extending the Vulne_Chatbot security benchmarking environment.
