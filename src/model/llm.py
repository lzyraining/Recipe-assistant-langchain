import logging
from typing import Optional

import boto3
from botocore.config import Config
from langchain_aws import ChatBedrock

from src.model.llm_config import LLMConfig

logger = logging.getLogger(__name__)

_llm_singleton: Optional["LLM"] = None


class LLM:
    """LLM client for interacting with AWS Bedrock.

    This class provides a wrapper around the ChatBedrock client
    with configuration management and singleton access.

    Attributes:
        _llm_config: Configuration for the LLM client
        _llm_instance: The underlying ChatBedrock instance
        _connect_timeout: Connection timeout in seconds
        _read_timeout: Read timeout in seconds
    """

    def __init__(self, llm_config: LLMConfig, connect_timeout: int = 10, read_timeout: int = 30):
        """Initialize the LLM client.

        Args:
            llm_config: Configuration for the LLM client
            connect_timeout: Connection timeout in seconds (default: 10)
            read_timeout: Read timeout in seconds (default: 30)
        """
        self._llm_config = llm_config
        self._llm_instance: Optional[ChatBedrock] = None
        self._connect_timeout = connect_timeout
        self._read_timeout = read_timeout

    def get_instance(self) -> ChatBedrock:
        """Get the ChatBedrock instance, creating it if necessary.

        Returns:
            The ChatBedrock instance
        """
        if not self._llm_instance:
            self.create_llm_instance()
        return self._llm_instance

    def create_llm_instance(self) -> None:
        """Create a new ChatBedrock instance.

        This method initializes the AWS Bedrock client with the
        configured parameters.
        """
        logger.info("Create LLM instance...")
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self._llm_config.region,
            config=Config(
                retries={"max_attempts": 3, "mode": "standard"},
                connect_timeout=self._connect_timeout,
                read_timeout=self._read_timeout,
            ),
        )
        self._llm_instance = ChatBedrock(
            client=bedrock_client,
            model_id=self._llm_config.model_id,
            streaming=True,
            model_kwargs={
                "temperature": self._llm_config.temperature,
                "max_tokens": self._llm_config.max_tokens,
            },
        )
        logger.info("LLM instance is created with streaming")

    def get_config(self) -> LLMConfig:
        """Get the LLM configuration.

        Returns:
            The LLM configuration
        """
        return self._llm_config


def initialize_llm(config: LLMConfig, eager_loading: bool = False) -> None:
    """Initialize the LLM singleton instance.

    Args:
        config: The LLM configuration
        eager_loading: Whether to create the LLM instance immediately

    Returns:
        None
    """
    global _llm_singleton
    if _llm_singleton is not None:
        logger.warning("LLM instance is already initialized")
        return
    _llm_singleton = LLM(config)
    if eager_loading is True:
        _llm_singleton.get_instance()


def get_llm() -> LLM:
    """Get the LLM singleton instance.

    Returns:
        The LLM singleton instance

    Raises:
        RuntimeError: If the LLM instance is not initialized
    """
    if _llm_singleton is None:
        raise RuntimeError("LLM instance is not initialized")
    return _llm_singleton


def is_llm_initialized() -> bool:
    """Check if the LLM singleton instance is initialized.

    Returns:
        True if the LLM instance is initialized, False otherwise
    """
    return _llm_singleton is not None


def reset_llm() -> None:
    """Reset the LLM singleton instance.

    This function sets the LLM singleton instance to None,
    allowing it to be garbage collected.

    Returns:
        None
    """
    global _llm_singleton
    _llm_singleton = None
    logger.info("LLM instance is reset")
