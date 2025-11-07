#!/bin/bash
# Run baseline agent (no RL training)

set -e

# Configuration
MODEL_NAME=${1:-"Qwen/Qwen2.5-Coder-7B-Instruct"}
NUM_EPISODES=${2:-10}
OUTPUT_DIR=${3:-"experiments/baselines/baseline_$(date +%Y%m%d_%H%M%S)"}

echo "=========================================="
echo "Running Baseline Agent"
echo "=========================================="
echo "Model: $MODEL_NAME"
echo "Episodes: $NUM_EPISODES"
echo "Output: $OUTPUT_DIR"
echo "=========================================="
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Copy configuration to output directory for reproducibility
cp agent/configs/agent_config.yaml "$OUTPUT_DIR/agent_config.yaml"

# Generate trajectories
echo "Generating trajectories..."
python agent/training/generate_trajectories.py \
    --num-episodes "$NUM_EPISODES" \
    --model-name "$MODEL_NAME" \
    --config agent/configs/agent_config.yaml \
    --output-dir "$OUTPUT_DIR/trajectories" \
    2>&1 | tee "$OUTPUT_DIR/generation.log"

# Evaluate
echo ""
echo "Evaluating baseline..."
python agent/training/evaluate.py \
    --model-path "$MODEL_NAME" \
    --config agent/configs/eval_config.yaml \
    --num-episodes "$NUM_EPISODES" \
    --output-dir "$OUTPUT_DIR/evaluation" \
    --verbose \
    2>&1 | tee "$OUTPUT_DIR/evaluation.log"

echo ""
echo "=========================================="
echo "Baseline run complete!"
echo "=========================================="
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "To view results:"
echo "  cat $OUTPUT_DIR/evaluation/eval_results_*.json"
echo ""
