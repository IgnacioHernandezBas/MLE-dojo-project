"""
Generate trajectories for RL training.

This script runs the agent in the MLE-Dojo environment to collect
trajectories that can be used for supervised fine-tuning or RL training.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.core.local_model import LocalModelAgent
from agent.wrappers.mledojo_wrapper import MLEDojoWrapper


def collect_trajectories(
    num_episodes: int,
    model_name: str,
    config_path: str,
    output_dir: str,
    max_steps_per_episode: int = 100
) -> List[Dict[str, Any]]:
    """
    Collect trajectories by running the agent.

    Args:
        num_episodes: Number of episodes to collect
        model_name: Model name or path
        config_path: Path to agent configuration
        output_dir: Directory to save trajectories
        max_steps_per_episode: Maximum steps per episode

    Returns:
        List of trajectory dictionaries
    """
    # Load configuration
    import yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize agent
    print(f"Initializing agent with model: {model_name}")
    agent = LocalModelAgent(model_name=model_name, config=config.get("agent", {}))

    # Create wrapper
    wrapper = MLEDojoWrapper(agent, config=config.get("wrapper", {}))

    # TODO: Initialize MLE-Dojo environment
    # For now, this is a placeholder
    print("\nWARNING: MLE-Dojo environment initialization not yet implemented")
    print("This is a template that needs to be completed once the environment is set up\n")

    trajectories = []

    for episode in range(num_episodes):
        print(f"\n{'='*60}")
        print(f"Episode {episode + 1}/{num_episodes}")
        print(f"{'='*60}")

        # Reset for new episode
        wrapper.reset()

        # TODO: Run episode in actual MLE-Dojo environment
        # episode_data = wrapper.run_episode(env, max_steps=max_steps_per_episode)

        # Placeholder trajectory structure
        episode_data = {
            "episode_id": episode,
            "steps": [],
            "total_reward": 0.0,
            "success": False
        }

        trajectories.append(episode_data)

        # Save trajectory
        output_path = Path(output_dir) / f"trajectory_{episode:04d}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(episode_data, f, indent=2)

        print(f"Saved trajectory to {output_path}")

    # Save summary
    summary = {
        "num_episodes": num_episodes,
        "model_name": model_name,
        "trajectories": trajectories
    }

    summary_path = Path(output_dir) / "summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nTrajectory collection complete!")
    print(f"Saved {len(trajectories)} trajectories to {output_dir}")

    return trajectories


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate trajectories for RL training"
    )
    parser.add_argument(
        "--num-episodes",
        type=int,
        default=10,
        help="Number of episodes to collect"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="Qwen/Qwen2.5-Coder-7B-Instruct",
        help="Model name or path"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="agent/configs/agent_config.yaml",
        help="Path to agent configuration file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="experiments/trajectories",
        help="Directory to save trajectories"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=100,
        help="Maximum steps per episode"
    )

    args = parser.parse_args()

    collect_trajectories(
        num_episodes=args.num_episodes,
        model_name=args.model_name,
        config_path=args.config,
        output_dir=args.output_dir,
        max_steps_per_episode=args.max_steps
    )


if __name__ == "__main__":
    main()
