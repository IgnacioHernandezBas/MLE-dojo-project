# Container Definitions

This directory contains container definitions for reproducible environments.

## Files

- **mle_agent.def** - Apptainer/Singularity definition file for the agent
- **requirements.txt** - Python dependencies for the agent

## Building the Container

### Using Apptainer (recommended for HPC)

```bash
# Build the container
apptainer build mle_agent.sif mle_agent.def

# Run with GPU support
apptainer run --nv mle_agent.sif

# Run with specific command
apptainer run --nv mle_agent.sif python3 agent/training/evaluate.py --help
```

### Using Docker (alternative)

```bash
# Create a Dockerfile from the definition (manual conversion needed)
# Or use Docker directly with a similar setup

docker build -t mle-agent:latest -f Dockerfile .
docker run --gpus all -it mle-agent:latest
```

## Usage on SLURM/HPC

```bash
# In your SLURM script
#SBATCH --gres=gpu:1

module load apptainer

apptainer exec --nv mle_agent.sif python3 agent/training/train_rl.py \
    --config agent/configs/training_config.yaml \
    --output-dir experiments/rl_runs/run_001
```

## Customization

To customize the container:

1. Edit `mle_agent.def`
2. Add dependencies to `requirements.txt`
3. Rebuild the container: `apptainer build mle_agent.sif mle_agent.def`

## Notes

- The container includes CUDA 12.1 support
- Python 3.10 is used as the base Python version
- PyTorch is installed with CUDA support
- The workspace directory is `/workspace` inside the container
