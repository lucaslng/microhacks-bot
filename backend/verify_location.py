from backend.gemini import gemini
from google import genai

def verify_location(client: genai.Client, maybeLocation: str) -> str | None:
	locationOrNo = gemini(client, maybeLocation, "You will be given a string that is a possible travel location (there may be typos). Output a no if you are not given a valid city/town/province/state/country/etc. Output the location if it is a proper location and fix any typos, or just repeat the location if it is fine.\nExamples:\n\nInput:\ntoroonto\n\nOutput:\nToronto\n\nInput:\nCow\n\nOutput:\nno\n\nInput:\nDisneyland\n\nOutput:\nno\n\nInput:\nHello\n\nOutput:\nno").text
	match locationOrNo:
		case 'no':
			return None
		case None:
			raise ValueError("Gemini did not verify location properly.")
		case _:
			return locationOrNo