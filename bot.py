import discord
from discord import app_commands
from dotenv import load_dotenv
from util.getenv import getenv
import googlemaps
from google import genai
from backend.gemini import gemini

assert load_dotenv()

# setup discord bot
guild_id = getenv("GUILD_ID")
guild = discord.Object(id=guild_id)
discord_token = getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
bot_client = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot_client)

# setup google maps api client
gmaps_key = getenv("GMAPS_KEY")
gmaps_client = googlemaps.Client(key=gmaps_key)

# setup gemini api client
gemini_key = getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=gemini_key)

@tree.command(
    description="Create a travel itinerary with your chosen location!",
    guild=guild,
)
@app_commands.describe(location="Your travel destination!")
async def create(interaction: discord.Interaction, location: str):
  await interaction.response.send_message(f"Creating travel itenary for {location}...")
  print(f"Creating travel itenary for {location}...")
  locations = gemini(gemini_client, f"Create a travel itenary for {location}").text
  assert locations
  print(locations)
  await interaction.followup.send(locations)
  # await interaction.followup.send("Done!")


@bot_client.event
async def on_ready():
  await tree.sync(guild=guild)
  print("Ready!")


bot_client.run(discord_token)
