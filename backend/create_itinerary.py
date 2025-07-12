from google import genai
from google.genai import types

from backend.geocoder import get_place_id
from backend.itinerary_functions.temperature_function import get_temperature
# import backend.itinerary_functions.directions_function


def create_itinerary(client: genai.Client, location: str) -> str:

	place_id = get_place_id(location)

	contents = f"{location}\n{place_id}"

	config = types.GenerateContentConfig(tools=[get_temperature], system_instruction="You will be given two lines of input. The first line is the name of a location. The second line is the google maps place_id of that location. Create a travel itinerary for the given location. Do not ask for more information, just create an itinerary. Keep your output under 900 characters. Do not use markup or special characters.",
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