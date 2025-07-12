from dotenv import load_dotenv
from util.getenv import getenv

assert load_dotenv()

guild_id = getenv("GUILD_ID")
discord_token = getenv("DISCORD_TOKEN")
gmaps_key = getenv("GMAPS_KEY")
gemini_key = getenv("GEMINI_API_KEY")