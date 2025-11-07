#!/bin/bash
# Train agent with RL

set -e

# Configuration
RUN_NAME=${1:-"run_$(date +%Y%m%d_%H%M%S)"}
TRAJECTORIES_DIR=${2:-"experiments/trajectories"}
OUTPUT_DIR="experiments/rl_runs/$RUN_NAME"

echo "=========================================="
echo "RL Training"
echo "=========================================="
echo "Run name: $RUN_NAME"
echo "Trajectories: $TRAJECTORIES_DIR"
echo "Output: $OUTPUT_DIR"
echo "=========================================="
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Copy configuration to output directory for reproducibility
cp agent/configs/training_config.yaml "$OUTPUT_DIR/training_config.yaml"

# Check if trajectories exist
if [ ! -d "$TRAJECTORIES_DIR" ]; then
    echo "Error: Trajectories directory not found: $TRAJECTORIES_DIR"
    echo ""
    echo "Please generate trajectories first:"
    echo "  bash scripts/run_baseline.sh"
    exit 1
fi

echo "Found trajectories directory"
TRAJ_COUNT=$(find "$TRAJECTORIES_DIR" -name "*.json" | wc -l)
echo "Number of trajectory files: $TRAJ_COUNT"
echo ""

# Train
echo "Starting RL training..."
python agent/training/train_rl.py \
    --trajectories-dir "$TRAJECTORIES_DIR" \
    --config agent/configs/training_config.yaml \
    --output-dir "$OUTPUT_DIR" \
    --num-iterations 100 \
    --checkpoint-freq 10 \
    2>&1 | tee "$OUTPUT_DIR/training.log"

echo ""
echo "=========================================="
echo "RL training complete!"
echo "=========================================="
echo "Checkpoints saved to: $OUTPUT_DIR/checkpoints"
echo "Logs saved to: $OUTPUT_DIR/training.log"
echo ""
echo "To evaluate the trained model:"
echo "  python agent/training/evaluate.py \\"
echo "    --model-path $OUTPUT_DIR/checkpoints/final \\"
echo "    --config agent/configs/eval_config.yaml"
echo ""
