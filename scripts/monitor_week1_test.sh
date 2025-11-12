#!/bin/bash
# Monitor Week 1 test job

JOB_ID=${1:-$(squeue -u $USER -n mle-week1-test -h -o "%i" | head -1)}

if [ -z "$JOB_ID" ]; then
    echo "No active Week 1 test job found"
    echo ""
    echo "Recent jobs:"
    sacct -u $USER --name=mle-week1-test --format=JobID,JobName,State,Start,End,Elapsed -n | head -5
    echo ""
    echo "Usage: $0 [job_id]"
    exit 1
fi

echo "=========================================="
echo "Monitoring Week 1 Test Job: $JOB_ID"
echo "=========================================="
echo ""

# Check job status
echo "Job Status:"
squeue -j $JOB_ID -o "%.18i %.9P %.30j %.8u %.8T %.10M %.9l %.6D %R" 2>/dev/null || {
    echo "Job $JOB_ID is not in queue (may have completed)"
    echo ""
    echo "Job Details:"
    sacct -j $JOB_ID --format=JobID,JobName,State,Start,End,Elapsed,MaxRSS,MaxVMSize -n
}
echo ""

# Show log file locations
LOG_OUT="logs/week1_test-${JOB_ID}.out"
LOG_ERR="logs/week1_test-${JOB_ID}.err"

echo "Log Files:"
echo "  STDOUT: $LOG_OUT"
echo "  STDERR: $LOG_ERR"
echo ""

# Check if logs exist and show tail
if [ -f "$LOG_OUT" ]; then
    echo "=========================================="
    echo "Recent Output (last 30 lines):"
    echo "=========================================="
    tail -30 "$LOG_OUT"
    echo ""
    echo "=========================================="
    echo ""
    echo "Follow live output:"
    echo "  tail -f $LOG_OUT"
    echo ""

    # Check for completion markers
    if grep -q "Week 1 Test Complete!" "$LOG_OUT"; then
        echo "✓ Job completed!"
        echo ""

        # Try to extract results directory
        RESULTS_DIR=$(grep "Results saved to:" "$LOG_OUT" | tail -1 | awk '{print $NF}')
        if [ -n "$RESULTS_DIR" ] && [ -d "$RESULTS_DIR" ]; then
            echo "Results directory: $RESULTS_DIR"
            echo ""

            # Show quick summary if available
            if [ -f "$RESULTS_DIR/eval_results_week1_test.json" ]; then
                echo "Quick Summary:"
                python3 -c "
import json
try:
    with open('$RESULTS_DIR/eval_results_week1_test.json', 'r') as f:
        results = json.load(f)
    metrics = results.get('metrics', {})
    print(f\"  Success Rate: {metrics.get('success_rate', 0)*100:.1f}%\")
    print(f\"  Avg Reward: {metrics.get('avg_reward', 0):.4f}\")
    print(f\"  Episodes: {metrics.get('total_episodes', 0)}\")
except: pass
"
                echo ""
                echo "Full results: cat $RESULTS_DIR/eval_results_week1_test.json"
            fi
        fi
    elif grep -q "Error" "$LOG_OUT" || grep -q "Traceback" "$LOG_OUT"; then
        echo "⚠️  Errors detected in output"
        echo ""
        echo "Check full log: cat $LOG_OUT"
    else
        echo "Job still running..."
        echo ""
        echo "Refresh status: $0 $JOB_ID"
    fi
else
    echo "Log file not created yet (job may be pending)"
    echo ""
    echo "Check again in a moment: $0 $JOB_ID"
fi

# Show error log if exists and non-empty
if [ -f "$LOG_ERR" ] && [ -s "$LOG_ERR" ]; then
    echo "=========================================="
    echo "⚠️  Errors (from stderr):"
    echo "=========================================="
    tail -20 "$LOG_ERR"
    echo ""
fi
