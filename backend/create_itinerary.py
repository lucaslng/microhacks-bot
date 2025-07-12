from backend.gemini import gemini
from google import genai

def create_itinerary(client: genai.Client, location: str) -> str:
	itinerary = gemini(client, location, "Create a travel itinerary for a given location. Keep your output under 900 characters.").text
	assert itinerary
	return itinerary