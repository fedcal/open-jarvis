"""Concrete LLM adapters."""

from jarvis_server.llm.adapters.anthropic import AnthropicAdapter
from jarvis_server.llm.adapters.echo import EchoAdapter
from jarvis_server.llm.adapters.ollama import OllamaAdapter
from jarvis_server.llm.adapters.openai import OpenAIAdapter

__all__ = [
    "AnthropicAdapter",
    "EchoAdapter",
    "OllamaAdapter",
    "OpenAIAdapter",
]
