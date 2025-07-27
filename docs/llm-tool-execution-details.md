# LLM Tool Use Guide

## High-Level Workflow

### Basic Flow

```
User Input → App → LLM → Response
```

### Tool Use Flow

```
User Input → App → LLM → Tool Decision → Tool Execution → Tool Results → LLM Synthesis → Final Response
```

## Claude Tool Use Complete Flow

### End-to-End Processing

```
                                                    Model
                                            Tool Calling      tool_name: get_recipe     Tool Invocation      History + Tool Result      Final Response
"Get me a chocolate cake recipe" ──────────▶    ┌───┐    ──────────▶ tool_args:        ──────────▶ {recipe data} ──────────▶ ┌───┐ ──────────▶ "Here's a delicious
                                                │🧠 │         ③     {                        ④                      ⑤      │🧠 │         ⑥   chocolate cake recipe
                                                └───┘               "name": "chocolate cake"                                 └───┘             I found for you..."
                                                   ⬆                 }                                ⬆                       ⬆   
                                            Tool Binding ②                                            │                        |
                                                   │                                                   │                        |   
                                                   │                                                   │         chat_history = [
                                                   │                                                   │                        HumanMessage("Get me a chocolate cake recipe"),
                                                   │                                                   │                        AIMessage(content=[
                                                   │                                                   │                          {"type": "text", "text": "I'll find that recipe"},
                                                   │                                                   │                          {"type": "tool_use", "name": "get_recipe", "id": "toolu_123", "input": {"name": "chocolate cake"}}
                                                   │                                                   │                        ]),
                                                   │                                                   │                        ToolMessage(content='{"title": "Chocolate Cake", "ingredients": [...]}', tool_call_id="toolu_123", name="get_recipe")
                                                   │                                                   │                      ]
                                                   │                                                   │
                                                   │                                                   │
                                            Recipe API Tool                                            │
                                         ┌─────────────┐                                               │
                                         │     🔧      │                                               │
                                         │  get_recipe │ ──────────────────────────────────────────────┘
                                         └─────────────┘
                                               ⬆
                                        Tool Creation  ①
                                               │
                                         ┌─────────────┐
                                         │     🌐      │
                                         │   Recipe    │
                                         │     API     │
                                         └─────────────┘
                                              
```

### Message History Flow

```
Step 1: User Input                    Step 2: LLM Response                    Step 3: Tool Execution
┌─────────────────────┐              ┌─────────────────────┐                 ┌─────────────────────┐
│ HumanMessage        │              │ AIMessage           │                 │ ToolMessage         │
│ "Get chocolate cake │ ────────────▶│ content=[           │ ──────────────▶ │ content=            │
│  recipe"            │              │   {"type": "text",  │                 │ "recipe_data"       │
└─────────────────────┘              │    "text": "I'll    │                 │ tool_call_id=       │
                                     │     find recipe"},  │                 │ "toolu_123"         │
                                     │   {"type":          │                 │ name="get_recipe"   │
                                     │    "tool_use",      │                 └─────────────────────┘
                                     │    "name":          │                           │
                                     │    "get_recipe",    │                           │
                                     │    "id": "toolu_123"│                           │
                                     │    "input": {...}}  │                           │
                                     │ ]                   │                           │
                                     └─────────────────────┘                           │
                                                                                       │
Step 4: Final Response                                                                 │
┌─────────────────────┐                                                                │
│ AIMessage           │ ◀──────────────────────────────────────────────────────────────┘
│ "Here's a delicious │
│ chocolate cake      │
│ recipe I found..."  │
└─────────────────────┘
```

## Required Message Structures

### AIMessage with Tool Call

```
AIMessage(
  content=[
    {
      "type": "text",
      "text": "I'll search for that recipe."
    },
    {
      "type": "tool_use",
      "name": "get_recipe",
      "id": "toolu_123456789",
      "input": {"name": "chocolate cake"}
    }
  ]
)
```

### ToolMessage with Results

```
ToolMessage(
  content="recipe_json_string",
  tool_call_id="toolu_123456789",
  name="get_recipe"
)
```

### Final AIMessage

```
AIMessage(
  content="Here's the chocolate cake recipe..."
)
```

## Implementation Steps

### Step 1: Tool Binding

```python
tools = [get_recipe]
chain = prompt | llm.bind_tools(tools)
```

### Step 2: Initial Invocation

```python
input_data = {"input": message, "chat_history": history[:-1]}
chain_result = llm_chain.invoke(input_data)
```

### Step 3: Response Parsing

```python
for step in chain_result.content:
    if step.get("type") == "text":
        response_text = step["text"]
    elif step.get("type") == "tool_use":
        tool_name = step["name"]
        tool_call_id = step["id"]
        tool_args = json.loads(step.get("partial_json", "{}"))
```

### Step 4: Tool Execution

```python
tool = Tools.tool_registry().get(tool_name)
tool_response = tool.invoke(input=tool_args)
```

### Step 5: History Update

```python
ai_message = AIMessage(content=[...])  # Include tool call
tool_message = ToolMessage(content=tool_response, ...)
chat_history.extend([ai_message, tool_message])
```

### Step 6: Final Response

```python
final_result = llm_chain.invoke({"input": message, "chat_history": chat_history})
final_response, _ = extract_bot_response(final_result)
```

## Critical Requirements

### Message Sequence

```
HumanMessage → AIMessage → ToolMessage → AIMessage
     ↓             ↓           ↓           ↓
User Input    Tool Call   Tool Result  Final Answer
```

### ID Matching

```
AIMessage.content[1]["id"] = "toolu_123"
                ↓
ToolMessage.tool_call_id = "toolu_123"
```

### Content Structure

```
Text Only:     AIMessage(content="string")
With Tools:    AIMessage(content=[{...}, {...}])
Tool Result:   ToolMessage(content="string")
```

## Common Patterns

### Direct Response (No Tools)

```
User → LLM → AIMessage(content="direct response")
```

### Single Tool Use

```
User → LLM → AIMessage(tool_call) → ToolMessage → LLM → AIMessage(final)
```

### Multiple Tools

```
User → LLM → AIMessage(tool_call_1, tool_call_2) → ToolMessage_1, ToolMessage_2 → LLM → AIMessage(final)
```

## Error Handling

### Tool Execution Failure

```
try:
    tool_response = tool.invoke(input=tool_args)
except Exception as e:
    tool_response = f"Error: {str(e)}"
```

### JSON Parsing Error

```
try:
    tool_args = json.loads(step.get("partial_json", "{}"))
except json.JSONDecodeError:
    tool_args = {}
```

### Missing Tool

```
tool = Tools.tool_registry().get(tool_name)
if not tool:
    tool_response = f"Tool {tool_name} not found"
