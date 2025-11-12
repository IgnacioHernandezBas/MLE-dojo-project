#!/bin/bash
# Pre-flight check before submitting Week 1 test

echo "=========================================="
echo "Week 1 Test - Pre-flight Check"
echo "=========================================="
echo ""

# Check 1: Competition data
echo "✓ Checking competition data..."
COMP_DATA="mle-dojo-source/data/prepared/home-data-for-ml-course/data"
if [ -d "$COMP_DATA/public" ] && [ -f "$COMP_DATA/public/train.csv" ]; then
    echo "  ✓ Competition data found"
    echo "    - train.csv: $(wc -l < $COMP_DATA/public/train.csv) lines"
    echo "    - test.csv: $(wc -l < $COMP_DATA/public/test.csv) lines"
else
    echo "  ✗ Competition data NOT found"
    exit 1
fi
echo ""

# Check 2: Required files
echo "✓ Checking required files..."
FILES=(
    "agent/training/evaluate.py"
    "agent/configs/eval_config.yaml"
    "agent/configs/agent_config.yaml"
    "agent/wrappers/mledojo_wrapper.py"
    "agent/core/prompts.py"
    "scripts/run_week1_test.sh"
    "scripts/submit_week1_test.sh"
)

ALL_EXIST=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = false ]; then
    echo ""
    echo "✗ Some required files are missing"
    exit 1
fi
echo ""

# Check 3: Conda environment
echo "✓ Checking conda environment..."
if conda env list | grep -q "mle-dojo"; then
    echo "  ✓ mle-dojo environment exists"
else
    echo "  ✗ mle-dojo environment NOT found"
    echo "    Create it with: conda create -n mle-dojo python=3.11"
    exit 1
fi
echo ""

# Check 4: Git status
echo "✓ Checking git status..."
if git diff --quiet HEAD -- agent/ scripts/ 2>/dev/null; then
    echo "  ✓ Week 1 fixes committed"
else
    echo "  ⚠️  Uncommitted changes detected (this is OK)"
fi
echo ""

# Check 5: Logs directory
echo "✓ Checking logs directory..."
mkdir -p logs
echo "  ✓ logs/ directory ready"
echo ""

# Summary
echo "=========================================="
echo "Pre-flight Check Complete!"
echo "=========================================="
echo ""
echo "Ready to submit Week 1 test!"
echo ""
echo "Submit with:"
echo "  sbatch scripts/submit_week1_test.sh [num_episodes]"
echo ""
echo "Examples:"
echo "  sbatch scripts/submit_week1_test.sh 5     # Quick test (5 episodes)"
echo "  sbatch scripts/submit_week1_test.sh 10    # Full test (10 episodes)"
echo ""
echo "Monitor with:"
echo "  squeue -u $USER"
echo "  tail -f logs/week1_test-<jobid>.out"
echo ""
