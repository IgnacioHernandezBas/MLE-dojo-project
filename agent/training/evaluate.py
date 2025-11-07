"""
Evaluation script for trained agents.

This script evaluates agent performance on the MLE-Dojo benchmark
and generates detailed performance reports.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.core.local_model import LocalModelAgent
from agent.wrappers.mledojo_wrapper import MLEDojoWrapper


def evaluate_agent(
    model_path: str,
    config_path: str,
    output_dir: str,
    num_episodes: int = 10,
    benchmark: str = "default",
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Evaluate agent on MLE-Dojo benchmark.

    Args:
        model_path: Path to trained model checkpoint
        config_path: Path to evaluation configuration
        output_dir: Directory to save evaluation results
        num_episodes: Number of episodes to evaluate
        benchmark: Benchmark name/difficulty level
        verbose: Whether to print detailed progress

    Returns:
        Dictionary containing evaluation metrics
    """
    print("="*60)
    print("Agent Evaluation")
    print("="*60)
    print(f"Model: {model_path}")
    print(f"Benchmark: {benchmark}")
    print(f"Episodes: {num_episodes}")
    print("="*60)

    # Load configuration
    import yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize agent
    print("\nLoading agent...")
    agent = LocalModelAgent(model_name=model_path, config=config.get("agent", {}))

    # Create wrapper
    wrapper = MLEDojoWrapper(agent, config=config.get("wrapper", {}))

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Evaluation results
    results = {
        "model_path": model_path,
        "benchmark": benchmark,
        "num_episodes": num_episodes,
        "episodes": [],
        "metrics": {}
    }

    # TODO: Initialize MLE-Dojo environment with benchmark
    print("\nWARNING: MLE-Dojo environment initialization not yet implemented")
    print("This is a template that needs to be completed once the environment is set up\n")

    # Run evaluation episodes
    total_reward = 0.0
    success_count = 0

    for episode in range(num_episodes):
        if verbose:
            print(f"\n{'='*60}")
            print(f"Evaluating Episode {episode + 1}/{num_episodes}")
            print(f"{'='*60}")

        # TODO: Run episode in actual environment
        # episode_result = wrapper.run_episode(env, verbose=verbose)

        # Placeholder episode result
        episode_result = {
            "episode_id": episode,
            "reward": 0.0,
            "success": False,
            "steps": 0
        }

        results["episodes"].append(episode_result)

        total_reward += episode_result["reward"]
        if episode_result["success"]:
            success_count += 1

        if verbose:
            print(f"Episode {episode + 1} - Reward: {episode_result['reward']:.2f}, "
                  f"Success: {episode_result['success']}")

    # Calculate aggregate metrics
    results["metrics"] = {
        "avg_reward": total_reward / num_episodes,
        "success_rate": success_count / num_episodes,
        "total_episodes": num_episodes,
        "successful_episodes": success_count
    }

    # Save results
    results_path = Path(output_dir) / f"eval_results_{benchmark}.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print("Evaluation Complete!")
    print("="*60)
    print(f"Average Reward: {results['metrics']['avg_reward']:.2f}")
    print(f"Success Rate: {results['metrics']['success_rate']:.2%}")
    print(f"Results saved to: {results_path}")
    print("="*60)

    return results


def compare_models(
    model_paths: List[str],
    config_path: str,
    output_dir: str,
    num_episodes: int = 10
) -> None:
    """
    Compare multiple models on the same benchmark.

    Args:
        model_paths: List of model paths to compare
        config_path: Path to evaluation configuration
        output_dir: Directory to save comparison results
        num_episodes: Number of episodes per model
    """
    print("="*60)
    print("Model Comparison")
    print("="*60)
    print(f"Models: {len(model_paths)}")
    print(f"Episodes per model: {num_episodes}")
    print("="*60)

    comparison_results = []

    for model_path in model_paths:
        print(f"\nEvaluating: {model_path}")
        result = evaluate_agent(
            model_path=model_path,
            config_path=config_path,
            output_dir=output_dir,
            num_episodes=num_episodes,
            verbose=False
        )
        comparison_results.append(result)

    # Save comparison
    comparison_path = Path(output_dir) / "model_comparison.json"
    with open(comparison_path, 'w') as f:
        json.dump(comparison_results, f, indent=2)

    print("\n" + "="*60)
    print("Comparison Results")
    print("="*60)
    for result in comparison_results:
        print(f"\nModel: {result['model_path']}")
        print(f"  Avg Reward: {result['metrics']['avg_reward']:.2f}")
        print(f"  Success Rate: {result['metrics']['success_rate']:.2%}")
    print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate trained agents"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        required=True,
        help="Path to trained model or checkpoint"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="agent/configs/eval_config.yaml",
        help="Path to evaluation configuration file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="experiments/evaluations",
        help="Directory to save evaluation results"
    )
    parser.add_argument(
        "--num-episodes",
        type=int,
        default=10,
        help="Number of episodes to evaluate"
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="default",
        help="Benchmark name or difficulty level"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress"
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        help="Compare multiple models (provide list of paths)"
    )

    args = parser.parse_args()

    if args.compare:
        compare_models(
            model_paths=args.compare,
            config_path=args.config,
            output_dir=args.output_dir,
            num_episodes=args.num_episodes
        )
    else:
        evaluate_agent(
            model_path=args.model_path,
            config_path=args.config,
            output_dir=args.output_dir,
            num_episodes=args.num_episodes,
            benchmark=args.benchmark,
            verbose=args.verbose
        )


if __name__ == "__main__":
    main()
