import logging
from typing import Any, Generator, List, Optional, Tuple

from langchain_core.messages import AIMessage, HumanMessage

from src.chat.chain import get_chain

logger = logging.getLogger(__name__)

_chat_manager: Optional["ChatManager"] = None


class ChatManager:
    """Chat manager for handling conversation with the LLM.

    This class manages the chat history and processes user messages
    through the LLM chain, handling streaming responses.

    Attributes:
        _chat_history: Internal history of messages for LangChain
        _llm_chain: The LangChain chain for processing messages
    """

    def __init__(self, llm_chain: Any):
        """Initialize the chat manager.

        Args:
            llm_chain: The LangChain chain for processing messages
        """
        self._chat_history = []
        self._llm_chain = llm_chain

    def add_user_message(self, message: str, chat_history: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Add a user message to the chat history.

        Args:
            message: The user's message
            chat_history: The current Gradio chat history

        Returns:
            Updated Gradio chat history with the user's message
        """
        self._chat_history.append(HumanMessage(content=message))
        chat_history.append((message, None))
        return chat_history

    def process_user_message(
        self, message: str, chat_history: List[Tuple[str, str]]
    ) -> Generator[List[Tuple[str, str]], None, List[Tuple[str, str]]]:
        """Process a user message and stream the response.

        This method streams the response from the LLM, updating the chat history
        with each chunk of the response.

        Args:
            message: The user's message
            chat_history: The current Gradio chat history

        Yields:
            Updated Gradio chat history with the partial response

        Returns:
            Final updated Gradio chat history with the complete response
        """
        input_data = {"input": message, "chat_history": self._chat_history[:-1]}

        partial_response = ""
        logger.info(f"Processing message: {message}")
        for chunk in self._llm_chain.stream(input_data):
            partial_response += chunk
            chat_history[-1] = (message, partial_response)
            yield chat_history

        self._chat_history.append(AIMessage(content=partial_response))
        logger.info("Message response completed")
        return chat_history

    def clear_history(self) -> List[Tuple[str, str]]:
        """Clear the chat history.

        This method clears both the internal LangChain chat history
        and returns an empty list for the Gradio chat history.

        Returns:
            Empty list for Gradio chat history
        """
        logger.info("Clearing chat history")
        self._chat_history = []
        return []


def _init_chat_manager() -> None:
    """Initialize the chat manager singleton.

    This function creates a new ChatManager instance with a LangChain
    and assigns it to the global _chat_manager variable.
    """
    global _chat_manager
    logger.info("Creating chat manager...")
    llm_chain = get_chain()
    _chat_manager = ChatManager(llm_chain)


def get_chat_manager() -> ChatManager:
    """Get the chat manager singleton instance.

    This function returns the global chat manager instance,
    initializing it if necessary.

    Returns:
        The ChatManager singleton instance
    """
    if _chat_manager is None:
        _init_chat_manager()
    return _chat_manager
