# Container Usage

This project uses the **existing MLE-Dojo framework container** (`mle-dojo.sif`). You do NOT need to build a separate container for your agent code.

## Why Use the Framework Container?

The MLE-Dojo framework already provides a complete containerized environment with:
- CUDA 12.1+ support
- Python 3.10
- PyTorch with CUDA support
- All MLE-Dojo dependencies

Instead of building a duplicate container, we **mount your agent code** into the framework container at runtime.

## Container Location

Your `mle-dojo.sif` container should be located at:
```
~/MLE-dojo-project/images/mle-dojo.sif
```

If you don't have it yet, follow the MLE-Dojo setup instructions to obtain it.

## Usage Examples

### Interactive Development

```bash
# Start an interactive shell with agent code mounted
apptainer shell --nv \
  --bind $(pwd)/agent:/workspace/agent \
  --bind $(pwd)/experiments:/workspace/experiments \
  images/mle-dojo.sif

# Inside the container, you can now run your agent code
python /workspace/agent/training/evaluate.py --help
```

### Running Scripts

```bash
# Run baseline generation
apptainer exec --nv \
  --bind $(pwd):/workspace \
  --pwd /workspace \
  images/mle-dojo.sif \
  bash scripts/run_baseline.sh

# Run evaluation
apptainer exec --nv \
  --bind $(pwd)/agent:/workspace/agent \
  --bind $(pwd)/experiments:/workspace/experiments \
  images/mle-dojo.sif \
  python /workspace/agent/training/evaluate.py \
    --model-path "Qwen/Qwen2.5-Coder-7B-Instruct" \
    --config /workspace/agent/configs/eval_config.yaml \
    --num-episodes 10 \
    --output-dir /workspace/experiments/evaluations/eval_001
```

### Key Bind Flags

- `--bind $(pwd):/workspace` - Mount entire project directory
- `--bind $(pwd)/agent:/workspace/agent` - Mount only agent code
- `--bind $(pwd)/experiments:/workspace/experiments` - Mount experiments directory
- `--nv` - Enable NVIDIA GPU support
- `--pwd /workspace` - Set working directory inside container

## SLURM/HPC Usage

The SLURM submission script automatically detects and uses the container:

```bash
# The script looks for images/mle-dojo.sif
sbatch scripts/submit_slurm.sh baseline
sbatch scripts/submit_slurm.sh eval "Qwen/Qwen2.5-Coder-7B-Instruct" 10
```

In your own SLURM scripts:

```bash
#!/bin/bash
#SBATCH --gres=gpu:1

module load apptainer

apptainer exec --nv \
  --bind $(pwd):/workspace \
  --pwd /workspace \
  images/mle-dojo.sif \
  python /workspace/agent/training/train_rl.py \
    --config /workspace/agent/configs/training_config.yaml \
    --output-dir /workspace/experiments/rl_runs/run_001
```

## Installing Additional Dependencies

If your agent requires additional Python packages not in the framework container:

### Option 1: Install at Runtime (Quick Testing)

```bash
# Inside the container
apptainer exec --nv images/mle-dojo.sif bash
pip install --user my-package

# Or in one command
apptainer exec --nv images/mle-dojo.sif pip install --user my-package
```

**Note:** Packages installed this way are stored in `~/.local` and persist across sessions.

### Option 2: Use requirements.txt

Create a `containers/requirements.txt` file with additional dependencies:

```bash
# Install your additional requirements
apptainer exec --nv images/mle-dojo.sif \
  pip install --user -r /workspace/containers/requirements.txt
```

### Option 3: Build Custom Container (Only if Necessary)

Only build a custom container if you need:
- System-level dependencies not in mle-dojo.sif
- Different CUDA version
- Specific Python version
- Complex environment modifications

See `mle_agent.def` for an example Apptainer definition file. This is a **reference only** - you typically won't need to build it.

## Troubleshooting

### Problem: Container not found

```bash
ls images/mle-dojo.sif
# If missing, check MLE-Dojo documentation for obtaining the container
```

### Problem: Permission denied when mounting

```bash
# Make sure directories exist and are readable
mkdir -p experiments/evaluations
chmod -R u+rwX agent/ experiments/
```

### Problem: GPU not available

```bash
# Check GPU is visible
nvidia-smi

# Make sure to use --nv flag
apptainer exec --nv images/mle-dojo.sif nvidia-smi
```

### Problem: Module not found inside container

```bash
# Check if module exists in container
apptainer exec images/mle-dojo.sif python -c "import module_name"

# If missing, install it (see "Installing Additional Dependencies" above)
```

## Files in This Directory

- **README.md** - This file
- **mle_agent.def** - Example Apptainer definition (reference only, not needed for normal use)
- **requirements.txt** - Additional Python dependencies for your agent (optional)

## Best Practices

1. **Always use --bind** to mount your code instead of copying it into the container
2. **Use --nv flag** when you need GPU access
3. **Set --pwd** to ensure scripts run from the correct directory
4. **Mount only what you need** for better isolation and security
5. **Keep the framework container unchanged** - install user packages with `pip install --user`

## Quick Reference

```bash
# Interactive development
apptainer shell --nv --bind $(pwd):/workspace images/mle-dojo.sif

# Run single command
apptainer exec --nv --bind $(pwd):/workspace images/mle-dojo.sif \
  python /workspace/agent/training/evaluate.py

# Submit SLURM job
sbatch scripts/submit_slurm.sh baseline

# Install additional packages
apptainer exec --nv images/mle-dojo.sif \
  pip install --user my-package
```
