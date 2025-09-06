# Garak Guidance: Probes, Metrics, and Limitations

This document provides answers to common questions regarding the use of the Garak LLM vulnerability scanner, tailored for the `Vulne_Chatbot` project.

---

### 1. Which Garak probes are most relevant for GenAI/LLM/chatbot testing?

Garak has over 150 probes, but many are designed for specific model types (e.g., classifiers). For a conversational GenAI application like `Vulne_Chatbot`, it's best to focus on probes that test for LLM-specific vulnerabilities. A targeted approach is more efficient than running the full suite.

**Top Recommended Probes:**

*   **Prompt Injection & Jailbreaking:** These are the most critical for chatbots.
    *   `promptinject`: A general-purpose probe for various injection attacks.
    *   `dan`: Tests the classic "Do Anything Now" and other jailbreak variants.
    *   `jailbreak`: A collection of community-sourced jailbreak prompts.
    *   `continuation`: Checks if the model can be prompted to continue harmful or inappropriate text.

*   **Data Leakage:** Crucial for this project, as the chatbot is designed to leak data.
    *   `leakreplicate`: Attempts to get the model to reproduce parts of its training data or prompt.
    *   `knownbugs`: Tests for known vulnerabilities that could lead to data exposure.
    *   `idor_custom.IdorCustomProbe`: Our custom probe to test for Insecure Direct Object References.

*   **SSRF & Insecure Commands:**
    *   `ssrf_custom.SsrfCustomProbe`: Our custom probe to test for Server-Side Request Forgery.
    *   `exploitation`: Probes for vulnerabilities like template injection that could lead to code execution.

*   **Harmful Content & Misinformation:**
    *   `toxicity`: Checks if the model can be prompted to generate toxic content.
    *   `misinformation`: Tests the model's propensity to generate false or misleading information.

*   **Evasion Techniques:**
    *   `encoding`: Tests if the model can be manipulated by encoded prompts (e.g., Base64, ROT13).

**Strategy:**
Start with a focused set of 15-20 probes from the categories above. This provides excellent coverage of the most significant risks for LLMs without the extreme runtime of a full scan.

---

### 2. Which metrics make the most sense to report?

While Garak provides a pass/fail count, a robust report requires more nuanced metrics to fairly evaluate the security posture of a model.

**Key Metrics to Report:**

*   **Success Rate / Detection Rate:** The percentage of probes that successfully detected a vulnerability (i.e., caused a failure in the model). This is the primary indicator of a tool's effectiveness.
*   **Coverage:** The percentage of probes that completed successfully without errors. A low coverage rate might indicate issues with the test setup or model stability.
*   **Runtime:** Total and average time per probe. This is critical for understanding the efficiency of the testing process, especially given the long runtimes you've experienced.
*   **Vulnerability-Specific Metrics:**
    *   **Detections by Category:** A breakdown of successful attacks by type (e.g., 10 prompt injections, 5 data leaks). This helps prioritize mitigation efforts.
    *   **Precision & Recall:** (As implemented in our scripts) This helps measure the accuracy of your detectors. 
        *   **Precision:** Of all the vulnerabilities detected, how many were actual vulnerabilities? (True Positives / (True Positives + False Positives))
        *   **Recall:** Of all the actual vulnerabilities present, how many were detected? (True Positives / (True Positives + False Negatives))
*   **Failure Analysis:** A list of probes that failed to run, along with their error messages. This is crucial for debugging the benchmarking suite itself.

---

### 3. How best to document limitations?

Transparently documenting the limitations of the testing process is essential for interpreting the results correctly.

**Recommended Approach:**

Create a `LIMITATIONS.md` file or a dedicated section in the main `README.md` that covers the following points:

*   **Runtime Constraints:** Clearly state that a full Garak scan is time-prohibitive (e.g., "A full scan of all 150+ probes can take over 40 hours per model"). Explain that the suite uses a curated list of probes to balance thoroughness and efficiency.
*   **"Unknown Probes" / Errors:** Explain that Garak may fail on certain probes due to model incompatibility, timeouts, or bugs in the probe itself. Document the solution used here: a retry mechanism and the ability to skip failing probes.
*   **Timeout Issues:** Note that slow models (like some OCI models) may require longer timeouts. Document that the timeout is configurable in `config.json`.
*   **Coverage Gaps:** Be clear that the selected probes, while relevant, do not represent an exhaustive list of all possible attacks. Novel or zero-day attacks may not be detected. Recommend supplementing the automated scan with manual red-teaming.
*   **Detector Reliability:** The detection of a successful attack depends on the `parse_garak_output` function and the detectors. These are based on keyword matching and may not be 100% accurate. False positives and negatives are possible.
*   **Environment Dependencies:** Note that the results depend on the specific versions of the tools (Garak, NeMo, etc.) and the models being tested. The provided `Dockerfile` helps mitigate this by creating a consistent environment.
