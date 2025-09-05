#!/bin/bash

GARAK_LOG="run_garak_test_v3.log"
export PYTHONWARNINGS='ignore:Unverified HTTPS request'

# Get clean probe list (strip ANSI junk)
PROBES=$(python -m garak --list_probes \
        | awk '{print $2}' \
        | grep '\.' \
        | sed 's/\x1B\[[0-9;]*[a-zA-Z]//g')

for PROBE in $PROBES; do
  START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
  echo "=== [$START_TIME] Running probe: $PROBE ===" | tee -a "$GARAK_LOG"

  for attempt in 1 2; do
    echo "Attempt $attempt for $PROBE" | tee -a "$GARAK_LOG"

    python -m garak --model_type rest \
          --generator_option_file garak_config.json \
          --probes "$PROBE" \
          --report_prefix "report_${PROBE//./_}" \
          >> "$GARAK_LOG" 2>&1

    EXIT_CODE=$?
    END_TIME=$(date +"%Y-%m-%d %H:%M:%S")

    if [ $EXIT_CODE -eq 0 ]; then
      echo "✔ [$END_TIME] Success: $PROBE" | tee -a "$GARAK_LOG"
      break
    else
      echo "✘ [$END_TIME] Failure: $PROBE (attempt $attempt, exit $EXIT_CODE)" | tee -a "$GARAK_LOG"
      if [ $attempt -eq 2 ]; then
        echo "→ Skipping $PROBE after 2 failures" | tee -a "$GARAK_LOG"
      else
        echo "Retrying in 5s..." | tee -a "$GARAK_LOG"
        sleep 5
      fi
    fi
  done
done

echo "=== All probes finished. Check $GARAK_LOG for details. ==="