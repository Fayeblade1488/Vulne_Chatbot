# Full How-To Guide for the GenAI Security Evaluation Platform

This guide provides a detailed walkthrough for setting up, running, and extending the GenAI Security Evaluation Platform and its associated benchmarking suite.

---

## 1. Installation and Setup

This section covers the detailed steps to get the project running.

### Step 1.1: Prerequisites

Ensure the following tools are installed on your system:

-   **Python:** Version 3.11 or higher.
-   **Docker:** For containerized deployment. [Install Docker](https://docs.docker.com/get-docker/)
-   **Ollama:** Required for running local LLMs. [Install Ollama](https://ollama.ai/)
-   **OCI CLI:** Required only if you intend to test models hosted on Oracle Cloud Infrastructure. [Install OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm)

### Step 1.2: Clone and Install Dependencies

```bash
# 1. Clone the repository from your source control
git clone <repository-url>
cd Vulne_Chatbot

# 2. Create a Python virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 3. Install all required Python packages
pip install --upgrade pip

# Install chatbot dependencies
pip install -r requirements.txt

# Install the benchmarking suite in editable mode
pip install -e benchmarking/
```

### Step 1.3: Configure Environment Variables

If you are using OCI GenAI models, you must provide your cloud credentials.

```bash
# 1. Copy the example environment file
cp .env.example .env.real

# 2. Edit the .env.real file with your details
# You can use any text editor, e.g., nano, vim, or VS Code
nano .env.real
```

Your `.env.real` file should look like this:

```ini
# Your OCI tenancy's compartment OCID
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..your-compartment-id

# The API endpoint for your OCI region
OCI_GENAI_ENDPOINT=https://inference.generativeai.us-chicago-1.oci.oraclecloud.com

# A random string for Flask session security
FLASK_SECRET_KEY=a_very_secret_key_12345
```

---

## 2. Running the Vulnerable Chatbot

The chatbot application must be running to serve as a target for the benchmarking suite.

### Option A: Run with Docker (Recommended)

This is the easiest and most reliable method.

```bash
# 1. Build the Docker image
docker build -t vulne-chatbot .

# 2. Run the container
# This command forwards port 7000 from the container to your local machine
docker run -p 7000:7000 -it vulne-chatbot
```

### Option B: Run Directly with Flask

Use this method if you are not using Docker.

```bash
# 1. Make sure your virtual environment is activated
source venv/bin/activate

# 2. If using local models, ensure Ollama is running in a separate terminal
ollama serve

# 3. Start the Flask application
python vulne_chat.py
```

### Verify the Application is Running

Open your web browser and navigate to `http://127.0.0.1:7000`. You should see the GenAI Security Evaluation Platform interface.

---

## 3. Running the Benchmarking Suite

### Step 3.1: Configure the Benchmark

All benchmark settings are controlled by the `benchmarking/vulne_bench/config.json` file. Before running, you can customize:

-   **`garak.probes`**: The list of Garak probes to run. Add or remove probes to target specific vulnerabilities.
-   **`nemo.test_cases`**: The list of prompts to test NeMo Guardrails against.
-   **`guardrailsai.test_cases`**: The list of prompts to test GuardrailsAI against.
-   **`general.models`**: The list of models to be tested by Garak.

### Step 3.2: Execute the Suite

The `run-vulne-bench` command becomes available after you install the package.

```bash
# Ensure the Vulnerable Chatbot is running in a separate terminal or Docker container

# Run the full benchmark suite using the default config path
run-vulne-bench
```

The script will execute the tests for Garak, NeMo, and GuardrailsAI sequentially. You will see progress bars and logging output in your terminal.

### Step 3.3: Understanding the Output

The suite will create a new directory named `master_results_[timestamp]` in your project root. Inside, you will find:

-   **`garak_results/`**: Raw logs and JSON results from the Garak run.
-   **`nemo_results/`**: JSON results from the NeMo run.
-   **`guardrailsai_results/`**: JSON results from the GuardrailsAI run.
-   **`final_report/`**: The final summary report (`summary_report.md`) and visualizations (`.png` files).

---

## 4. Advanced Usage

### Adding New Custom Garak Probes

1.  Open `benchmarking/vulne_bench/custom_probes.py`.
2.  Create a new class that inherits from `garak.probes.base.Probe`.
3.  Define the `prompts` list with your new attack strings.
4.  Add the new probe's class name to the `probes` list in `config.json` (e.g., `"custom_probes.MyNewProbe"`).

### Adding New Test Cases for NeMo/GuardrailsAI

1.  Open `benchmarking/vulne_bench/config.json`.
2.  Navigate to the `nemo` or `guardrailsai` section.
3.  Add a new JSON object to the `test_cases` array with your desired `input`, `expected_block`/`expected_fail`, and `type`.

---

## 5. Troubleshooting

-   **Connection Refused Error:** This usually means the `Vulne_Chatbot` application is not running. Make sure it's active on `http://127.0.0.1:7000`.
-   **Garak `ModuleNotFoundError` for `custom_probes`:** This can happen if the benchmarking package was not installed correctly. Run `pip install -e benchmarking/` from the project root.
-   **OCI Authentication Errors:** Ensure your OCI config file (`~/.oci/config`) and the `.env.real` file are set up correctly with the right OCIDs and region.
-   **Ollama Model Not Found:** Make sure you have pulled the model using `ollama pull <model_name>` and that the Ollama service is running (`ollama serve`).
