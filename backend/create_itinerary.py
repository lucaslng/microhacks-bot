from typing import TypedDict
from google import genai
from google.genai import types
import json

from backend.geocoder import get_place_id
from backend.itinerary_functions.temperature_function import get_temperature
from backend.itinerary_functions.location_functions import get_restauraunts, get_place
# import backend.itinerary_functions.directions_function

class Day(TypedDict):
  day: int
  sublocation: str
  activities: dict[str, str]

def create_itinerary(client: genai.Client, location: str, days: int):

  place_id = get_place_id(location)

  contents = f"{location}\n{place_id}\n{days}"

  # grounding_tool = types.Tool(
  #     google_search=types.GoogleSearch()
  # )

  config = types.GenerateContentConfig(tools=[get_temperature, get_restauraunts, get_place], system_instruction="Create a travel itinerary for {{location}}. Return it strictly and only as JSON in this shape:\n{\n  \"itinerary\": [\n    { \"day\": 1, \"sublocation\": \"Los Angeles\", \"activities\": {\"Explore Hollywood\": \"Short 3-4 sentence description about Hollywood\",\"Santa Monica Pier\": \"Short 3-4 sentence description\",\"Griffith Observatory\": \"Short 3-4 sentence description\"} }\n  ]\n}\n Do not ask for more information. You will be given the name of the location and then the google maps place_id of the location then the number of days on seperate lines.  Use the place_id with the functions to gain more information and find restauraunts along the route. Do not use markup or special characters.",
                                       thinking_config=types.ThinkingConfig(
    thinking_budget=0)  # Disables thinking
    )

  response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=contents,
      config=config
  )
  itinerary_str = response.text
  print(itinerary_str)
  assert itinerary_str
  itinerary: list[Day] = json.loads(itinerary_str)['itinerary']
  return itinerary
