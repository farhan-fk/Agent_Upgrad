"""
Automatic Function Calling with Google Gen AI SDK

The Google Gen AI SDK simplifies function calling by:
1. Automatically generating schemas from Python functions (using type hints and docstrings)
2. Handling the complete execution loop in ONE generate_content() call
3. No need for manual tool schemas or multi-step workflows

Benefits over manual approach:
- Single LLM call instead of two separate calls
- Automatic schema generation (no JSON schemas needed)
- SDK automatically executes functions and sends results back
"""

# ------------------------------------------------------------
#  SETUP
# ------------------------------------------------------------
from google import genai
from google.genai import types
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()


# ------------------------------------------------------------
#  FIRST CALL — NO TOOLS ENABLED
#  We ask the model for the time, but it has no tool to call.
#  The LLM will answer ON ITS OWN (hallucinated or wrong).
# ------------------------------------------------------------

print("\n================= FIRST CALL (NO TOOLS) =================")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the current time in India?"
)

# Since no tools are available, the model will answer without calling anything.
print("LLM response WITHOUT tools:", response.text)



# ------------------------------------------------------------
#  DEFINE OUR PYTHON TOOL (ACTUAL CODE WE WANT TO CONNECT)
# ------------------------------------------------------------

def get_current_time(timezone: str = "UTC") -> str:
    """Returns the current time in the specified timezone.
    
    Args:
        timezone: The timezone name (e.g., 'Asia/Kolkata' for India, 'America/New_York', 'UTC')
    
    Returns:
        Current time in the specified timezone as a string with timezone info.
    """
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(timezone)
    current_time = datetime.now(tz)
    return current_time.strftime("%I:%M:%S %p %Z")



# ------------------------------------------------------------
#  SINGLE CALL WITH AUTOMATIC FUNCTION CALLING
#  The SDK handles EVERYTHING:
#  1. Detects need for function call
#  2. Executes get_current_time()
#  3. Sends result back to model
#  4. Returns final answer
#  ALL IN ONE generate_content() call!
# ------------------------------------------------------------

print("\n\n================= SINGLE CALL WITH AUTOMATIC TOOL EXECUTION =================")

config = types.GenerateContentConfig(
    tools=[get_current_time]  # Pass the actual Python function
)

response_with_tool = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the current time in India?",
    config=config
)

print("Final LLM Answer:", response_with_tool.text)

# Note: The SDK automatically:
# - Generated the function schema from the docstring and type hints
# - Detected the need to call get_current_time()
# - Executed the function
# - Sent the result back to the model
# - Generated the final response
# All without any manual intervention!
