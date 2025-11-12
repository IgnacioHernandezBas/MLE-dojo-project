#!/bin/bash
# Week 1 Test Script - Verify fixes work with simple competition
# This script tests the Week 1 fixes on a small number of episodes

set -e

# Configuration
MODEL_NAME=${1:-"Qwen/Qwen2.5-Coder-7B-Instruct"}
NUM_EPISODES=${2:-5}  # Start with fewer episodes for quick testing
OUTPUT_DIR=${3:-"experiments/week1_test/test_$(date +%Y%m%d_%H%M%S)"}

echo "=========================================="
echo "Week 1 Fixes Test"
echo "=========================================="
echo "Model: $MODEL_NAME"
echo "Episodes: $NUM_EPISODES"
echo "Output: $OUTPUT_DIR"
echo "Competition: home-data-for-ml-course (beginner)"
echo "=========================================="
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Copy configurations for reproducibility
cp agent/configs/agent_config.yaml "$OUTPUT_DIR/agent_config.yaml"
cp agent/configs/eval_config.yaml "$OUTPUT_DIR/eval_config.yaml"
cp WEEK1_FIXES_SUMMARY.md "$OUTPUT_DIR/WEEK1_FIXES_SUMMARY.md"

# Create a test summary file
cat > "$OUTPUT_DIR/TEST_INFO.md" <<EOF
# Week 1 Test Run

## Test Information
- Date: $(date)
- Model: $MODEL_NAME
- Episodes: $NUM_EPISODES
- Competition: home-data-for-ml-course
- Job ID: ${SLURM_JOB_ID:-local}
- Node: ${SLURM_NODELIST:-local}

## Fixes Being Tested
1. ✅ Robust code extraction with AST validation
2. ✅ Enhanced error handling and recovery
3. ✅ MLE-Dojo specific prompts
4. ✅ Increased context limits (2048 tokens, 10 turns, 20 steps)

## Expected Improvements
- Success rate: > 0% (baseline was 0%)
- Steps per episode: > 5 (baseline was 0)
- Trajectories: Non-empty with actual interactions

## Evaluation Criteria
- **Minimum Success**: Agent completes episodes with steps > 0
- **Good Success**: Success rate > 5%, avg steps > 5
- **Excellent Success**: Success rate > 20%, meaningful ML workflow

EOF

echo "Test configuration saved to $OUTPUT_DIR"
echo ""

# Check if competition data exists
COMP_DATA="mle-dojo-source/data/prepared/home-data-for-ml-course/data"
if [ ! -d "$COMP_DATA" ]; then
    echo "⚠️  WARNING: Competition data not found at $COMP_DATA"
    echo "Please prepare the competition first:"
    echo "  cd mle-dojo-source"
    echo "  echo 'home-data-for-ml-course' > prepare/comp.txt"
    echo "  PYTHONPATH='.' python prepare/mle.py --competitions-file prepare/comp.txt --data-dir data/prepared --logs-dir data/prepare_logs"
    echo ""
    exit 1
fi

echo "✓ Competition data found at $COMP_DATA"
echo ""

# Run evaluation (skip trajectory generation for now since it's incomplete)
echo "=========================================="
echo "Running Evaluation"
echo "=========================================="
python agent/training/evaluate.py \
    --model-path "$MODEL_NAME" \
    --config agent/configs/eval_config.yaml \
    --num-episodes "$NUM_EPISODES" \
    --output-dir "$OUTPUT_DIR" \
    --benchmark "week1_test" \
    --verbose \
    2>&1 | tee "$OUTPUT_DIR/evaluation.log"

echo ""
echo "=========================================="
echo "Week 1 Test Complete!"
echo "=========================================="
echo "Results saved to: $OUTPUT_DIR"
echo ""

# Analyze results
RESULTS_FILE="$OUTPUT_DIR/eval_results_week1_test.json"
if [ -f "$RESULTS_FILE" ]; then
    echo "📊 Test Results Summary:"
    echo "------------------------"
    python3 -c "
import json
import sys

try:
    with open('$RESULTS_FILE', 'r') as f:
        results = json.load(f)

    metrics = results.get('metrics', {})
    episodes = results.get('episodes', [])

    print(f\"Total Episodes: {metrics.get('total_episodes', 0)}\")
    print(f\"Success Rate: {metrics.get('success_rate', 0)*100:.1f}%\")
    print(f\"Avg Reward: {metrics.get('avg_reward', 0):.4f}\")
    print(f\"Successful Episodes: {metrics.get('successful_episodes', 0)}\")
    print()

    # Check if any steps were taken
    steps_taken = [ep.get('steps', 0) for ep in episodes]
    total_steps = sum(steps_taken)
    avg_steps = total_steps / len(steps_taken) if steps_taken else 0

    print(f\"Total Steps Taken: {total_steps}\")
    print(f\"Avg Steps per Episode: {avg_steps:.1f}\")
    print()

    # Evaluation
    if total_steps == 0:
        print(\"❌ CRITICAL: No steps taken - fixes did not work\")
        print(\"   Check evaluation.log for errors\")
    elif metrics.get('success_rate', 0) == 0:
        print(\"⚠️  PARTIAL: Agent takes actions but not successful yet\")
        print(\"   This is progress! Review trajectories for issues.\")
    elif metrics.get('success_rate', 0) < 0.2:
        print(\"✓ GOOD: Agent working with low success rate\")
        print(\"   Proceed to Week 2 improvements\")
    else:
        print(\"✓✓ EXCELLENT: Strong success rate!\")
        print(\"   Proceed to Week 2 and test on more competitions\")

except Exception as e:
    print(f\"Error analyzing results: {e}\", file=sys.stderr)
    sys.exit(1)
"
    echo ""
    echo "📁 Full results: $RESULTS_FILE"
    echo "📋 Logs: $OUTPUT_DIR/evaluation.log"
    echo ""

    # Check for trajectories
    if [ -d "$OUTPUT_DIR/episode_0" ]; then
        echo "📂 Episode outputs available in $OUTPUT_DIR/episode_*"
    fi
else
    echo "⚠️  Results file not found: $RESULTS_FILE"
    echo "Check evaluation.log for errors"
fi

echo ""
echo "Next Steps:"
echo "1. Review logs: cat $OUTPUT_DIR/evaluation.log"
echo "2. Check results: cat $RESULTS_FILE"
echo "3. If successful, proceed to Week 2 improvements"
echo "4. If issues remain, debug using test info above"
echo ""
