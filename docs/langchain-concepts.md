# LangChain Concepts - Recipe Assistant

## Overview

This project demonstrates core LangChain concepts through a practical recipe assistant application. The codebase covers essential LangChain features that beginners need to understand.

## 🎯 Key LangChain Patterns Demonstrated

### 1. Chain Composition
Using LCEL to build processing pipelines declaratively.

### 2. Prompt Engineering
Structuring prompts for conversational AI with system instructions.

### 3. Tool Integration
Extending LLM capabilities with external function calls.

### 4. Streaming Processing
Handling real-time response generation for better UX.

### 5. State Management
Managing conversation history and context across interactions.

### 6. Response Processing
Parsing and handling different types of LLM outputs.

---

## 🔧 LangChain Concepts Covered

### 1. LangChain Expression Language (LCEL)

**Location**: `src/chat/chain.py`

LCEL uses the pipe operator (`|`) to chain components together declaratively.

```python
def get_chain() -> RunnableSequence:
    llm = get_llm().get_instance()
    prompt = create_recipe_assistant_chat_prompt_template()
    tools = Tools.available_tools()

    return prompt | llm.bind_tools(tools)
```

**Key Takeaways:**
- Pipe operator (`|`) chains LangChain components
- `RunnableSequence` is the result of LCEL composition
- Components flow: prompt → llm → tools
- Declarative approach to building chains

### 2. Prompt Templates

**Location**: `src/chat/prompt.py`

Chat prompt templates structure conversations with the LLM.

```python
def create_recipe_assistant_chat_prompt_template() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", RECIPE_ASSISTANT_SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
```

**Key Takeaways:**
- `ChatPromptTemplate.from_messages()` creates conversational prompts
- `MessagesPlaceholder` inserts dynamic chat history
- Variable substitution with `{input}`
- Different message types: system, human, AI

### 3. Streaming Responses

**Location**: `src/chat/chain.py` - `extract_bot_response_from_streaming()`

Streaming provides real-time response generation.

```python
# Start streaming
for parsed_chunk in parse_streaming_response(chunks):
    # Process each chunk as it arrives
    yield parsed_chunk.accumulated_text, chunk_completed_tools, False
```

**Key Takeaways:**
- `.stream()` method enables streaming from LangChain chains
- Streaming returns chunks that need to be processed incrementally
- Real-time UI updates possible with streaming
- Streaming works with tool calls

### 4. Tool Calling

**Location**: `src/tools/recipe_tool.py`

Tools extend LLM capabilities by calling external functions.

```python
@tool
def get_recipe(recipe_name: str) -> str:
    """Get a recipe for the specified dish.
    
    Args:
        recipe_name: The name of the recipe to retrieve
        
    Returns:
        A detailed recipe with ingredients and instructions
    """
    # Tool implementation here
    return recipe_data
```

**Key Takeaways:**
- `@tool` decorator converts functions to LangChain tools
- Tool docstrings are important - LLM uses them to understand when to call tools
- Tools receive structured arguments from the LLM
- Tools return string responses back to the LLM

### 5. Tool Binding and Execution

**Location**: `src/chat/chain.py`

Tools are bound to the LLM and executed when needed.

```python
# Binding tools to LLM
llm.bind_tools(tools)

# Tool execution during response processing
tool = Tools.tool_registry().get(tool_call.name)
tool_response = tool.invoke(input=tool_call.tool_args)
```

**Key Takeaways:**
- `bind_tools()` makes tools available to the LLM
- LLM decides when to call tools based on user input
- Tool execution happens during response processing
- Tool responses are fed back to the LLM for final response

### 6. Structured Output Parsing

**Location**: `src/chat/streaming_parser.py` and `src/chat/response_parser.py`

LLM responses need to be parsed to extract text and tool calls.

```python
# Parsing LLM response structure
for step in bot_response.content:
    if step.get("type") == "text":
        response_text = step["text"]
    elif step.get("type") == "tool_use":
        # Extract tool call information
        tool_name = step["name"]
        tool_call_id = step["id"]
        tool_args = json.loads(step.get("partial_json", "{}"))
```

**Key Takeaways:**
- LLM responses have structured content with different step types
- Text content and tool calls are separate steps
- Tool arguments come as JSON that needs parsing
- Streaming responses require incremental parsing

### 7. Chat History Management

**Location**: `src/ui/chat_manager.py`

LangChain uses message objects to maintain conversation context.

```python
# Adding messages to chat history
self._chat_history.append(HumanMessage(content=message))
self._chat_history.append(AIMessage(content=response_text))

# Tool messages for tool call context
ai_message = AIMessage(content=[...])  # Contains tool call
tool_message = ToolMessage(
    content=tool_response,
    tool_call_id=tool_call.tool_call_id,
    name=tool_call.name,
)
```

**Key Takeaways:**
- `HumanMessage`, `AIMessage`, `ToolMessage` represent different message types
- Chat history is a list of message objects
- Tool calls create both AI messages (with tool call) and tool messages (with response)
- Message history provides context for the LLM

### 8. Chain Invocation

**Location**: `src/ui/chat_manager.py`

Chains are invoked with input data and chat history.

```python
# Preparing input for the chain
input_data = {"input": message, "chat_history": self._chat_history[:-1]}

# Non-streaming invocation
chain_result = self._llm_chain.invoke(input_data)

# Streaming invocation
streaming_chunks = self._llm_chain.stream(input_data)
```

**Key Takeaways:**
- Chains expect specific input format (dict with keys)
- Chat history is passed as context
- `invoke()` for single response, `stream()` for streaming
- Input data structure must match prompt template variables

---

## 📝 What's Not Covered

This project focuses on core concepts and doesn't cover:
- Advanced prompt techniques (few-shot, chain-of-thought)
- Multiple tool calls in single response
- Custom LLM implementations
- Vector databases or retrieval
- Advanced chain types (sequential, parallel)
- Memory management beyond basic chat history

---

## 🎓 Next Steps

After understanding this codebase:
1. Try modifying the system prompt
2. Add a new tool following the existing pattern
3. Experiment with different LLM providers
4. Add validation to tool inputs
5. Implement error handling for tool failures

This codebase provides a solid foundation for understanding how LangChain applications work in practice.
