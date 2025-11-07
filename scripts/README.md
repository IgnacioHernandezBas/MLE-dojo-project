# Scripts

Utility scripts for data preparation, training, and evaluation.

## Data Preparation

### prepare-competition.sh
Prepares competition data from Kaggle for MLE-Dojo.

```bash
# Prepare default competition (titanic)
bash scripts/prepare-competition.sh

# Prepare specific competition
bash scripts/prepare-competition.sh house-prices-advanced-regression-techniques
```

**Prerequisites:**
- Kaggle API credentials in `~/.kaggle/kaggle.json`
- Accepted competition terms on Kaggle website
- MLE-Dojo repository cloned in `MLE-Dojo/`

### set_up_env.sh
Sets up environment variables for Singularity/Apptainer containers.

```bash
source scripts/set_up_env.sh
```

## Agent Execution

### run_baseline.sh
Runs the baseline agent (no RL training).

```bash
# Run with defaults
bash scripts/run_baseline.sh

# Specify model and episodes
bash scripts/run_baseline.sh "Qwen/Qwen2.5-Coder-7B-Instruct" 20

# Specify output directory
bash scripts/run_baseline.sh "Qwen/Qwen2.5-Coder-7B-Instruct" 10 "experiments/baselines/my_baseline"
```

**Arguments:**
1. Model name (default: Qwen/Qwen2.5-Coder-7B-Instruct)
2. Number of episodes (default: 10)
3. Output directory (default: auto-generated with timestamp)

### train_rl.sh
Trains the agent using RL.

```bash
# Run with defaults
bash scripts/train_rl.sh

# Specify run name
bash scripts/train_rl.sh "my_experiment"

# Specify run name and trajectory directory
bash scripts/train_rl.sh "my_experiment" "experiments/trajectories"
```

**Arguments:**
1. Run name (default: auto-generated with timestamp)
2. Trajectories directory (default: experiments/trajectories)

## SLURM Submission

### submit_slurm.sh
Submits jobs to SLURM scheduler for HPC environments.

```bash
# Run baseline
sbatch scripts/submit_slurm.sh baseline

# Run RL training
sbatch scripts/submit_slurm.sh train run_001 experiments/trajectories

# Run evaluation
sbatch scripts/submit_slurm.sh eval experiments/checkpoints/model_001 10
```

**Modes:**
- `baseline`: Run baseline agent
- `train [run_name] [trajectories_dir]`: Run RL training
- `eval [model_path] [num_episodes]`: Run evaluation

**SLURM Configuration:**
- Default time: 24 hours
- GPUs: 1
- Memory: 32GB
- CPUs: 8

Edit the `#SBATCH` directives in the script to adjust resource requirements.

## Testing

### test_env.py
Tests the MLE-Dojo environment setup.

```bash
# Run directly
python scripts/test_env.py

# Or with container
apptainer exec --nv --bind $(pwd):/workspace images/mle-dojo.sif \
  python /workspace/scripts/test_env.py
```

## Workflow Examples

### Complete Training Workflow

```bash
# 1. Prepare data
bash scripts/prepare-competition.sh titanic

# 2. Generate baseline trajectories
bash scripts/run_baseline.sh

# 3. Train with RL
bash scripts/train_rl.sh my_experiment

# 4. Evaluate trained model
python agent/training/evaluate.py \
    --model-path experiments/rl_runs/my_experiment/checkpoints/final \
    --config agent/configs/eval_config.yaml \
    --num-episodes 20
```

### SLURM Workflow

```bash
# 1. Submit baseline job
BASELINE_JOB=$(sbatch --parsable scripts/submit_slurm.sh baseline)

# 2. Submit training job (depends on baseline completing)
TRAIN_JOB=$(sbatch --parsable --dependency=afterok:$BASELINE_JOB \
    scripts/submit_slurm.sh train run_001)

# 3. Submit evaluation job (depends on training completing)
sbatch --dependency=afterok:$TRAIN_JOB \
    scripts/submit_slurm.sh eval experiments/rl_runs/run_001/checkpoints/final
```

## Customization

To customize scripts:

1. Edit SLURM resource requirements in `submit_slurm.sh`
2. Adjust default parameters in individual scripts
3. Modify configuration files in `agent/configs/`

## Troubleshooting

### Common Issues

**Problem:** Script fails with "command not found"
- **Solution:** Make scripts executable: `chmod +x scripts/*.sh`

**Problem:** GPU not available in SLURM job
- **Solution:** Check SLURM partition and GPU availability with `sinfo`

**Problem:** Out of memory error
- **Solution:** Increase `--mem` in SLURM script or reduce batch size in config

**Problem:** Container not found
- **Solution:** Make sure `images/mle-dojo.sif` exists. Follow MLE-Dojo setup instructions to obtain the framework container.
