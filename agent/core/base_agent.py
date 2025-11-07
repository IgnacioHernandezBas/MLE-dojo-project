"""
Base agent class providing the core interface for MLE-Dojo agents.

This module defines the abstract base class that all agents must implement,
ensuring a consistent interface across different implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class BaseAgent(ABC):
    """
    Abstract base class for MLE-Dojo agents.

    This class defines the core interface that all agents must implement,
    regardless of the underlying model or framework.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.

        Args:
            config: Configuration dictionary for the agent
        """
        self.config = config or {}
        self.conversation_history: List[Dict[str, str]] = []

    @abstractmethod
    def generate_response(
        self,
        observation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response given an observation.

        Args:
            observation: The current observation/state from the environment
            context: Optional additional context for generating the response

        Returns:
            The generated response/action as a string
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the agent's internal state.

        This should be called at the start of each new episode.
        """
        pass

    def update_history(self, observation: str, response: str) -> None:
        """
        Update the conversation history.

        Args:
            observation: The observation that was processed
            response: The response that was generated
        """
        self.conversation_history.append({
            "observation": observation,
            "response": response
        })

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.

        Returns:
            List of observation-response pairs
        """
        return self.conversation_history

    def save_checkpoint(self, path: str) -> None:
        """
        Save agent checkpoint.

        Args:
            path: Path to save the checkpoint
        """
        raise NotImplementedError("Checkpoint saving not implemented for this agent")

    def load_checkpoint(self, path: str) -> None:
        """
        Load agent checkpoint.

        Args:
            path: Path to load the checkpoint from
        """
        raise NotImplementedError("Checkpoint loading not implemented for this agent")
