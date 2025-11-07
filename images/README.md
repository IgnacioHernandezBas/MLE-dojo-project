# Container Images

This directory contains the MLE-Dojo framework container.

## Required Container

Place your **mle-dojo.sif** container file here:

```
images/mle-dojo.sif
```

## Obtaining the Container

Follow the MLE-Dojo framework documentation to obtain the `mle-dojo.sif` container. This is the official MLE-Dojo benchmark container that includes:

- CUDA 12.1+ support
- Python 3.10
- PyTorch with CUDA support
- All MLE-Dojo framework dependencies

## Important Notes

- **Do NOT commit** the `.sif` file to git (it's already in `.gitignore`)
- The container file is typically several GB in size
- You only need one copy of `mle-dojo.sif` for all your experiments
- Your agent code will be mounted into this container at runtime

## Usage

Once you have `mle-dojo.sif` in this directory, you can:

```bash
# Run with container
apptainer exec --nv --bind $(pwd):/workspace images/mle-dojo.sif \
  python /workspace/agent/training/evaluate.py

# Or use the SLURM scripts (they auto-detect the container)
sbatch scripts/submit_slurm.sh baseline
```

For detailed usage instructions, see:
- `containers/README.md` - Complete container usage guide
- `README.md` - Main project documentation
