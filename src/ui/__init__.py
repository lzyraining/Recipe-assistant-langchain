"""UI components for the recipe assistant.

This package provides the user interface components for the recipe assistant,
including the chat interface and chat manager.
"""

from .chat_interface import ChatUI
from .chat_manager import ChatManager, get_chat_manager

__all__ = ["ChatUI", "ChatManager", "get_chat_manager"]
