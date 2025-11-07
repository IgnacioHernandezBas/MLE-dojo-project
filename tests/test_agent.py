"""
Unit tests for the agent package.

Run with: pytest tests/test_agent.py
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.core.base_agent import BaseAgent
from agent.core.prompts import PromptManager


class DummyAgent(BaseAgent):
    """Dummy agent for testing."""

    def generate_response(self, observation, context=None):
        return "dummy response"

    def reset(self):
        self.conversation_history = []


class TestBaseAgent:
    """Test cases for BaseAgent."""

    def test_initialization(self):
        """Test agent initialization."""
        config = {"test": "value"}
        agent = DummyAgent(config=config)
        assert agent.config == config
        assert agent.conversation_history == []

    def test_update_history(self):
        """Test conversation history updates."""
        agent = DummyAgent()
        agent.update_history("obs1", "resp1")
        agent.update_history("obs2", "resp2")

        history = agent.get_history()
        assert len(history) == 2
        assert history[0]["observation"] == "obs1"
        assert history[0]["response"] == "resp1"

    def test_reset(self):
        """Test agent reset."""
        agent = DummyAgent()
        agent.update_history("obs", "resp")
        assert len(agent.get_history()) == 1

        agent.reset()
        assert len(agent.get_history()) == 0

    def test_generate_response(self):
        """Test response generation."""
        agent = DummyAgent()
        response = agent.generate_response("test observation")
        assert response == "dummy response"


class TestPromptManager:
    """Test cases for PromptManager."""

    def test_initialization(self):
        """Test prompt manager initialization."""
        manager = PromptManager()
        assert manager.custom_templates == {}

    def test_build_simple_prompt(self):
        """Test building a simple prompt."""
        manager = PromptManager()
        prompt = manager.build_prompt(observation="Test observation")

        assert "Test observation" in prompt
        assert manager.SYSTEM_PROMPT in prompt

    def test_build_prompt_with_context(self):
        """Test building prompt with task context."""
        manager = PromptManager()
        context = {"task_description": "Solve this problem"}
        prompt = manager.build_prompt(
            observation="Test observation",
            context=context
        )

        assert "Test observation" in prompt
        assert "Solve this problem" in prompt

    def test_build_prompt_with_history(self):
        """Test building prompt with conversation history."""
        manager = PromptManager()
        history = [
            {"observation": "obs1", "response": "resp1"},
            {"observation": "obs2", "response": "resp2"}
        ]
        prompt = manager.build_prompt(
            observation="obs3",
            history=history
        )

        assert "obs1" in prompt
        assert "resp1" in prompt
        assert "obs3" in prompt

    def test_format_history(self):
        """Test history formatting."""
        manager = PromptManager()
        history = [
            {"observation": f"obs{i}", "response": f"resp{i}"}
            for i in range(10)
        ]

        formatted = manager._format_history(history, max_turns=3)

        # Should only include last 3 turns
        assert "obs7" in formatted
        assert "obs8" in formatted
        assert "obs9" in formatted
        assert "obs0" not in formatted

    def test_reflection_prompt(self):
        """Test reflection prompt generation."""
        manager = PromptManager()
        trajectory = [
            {
                "observation": "obs1",
                "action": "action1",
                "reward": 1.0
            },
            {
                "observation": "obs2",
                "action": "action2",
                "reward": 0.5
            }
        ]

        prompt = manager.build_reflection_prompt(trajectory)

        assert "obs1" in prompt
        assert "action1" in prompt
        assert "1.0" in prompt
        assert "What went well" in prompt

    def test_get_template(self):
        """Test template retrieval."""
        manager = PromptManager()

        system_template = manager.get_template("system")
        assert system_template == manager.SYSTEM_PROMPT

        task_template = manager.get_template("task")
        assert task_template == manager.TASK_TEMPLATE

    def test_custom_templates(self):
        """Test custom template support."""
        custom = {"my_template": "Custom content"}
        manager = PromptManager(custom_templates=custom)

        template = manager.get_template("my_template")
        assert template == "Custom content"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
