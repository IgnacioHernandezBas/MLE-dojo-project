#!/bin/bash
#SBATCH --job-name=mle-agent
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#SBATCH --time=24:00:00
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpu

# SLURM job script for running MLE-Dojo agent training
# Usage: sbatch scripts/submit_slurm.sh [mode] [args...]
#   mode: "baseline", "train", or "eval"
#
# Examples:
#   sbatch scripts/submit_slurm.sh baseline
#   sbatch scripts/submit_slurm.sh train run_001
#   sbatch scripts/submit_slurm.sh eval experiments/checkpoints/model_001

set -e

MODE=${1:-baseline}

echo "=========================================="
echo "SLURM Job Information"
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPUs: $CUDA_VISIBLE_DEVICES"
echo "Mode: $MODE"
echo "=========================================="
echo ""

# Load modules (adjust for your HPC environment)
# module load cuda/12.1
# module load python/3.10
# module load apptainer

# Print environment info
echo "Environment:"
nvidia-smi
python --version
echo ""

# Set up container if available
CONTAINER="images/mle-dojo.sif"
if [ -f "$CONTAINER" ]; then
    echo "Using container: $CONTAINER"
    # Mount the entire project directory for easy access
    RUNNER="apptainer exec --nv --bind $(pwd):/workspace --pwd /workspace $CONTAINER"
else
    echo "Running without container (using local environment)"
    RUNNER=""
fi

# Create logs directory
mkdir -p logs

# Run based on mode
case $MODE in
    baseline)
        echo "Running baseline..."
        $RUNNER bash scripts/run_baseline.sh
        ;;

    train)
        RUN_NAME=${2:-"run_$SLURM_JOB_ID"}
        TRAJECTORIES_DIR=${3:-"experiments/trajectories"}
        echo "Running RL training: $RUN_NAME"
        $RUNNER bash scripts/train_rl.sh "$RUN_NAME" "$TRAJECTORIES_DIR"
        ;;

    eval)
        MODEL_PATH=${2:-"Qwen/Qwen2.5-Coder-7B-Instruct"}
        NUM_EPISODES=${3:-10}
        echo "Running evaluation: $MODEL_PATH"
        $RUNNER python agent/training/evaluate.py \
            --model-path "$MODEL_PATH" \
            --config agent/configs/eval_config.yaml \
            --num-episodes "$NUM_EPISODES" \
            --output-dir "experiments/evaluations/eval_$SLURM_JOB_ID" \
            --verbose
        ;;

    *)
        echo "Error: Unknown mode '$MODE'"
        echo "Usage: sbatch $0 [baseline|train|eval] [args...]"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Job complete!"
echo "=========================================="
