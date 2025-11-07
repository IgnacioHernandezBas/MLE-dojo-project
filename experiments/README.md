# Experiments Directory

This directory contains all experimental runs, checkpoints, and results.

## Structure

- **baselines/** - Baseline agent runs (no RL training)
- **rl_runs/** - RL training runs with different configurations
- **checkpoints/** - Model checkpoints from training
- **trajectories/** - Collected trajectories for training
- **evaluations/** - Evaluation results and reports

## Organization

Each experiment run should follow this naming convention:
- `baselines/baseline_<date>_<description>/`
- `rl_runs/run_<id>_<description>/`

Example:
```
experiments/
├── baselines/
│   └── baseline_20240115_qwen7b/
│       ├── config.yaml
│       ├── results.json
│       └── logs/
├── rl_runs/
│   └── run_001_ppo_default/
│       ├── config.yaml
│       ├── checkpoints/
│       └── logs/
└── evaluations/
    └── eval_20240115/
        ├── results.json
        └── plots/
```

## Best Practices

1. Always include a `config.yaml` or `config.json` with each experiment
2. Use descriptive names for experiment directories
3. Keep detailed logs of each run
4. Document any manual changes or interventions
5. Use git to track experiment configurations (but not large model files)
