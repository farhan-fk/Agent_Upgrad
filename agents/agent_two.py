# ------------------------------------------------------------
#  SETUP
# ------------------------------------------------------------
from openai import OpenAI
import json
from datetime import datetime
from dotenv import load_dotenv
import requests
import qrcode
from qrcode.image.styledpil import StyledPilImage
import os

load_dotenv()
client = OpenAI()


# ------------------------------------------------------------
#  WEATHER TOOL SCHEMA + PYTHON FUNCTION
# ------------------------------------------------------------

weather_tool = {
    "type": "function",
    "name": "get_weather_from_ip",
    "description": (
        "Get the user's current local weather in Celsius, including the current "
        "temperature and today's high and low, using their IP-based location."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

def get_weather_from_ip():
    """Fetch local weather using IP location."""
    ip_info = requests.get("https://ipinfo.io/json").json()
    lat, lon = ip_info["loc"].split(",")

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "temperature_unit": "celsius",
        "timezone": "auto"
    }

    weather_data = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params=params
    ).json()

    current = weather_data["current"]["temperature_2m"]
    high = weather_data["daily"]["temperature_2m_max"][0]
    low = weather_data["daily"]["temperature_2m_min"][0]

    return f"Current: {current}°C, High: {high}°C, Low: {low}°C"


# ------------------------------------------------------------
#  WRITE FILE TOOL SCHEMA + PYTHON FUNCTION
# ------------------------------------------------------------

write_txt_file_tool = {
    "type": "function",
    "name": "write_txt_file",
    "description": (
        "Write text content into a .txt file on disk. "
        "Use this tool whenever the user asks you to save, store, document, or write information into a file. "
        "You cannot actually create or save files yourself without calling this tool."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["file_path", "content"]
    }
}

def write_txt_file(file_path: str, content: str):
    """Write content to a text file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File saved at {file_path}"


# ------------------------------------------------------------
#  QR CODE TOOL SCHEMA + PYTHON FUNCTION
# ------------------------------------------------------------

qr_code_tool = {
    "type": "function",
    "name": "generate_qr_code",
    "description": (
        "Generate a QR code PNG image containing the given data and optional embedded logo."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "data": {"type": "string"},
            "filename": {"type": "string"},
            "image_path": {"type": "string"}
        },
        "required": ["data", "filename", "image_path"]
    }
}

def generate_qr_code(data: str, filename: str, image_path: str):
    """Create a QR code with an embedded image."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(data)
    img = qr.make_image(
        image_factory=StyledPilImage,
        embedded_image_path=image_path
    )
    output_file = f"{filename}.png"
    img.save(output_file)
    return f"QR code saved as {output_file} (data preview: {data[:40]}...)"


# ------------------------------------------------------------
#  TOOL REGISTRY
# ------------------------------------------------------------

tool_impls = {
    "get_weather_from_ip": get_weather_from_ip,
    "write_txt_file": write_txt_file,
    "generate_qr_code": generate_qr_code,
}


# ------------------------------------------------------------
#  USER PROMPT
# ------------------------------------------------------------

# prompt = (
#     "How is the weather today? Document it and save it in a file with a heading showing today's date."
# )

# prompt = (
#     "1. Check the current weather in my location.\n"
#     "2. Based on the temperature, suggest what clothes I should wear today.\n"
#     "3. Write a creative 4-line poem about the weather.\n"
#     "4. Translate the poem into Hindi.\n"
#     "5. Save EVERYTHING (weather, clothing suggestion, English poem, Hindi poem) in a file called 'daily_report.txt'.\n"
#     "6. Generate a QR code linking to 'https://weather.com' with filename 'weather_link' and 'logo.png' as the embedded image."
# )

prompt = (
    "1. Check the current weather in my location.\n"
    "2. Based on the weather data, create a fun 5-question multiple choice quiz about weather and climate.\n"
    "   - Each question should have 4 options (A, B, C, D)\n"
    "   - Make questions related to today's actual weather (temperature, conditions, etc.)\n"
    "   - Include correct answers at the bottom\n"
    "3. Format the quiz as a beautiful HTML page with:\n"
    "   - A nice title with today's date\n"
    "   - Styled questions and options\n"
    "   - Answers section at the bottom\n"
    "4. Save the HTML quiz to a file called 'weather_quiz.html'.\n"
    "5. Generate a QR code that links to 'file://" + os.getcwd() + "/weather_quiz.html' with filename 'quiz_qr' and use 'logo.png' as embedded image."
)

today = datetime.now().strftime("%Y-%m-%d")


# ------------------------------------------------------------
#  FIRST CALL TO LLM
# ------------------------------------------------------------

print("\n================= FIRST CALL WITH TOOLS =================")

resp = client.responses.create(
    model="gpt-4o-mini",
    input=prompt,
    instructions=f"Use tools if needed. Today's date is: {today}.",
    tools=[weather_tool, write_txt_file_tool, qr_code_tool]
)


# ------------------------------------------------------------
#  PREPARE INPUT LIST WITH USER MESSAGE
# ------------------------------------------------------------

input_list = []

input_list.append({
    "role": "user",
    "content": prompt
})


# ------------------------------------------------------------
#  AGENTIC LOOP - KEEP GOING UNTIL NO MORE TOOL CALLS
# ------------------------------------------------------------

call_number = 1
max_iterations = 10

while call_number <= max_iterations:

    print(f"\n================= PROCESSING CALL #{call_number} =================")

    # ------------------------------------------------------------
    #  CHECK: DOES RESPONSE HAVE TOOL CALLS?
    # ------------------------------------------------------------

    has_tool_calls = False
    for item in resp.output:
        if item.type == "function_call":
            has_tool_calls = True
            break

    # ------------------------------------------------------------
    #  IF NO TOOL CALLS → FINAL ANSWER, EXIT LOOP
    # ------------------------------------------------------------

    if not has_tool_calls:
        print("\nNo tool calls. This is the final answer.")
        print("\n================= FINAL ANSWER =================")
        print(resp.output_text)
        break

    # ------------------------------------------------------------
    #  DEBUG: SHOW TOOL CALLS FROM MODEL
    # ------------------------------------------------------------

    print("\n================= RAW MODEL TOOL CALLS =================")
    for item in resp.output:
        if item.type == "function_call":
            print("TOOL CALLED:", item.name)
            print("CALL ID:", item.call_id)
            print("ARGUMENTS:", item.arguments)

    # ------------------------------------------------------------
    #  COPY TOOL CALLS TO INPUT LIST
    # ------------------------------------------------------------

    for item in resp.output:
        if item.type == "function_call":
            input_list.append({
                "type": "function_call",
                "call_id": item.call_id,
                "name": item.name,
                "arguments": item.arguments
            })

    # ------------------------------------------------------------
    #  EXECUTE TOOLS AND ADD OUTPUTS TO INPUT LIST
    # ------------------------------------------------------------

    for item in resp.output:
        if item.type == "function_call":

            tool_name = item.name
            raw_args = item.arguments
            args = json.loads(raw_args) if raw_args else {}

            python_func = tool_impls[tool_name]

            print(f"\n[PYTHON EXECUTING TOOL] {tool_name}")
            print("Arguments:", args)

            try:
                result = python_func(**args)
            except TypeError:
                result = python_func()

            print("Tool returned:", result)

            input_list.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": result
            })

    # ------------------------------------------------------------
    #  DEBUG: WHAT LLM RECEIVES IN NEXT CALL
    # ------------------------------------------------------------

    print("\n================= INPUT FOR NEXT CALL =================")
    print(json.dumps(input_list, indent=2))

    # ------------------------------------------------------------
    #  NEXT CALL TO LLM
    # ------------------------------------------------------------

    call_number += 1

    print(f"\n================= CALL #{call_number} TO LLM =================")

    resp = client.responses.create(
        model="gpt-4o-mini",
        input=input_list,
        instructions=f"Use tools if needed. Today's date is: {today}.",
        tools=[weather_tool, write_txt_file_tool, qr_code_tool]
    )

    # Loop continues...


# ------------------------------------------------------------
#  SAFETY CHECK
# ------------------------------------------------------------

if call_number > max_iterations:
    print(f"\n[WARNING] Hit max iterations ({max_iterations}). Stopping.")
