# 🔧 OpenAI Tool Calling - Cheat Sheet

## 📚 Key Concepts

### 1. **What is Tool Calling?**
- Allows LLM to call external functions
- LLM decides WHEN and WHICH tool to use
- You execute the function and return results
- LLM uses results to generate final response

### 2. **Tool Calling Flow**
```
User Query → LLM Decides Tool → LLM Returns Tool Call
    ↓
Execute Function → Return Results → LLM Generates Answer
```

## 💡 Complete Example

### Step 1: Define Tool
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["city"]
            }
        }
    }
]
```

### Step 2: Call LLM with Tools
```python
response = client.responses.create(
    model="gpt-4o-mini",
    tools=tools,
    input="What's the weather in London?"
)
```

### Step 3: Check if Tool was Called
```python
if response.output.includes_tool_call:
    tool_calls = response.output.tool_calls
    
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Execute function
        if function_name == "get_weather":
            result = get_weather(arguments["city"])
```

### Step 4: Return Results to LLM
```python
response = client.responses.create(
    model="gpt-4o-mini",
    tools=tools,
    input=[
        {"role": "user", "content": "What's the weather?"},
        {"role": "tool_result", "content": result, "tool_call_id": tool_call.id}
    ]
)
```

## 🎯 Tool Definition Best Practices

### 1. **Clear Descriptions**
```python
# ❌ Bad
"description": "Get data"

# ✅ Good
"description": "Get current weather data for a specific city including temperature, conditions, and humidity"
```

### 2. **Detailed Parameters**
```python
"parameters": {
    "type": "object",
    "properties": {
        "city": {
            "type": "string",
            "description": "City name (e.g., 'London', 'New York')"
        },
        "date": {
            "type": "string",
            "description": "Date in YYYY-MM-DD format"
        }
    },
    "required": ["city"]
}
```

### 3. **Use Enums for Choices**
```python
"unit": {
    "type": "string",
    "enum": ["celsius", "fahrenheit"],
    "description": "Temperature unit"
}
```

## 🔑 Common Tool Patterns

### Database Query Tool
```python
{
    "name": "query_orders",
    "description": "Query order database by ID or customer",
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string"},
            "customer_name": {"type": "string"}
        }
    }
}
```

### API Call Tool
```python
{
    "name": "get_stock_price",
    "description": "Get current stock price",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol (e.g., AAPL)"
            }
        },
        "required": ["symbol"]
    }
}
```

### Calculation Tool
```python
{
    "name": "calculate_shipping_cost",
    "description": "Calculate shipping cost based on weight and distance",
    "parameters": {
        "type": "object",
        "properties": {
            "weight_kg": {"type": "number"},
            "distance_km": {"type": "number"}
        },
        "required": ["weight_kg", "distance_km"]
    }
}
```

## 🚨 Common Pitfalls

### 1. **Vague Descriptions**
```python
# ❌ LLM won't know when to use this
"description": "Does something"

# ✅ Clear purpose
"description": "Retrieves customer order history for the last 90 days"
```

### 2. **Missing Required Fields**
```python
# ❌ LLM might call without necessary data
"required": []

# ✅ Specify what's mandatory
"required": ["order_id"]
```

### 3. **Not Handling Multiple Tools**
```python
# ✅ Always loop through tool calls
for tool_call in response.output.tool_calls:
    result = execute_tool(tool_call)
```

## 🎓 Learning Path
1. ✅ Understand tool calling flow
2. ✅ Define simple function
3. ✅ Handle single tool call
4. ✅ Handle multiple tool calls
5. ✅ Create complex tools with validation
6. ✅ Build multi-tool agents

## 🚀 Quick Start Template
```python
from openai import OpenAI
import json

client = OpenAI()

# 1. Define your function
def get_weather(city):
    return f"Weather in {city}: 20°C, Sunny"

# 2. Define tool
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    }
}]

# 3. Call LLM
response = client.responses.create(
    model="gpt-4o-mini",
    tools=tools,
    input="What's the weather in Paris?"
)

# 4. Execute tool if called
if response.output.includes_tool_call:
    for tool_call in response.output.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = get_weather(args["city"])
        print(result)
```

## 📊 Tool Types Comparison

| Type | When to Use | Example |
|------|-------------|---------|
| **Function** | Custom logic | Database queries |
| **Web Search** | Current info | News, trends |
| **Code Interpreter** | Calculations | Data analysis |
| **File Search** | Document Q&A | FAQ, manuals |

## 💡 Pro Tips
- Test tools individually before combining
- Log tool calls for debugging
- Handle errors gracefully
- Use type hints in Python functions
- Keep tool descriptions under 200 chars
- Return structured data (JSON) from tools
