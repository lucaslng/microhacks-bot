from google import genai
from google.genai import types


def gemini(client: genai.Client, contents: types.ContentListUnion | types.ContentListUnionDict,):
  return client.models.generate_content(
      model="gemini-2.5-flash",
      contents=contents,
      config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
          thinking_budget=0)  # Disables thinking
          ),
  )
