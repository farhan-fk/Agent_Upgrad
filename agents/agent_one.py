

# ------------------------------------------------------------
#  SETUP
# ------------------------------------------------------------
from openai import OpenAI
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


# ------------------------------------------------------------
#  FIRST CALL — NO TOOLS ENABLED
#  We ask the model for the time, but it has no tool to call.
#  The LLM will answer ON ITS OWN (hallucinated or wrong).
# ------------------------------------------------------------

print("\n================= FIRST CALL (NO TOOLS) =================")

resp = client.responses.create(
    model="gpt-4o-mini",
    input="What is the current time in Delhi, India?",
    instructions="Use tools if necessary."
)

# Since no tools are available, the model will answer without calling anything.
print("LLM response WITHOUT tools:", resp.output_text)



# ------------------------------------------------------------
#  DEFINE OUR PYTHON TOOL (ACTUAL CODE WE WANT TO CONNECT)
# ------------------------------------------------------------

def get_current_time():
    """
    Returns the actual current time in HH:MM:SS format.
    The LLM CANNOT execute this — it can only REQUEST it.
    """
    return datetime.now().strftime("%H:%M:%S")

# JSON schema describing the tool to the model
time_tool = {
    "type": "function",
    "name": "get_current_time",
    "description": "Get the current time in HH:MM:SS format",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}



# ------------------------------------------------------------
#  SECOND CALL — TOOLS ENABLED
#  Now the LLM CAN choose to call get_current_time().
#  It will NOT execute Python — it only RETURNS a tool_call.
# ------------------------------------------------------------

print("\n\n================= FIRST CALL WITH TOOL =================")

resp_one = client.responses.create(
    model="gpt-4o-mini",
    input="What is the current time in Delhi, India?",
    instructions="Use tools if you find it necessary.",
    tools=[time_tool]              # <-- Tools available now
)

print("LLM text output:", resp_one.output_text)
print("\nFull raw response (shows function_call):\n", resp_one)

# Show the structured output
print("\nStructured items from model:")
for item in resp_one.output:
    print(item)



# ------------------------------------------------------------
#  PREPARE SECOND CALL
#  We will replay:
#    1. User question
#    2. Model's tool_call
#    3. Our tool result from get_current_time()
# ------------------------------------------------------------

print("\n\n================= PREPARE SECOND CALL =================")

input_list = []

# 0. Add original question so model knows what it's answering
input_list.append({
    "role": "user",
    "content": "What is the current time in Delhi, India?"
})


# 1. Copy the model's tool_call into call #2
for item in resp_one.output:
    if item.type == "function_call":
        input_list.append({
            "type": "function_call",
            "call_id": item.call_id,
            "name": item.name,
            "arguments": item.arguments
        })


# 2. Execute the Python function and append the tool_call_output
for item in resp_one.output:
    if item.type == "function_call" and item.name == "get_current_time":

        # This is where REAL PYTHON executes the tool
        real_result = get_current_time()

        # Tell the LLM: "Here is your tool result"
        input_list.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": real_result
        })


# Optional: show what we are sending back to model
# print("\nWhat the LLM will receive on second call:\n")
# print(json.dumps(input_list, indent=2))



# ------------------------------------------------------------
#  SECOND CALL — LLM RECEIVES TOOL RESULT AND ANSWERS
# ------------------------------------------------------------

print("\n================= SECOND CALL (FINAL ANSWER) =================")

resp_two = client.responses.create(
    model="gpt-4o-mini",
    input=input_list
)

print("\nFinal LLM Answer:", resp_two.output_text)
