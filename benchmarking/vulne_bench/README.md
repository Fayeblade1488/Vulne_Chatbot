# Vulne_Chatbot Benchmarking Suite

## Overview
This suite automates benchmarking of Garak, NeMo Guardrails, and GuardrailsAI against the vulnerable chatbot. It handles long runs with parallelization, retries, selective probes, and generates reports with metrics like success rate, coverage, runtime, and detected vulnerabilities.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Ensure Vulne_Chatbot is running at http://127.0.0.1:7000/chat
3. Run: `python run_all_benchmarks.py --target-url <url> --models <comma-separated models> --output-dir results`

## Features
-  Selective Garak probes for GenAI focus
-  Parallel execution to reduce runtime
-  Automatic metric calculation and visualization
-  Error handling with retries and logging

## Customization
-  Edit probes/test cases in respective scripts
-  Adjust workers/timeouts for performance
