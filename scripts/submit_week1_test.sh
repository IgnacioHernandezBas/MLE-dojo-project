#!/bin/bash
#SBATCH --job-name=mle-week1-test
#SBATCH --output=logs/week1_test-%j.out
#SBATCH --error=logs/week1_test-%j.err
#SBATCH --time=04:00:00
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --account=cml-furongh
#SBATCH --partition=cml-dpart
#SBATCH --qos=cml-high

# Week 1 Test SLURM Job
# Tests the Week 1 fixes on a simple competition
# Usage: sbatch scripts/submit_week1_test.sh [num_episodes]

set -e

NUM_EPISODES=${1:-5}

echo "=========================================="
echo "Week 1 Test - SLURM Job"
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPUs: $CUDA_VISIBLE_DEVICES"
echo "Episodes: $NUM_EPISODES"
echo "=========================================="
echo ""

# Load environment
echo "Activating conda environment: mle-dojo"
source /fs/nexus-scratch/ihbas/miniconda3/etc/profile.d/conda.sh
conda activate mle-dojo

# Set PyTorch memory optimization
export PYTORCH_ALLOC_CONF=expandable_segments:True

# Print environment info
echo "Environment:"
echo "Python: $(which python)"
python --version
echo ""
echo "CUDA available:"
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv
echo ""
echo "Installed packages:"
pip list | grep -E "(torch|transformers|accelerate|bitsandbytes|mledojo)"
echo ""

# Create logs directory
mkdir -p logs

# Run Week 1 test
echo "Starting Week 1 test..."
echo ""
bash scripts/run_week1_test.sh \
    "Qwen/Qwen2.5-Coder-7B-Instruct" \
    "$NUM_EPISODES" \
    "experiments/week1_test/test_$SLURM_JOB_ID"

echo ""
echo "=========================================="
echo "Week 1 Test Complete!"
echo "=========================================="
echo "Check results in: experiments/week1_test/test_$SLURM_JOB_ID"
echo "Check logs in: logs/week1_test-$SLURM_JOB_ID.out"
echo "=========================================="
