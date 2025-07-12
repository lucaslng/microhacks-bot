from google import genai
from google.genai import types

from backend.itinerary_functions.weather_function import get_temperature


def create_itinerary(client: genai.Client, location: str) -> str:

  tools = types.Tool(function_declarations=[get_temperature])
  config = types.GenerateContentConfig(tools=[tools], system_instruction="Create a travel itinerary for a given location. Keep your output under 900 characters. Do not use markup or special characters.",
                                       thinking_config=types.ThinkingConfig(
    thinking_budget=0)  # Disables thinking
    )

  response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=location,
      config=config
  )

  itinerary = response.text
  assert itinerary
  return itinerary
