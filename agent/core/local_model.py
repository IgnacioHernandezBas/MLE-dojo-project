"""
Local model agent implementation using Qwen or other local LLMs.

This module provides an implementation of the BaseAgent for local models,
with support for models like Qwen2.5-Coder that can run locally.
"""

import torch
from typing import Any, Dict, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig

from agent.core.base_agent import BaseAgent
from agent.core.prompts import PromptManager


class LocalModelAgent(BaseAgent):
    """
    Agent implementation using local language models.

    This agent can use models like Qwen2.5-Coder-7B-Instruct or other
    local models for generating responses.
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
        config: Optional[Dict[str, Any]] = None,
        device: Optional[str] = None
    ):
        """
        Initialize the local model agent.

        Args:
            model_name: HuggingFace model name or path to local model
            config: Configuration dictionary
            device: Device to run the model on (cuda/cpu)
        """
        super().__init__(config)

        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Model parameters from config
        self.max_new_tokens = self.config.get("max_new_tokens", 512)
        self.temperature = self.config.get("temperature", 0.7)
        self.top_p = self.config.get("top_p", 0.9)

        # Initialize prompt manager
        self.prompt_manager = PromptManager()

        # Load model and tokenizer
        self._load_model()

    def _load_model(self) -> None:
        """Load the model and tokenizer."""
        print(f"Loading model {self.model_name} on {self.device}...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        # Load model with device_map for optimal memory management (requires accelerate)
        dtype = torch.float16 if self.device == "cuda" else torch.float32

        # Check for quantization settings from config
        performance_config = self.config.get("performance", {})
        use_4bit = performance_config.get("use_4bit_quantization", False)
        use_8bit = performance_config.get("use_8bit_quantization", False)

        # Prepare quantization config if needed
        quantization_config = None
        if use_4bit:
            print("Using 4-bit quantization")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=dtype,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        elif use_8bit:
            print("Using 8-bit quantization")
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True
            )

        # Use device_map="auto" for better performance with accelerate library
        # Falls back to manual device placement if accelerate is not available
        try:
            model_kwargs = {
                "device_map": "auto",
                "trust_remote_code": True
            }

            # Add quantization config if specified
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
            else:
                model_kwargs["torch_dtype"] = dtype

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
        except ValueError as e:
            if "accelerate" in str(e):
                print("Warning: accelerate not found, falling back to manual device placement")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=dtype,
                    trust_remote_code=True
                )
                self.model = self.model.to(self.device)
            else:
                raise

        # Create text generation pipeline
        # Note: When using device_map="auto", don't specify device parameter
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer
        )

        print(f"Model loaded successfully on {self.device}")

    def generate_response(
        self,
        observation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response using the local model.

        Args:
            observation: Current observation from the environment
            context: Optional context including task description, etc.

        Returns:
            Generated response/action
        """
        # Build prompt using the prompt manager
        prompt = self.prompt_manager.build_prompt(
            observation=observation,
            history=self.conversation_history,
            context=context
        )

        # Generate response
        outputs = self.pipe(
            prompt,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            do_sample=True,
            return_full_text=False
        )

        response = outputs[0]["generated_text"].strip()

        # Update history
        self.update_history(observation, response)

        return response

    def reset(self) -> None:
        """Reset the agent's conversation history."""
        self.conversation_history = []

    def save_checkpoint(self, path: str) -> None:
        """
        Save model checkpoint (if fine-tuned).

        Args:
            path: Path to save the checkpoint
        """
        if hasattr(self.model, 'save_pretrained'):
            self.model.save_pretrained(path)
            self.tokenizer.save_pretrained(path)
            print(f"Checkpoint saved to {path}")
        else:
            raise NotImplementedError("Model does not support checkpoint saving")

    def load_checkpoint(self, path: str) -> None:
        """
        Load model checkpoint.

        Args:
            path: Path to load the checkpoint from
        """
        print(f"Loading checkpoint from {path}...")
        self.model = AutoModelForCausalLM.from_pretrained(
            path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map=self.device,
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)

        # Recreate pipeline
        # Note: When using device_map, don't specify device parameter
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer
        )
        print("Checkpoint loaded successfully")
