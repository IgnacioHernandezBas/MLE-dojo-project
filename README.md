# MLE-Dojo Agent Project

A modular, extensible agent implementation for the [MLE-Dojo](https://github.com/MLEDojo/mle-dojo) machine learning engineering benchmark, designed for both baseline evaluation and reinforcement learning training.

## Overview

This project provides a clean separation between the MLE-Dojo framework (treated as a dependency) and custom agent code. The architecture is designed to be:

- **Modular**: Core agent logic is framework-agnostic
- **Extensible**: Easy to add new models, wrappers, and training methods
- **Reproducible**: Container definitions and detailed configurations
- **Research-friendly**: Organized structure for running experiments

## Project Structure

```
~/MLE-dojo-project/
├── MLE-Dojo/                    # The cloned MLE-Dojo repo (dependency)
│   └── README.md               # Setup instructions
├── agent/                       # YOUR agent code
│   ├── core/                   # Framework-agnostic core
│   │   ├── base_agent.py       # Abstract base class
│   │   ├── local_model.py      # Qwen/local model implementation
│   │   └── prompts.py          # Prompt templates
│   ├── wrappers/               # Framework-specific wrappers
│   │   ├── mledojo_wrapper.py  # MLE-Dojo interface
│   │   └── verl_wrapper.py     # Verl interface (placeholder)
│   ├── training/               # Training scripts
│   │   ├── generate_trajectories.py
│   │   ├── train_rl.py
│   │   └── evaluate.py
│   └── configs/                # Configuration files
│       ├── agent_config.yaml
│       ├── training_config.yaml
│       └── eval_config.yaml
├── experiments/                 # Experiment logs and results
│   ├── baselines/
│   ├── rl_runs/
│   ├── checkpoints/
│   ├── trajectories/
│   └── evaluations/
├── scripts/                     # Batch job scripts
│   ├── run_baseline.sh
│   ├── train_rl.sh
│   └── submit_slurm.sh
├── containers/                  # Container definitions
│   ├── mle_agent.def           # Apptainer definition
│   └── requirements.txt
├── tests/                       # Unit tests
│   ├── test_agent.py
│   └── README.md
├── README.md                    # This file
└── pyproject.toml              # Package configuration
```

## Quick Start

### 1. Setup MLE-Dojo Dependency

```bash
# Clone MLE-Dojo into the dependency directory
cd MLE-Dojo
git clone https://github.com/MLEDojo/mle-dojo.git .
cd ..

# Or if you prefer to clone from parent directory
git clone https://github.com/MLEDojo/mle-dojo.git MLE-Dojo/

# Follow MLE-Dojo's setup instructions
cd MLE-Dojo
pip install -e .
cd ..
```

### 2. Install Agent Package

```bash
# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### 3. Run a Baseline

```bash
# Generate trajectories with the base model
python agent/training/generate_trajectories.py \
    --num-episodes 10 \
    --model-name Qwen/Qwen2.5-Coder-7B-Instruct \
    --config agent/configs/agent_config.yaml \
    --output-dir experiments/baselines/baseline_001
```

### 4. Train with RL (when implemented)

```bash
# Train using collected trajectories
python agent/training/train_rl.py \
    --trajectories-dir experiments/trajectories \
    --config agent/configs/training_config.yaml \
    --output-dir experiments/rl_runs/run_001
```

### 5. Evaluate

```bash
# Evaluate a trained model
python agent/training/evaluate.py \
    --model-path experiments/checkpoints/model_001 \
    --config agent/configs/eval_config.yaml \
    --num-episodes 10 \
    --output-dir experiments/evaluations/eval_001
```

## Configuration

All configurations are managed through YAML files in `agent/configs/`:

- **agent_config.yaml**: Agent and model settings
- **training_config.yaml**: RL training hyperparameters
- **eval_config.yaml**: Evaluation settings

Edit these files to customize behavior without changing code.

## Container Usage

For reproducible environments, especially on HPC systems:

### Build Container

```bash
cd containers
apptainer build mle_agent.sif mle_agent.def
```

### Run with Container

```bash
# Interactive session
apptainer shell --nv mle_agent.sif

# Run specific command
apptainer exec --nv mle_agent.sif python agent/training/evaluate.py --help
```

### SLURM Job

```bash
sbatch scripts/submit_slurm.sh
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# With coverage
pytest tests/ --cov=agent --cov-report=html
```

### Code Formatting

```bash
# Format code
black agent/ tests/

# Check formatting
black --check agent/ tests/

# Sort imports
isort agent/ tests/
```

### Type Checking

```bash
mypy agent/
```

## Architecture

### Core Components

1. **BaseAgent** (`agent/core/base_agent.py`)
   - Abstract base class defining the agent interface
   - All agents must implement `generate_response()` and `reset()`

2. **LocalModelAgent** (`agent/core/local_model.py`)
   - Concrete implementation using local LLMs (Qwen, etc.)
   - Handles model loading, inference, and checkpointing

3. **PromptManager** (`agent/core/prompts.py`)
   - Manages prompt templates and construction
   - Supports custom templates and history management

### Wrappers

4. **MLEDojoWrapper** (`agent/wrappers/mledojo_wrapper.py`)
   - Interfaces agent with MLE-Dojo environment
   - Handles observation formatting and episode management

5. **VerlWrapper** (`agent/wrappers/verl_wrapper.py`)
   - Placeholder for Verl RL framework integration
   - Will support PPO and other RL algorithms

### Training Pipeline

6. **generate_trajectories.py**
   - Collects agent trajectories for training
   - Saves in format suitable for RL training

7. **train_rl.py**
   - RL training loop (to be implemented)
   - Supports various RL algorithms

8. **evaluate.py**
   - Evaluates trained agents on benchmarks
   - Generates detailed performance reports

## Experiment Management

### Organizing Experiments

Each experiment should have its own directory with:
- Configuration file (YAML)
- Results and logs
- Checkpoints (if applicable)

Example:
```
experiments/rl_runs/run_001_ppo_default/
├── config.yaml
├── checkpoints/
│   ├── iter_010/
│   └── iter_020/
└── logs/
    ├── train.log
    └── tensorboard/
```

### Tracking Experiments

Use the configuration files to document:
- Model architecture and hyperparameters
- Training procedure and settings
- Random seeds for reproducibility

Consider using tools like:
- **TensorBoard**: Built-in logging support
- **Weights & Biases**: Configure in `training_config.yaml`

## Roadmap

### Current Status

- [x] Base agent architecture
- [x] Local model implementation (Qwen)
- [x] MLE-Dojo wrapper
- [x] Configuration management
- [x] Container definitions
- [x] Basic testing framework

### Planned Features

- [ ] Complete MLE-Dojo environment integration
- [ ] Verl RL framework integration
- [ ] PPO training implementation
- [ ] Advanced prompt engineering
- [ ] Multi-task learning support
- [ ] Distributed training
- [ ] Comprehensive evaluation suite

## Contributing

When adding new features:

1. Follow the existing code structure
2. Add tests for new functionality
3. Update relevant documentation
4. Use type hints where appropriate
5. Format code with `black` and `isort`

## Resources

- [MLE-Dojo GitHub](https://github.com/MLEDojo/mle-dojo)
- [Qwen Models](https://huggingface.co/Qwen)
- [Transformers Documentation](https://huggingface.co/docs/transformers)

## License

MIT License - See LICENSE file for details

## Citation

If you use this project in your research, please cite:

```bibtex
@software{mle_dojo_agent,
  title = {MLE-Dojo Agent Implementation},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/MLE-dojo-project}
}
```

## Contact

For questions or issues, please open an issue on GitHub or contact [your.email@example.com](mailto:your.email@example.com).
