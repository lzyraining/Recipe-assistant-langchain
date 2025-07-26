from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence

from src.model.llm import get_llm

from .prompt import create_recipe_assistant_chat_prompt_template


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

    return prompt | llm | StrOutputParser()
