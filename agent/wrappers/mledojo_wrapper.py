"""
MLE-Dojo wrapper for integrating agents with the MLE-Dojo environment.

This module provides the interface layer between our agent implementation
and the MLE-Dojo competition framework.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add mle-dojo to path if not already there
mle_dojo_path = Path(__file__).parent.parent.parent / "mle-dojo"
if str(mle_dojo_path) not in sys.path:
    sys.path.insert(0, str(mle_dojo_path))

from agent.core.base_agent import BaseAgent


class MLEDojoWrapper:
    """
    Wrapper class for interfacing agents with MLE-Dojo environment.

    This class handles the communication between our agent implementation
    and the MLE-Dojo competition framework, managing state, observations,
    and actions in the format expected by MLE-Dojo.
    """

    def __init__(
        self,
        agent: BaseAgent,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the MLE-Dojo wrapper.

        Args:
            agent: The agent instance to use (must inherit from BaseAgent)
            config: Optional configuration for the wrapper
        """
        self.agent = agent
        self.config = config or {}
        self.episode_count = 0
        self.total_reward = 0.0
        self.current_episode_reward = 0.0

    def reset(self) -> None:
        """
        Reset the wrapper and agent for a new episode.

        This should be called at the start of each new task/episode.
        """
        self.agent.reset()
        self.current_episode_reward = 0.0
        self.episode_count += 1

    def step(
        self,
        observation: Dict[str, Any],
        reward: Optional[float] = None,
        done: bool = False,
        info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process one step in the environment.

        Args:
            observation: Observation from the MLE-Dojo environment
            reward: Reward from the previous action
            done: Whether the episode is finished
            info: Additional information from the environment

        Returns:
            Action to take (as a string)
        """
        # Update reward tracking
        if reward is not None:
            self.current_episode_reward += reward
            self.total_reward += reward

        # Extract the actual observation text
        obs_text = self._format_observation(observation)

        # Build context with task information if available
        context = {}
        if info and "task_description" in info:
            context["task_description"] = info["task_description"]

        # Generate action using the agent
        action = self.agent.generate_response(obs_text, context=context)

        # Handle episode completion
        if done:
            self._on_episode_end()

        return action

    def _format_observation(self, observation: Dict[str, Any]) -> str:
        """
        Format the observation dictionary into a string for the agent.

        Args:
            observation: Raw observation from MLE-Dojo

        Returns:
            Formatted observation string
        """
        # Handle different observation formats
        if isinstance(observation, dict):
            # Check for common keys
            if "text" in observation:
                return observation["text"]
            elif "state" in observation:
                return str(observation["state"])
            else:
                # Format all keys
                parts = []
                for key, value in observation.items():
                    parts.append(f"{key}: {value}")
                return "\n".join(parts)
        else:
            # If not a dict, just convert to string
            return str(observation)

    def _on_episode_end(self) -> None:
        """
        Handle episode completion.

        This method is called when an episode ends and can be used
        for logging, checkpointing, etc.
        """
        print(f"\nEpisode {self.episode_count} completed")
        print(f"Episode reward: {self.current_episode_reward:.2f}")
        print(f"Total reward: {self.total_reward:.2f}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get wrapper statistics.

        Returns:
            Dictionary containing statistics
        """
        return {
            "episode_count": self.episode_count,
            "total_reward": self.total_reward,
            "current_episode_reward": self.current_episode_reward,
            "avg_reward_per_episode": (
                self.total_reward / self.episode_count if self.episode_count > 0 else 0.0
            )
        }

    def save_trajectory(self, path: str) -> None:
        """
        Save the agent's trajectory to a file.

        Args:
            path: Path to save the trajectory
        """
        import json

        trajectory_data = {
            "episode_count": self.episode_count,
            "total_reward": self.total_reward,
            "history": self.agent.get_history(),
            "stats": self.get_stats()
        }

        with open(path, 'w') as f:
            json.dump(trajectory_data, f, indent=2)

        print(f"Trajectory saved to {path}")

    def run_episode(
        self,
        env: Any,
        max_steps: Optional[int] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Run a complete episode in the MLE-Dojo environment.

        Args:
            env: MLE-Dojo environment instance
            max_steps: Maximum number of steps (None for unlimited)
            verbose: Whether to print progress

        Returns:
            Episode statistics
        """
        self.reset()

        # Get initial observation
        obs = env.reset()
        done = False
        step_count = 0

        while not done and (max_steps is None or step_count < max_steps):
            # Generate and execute action
            action = self.step(obs, done=False)

            if verbose:
                print(f"\n--- Step {step_count + 1} ---")
                print(f"Action: {action[:100]}...")  # Print first 100 chars

            # Execute action in environment
            obs, reward, done, info = env.step(action)

            # Update wrapper with new observation and reward
            if step_count + 1 < (max_steps or float('inf')):
                self.step(obs, reward=reward, done=done, info=info)

            step_count += 1

        # Final step to mark episode as done
        if not done:
            self.step(obs, done=True)

        return self.get_stats()
