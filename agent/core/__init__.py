"""
Core agent components.

This module contains framework-agnostic base classes and implementations.
"""

from agent.core.base_agent import BaseAgent
from agent.core.local_model import LocalModelAgent
from agent.core.prompts import PromptManager

__all__ = ["BaseAgent", "LocalModelAgent", "PromptManager"]
