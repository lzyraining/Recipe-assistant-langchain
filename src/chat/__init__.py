"""Chat components for the recipe assistant.

This package provides the chat components for the recipe assistant,
including the LangChain chain, prompt templates, and recipe model.
"""

from .chain import extract_bot_response, get_chain

__all__ = ["get_chain", "extract_bot_response"]
