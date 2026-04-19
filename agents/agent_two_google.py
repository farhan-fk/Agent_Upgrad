"""
Multi-Tool Agent with Google Gen AI Automatic Function Calling

This demonstrates how Google Gen AI SDK handles complex multi-step workflows:
1. Automatically chains multiple function calls
2. Handles dependencies between tools
3. Executes everything in ONE generate_content() call
4. No manual loop needed!

The SDK automatically handles:
- Weather data fetching
- File writing
- QR code generation
All in the correct order based on dependencies.
"""

# ------------------------------------------------------------
#  SETUP
# ------------------------------------------------------------
from google import genai
from google.genai import types
import json
from datetime import datetime
from dotenv import load_dotenv
import requests
import qrcode
from qrcode.image.styledpil import StyledPilImage
import os

load_dotenv()
client = genai.Client()


# ------------------------------------------------------------
#  PYTHON FUNCTIONS WITH TYPE HINTS & DOCSTRINGS
#  (Google SDK auto-generates schemas from these)
# ------------------------------------------------------------

def get_weather_from_ip() -> str:
    """Get the user's current local weather in Celsius using their IP-based location.
    
    Returns:
        Weather information including current temperature, high and low temperatures.
    """
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


def write_txt_file(file_path: str, content: str) -> str:
    """Write text content into a file on disk.
    
    Use this tool whenever you need to save, store, document, or write information into a file.
    
    Args:
        file_path: Path where the file should be saved
        content: Text content to write to the file
    
    Returns:
        Confirmation message with file path.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File saved at {file_path}"


def generate_qr_code(data: str, filename: str, image_path: str) -> str:
    """Generate a QR code PNG image containing the given data with an optional embedded logo.
    
    Args:
        data: The data/URL to encode in the QR code
        filename: Name for the output file (without .png extension)
        image_path: Path to the logo image to embed in the QR code
    
    Returns:
        Confirmation message with filename and data preview.
    """
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
#  USER PROMPT
# ------------------------------------------------------------

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
#  SINGLE CALL WITH AUTOMATIC MULTI-TOOL EXECUTION
#  Google SDK handles the entire workflow automatically!
# ------------------------------------------------------------

print("\n================= AUTOMATIC MULTI-TOOL EXECUTION =================")
print(f"Today's date: {today}\n")

config = types.GenerateContentConfig(
    tools=[get_weather_from_ip, write_txt_file, generate_qr_code],
    system_instruction=f"Use tools as needed. Today's date is: {today}."
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=config
)

print("\n================= FINAL RESULT =================")
print(response.text)

print("\n✅ All tools executed automatically!")
print("📁 Check 'weather_quiz.html' for the quiz")
print("📱 Check 'quiz_qr.png' for the QR code")
