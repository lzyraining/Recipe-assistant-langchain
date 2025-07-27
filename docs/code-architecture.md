# Code Architecture - Recipe Assistant

## Overview

This document describes the architecture and design of the Recipe Assistant application, a LangChain-based conversational AI system with streaming capabilities and tool integration.

## 🏗️ System Architecture

```
┌─────────────────┐     ┌─────────────────┐    ┌─────────────────┐
│   User Interface │    │  Chat Manager   │    │   LLM Chain     │
│   (Gradio UI)    │◄──►│   (Business)    │◄──►│  (LangChain)    │
└─────────────────┘     └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │    Parsers      │    │     Tools       │
                       │ (Data Extract)  │    │  (Execution)    │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   LLM Model     │    │   External      │
                       │ (Claude/Bedrock)│    │     APIs        │
                       └─────────────────┘    └─────────────────┘
```

## 📁 Directory Structure

```
src/
├── apis/                   # External API integrations
│   ├── __init__.py
│   └── api_client.py      # HTTP client utilities
├── chat/                   # Core conversation logic
│   ├── __init__.py
│   ├── chain.py           # LangChain pipeline and tool execution
│   ├── prompt.py          # Prompt template definitions
│   ├── response_parser.py # Non-streaming response parsing
│   └── streaming_parser.py # Streaming response parsing
├── model/                  # LLM configuration and management
│   ├── __init__.py
│   ├── llm.py            # LLM instance management
│   └── llm_config.py     # Configuration settings
├── tools/                  # Tool definitions and registry
│   ├── __init__.py
│   ├── recipe_tool.py    # Recipe-specific tools
│   ├── tool_call.py      # Tool call data structures
│   └── tools.py          # Tool registry and management
└── ui/                     # User interface components
    ├── __init__.py
    ├── chat_interface.py  # Gradio UI components
    └── chat_manager.py    # Business logic and state management
```

## 🔧 Core Components

### 1. UI Layer (`src/ui/`)

**Purpose**: Handles user interaction and presentation logic.

**Components**:
- `chat_interface.py`: Gradio web interface with streaming toggle
- `chat_manager.py`: Business logic, state management, and LangChain integration

**Key Features**:
- Real-time streaming responses
- Input validation and error handling
- Chat history management
- Streaming/non-streaming mode toggle

### 2. Chat Layer (`src/chat/`)

**Purpose**: Core conversation processing and response handling.

**Components**:
- `chain.py`: LangChain pipeline composition and tool execution
- `prompt.py`: System prompts and template definitions
- `streaming_parser.py`: Incremental parsing of streaming responses
- `response_parser.py`: Parsing of complete responses

**Key Features**:
- LCEL (LangChain Expression Language) pipeline
- Separation of parsing and execution logic
- Support for both streaming and batch processing
- Tool call detection and execution

### 3. Tools Layer (`src/tools/`)

**Purpose**: External function integration and tool management.

**Components**:
- `tools.py`: Tool registry and discovery
- `tool_call.py`: Data structures for tool interactions
- `recipe_tool.py`: Recipe-specific tool implementations

**Key Features**:
- Registry pattern for tool management
- Type-safe tool call structures
- Easy extensibility for new tools

### 4. Model Layer (`src/model/`)

**Purpose**: LLM configuration and instance management.

**Components**:
- `llm.py`: LLM instance creation and management
- `llm_config.py`: Configuration settings and environment handling

**Key Features**:
- Configuration management
- Singleton pattern for resource efficiency

### 5. APIs Layer (`src/apis/`)

**Purpose**: External service integration utilities.

**Components**:
- `api_client.py`: HTTP client utilities and common patterns

## 🔄 Data Flow

### 1. Non-Streaming Request Flow

```
1. User Input (UI)
   ↓
2. Chat Manager (validate, add to history)
   ↓
3. LangChain Chain (prompt + LLM + tools)
   ↓
4. Response Parser (extract text and tool calls)
   ↓
5. Tool Execution (if tools detected)
   ↓
6. Final Response (back to UI)
```

### 2. Streaming Request Flow

```
1. User Input (UI)
   ↓
2. Chat Manager (validate, add to history)
   ↓
3. LangChain Chain Stream (real-time chunks)
   ↓
4. Streaming Parser (incremental parsing)
   ↓
5. Tool Execution (as tools complete)
   ↓
6. Real-time UI Updates (yield partial responses)
```

## 🎯 Design Principles

### 1. Separation of Concerns
- **Parsing Logic**: Separated from execution logic
- **UI Logic**: Separated from business logic
- **Configuration**: Externalized from implementation

### 2. Single Responsibility
- Each module has a clear, focused purpose
- Functions do one thing well
- Classes have single reasons to change

### 3. Dependency Inversion
- High-level modules don't depend on low-level details
- Dependencies injected rather than created internally
- Interfaces define contracts between layers

### 4. Open/Closed Principle
- Easy to extend (add new tools, parsers)
- Closed to modification of existing stable code
- Registry patterns support extensibility

## 🔌 Key Interfaces

### 1. Parser Interface

```python
# Streaming Parser
def parse_streaming_response(chunks) -> Generator[ParsedChunk, None, None]:
    """Parse streaming chunks into structured data."""

# Response Parser  
def parse_response(bot_response) -> ParsedResponse:
    """Parse complete response into structured data."""
```

### 2. Tool Interface

```python
@tool
def tool_function(arg: str) -> str:
    """Tool function with LangChain decorator."""
    return result
```

### 3. Chain Interface

```python
# LCEL Composition
chain = prompt | llm.bind_tools(tools)

# Invocation
result = chain.invoke(input_data)
chunks = chain.stream(input_data)
```

## 📊 State Management

### 1. Chat History
- Maintained as list of LangChain message objects
- Includes `HumanMessage`, `AIMessage`, `ToolMessage`
- Provides context for subsequent interactions

### 2. Tool State
- Tools are stateless functions
- Tool calls tracked with unique IDs
- Responses linked back to original calls

### 3. UI State
- Gradio manages UI component state
- Chat history synchronized between backend and frontend
- Streaming state managed through generators

## 🚀 Execution Flow

### 1. Application Startup
```python
# main.py
chat_manager = get_chat_manager()  # Singleton initialization
ChatUI.launch_chat_interface(chat_manager)  # UI launch
```

### 2. Message Processing
```python
# User input → Chat Manager → Chain → Parser → Tools → Response
input_data = {"input": message, "chat_history": history}
result = chain.invoke(input_data)
parsed = parse_response(result)
executed_tools = execute_tools(parsed.tool_calls)
```

### 3. Streaming Processing
```python
# Real-time chunk processing with tool execution
for chunk in parse_streaming_response(chain.stream(input_data)):
    if chunk.completed_tools:
        execute_tools(chunk.completed_tools)
    yield chunk.accumulated_text
```

## 🔧 Configuration Management

### 1. Environment-based Configuration
- LLM provider settings
- API keys and credentials
- Feature flags and toggles

### 2. Runtime Configuration
- Tool registry contents
- Prompt templates
- UI component settings

## 📈 Scalability Considerations

### 1. Stateless Design
- Core processing functions are stateless
- Easy to scale horizontally
- Session state isolated to chat manager

### 2. Resource Management
- Singleton pattern for expensive resources
- Lazy initialization of components
- Efficient memory usage with generators

### 3. Modularity
- Independent modules can be scaled separately
- Clear interfaces enable distributed deployment
- Tool registry supports dynamic loading

## 🔍 Error Handling Strategy

### 1. Graceful Degradation
- Fallback to non-streaming on streaming errors
- Default responses for tool failures
- User-friendly error messages

### 2. Error Boundaries
- Try-catch blocks at appropriate levels
- Logging for debugging and monitoring
- Clean error propagation

### 3. Validation
- Input validation at UI level
- Type checking throughout the pipeline
- Tool argument validation

This architecture provides a solid foundation for building scalable, maintainable LangChain applications with clear separation of concerns and extensible design patterns.
