"""
Prompt templates and management for MLE-Dojo agents.

This module provides templates and utilities for building effective prompts
for the agent to interact with the environment.
"""

from typing import Any, Dict, List, Optional


class PromptManager:
    """
    Manages prompt templates and construction for agents.

    This class handles building prompts from observations, history,
    and context to create effective inputs for language models.
    """

    # System prompt that defines the agent's role
    SYSTEM_PROMPT = """You are an expert machine learning engineer competing in Kaggle-style ML competitions.
You are working in the MLE-Dojo environment where you can iteratively develop ML solutions.

## Environment Actions Available:
1. **request_info** - Request information about the competition
   - info_type="overview": Get competition description and goals
   - info_type="data_structure": Get data file structure and columns
   - info_type="metric": Get evaluation metric details

2. **execute_code** - Execute Python code in the environment
   - Write code to explore data, train models, generate predictions
   - Code runs in a sandboxed Python environment with ML libraries available
   - Always save predictions to 'submission.csv' in the correct format

## Your Workflow Should Follow:
1. **Understand** - Request overview and data structure
2. **Explore** - Write code to load and analyze the data
3. **Develop** - Iteratively build and improve your solution:
   - Start with simple baseline models
   - Experiment with feature engineering
   - Try different algorithms
   - Tune hyperparameters
4. **Submit** - Generate final predictions in the required format

## Code Response Format:
When you want to execute code, wrap it in markdown code blocks:

```python
# Your code here
import pandas as pd
# ... rest of code
```

## Important Guidelines:
- Start simple, then iterate and improve
- Always handle errors gracefully
- Read feedback from previous actions carefully
- The environment gives you feedback after each action
- Your score improves when predictions are better
- Think step-by-step and explain your reasoning before coding"""

    # Template for the main task prompt
    TASK_TEMPLATE = """
## Competition Details
{task_description}

## Current Feedback from Environment
{observation}

## Your Next Action
Based on the feedback above, decide your next step:

1. If you need more information: Explain what you need to know
2. If you're ready to code: Provide your reasoning, then write the code in a ```python``` block

Think step-by-step:
- What did the last action accomplish?
- What information do I have now?
- What should I do next to improve my solution?
"""

    # Template with conversation history
    HISTORY_TEMPLATE = """
## Previous Actions and Feedback
{history}

## Latest Feedback from Environment
{observation}

## Analysis and Next Action
Review what you've tried so far. Then:

1. **Analyze**: What worked? What didn't? What did you learn?
2. **Decide**: What's the logical next step to improve your solution?
3. **Act**: Write code in a ```python``` block OR explain what information you need

Remember: Iterate and improve! Each action should build on previous learning.
"""

    def __init__(self, custom_templates: Optional[Dict[str, str]] = None):
        """
        Initialize the prompt manager.

        Args:
            custom_templates: Optional custom prompt templates
        """
        self.custom_templates = custom_templates or {}

    def build_prompt(
        self,
        observation: str,
        history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a complete prompt from components.

        Args:
            observation: Current observation from the environment
            history: Previous observation-response pairs
            context: Additional context (e.g., task description)

        Returns:
            Complete prompt string
        """
        parts = [self.SYSTEM_PROMPT]

        # Add task description if provided in context
        if context and "task_description" in context:
            parts.append(
                self.TASK_TEMPLATE.format(
                    task_description=context["task_description"],
                    observation=observation
                )
            )
        else:
            # Use history template if we have history
            if history and len(history) > 0:
                history_text = self._format_history(history)
                parts.append(
                    self.HISTORY_TEMPLATE.format(
                        history=history_text,
                        observation=observation
                    )
                )
            else:
                # Simple prompt with just observation
                parts.append(f"\n## Current Observation\n{observation}\n")
                parts.append("\n## Your Response\n")

        return "\n".join(parts)

    def _format_history(self, history: List[Dict[str, str]], max_turns: int = 10) -> str:
        """
        Format conversation history into a readable string.

        Args:
            history: List of observation-response pairs
            max_turns: Maximum number of turns to include

        Returns:
            Formatted history string
        """
        # Only include last N turns to avoid context overflow
        recent_history = history[-max_turns:] if len(history) > max_turns else history

        formatted = []
        for i, turn in enumerate(recent_history, 1):
            formatted.append(f"### Turn {i}")
            formatted.append(f"**Observation:** {turn['observation']}")
            formatted.append(f"**Response:** {turn['response']}")
            formatted.append("")

        return "\n".join(formatted)

    def build_reflection_prompt(self, trajectory: List[Dict[str, Any]]) -> str:
        """
        Build a prompt for reflecting on a completed trajectory.

        Args:
            trajectory: Complete trajectory (observations, actions, rewards)

        Returns:
            Reflection prompt
        """
        prompt = """## Trajectory Reflection

You completed a task. Here's what happened:

"""
        for i, step in enumerate(trajectory, 1):
            prompt += f"### Step {i}\n"
            prompt += f"Observation: {step.get('observation', 'N/A')}\n"
            prompt += f"Action: {step.get('action', 'N/A')}\n"
            prompt += f"Reward: {step.get('reward', 'N/A')}\n\n"

        prompt += """
## Analysis Questions
1. What went well in this trajectory?
2. What could have been done better?
3. What key insights did you gain?

Provide a brief reflection on each question.
"""

        return prompt

    def get_template(self, template_name: str) -> str:
        """
        Get a specific template by name.

        Args:
            template_name: Name of the template

        Returns:
            Template string
        """
        # Check custom templates first
        if template_name in self.custom_templates:
            return self.custom_templates[template_name]

        # Fall back to default templates
        templates = {
            "system": self.SYSTEM_PROMPT,
            "task": self.TASK_TEMPLATE,
            "history": self.HISTORY_TEMPLATE
        }

        return templates.get(template_name, "")
