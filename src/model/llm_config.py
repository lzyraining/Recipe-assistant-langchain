import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    """Configuration for the LLM client.

    Attributes:
        model_id: The identifier for the LLM model
        region: AWS region for the Bedrock service
        api_key: API key for authentication
        temperature: Controls randomness in output generation
        max_tokens: Maximum number of tokens in the response
    """

    model_id: str
    region: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 3000

    class Builder:
        """Builder class for LLMConfig.

        Provides a fluent interface for constructing LLMConfig objects.
        """

        def __init__(self):
            self._model_id: Optional[str] = None
            self._region: Optional[str] = None
            self._api_key: Optional[str] = None
            self._temperature: float = 0.7
            self._max_tokens: int = 3000

        def model_id(self, model_id: str):
            """Set the model ID.

            Args:
                model_id: The identifier for the LLM model

            Returns:
                Self for method chaining
            """
            self._model_id = model_id
            return self

        def region(self, region: str):
            """Set the AWS region.

            Args:
                region: AWS region for the Bedrock service

            Returns:
                Self for method chaining
            """
            self._region = region
            return self

        def api_key(self, api_key: str):
            """Set the API key.

            Args:
                api_key: API key for authentication

            Returns:
                Self for method chaining
            """
            self._api_key = api_key
            return self

        def temperature(self, temperature: float):
            """Set the temperature parameter.

            Args:
                temperature: Controls randomness in output generation

            Returns:
                Self for method chaining
            """
            self._temperature = temperature
            return self

        def max_tokens(self, max_tokens: int):
            """Set the maximum tokens parameter.

            Args:
                max_tokens: Maximum number of tokens in the response

            Returns:
                Self for method chaining
            """
            self._max_tokens = max_tokens
            return self

        def build(self):
            """Build and return a new LLMConfig instance.

            Returns:
                A new LLMConfig instance

            Raises:
                ValueError: If any required fields are not set
            """
            required_fields = [self._model_id, self._region, self._api_key]
            if not all(field is not None for field in required_fields):
                raise ValueError("Required fields (model_id, region, api_key) must be set")
            return LLMConfig(
                model_id=self._model_id,
                region=self._region,
                api_key=self._api_key,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )

    @classmethod
    def builder(cls):
        """Create a new builder instance.

        Returns:
            A new Builder instance
        """
        return cls.Builder()


def load_llm_config() -> LLMConfig:
    """Load LLM configuration from environment variables.

    Returns:
        A configured LLMConfig instance

    Raises:
        ValueError: If required environment variables are not set
    """
    model_id = os.getenv("AWS_BEDROCK_MODEL_ID")
    if not model_id:
        raise ValueError("AWS_BEDROCK_MODEL_ID environment variable is not set")

    region = os.getenv("AWS_REGION")
    if not region:
        raise ValueError("AWS_REGION environment variable is not set")

    api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    if not api_key:
        raise ValueError("AWS_BEARER_TOKEN_BEDROCK environment variable is not set")

    return LLMConfig.builder().model_id(model_id).region(region).api_key(api_key).build()
