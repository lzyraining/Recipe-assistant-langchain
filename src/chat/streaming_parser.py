import json
import logging
from dataclasses import dataclass
from typing import Generator, List

from src.tools import ToolCall

logger = logging.getLogger(__name__)


@dataclass
class ParsedResponse:
    """Result of parsing a non-streaming response."""

    text: str
    tool_calls: List[ToolCall]  # Tools ready for execution (tool_response=None)


@dataclass
class ParsedChunk:
    """Result of parsing a single streaming chunk."""

    text_delta: str  # New text content from this chunk
    accumulated_text: str  # Total text accumulated so far
    completed_tools: List[ToolCall]  # Tools ready for execution (tool_response=None)


def parse_streaming_response(chunks) -> Generator[ParsedChunk, None, None]:
    """Parse streaming chunks into structured data.

    This function handles pure data parsing without any tool execution:
    - Accumulates text content from streaming chunks
    - Extracts and tracks tool call metadata
    - Accumulates partial JSON arguments across chunks
    - Detects when tool calls are complete and ready for execution

    Args:
        chunks: Iterator of streaming chunks from LLM

    Yields:
        ParsedChunk: Structured data for each processed chunk

    Returns:
        None (generator function)
    """
    accumulated_text = ""
    partial_tool_calls = {}  # key -> partial tool call data

    logger.info("Starting streaming response parsing")

    try:
        for chunk in chunks:
            text_delta = ""
            completed_tools = []

            # Process chunk content
            if hasattr(chunk, "content") and chunk.content:
                # Handle string content directly
                if isinstance(chunk.content, str):
                    text_delta = chunk.content
                    accumulated_text += text_delta

                # Handle list content with steps
                elif isinstance(chunk.content, list):
                    for step in chunk.content:
                        if isinstance(step, dict):
                            if step.get("type") == "text":
                                step_text = step.get("text", "")
                                text_delta += step_text
                                accumulated_text += step_text

                            elif step.get("type") == "tool_use":
                                tool_call_id = step.get("id")
                                tool_name = step.get("name")
                                partial_json = step.get("partial_json", "")
                                tool_index = step.get("index")

                                # Use index as key for consistency across chunks
                                key = f"index_{tool_index}" if tool_index is not None else tool_call_id

                                if key:
                                    # Initialize or update partial tool call
                                    if key not in partial_tool_calls:
                                        partial_tool_calls[key] = {
                                            "name": tool_name,
                                            "id": tool_call_id,
                                            "partial_json": "",
                                        }

                                    # Update tool metadata
                                    if tool_name:
                                        partial_tool_calls[key]["name"] = tool_name
                                    if tool_call_id:
                                        partial_tool_calls[key]["id"] = tool_call_id

                                    # Accumulate partial JSON
                                    partial_tool_calls[key]["partial_json"] += partial_json

                                    # Check if tool call is complete
                                    try:
                                        current_json = partial_tool_calls[key]["partial_json"]
                                        tool_args = json.loads(current_json)

                                        final_tool_name = partial_tool_calls[key]["name"]
                                        final_tool_id = partial_tool_calls[key]["id"]

                                        if final_tool_name and final_tool_id:
                                            # Create ToolCall without tool_response (will be populated after execution)
                                            tool_call = ToolCall(
                                                name=final_tool_name,
                                                tool_call_id=final_tool_id,
                                                tool_args=tool_args,
                                                tool_response=None,
                                            )
                                            completed_tools.append(tool_call)
                                            logger.info(
                                                f"Tool call completed and removed from partial_tool_calls: {key}"
                                            )
                                            del partial_tool_calls[key]

                                    except json.JSONDecodeError:
                                        # JSON not complete yet, continue accumulating
                                        pass

                        elif isinstance(step, str):
                            text_delta += step
                            accumulated_text += step

            # Yield parsed chunk data
            yield ParsedChunk(text_delta=text_delta, accumulated_text=accumulated_text, completed_tools=completed_tools)

        logger.info(f"Streaming parsing complete. Final text length: {len(accumulated_text)}")

    except Exception as e:
        logger.error(f"Error in streaming parsing: {e}")
        # Yield what we have so far
        yield ParsedChunk(text_delta="", accumulated_text=accumulated_text, completed_tools=[])
