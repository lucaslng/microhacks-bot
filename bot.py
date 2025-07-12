import discord
from discord import app_commands
from dotenv import load_dotenv
from backend.verify_location import verify_location
from util.getenv import getenv
import googlemaps
from google import genai

from backend.gemini import gemini

assert load_dotenv()

guild_id = getenv("GUILD_ID")
assert guild_id
guild = discord.Object(id=guild_id)

discord_token = getenv("DISCORD_TOKEN")
assert discord_token

intents = discord.Intents.default()
bot_client = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot_client)

gmaps_key = getenv("GMAPS_KEY")
assert gmaps_key
gmaps_client = googlemaps.Client(key=gmaps_key)

project = getenv("GCP_PROJECT_ID")
assert project, "GCP_PROJECT_ID environment variable not set"
location = getenv("GCP_LOCATION", "us-central1")
gemini_client = genai.Client(vertexai=True, project=project, location=location)

events = {}  

@tree.command(
    description="Create a travel itinerary with your chosen location!",
    guild=guild,
)
@app_commands.describe(location="Your travel destination!")
async def create(interaction: discord.Interaction, location: str):
  verifiedLocation = verify_location(gemini_client, location)
  if verifiedLocation is None:
    await interaction.response.send_message(f"{location} is not a valid location!")
    return
  await interaction.response.send_message(f"Creating travel itinerary for {verifiedLocation}...")
  print(f"Creating travel itinerary for {verifiedLocation}...")
  itinerary = gemini(gemini_client, verifiedLocation, "Create a travel itinerary for a given location. Keep your output under 800 characters.").text
  assert itinerary
  await interaction.followup.send(itinerary)


@tree.command(
    description="Add a new event",
    guild=guild
)
@app_commands.describe(
    name="Event name",
    date="Event date"
)
async def add_event(interaction: discord.Interaction, name: str, date: str):
    user_id, user_name= str(interaction.user.id), str(interaction.user.global_name)

    if str(user_id) not in events:
        events[user_id] = []

    events[user_id].append({"name": name, "date": date})
    await interaction.response.send_message(f"Event '{name}' on {date} added for {user_name}!")

@tree.command (
    description="List all of your events",
    guild=guild
)
async def list_events(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_events = events.get(user_id, [])

    if not user_events:
        await interaction.response.send_message("You have no events.")
        return
    
    embed = discord.Embed(title="Your Events")
    embed.set_author(
        name=interaction.user.global_name,
        icon_url=interaction.user.display_avatar.url
    )

    for event in user_events:
        embed.add_field(
            name=event["name"],
            value=event["date"],
            inline=False
        )
    await interaction.response.send_message(embed=embed)

@bot_client.event
async def on_ready():
  await tree.sync(guild=guild)
  print("Ready!")


bot_client.run(discord_token)
