from google import genai
from google.genai import types
import json,re
# import backend.itinerary_functions.directions_function


def chat(client: genai.Client, userInput: str, conversation_context: dict | None = None) -> str:
	# Check if user wants to end the chat
	if userInput.lower().strip() in ["i'm satisfied", "im satisfied", "satisfied", "done", "end", "stop"]:
		return "Great! I'm glad I could help with your travel planning. Your chat session has ended. Feel free to create a new itinerary anytime!"

	# Build context-aware prompt
	if conversation_context:
		location = conversation_context.get("location", "")
		days = conversation_context.get("days", 0)
		itinerary = conversation_context.get("itinerary", [])
		
		# Create itinerary summary for context
		itinerary_summary = ""
		for day in itinerary:
			itinerary_summary += f"Day {day['day']} - {day['sublocation']}: "
			activities = list(day['activities'].keys())
			itinerary_summary += ", ".join(activities) + "\n"
		
		contents = f"""You are a helpful travel assistant helping with a trip to {location} for {days} days.

Current itinerary:
{itinerary_summary}

User question: {userInput}

Please provide helpful, specific advice about their trip to {location}. Keep your response under 900 characters and do not use markup or special characters."""
	else:
		contents = userInput

	config = types.GenerateContentConfig(
		system_instruction="Guide the user with their travel specifically. Keep your output under 900 characters. Do not use markup or special characters.",
		thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
	)
     
	# Generate the response
	response = client.models.generate_content(
	    model="gemini-2.5-flash",
	    contents=contents,
	    config=config
	)
	response_text = response.text  # Extract text from GenerateContentResponse
	if response_text is None:
		return "Sorry, I couldn't generate a response. Please try again."
	clean = re.sub(r"^```(?:json)?\s*|```$", "", response_text, flags=re.MULTILINE).strip()

	assert clean
	return clean