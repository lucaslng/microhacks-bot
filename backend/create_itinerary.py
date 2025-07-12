from google import genai
from google.genai import types
import json

from backend.geocoder import get_place_id
from backend.itinerary_functions.temperature_function import get_temperature
# import backend.itinerary_functions.directions_function


def create_itinerary(client: genai.Client, location: str) -> str:

	place_id = get_place_id(location)

	contents = f"{location}\n{place_id}"

	config = types.GenerateContentConfig(tools=[get_temperature], system_instruction="Create a travel itinerary for {{location}}. Return it strictly as JSON in this shape:\n{\n  \"itinerary\": [\n    { \"day\": \"Day 1–3\", \"location\": \"Los Angeles, CA\", \"activities\": [\"Explore Hollywood\",\"Santa Monica Pier\",\"Griffith Observatory\",\"Universal Studios Hollywood or Disneyland\"] }\n  ]\n}\n Do not ask for more information. Keep your output under 900 characters. Do not use markup or special characters.",
	                                     thinking_config=types.ThinkingConfig(
	  thinking_budget=0)  # Disables thinking
	  )
     
	response = client.models.generate_content(
	    model="gemini-2.5-flash",
	    contents=contents,
	    config=config
	)	
	itinerary = response.text
	
	assert itinerary
	return itinerary