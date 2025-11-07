#!/bin/bash

PROJECT_DIR="/fs/nexus-scratch/$USER/MLE-dojo-project"
SOURCE_DIR="$PROJECT_DIR/MLE-Dojo"
COMPETITION=${1:-"titanic"}

echo "=========================================="
echo "Preparing MLE-Dojo Competition Data"
echo "=========================================="
echo "Competition: $COMPETITION"
echo "Project dir: $PROJECT_DIR"
echo ""

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory not found!"
    echo "Please clone first:"
    echo "  cd $PROJECT_DIR"
    echo "  git clone https://github.com/MLEDojo/mle-dojo.git MLE-Dojo"
    exit 1
fi

# Check Kaggle credentials
if [ ! -f "$HOME/.kaggle/kaggle.json" ]; then
    echo "ERROR: Kaggle credentials not found!"
    echo ""
    echo "Setup instructions:"
    echo "  1. Go to https://www.kaggle.com/settings"
    echo "  2. Click 'Create New API Token'"
    echo "  3. Move kaggle.json to ~/.kaggle/"
    echo "     mkdir -p ~/.kaggle"
    echo "     mv ~/Downloads/kaggle.json ~/.kaggle/"
    echo "     chmod 600 ~/.kaggle/kaggle.json"
    exit 1
fi

echo "✓ Kaggle credentials found"

# Check if user has conda/python environment
if ! command -v python &> /dev/null; then
    echo "ERROR: Python not found!"
    echo "Make sure you have a Python environment activated"
    exit 1
fi

echo "✓ Python found: $(which python)"
echo "✓ Python version: $(python --version)"

# Remind about accepting terms
echo ""
echo "=========================================="
echo "IMPORTANT: Competition Terms"
echo "=========================================="
echo "Have you accepted the competition terms?"
echo "Visit: https://www.kaggle.com/c/$COMPETITION"
echo "Click: 'I Understand and Accept'"
echo ""
read -p "Press Enter to continue (or Ctrl+C to cancel)..."
echo ""

# Create directories
mkdir -p $PROJECT_DIR/data/prepared
mkdir -p $PROJECT_DIR/data/prepare_logs

# Prepare data
echo "Preparing data for: $COMPETITION"
echo "This may take several minutes..."
echo ""

cd $SOURCE_DIR

PYTHONPATH="." python prepare/mle.py \
  --competitions $COMPETITION \
  --data-dir $PROJECT_DIR/data/prepared \
  --logs-dir $PROJECT_DIR/data/prepare_logs

# Check if successful
if [ -d "$PROJECT_DIR/data/prepared/$COMPETITION/data" ]; then
    echo ""
    echo "=========================================="
    echo "✓ Data preparation complete!"
    echo "=========================================="
    echo "Data location: $PROJECT_DIR/data/prepared/$COMPETITION"
    echo ""
    echo "Directory structure:"
    tree -L 3 $PROJECT_DIR/data/prepared/$COMPETITION || ls -R $PROJECT_DIR/data/prepared/$COMPETITION
    echo ""
    echo "Files in public directory:"
    ls -lh $PROJECT_DIR/data/prepared/$COMPETITION/data/public/
else
    echo ""
    echo "=========================================="
    echo "✗ Data preparation failed!"
    echo "=========================================="
    echo "Check logs at: $PROJECT_DIR/data/prepare_logs/"
    echo ""
    echo "Common issues:"
    echo "  - Competition terms not accepted"
    echo "  - Invalid competition name"
    echo "  - Network issues"
    echo "  - Missing dependencies"
    exit 1
fi