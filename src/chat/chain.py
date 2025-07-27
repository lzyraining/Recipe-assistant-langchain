import logging
from typing import Generator, List, Tuple

from langchain_core.runnables import RunnableSequence

from src.model.llm import get_llm
from src.tools import ToolCall, Tools

from .prompt import create_recipe_assistant_chat_prompt_template
from .response_parser import parse_response
from .streaming_parser import parse_streaming_response

logger = logging.getLogger(__name__)


def get_chain() -> RunnableSequence:
    """Create a LangChain processing chain for the recipe assistant.

    This function creates a chain that processes user input through
    a prompt template, sends it to the LLM, and parses the output
    as a string.

    Returns:
        A runnable sequence that can process user input and return
        a string response
    """
    llm = get_llm().get_instance()
    prompt = create_recipe_assistant_chat_prompt_template()
    tools = Tools.available_tools()

    return prompt | llm.bind_tools(tools)


def extract_bot_response(bot_response: any) -> Tuple[str, List[ToolCall]]:
    """Extract the bot response from the LLM output with tool execution.

    This function uses the response parser for data extraction and handles
    tool execution when tools are ready.

    Args:
        bot_response: LangChain bot response from the LLM

    Returns:
        Tuple[str, List[ToolCall]]: response text and executed tool calls
    """
    logger.info("Starting response extraction with parser")

    try:
        # Parse the response to extract text and tool calls
        parsed_response = parse_response(bot_response)

        # Execute tools
        executed_tool_calls = []
        for tool_call in parsed_response.tool_calls:
            tool = Tools.tool_registry().get(tool_call.name)
            if tool:
                logger.info(
                    f"Executing tool: {tool_call.name} "
                    f"(ID: {tool_call.tool_call_id}) with args: {tool_call.tool_args}"
                )
                tool_response = tool.invoke(input=tool_call.tool_args)

                # Update the tool_call with the response
                tool_call.tool_response = tool_response

                executed_tool_calls.append(tool_call)
                logger.info(f"Tool execution completed: {tool_call.name} (ID: {tool_call.tool_call_id})")
            else:
                logger.error(f"Tool {tool_call.name} not found in registry")

        logger.info(
            f"Response extraction complete. Text length: {len(parsed_response.text)}, "
            f"Tool calls: {len(executed_tool_calls)}"
        )
        return parsed_response.text, executed_tool_calls

    except Exception as e:
        logger.error(f"Error in response extraction: {e}")
        return "", []

def extract_bot_response_from_streaming(
    chunks,
) -> Generator[Tuple[str, List[ToolCall], bool], None, Tuple[str, List[ToolCall]]]:
    """Extract bot response from streaming chunks with tool execution.

    This function uses the streaming parser for data extraction and handles
    tool execution when tools are ready.

    Args:
        chunks: Iterator of streaming chunks from LLM

    Yields:
        Tuple[str, List[ToolCall], bool]: (accumulated_text, completed_tool_calls, is_final_chunk)

    Returns:
        Tuple[str, List[ToolCall]]: Final (complete_text, all_tool_calls)
    """
    all_tool_calls = []
    final_text = ""

    logger.info("Starting streaming response extraction with parser")

    try:
        for parsed_chunk in parse_streaming_response(chunks):
            chunk_completed_tools = []

            # Execute completed tools
            for tool_call in parsed_chunk.completed_tools:
                tool = Tools.tool_registry().get(tool_call.name)
                if tool:
                    logger.info(
                        f"Executing tool: {tool_call.name} "
                        f"(ID: {tool_call.tool_call_id}) with args: {tool_call.tool_args}"
                    )
                    tool_response = tool.invoke(input=tool_call.tool_args)

                    # Update the tool_call with the response
                    tool_call.tool_response = tool_response

                    chunk_completed_tools.append(tool_call)
                    all_tool_calls.append(tool_call)
                    logger.info(f"Tool execution completed: {tool_call.name} (ID: {tool_call.tool_call_id})")
                else:
                    logger.error(f"Tool {tool_call.name} not found in registry")

            final_text = parsed_chunk.accumulated_text

            # Yield current state
            yield parsed_chunk.accumulated_text, chunk_completed_tools, False

        logger.info(
            f"Streaming extraction complete. Text length: {len(final_text)}, "
            f"Tool calls: {len(all_tool_calls)}"
        )
        return final_text, all_tool_calls

    except Exception as e:
        logger.error(f"Error in streaming extraction: {e}")
        return final_text, all_tool_calls
