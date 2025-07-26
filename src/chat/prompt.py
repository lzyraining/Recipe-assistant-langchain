from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)


def create_recipe_assistant_system_message_template() -> SystemMessagePromptTemplate:
    """Create a system message template for the recipe assistant.

    This function creates a system message template that instructs the LLM
    to act as a helpful recipe assistant.

    Returns:
        A system message prompt template for the recipe assistant
    """
    system_template = """
    You are a helpful recipe assistant that provides cooking recipes, nutritional information.
    Respond in a friendly, conversational manner.
    """
    return SystemMessagePromptTemplate.from_template(system_template)


def create_recipe_assistant_human_message_template() -> HumanMessagePromptTemplate:
    """Create a human message template for the recipe assistant.

    This function creates a human message template that formats
    the user's input for the LLM.

    Returns:
        A human message prompt template for the recipe assistant
    """
    human_template = """
    {input}
    """
    return HumanMessagePromptTemplate.from_template(human_template)


def create_recipe_assistant_chat_prompt_template() -> ChatPromptTemplate:
    """Create a chat prompt template for the recipe assistant.

    This function creates a chat prompt template that combines
    the system message, chat history, and human message templates.

    Returns:
        A chat prompt template for the recipe assistant
    """
    system_template = create_recipe_assistant_system_message_template()
    human_template = create_recipe_assistant_human_message_template()

    return ChatPromptTemplate.from_messages(
        [
            system_template,
            MessagesPlaceholder(variable_name="chat_history"),
            human_template,
        ]
    )
