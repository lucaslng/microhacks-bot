from google import genai
from google.genai import types


def gemini(client: genai.Client, contents: types.ContentListUnion | types.ContentListUnionDict, system_instruction: types.ContentUnion = None):
	
	extra_instruction = "Do not use markup or special characters."
	
	if system_instruction:
		system_instruction = (extra_instruction, system_instruction)
	else:
		system_instruction = extra_instruction


	return client.models.generate_content(
      model="gemini-2.5-flash",
      contents=contents,
      config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        thinking_config=types.ThinkingConfig(
          thinking_budget=0)  # Disables thinking
          ),
  )