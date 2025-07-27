import json
import logging
from dataclasses import dataclass
from typing import List

from src.tools import ToolCall

logger = logging.getLogger(__name__)


@dataclass
class ParsedResponse:
    """Result of parsing a response."""

    text: str
    tool_calls: List[ToolCall]  # Tools ready for execution (tool_response=None)


def parse_response(bot_response) -> ParsedResponse:
    """Parse a response into structured data.

    This function handles pure data parsing without any tool execution:
    - Extracts text content from response steps
    - Extracts tool call metadata and arguments
    - Creates ToolCall objects ready for execution

    Args:
        bot_response: LangChain bot response from the LLM

    Returns:
        ParsedResponse: Structured data with text and tool calls
    """
    steps = bot_response.content
    logger.info(f"Starting response parsing from steps: {steps}")

    response_text = ""
    tool_calls = []

    try:
        for step in steps:
            if step.get("type") == "text":
                response_text = step["text"]

            elif step.get("type") == "tool_use":
                tool_name = step["name"]
                tool_call_id = step["id"]
                tool_args_str = step.get("partial_json", "{}")
                tool_args = json.loads(tool_args_str)

                # Create ToolCall without tool_response (will be populated after execution)
                tool_call = ToolCall(name=tool_name, tool_call_id=tool_call_id, tool_args=tool_args, tool_response=None)
                tool_calls.append(tool_call)
                logger.info(f"Tool call parsed: {tool_name} (ID: {tool_call_id}) with args: {tool_args}")

        logger.info(f"Response parsing complete. Text length: {len(response_text)}, Tool calls: {len(tool_calls)}")
        return ParsedResponse(text=response_text, tool_calls=tool_calls)

    except Exception as e:
        logger.error(f"Error in response parsing: {e}")
        return ParsedResponse(text=response_text, tool_calls=tool_calls)
