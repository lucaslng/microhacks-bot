from google import genai
from google.genai import types

from backend.itinerary_functions.temperature_function import get_temperature


def create_itinerary(client: genai.Client, location: str) -> str:

	config = types.GenerateContentConfig(tools=[get_temperature], system_instruction="Create a travel itinerary for a given location. Do not ask for more information. Keep your output under 900 characters. Do not use markup or special characters.",
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