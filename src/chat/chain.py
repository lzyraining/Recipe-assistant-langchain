import json
import logging
from typing import List, Tuple

from langchain_core.runnables import RunnableSequence

from src.model.llm import get_llm
from src.tools import ToolCall, Tools

from .prompt import create_recipe_assistant_chat_prompt_template

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
    """Extract the bot response from the LLM output.

    Args:
        bot_respose (List[dict]): langchain bot response from the LLM

    Returns:
        Tuple[str, List[str]]: response text and tool calls
    """
    steps = bot_response.content
    logger.info(f"Extracting bot response from steps: {steps}")
    response_text: str = ""
    tool_calls: List[ToolCall] = []
    for step in steps:
        if step.get("type") == "text":
            response_text = step["text"]
        elif step.get("type") == "tool_use":
            tool_name = step["name"]
            tool_call_id = step["id"]
            tool_args_str = step.get("partial_json", "{}")
            tool_args = json.loads(tool_args_str)

            tool = Tools.tool_registry().get(tool_name)
            logger.info(f"Invoking tool: {tool_name} with args: {tool_args}")
            tool_response = tool.invoke(input=tool_args)

            tool_calls.append(
                ToolCall(name=tool_name, tool_call_id=tool_call_id, tool_response=tool_response, tool_args=tool_args)
            )
    return response_text, tool_calls
