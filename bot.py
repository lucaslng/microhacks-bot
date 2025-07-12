import discord
from discord import app_commands
from dotenv import load_dotenv
from os import getenv
import googlemaps
from google import genai

assert load_dotenv()

guild_id = getenv("GUILD_ID")
assert guild_id
guild = discord.Object(id=guild_id)

discord_token = getenv("DISCORD_TOKEN")
assert discord_token

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

gmaps_key = getenv("GMAPS_KEY")
assert gmaps_key
gmaps = googlemaps.Client(key=gmaps_key)

client = genai.Client()

@tree.command(
    description="Create a travel itinerary with your chosen location!",
    guild=guild,
)
@app_commands.describe(location="Your travel destination!")
async def create(interaction: discord.Interaction, location: str):
  await interaction.response.send_message(f"Creating travel itenary for {location}...")
  await interaction.followup.send("Done!")


@client.event
async def on_ready():
  await tree.sync(guild=guild)
  print("Ready!")


client.run(discord_token)
