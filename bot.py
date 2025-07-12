import discord
from discord import app_commands
from discord.ui import View, Select
from discord import SelectOption
from dotenv import load_dotenv
from backend.create_itinerary import create_itinerary
from backend.verify_location import verify_location
from util.getenv import getenv
import googlemaps
from google import genai

assert load_dotenv()

guild_id = getenv("GUILD_ID")
guild = discord.Object(id=guild_id)
discord_token = getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
bot_client = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot_client)

gmaps_key = getenv("GMAPS_KEY")
gmaps_client = googlemaps.Client(key=gmaps_key)

gemini_key = getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=gemini_key)


events = {}

class EventSelect(Select):
    def __init__(self, user_events):
        options = [
            SelectOption(label=event["name"], description=event["date"], value=str(idx))
            for idx, event in enumerate(user_events)
        ]
        super().__init__(placeholder="Select an event...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        idx = int(self.values[0])
        event = events[str(interaction.user.id)][idx]
        await interaction.response.send_message(
            f"You selected: {event['name']} on {event['date']}", ephemeral=True
        )

class EventView(View):
    def __init__(self, user_events):
        super().__init__(timeout=60)
        self.add_item(EventSelect(user_events))

@tree.command(
    description="Create a travel itinerary with your chosen location!",
    guild=guild,
)
@app_commands.describe(location="Your travel destination!")
async def create(interaction: discord.Interaction, location: str):
  verifiedLocation = verify_location(gemini_client, location)
  if verifiedLocation is None:
    await interaction.response.send_message(f"{location} is not a valid location!")
    print(f"invalid location: {location}")
    return
  await interaction.response.send_message(f"Creating travel itinerary for {verifiedLocation}...")
  print(f"Creating travel itinerary for {verifiedLocation}...")
  itinerary = create_itinerary(gemini_client, verifiedLocation)
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
    
    view = EventView(user_events)
    await interaction.response.send_message("Choose an event from the dropdown:", view=view)

@bot_client.event
async def on_ready():
  await tree.sync(guild=guild)
  print("Ready!")


bot_client.run(discord_token)
