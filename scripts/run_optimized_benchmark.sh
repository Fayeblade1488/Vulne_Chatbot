#!/bin/bash

# Optimized Garak Benchmark Runner for GenAI/LLM Testing
# Focuses on relevant probes with proper timeout handling

set -e

# Configuration
RESULTS_DIR="data/results/garak_benchmark_$(date +%Y%m%d_%H%M%S)"
CONFIG_FILE="configs/garak/optimized_config.json"
LOG_FILE="$RESULTS_DIR/benchmark.log"
SUMMARY_FILE="$RESULTS_DIR/summary.json"

# Create results directory
mkdir -p "$RESULTS_DIR"

# High-priority probes for GenAI testing (2-4 hours runtime)
PROBES=(
    "promptinject"
    "jailbreak"
    "dan"
    "leakreplicate"
    "encoding"
    "malwaregen"
    "continuation"
    "toxicity.simple"
    "custom_probes.SsrfCustomProbe"
    "custom_probes.IdorCustomProbe"
)

# Quick test probes (30 minutes runtime)
QUICK_PROBES=(
    "promptinject.basic"
    "jailbreak"
    "leakreplicate"
    "encoding"
    "custom_probes.SsrfCustomProbe"
)

# Function to run a single probe with retry
run_probe() {
    local probe=$1
    local attempt=1
    local max_attempts=2
    
    echo "[$(date)] Starting probe: $probe" | tee -a "$LOG_FILE"
    
    while [ $attempt -le $max_attempts ]; do
        echo "[$(date)] Attempt $attempt of $max_attempts for $probe" | tee -a "$LOG_FILE"
        
        # Run with timeout (5 minutes per probe)
        if timeout 300 garak \
            --model_type rest \
            --model_name vulnerable_chatbot \
            --generator_option_file "$CONFIG_FILE" \
            --probes "$probe" \
            --report_path "$RESULTS_DIR/${probe//\./_}_report.json" \
            --verbose \
            2>&1 | tee -a "$LOG_FILE"; then
            
            echo "[$(date)] ✓ Probe $probe completed successfully" | tee -a "$LOG_FILE"
            return 0
        else
            echo "[$(date)] ✗ Probe $probe failed (attempt $attempt)" | tee -a "$LOG_FILE"
            ((attempt++))
            
            if [ $attempt -le $max_attempts ]; then
                echo "[$(date)] Retrying in 5 seconds..." | tee -a "$LOG_FILE"
                sleep 5
            fi
        fi
    done
    
    echo "[$(date)] ✗ Probe $probe failed after all attempts" | tee -a "$LOG_FILE"
    return 1
}

# Parse command line arguments
MODE="standard"
if [ "$1" == "--quick" ]; then
    MODE="quick"
    PROBES=("${QUICK_PROBES[@]}")
    echo "Running in QUICK mode (30 minutes)" | tee -a "$LOG_FILE"
elif [ "$1" == "--full" ]; then
    # Add more probes for comprehensive testing
    PROBES+=(
        "misinformation"
        "privacy"
        "pii"
        "roleplay"
    )
    echo "Running in FULL mode (4-6 hours)" | tee -a "$LOG_FILE"
else
    echo "Running in STANDARD mode (2-4 hours)" | tee -a "$LOG_FILE"
fi

# Start benchmark
echo "================================================" | tee -a "$LOG_FILE"
echo "GenAI Security Benchmark Started" | tee -a "$LOG_FILE"
echo "Time: $(date)" | tee -a "$LOG_FILE"
echo "Mode: $MODE" | tee -a "$LOG_FILE"
echo "Total Probes: ${#PROBES[@]}" | tee -a "$LOG_FILE"
echo "Results Directory: $RESULTS_DIR" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"

# Track statistics
TOTAL_PROBES=${#PROBES[@]}
SUCCESSFUL_PROBES=0
FAILED_PROBES=0
START_TIME=$(date +%s)

# Initialize summary JSON
echo "{" > "$SUMMARY_FILE"
echo "  \"start_time\": \"$(date -Iseconds)\"," >> "$SUMMARY_FILE"
echo "  \"mode\": \"$MODE\"," >> "$SUMMARY_FILE"
echo "  \"total_probes\": $TOTAL_PROBES," >> "$SUMMARY_FILE"
echo "  \"probes\": [" >> "$SUMMARY_FILE"

# Run each probe
for i in "${!PROBES[@]}"; do
    probe="${PROBES[$i]}"
    echo "" | tee -a "$LOG_FILE"
    echo "[$((i+1))/$TOTAL_PROBES] Processing: $probe" | tee -a "$LOG_FILE"
    echo "------------------------------------------------" | tee -a "$LOG_FILE"
    
    PROBE_START=$(date +%s)
    
    if run_probe "$probe"; then
        ((SUCCESSFUL_PROBES++))
        STATUS="success"
    else
        ((FAILED_PROBES++))
        STATUS="failed"
    fi
    
    PROBE_END=$(date +%s)
    PROBE_DURATION=$((PROBE_END - PROBE_START))
    
    # Add to summary (with comma handling)
    if [ $i -gt 0 ]; then
        echo "," >> "$SUMMARY_FILE"
    fi
    echo -n "    {\"name\": \"$probe\", \"status\": \"$STATUS\", \"duration\": $PROBE_DURATION}" >> "$SUMMARY_FILE"
    
    echo "[$(date)] Probe duration: ${PROBE_DURATION}s" | tee -a "$LOG_FILE"
    echo "[$(date)] Progress: Success=$SUCCESSFUL_PROBES, Failed=$FAILED_PROBES" | tee -a "$LOG_FILE"
done

# Calculate total runtime
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))
HOURS=$((TOTAL_DURATION / 3600))
MINUTES=$(((TOTAL_DURATION % 3600) / 60))
SECONDS=$((TOTAL_DURATION % 60))

# Finalize summary JSON
echo "" >> "$SUMMARY_FILE"
echo "  ]," >> "$SUMMARY_FILE"
echo "  \"end_time\": \"$(date -Iseconds)\"," >> "$SUMMARY_FILE"
echo "  \"total_duration_seconds\": $TOTAL_DURATION," >> "$SUMMARY_FILE"
echo "  \"successful_probes\": $SUCCESSFUL_PROBES," >> "$SUMMARY_FILE"
echo "  \"failed_probes\": $FAILED_PROBES," >> "$SUMMARY_FILE"
echo "  \"success_rate\": $(echo "scale=2; $SUCCESSFUL_PROBES * 100 / $TOTAL_PROBES" | bc)," >> "$SUMMARY_FILE"
echo "  \"runtime_formatted\": \"${HOURS}h ${MINUTES}m ${SECONDS}s\"" >> "$SUMMARY_FILE"
echo "}" >> "$SUMMARY_FILE"

# Print summary
echo "" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "Benchmark Complete!" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "Total Runtime: ${HOURS}h ${MINUTES}m ${SECONDS}s" | tee -a "$LOG_FILE"
echo "Successful Probes: $SUCCESSFUL_PROBES/$TOTAL_PROBES" | tee -a "$LOG_FILE"
echo "Failed Probes: $FAILED_PROBES/$TOTAL_PROBES" | tee -a "$LOG_FILE"
echo "Success Rate: $(echo "scale=2; $SUCCESSFUL_PROBES * 100 / $TOTAL_PROBES" | bc)%" | tee -a "$LOG_FILE"
echo "Results saved to: $RESULTS_DIR" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"

# Generate HTML report if Python is available
if command -v python3 &> /dev/null; then
    echo "Generating HTML report..." | tee -a "$LOG_FILE"
    python3 scripts/generate_benchmark_report.py "$RESULTS_DIR" || echo "HTML report generation failed"
fi

exit 0
