# GenAI Security Evaluation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, containerized testing environment for evaluating AI model vulnerabilities, prompt injection attacks, and defensive mechanisms. This platform provides a deliberately vulnerable Flask application and an extensible benchmarking suite to test AI security tools like Garak, NeMo Guardrails, and GuardrailsAI.

---

## Features

-   **Vulnerable Target App:** A Flask-based chatbot with intentional vulnerabilities (Data Leakage, SQLi, RCE, IDOR) for realistic testing.
-   **Multi-Model Support:** Test against local Ollama models and cloud-based OCI GenAI models.
-   **Automated Benchmarking Suite:** A fully packaged (`vulne_bench`) and configurable suite for running security tools.
-   **Extensible Probes:** Includes custom Garak probes for SSRF and IDOR, with an easy-to-extend structure.
-   **Robust & Parallelized Testing:** Hardened scripts with retries, timeouts, and parallel execution to speed up tests.
-   **Comprehensive Reporting:** Generates detailed Markdown reports and visualizations of benchmark results.
-   **Containerized Environment:** A `Dockerfile` is included for easy, reproducible deployment of the entire application stack.
-   **CI/CD Integration:** A GitHub Actions workflow is included to automate security scans and basic testing.

## Project Architecture

This project consists of two main components:

1.  **The Vulnerable Chatbot (`vulne_chat.py`):** A Flask application that serves a web UI and a `/chat` API endpoint. It is designed to be insecure to provide a target for security tools.
2.  **The Benchmarking Suite (`benchmarking/`):** An installable Python package (`vulne_bench`) that contains the tools and scripts to automate security testing against the chatbot. It is highly configurable via `vulne_bench/config.json`.

## Getting Started

### Prerequisites

-   Python 3.11+
-   Docker
-   [Ollama](https://ollama.ai/) (for running local models)
-   [OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm) (for running OCI GenAI models)

### 1. Installation

Clone the repository and install the required dependencies. It is recommended to use a virtual environment.

```bash
# Clone the repository
git clone <repository-url>
cd Vulne_Chatbot

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies for the chatbot and the benchmark suite
pip install --upgrade pip
pip install -r requirements.txt
pip install -e benchmarking/
```

### 2. Configuration

If you plan to use OCI GenAI models, you need to configure your credentials.

```bash
# Set up your OCI credentials
oci setup config

# Create and edit the environment file for the application
cp .env.example .env.real
nano .env.real # Add your OCI_COMPARTMENT_ID and other details
```

## How to Use

### Running the Vulnerable Chatbot

You can run the chatbot application either directly with Flask or using Docker.

**Option A: Run with Flask**

```bash
# Ensure Ollama is running in another terminal if you use local models
ollama serve

# Start the Flask application
python vulne_chat.py
```

**Option B: Run with Docker (Recommended)**

```bash
# Build and run the Docker container
docker build -t vulne-chatbot .
docker run -p 7000:7000 -it vulne-chatbot
```

The application will be available at `http://127.0.0.1:7000`.

### Running the Benchmarking Suite

The benchmarking suite is controlled by the `run-vulne-bench` command, which becomes available after you install the package.

1.  **Ensure the Vulnerable Chatbot is running.**
2.  **Configure the benchmark** by editing `benchmarking/vulne_bench/config.json`.
3.  **Run the suite** from the project's root directory:

    ```bash
    run-vulne-bench --config benchmarking/vulne_bench/config.json
    ```

Results will be saved to a `master_results_[timestamp]` directory.

## Documentation & Legal

-   **[Full How-To Guide](./GUIDE.md):** A detailed user manual for the benchmarking suite.
-   **[Garak Guidance](./GARAK_GUIDANCE.md):** Answers to common questions about using Garak effectively.
-   **[Disclaimer](./DISCLAIMER.md):** Important ethical use and legal guidelines.
-   **[License](./LICENSE):** This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
