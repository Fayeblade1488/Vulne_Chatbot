# Vulne_Chatbot Enhanced Benchmarking Suite

## 🚀 Quick Start - Solving the 39+ Hour Runtime Issue

The enhanced Garak benchmarker provides **massive performance improvements** and better GenAI focus:

### Fast Daily Security Check (5-15 minutes)
```bash
python run_garak.py --priority high --timeout 150
```
*Covers the 4 most critical GenAI vulnerabilities*

### Weekly Comprehensive Assessment (30-60 minutes)  
```bash
python run_garak.py --priority all --timeout 180
```
*Full security coverage for all relevant GenAI tests*

### OCI-Optimized Configuration
```bash
python run_garak.py --priority high --timeout 300 --parallel-workers 1
```
*Handles >20s OCI response times with proper timeout management*

## 📊 Key Improvements Over Original

| Aspect | Before | After |
|--------|--------|-------|
| Runtime | 39+ hours (21% completion) | 15 minutes (core vulnerabilities) |
| Timeout | Fixed 300s | Adaptive 60s-600s |
| Probe Selection | All 153 probes | 10 GenAI-relevant, prioritized |
| Retry Logic | Manual bash scripts | Automatic with smart handling |
| Documentation | Limited | Comprehensive with limitations |

## 🎯 Probe Selection Guidance

**High Priority (15 min):** `promptinject`, `jailbreak`, `dan`, `leakreplicate`  
**Medium Priority (45 min):** + `continuation`, `encoding`, `toxicity`, `misinformation`  
**Low Priority (60 min):** + `snowball`, `knownbugs`

## 📋 Available Tools

- `run_garak.py` - **Main enhanced benchmarker** (use this!)
- `validate_garak.py` - Functionality validation
- `examples.py` - Usage examples and configurations  
- `../GARAK_BENCHMARKING_GUIDE.md` - Comprehensive guide
- `../GARAK_IMPROVEMENTS_SUMMARY.py` - Improvement overview

## 🔧 Command Reference

```bash
# Get probe recommendations
python run_garak.py --list-probes

# Validate functionality  
python validate_garak.py

# See usage examples
python examples.py

# Debug mode
python run_garak.py --priority high --timeout 60 --parallel-workers 1
```

## 📚 Documentation

- **Comprehensive Guide**: `../GARAK_BENCHMARKING_GUIDE.md`
- **Limitations & Mitigations**: Documented with specific strategies
- **Performance Optimization**: Timeout recommendations for OCI/slow models
- **Metrics Guidance**: Which metrics to report and why

## 🏗️ Legacy Components

- `vuln/` - Original implementation  
- `vuvl2/` - Alternative implementation
- `notes/` - Manual bash scripts (for reference)

**Use the enhanced `benchmarking/run_garak.py` for all new testing.**

## Setup
1. Install dependencies: `pip install -r ../requirements.txt`
2. Ensure Vulne_Chatbot is running at http://127.0.0.1:7000/chat  
3. Run enhanced benchmarks with priority selection

For detailed setup and troubleshooting, see `../GARAK_BENCHMARKING_GUIDE.md`.
