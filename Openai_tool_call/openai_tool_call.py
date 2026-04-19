# Lot of time Model alone can not solve the Problems
# We need to give it some tools to help it solve the problems   
# for example : Web search tool to get latest information from the web
# Calculator tool to do mathematical calculations   
# Calendar tool to manage your schedule

# In Order to make use Custom Function calling we need to define the tools Schema 
# This is done using JSON Schema
# Then we need to embed the tool schema in the prompt and define the function calling behaviour
# This is done by setting the function_call parameter to "auto" or "none" or
# We can also use the inbuilt tools provided by OpenAI

# Lesson1 Custom Tools and Function Calling
# First Define The Tool Schema (JSON Schema as suggested by OpenAI)
# https://platform.openai.com/docs/guides/function-calling (Link for explanation of JSON Schema)
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

client = OpenAI()

my_tools = [
    {
        "type": "function",
        "name": "get_horoscope",
        "description": "Get today's horoscope for an astrological sign.",
        "parameters": {
            "type": "object",
            "properties": {
                "sign": {
                    "type": "string",
                    "description": "An astrological sign like Taurus or Aquarius",
                },
            },
            "required": ["sign"],
        },
    },
]

def get_horoscope(sign: str):
    return f"{sign}: You are an idiot?."

# # Running conversation state
input_list = [
    {"role": "user", "content": "What is my horoscope? I am an Aquarius."}
]

# --- Call #1: let model decide to call tool ---
resp1 = client.responses.create(
    model="gpt-4o-mini",
    tools=my_tools,
    input=input_list,
    instructions="Use Tools if you find it necessary.",
)


print("First output after tool call (if any): ", resp1.output_text) # Text output is flattened because the model chose to invoke a tool
print("\nFull raw model output:",resp1)
print("=== RAW MODEL OUTPUT ===")
for item in resp1.output:
    print(item)


# IMPORTANT: append the model's structured output items, not output_text
for item in resp1.output:
    if item.type == "function_call":
        input_list.append({
            "type": "function_call",
            "call_id": item.call_id,
            "name": item.name,
            "arguments": item.arguments
        })

# Run any tool calls and append their outputs with matching call_id
for item in resp1.output:
    if item.type == "function_call" and item.name == "get_horoscope":
        args = json.loads(item.arguments)      # parse JSON string -> dict
        sign = args["sign"]                    # extract the sign string
        result = get_horoscope(sign)

        # Append function_call_output that matches the call_id above
        input_list.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            # You can pass a plain string; JSON-dumping is optional.
            "output": result
        })

# print("Final input just before call #2:")
# print(input_list)

# --- Call #2: produce final answer (disable further tool calls if you want) ---
resp2 = client.responses.create(
    model="gpt-4o-mini",
    instructions="Return ONLY the exact text from the get_horoscope function output. Do not modify, explain, or add anything.",
    tool_choice="none",           # prevents new tool calls on this pass
    input=input_list,             # now includes user, function_call, and function_call_output
)

print("Final output after everything:")
print(resp2.model_dump_json(indent=2))
print("\n" + resp2.output_text)
