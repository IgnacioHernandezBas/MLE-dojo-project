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

# Import MLE-Dojo components
from mledojo.gym.env import KaggleEnvironment
from mledojo.gym.competition import CompetitionRegistry, CompInfo
from mledojo.competitions import get_metric


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

    # Initialize MLE-Dojo environment
    print("\nInitializing MLE-Dojo environment...")

    # Get competition configuration from config or use default
    competition_name = config.get("competition", {}).get("name", "home-data-for-ml-course")
    mle_dojo_source = Path(__file__).parent.parent.parent / "mle-dojo-source"
    competition_data_dir = mle_dojo_source / "data" / "prepared" / competition_name / "data"

    if not competition_data_dir.exists():
        raise FileNotFoundError(
            f"Competition data not found at {competition_data_dir}\n"
            f"Please prepare the competition first using:\n"
            f"  cd {mle_dojo_source}\n"
            f"  echo '{competition_name}' > prepare/comp.txt\n"
            f"  PYTHONPATH='.' python prepare/mle.py --competitions-file prepare/comp.txt --data-dir data/prepared --logs-dir data/prepare_logs"
        )

    # Create competition registry
    registry = CompetitionRegistry(
        name=competition_name,
        data_dir=str(competition_data_dir),
        comp_info=CompInfo(
            category="General",
            level="beginner",
            output_type="submission.csv",
            higher_is_better=True
        ),
        metric_class=get_metric(competition_name)
    )

    # Get environment configuration
    env_config = config.get("env", {})
    max_steps = env_config.get("max_steps", 10)

    print(f"Competition: {competition_name}")
    print(f"Max steps per episode: {max_steps}")
    print()

    # Run evaluation episodes
    total_reward = 0.0
    success_count = 0

    for episode in range(num_episodes):
        if verbose:
            print(f"\n{'='*60}")
            print(f"Evaluating Episode {episode + 1}/{num_episodes}")
            print(f"{'='*60}")

        # Create fresh environment for each episode
        episode_output_dir = Path(output_dir) / f"episode_{episode}"
        env = KaggleEnvironment.make(
            competition_name=competition_name,
            output_dir=str(episode_output_dir),
            competition_registry=registry,
            render_mode="human" if verbose else None,
            score_mode="position",
            gpu_device=env_config.get("gpu_device", 0),
            gpu_memory_limit=env_config.get("gpu_memory_limit", 32),
            execution_timeout=env_config.get("execution_timeout", 600)
        )

        # Run episode using wrapper
        episode_result = wrapper.run_episode(env, max_steps=max_steps, verbose=verbose)

        # Extract detailed results
        final_position_score = episode_result.get("final_position_score", 0.0)
        best_position_score = episode_result.get("best_position_score", 0.0)
        steps_taken = episode_result.get("steps_taken", 0)

        # Success is defined as achieving any positive position score
        success = best_position_score > 0.0

        episode_data = {
            "episode_id": episode,
            "final_position_score": float(final_position_score),
            "best_position_score": float(best_position_score) if best_position_score is not None else 0.0,
            "steps_taken": int(steps_taken),
            "success": bool(success),
            "feedback_history": episode_result.get("feedback_history", [])
        }

        results["episodes"].append(episode_data)

        total_reward += best_position_score if best_position_score is not None else 0.0
        if success:
            success_count += 1

        if verbose:
            print(f"Episode {episode + 1} - Best Position Score: {best_position_score:.4f}, "
                  f"Steps: {steps_taken}, Success: {success}")

        # Clean up environment
        env.close()

    # Calculate aggregate metrics
    all_best_scores = [ep.get("best_position_score", 0.0) for ep in results["episodes"]]
    all_steps = [ep.get("steps_taken", 0) for ep in results["episodes"]]

    results["metrics"] = {
        "avg_best_position_score": total_reward / num_episodes,
        "max_best_position_score": max(all_best_scores) if all_best_scores else 0.0,
        "min_best_position_score": min(all_best_scores) if all_best_scores else 0.0,
        "success_rate": success_count / num_episodes,
        "total_episodes": num_episodes,
        "successful_episodes": success_count,
        "avg_steps_taken": sum(all_steps) / len(all_steps) if all_steps else 0,
        "episodes_with_steps": sum(1 for s in all_steps if s > 0)
    }

    # Save results
    results_path = Path(output_dir) / f"eval_results_{benchmark}.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print("Evaluation Complete!")
    print("="*60)
    print(f"Average Best Position Score: {results['metrics']['avg_best_position_score']:.4f}")
    print(f"Max Position Score: {results['metrics']['max_best_position_score']:.4f}")
    print(f"Success Rate: {results['metrics']['success_rate']:.2%}")
    print(f"Avg Steps Taken: {results['metrics']['avg_steps_taken']:.1f}")
    print(f"Episodes with Actions: {results['metrics']['episodes_with_steps']}/{num_episodes}")
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
