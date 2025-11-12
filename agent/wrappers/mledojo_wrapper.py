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
            env: MLE-Dojo KaggleEnvironment instance
            max_steps: Maximum number of steps
            verbose: Whether to print progress

        Returns:
            Episode statistics including reward and steps
        """
        self.reset()

        # MLE-Dojo uses different API - get initial info
        # First, request competition overview
        obs, reward = env.step("request_info", info_type="overview")

        step_count = 0
        max_steps = max_steps or 10

        # Store feedback from environment
        feedback_history = []

        if verbose:
            print(f"Starting episode with max {max_steps} steps...")
            print(f"Initial feedback: {obs.get('feedback', {}).get('base', {}).get('feedback', '')[:200]}...")

        # Track current reward (position score from MLE-Dojo)
        self.current_episode_reward = obs.get('current_position_score', 0.0)

        # Main interaction loop
        for step in range(max_steps):
            step_count += 1

            if verbose:
                print(f"\n--- Step {step_count}/{max_steps} ---")

            # Extract feedback as observation for agent
            feedback = obs.get('feedback', {}).get('base', {}).get('feedback', '')

            # Build context for agent
            context = {
                "step": step_count,
                "max_steps": max_steps,
                "current_reward": obs.get('current_position_score', 0.0),
                "best_reward": obs.get('best_position_score', 0.0),
                "feedback": feedback
            }

            # Get agent's response
            agent_response = self.agent.generate_response(feedback, context=context)

            if verbose:
                print(f"Agent response (first 300 chars):\n{agent_response[:300]}...")

            # Parse agent response to determine action
            try:
                # Try to extract and execute code
                if "```python" in agent_response or "```py" in agent_response or "<code>" in agent_response or "import " in agent_response:
                    code = self._extract_code(agent_response)

                    if verbose:
                        print(f"Executing code ({len(code)} chars)...")
                        print(f"Code preview:\n{code[:200]}...")

                    # Execute code in environment
                    obs, step_reward = env.step("execute_code", code=code)

                else:
                    # Otherwise, request more information
                    if verbose:
                        print("No code detected, requesting data structure information...")
                    obs, step_reward = env.step("request_info", info_type="data_structure")

            except ValueError as e:
                # Code extraction failed
                if verbose:
                    print(f"Code extraction failed: {e}")
                    print("Requesting information instead...")

                # Fall back to requesting information
                obs, step_reward = env.step("request_info", info_type="data_structure")

            except Exception as e:
                # Other errors during execution
                if verbose:
                    print(f"Error during action execution: {e}")
                    print("Requesting information to recover...")

                # Try to recover by requesting info
                try:
                    obs, step_reward = env.step("request_info", info_type="overview")
                except Exception as e2:
                    if verbose:
                        print(f"Recovery failed: {e2}")
                    # If everything fails, create a minimal observation
                    obs = {"feedback": {"base": {"feedback": f"Error: {str(e)}"}}, "action_status": "ERROR"}
                    step_reward = 0.0

            # Update reward tracking
            current_score = obs.get('current_position_score', 0.0)
            self.current_episode_reward = current_score
            self.total_reward += step_reward

            feedback_history.append({
                "step": step_count,
                "action_status": obs.get('action_status', 'UNKNOWN'),
                "reward": step_reward,
                "cumulative_score": current_score
            })

            if verbose:
                print(f"Action status: {obs.get('action_status', 'UNKNOWN')}")
                print(f"Step reward: {step_reward:.4f}")
                print(f"Current score: {current_score:.4f}")
                best_score = obs.get('best_position_score', 0.0)
                print(f"Best score: {best_score if best_score is not None else 0.0:.4f}")

        if verbose:
            print(f"\nEpisode completed: {step_count} steps")
            print(f"Final score: {self.current_episode_reward:.4f}")

        # Get final environment state for detailed metrics
        final_obs = obs if obs else {}

        return {
            **self.get_stats(),
            "feedback_history": feedback_history,
            "final_position_score": self.current_episode_reward,
            "best_position_score": final_obs.get('best_position_score', 0.0),
            "steps_taken": step_count,
            "final_observation": final_obs
        }

    def _extract_code(self, response: str) -> str:
        """
        Extract Python code from agent response with validation.

        Args:
            response: Agent's text response

        Returns:
            Extracted and validated Python code

        Raises:
            ValueError: If no valid code can be extracted
        """
        import re
        import ast

        # Strategy 1: Extract from markdown code blocks
        code_candidates = []

        # Try markdown code blocks with language specification
        markdown_pattern = r"```(?:python|py)\s*\n(.*?)```"
        markdown_matches = re.findall(markdown_pattern, response, re.DOTALL)
        code_candidates.extend(markdown_matches)

        # Try plain code blocks without language specification
        if not code_candidates:
            plain_pattern = r"```\s*\n(.*?)```"
            plain_matches = re.findall(plain_pattern, response, re.DOTALL)
            code_candidates.extend(plain_matches)

        # Strategy 2: Extract from XML-like tags (if using structured responses)
        xml_pattern = r"<code>(.*?)</code>"
        xml_matches = re.findall(xml_pattern, response, re.DOTALL)
        code_candidates.extend(xml_matches)

        # Strategy 3: Look for lines starting with imports or code patterns
        if not code_candidates:
            lines = response.split("\n")
            code_lines = []
            in_code = False

            for line in lines:
                stripped = line.strip()

                # Start of code block indicators
                if stripped.startswith(("import ", "from ", "def ", "class ", "async def")):
                    in_code = True

                if in_code:
                    # Skip lines that look like natural language
                    if stripped and not any([
                        stripped.startswith(("I will", "Let me", "First", "Then", "Now", "Here", "This")),
                        stripped.endswith(("?", ":")),
                        len(stripped.split()) > 15 and "=" not in stripped  # Long natural language lines
                    ]):
                        code_lines.append(line)
                    elif not stripped:  # Keep empty lines in code
                        code_lines.append(line)

            if code_lines:
                code_candidates.append("\n".join(code_lines))

        # Validate and select best candidate
        for candidate in code_candidates:
            candidate = candidate.strip()
            if not candidate:
                continue

            # Try to parse with AST to validate syntax
            try:
                ast.parse(candidate)
                # Valid Python code found
                return candidate
            except SyntaxError:
                # Try to fix common issues
                # Remove leading/trailing explanatory text
                fixed_candidate = self._clean_code(candidate)
                try:
                    ast.parse(fixed_candidate)
                    return fixed_candidate
                except SyntaxError:
                    continue

        # If no valid code found, return empty string instead of whole response
        # This prevents executing invalid code
        raise ValueError(f"No valid Python code found in response. Response preview: {response[:200]}...")

    def _clean_code(self, code: str) -> str:
        """
        Clean extracted code by removing common issues.

        Args:
            code: Raw code string

        Returns:
            Cleaned code string
        """
        lines = code.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            # Skip lines that are clearly explanatory text
            if stripped.startswith(("Note:", "This will", "The above", "Output:")):
                continue
            # Skip lines that are just comments explaining the code
            if stripped.startswith("#") and len(stripped) > 50:
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()
