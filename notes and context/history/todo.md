```md
Okay so here is a quick TL;DR of my project:

I built a vulnerable chatbot app (Vulne_Chatbot) as a test target.

Goal: benchmark Garak (I initially included TextAttack, but it’s not really useful for GenAI/LLMs beyond predAI) alongside NeMo Guardrails and GuardrailsAI, against realistic GenAI vulnerabilities (prompt injection, leakage, SSRF, IDOR).

For Garak specifically, I’d love advice on:

 -- Which probes are most relevant for GenAI/LLM/chatbot testing (some look more classifier-focused).

 -- Which metrics make the most sense to report (success rate, coverage, runtime, etc.).

 -- How best to document limitations (e.g. very long runs, “unknown probes”).

Extra context:
I tried running Garak in “full mode” against a model hosted on OCI through my vulnerable app. It took ~39 hours just to reach ~21% of the 153 probes. At first I hit timeouts, so I tweaked Garak’s timeout code for OCI (since responses can take >20s) to 100. Later one probe kept failing, so I wrote a bash script to run each probe individually (retry once, then skip). That’s working, but it’s very slow. I recorded logs (dump.log) for reproducibility.

Any quick notes that could help on this subject would be much helpful
```