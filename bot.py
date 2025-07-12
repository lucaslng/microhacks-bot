import discord
from discord import app_commands
from dotenv import load_dotenv
from os import getenv

assert load_dotenv()

guild_id = getenv("GUILD_ID")
assert guild_id

token = getenv("DISCORD_TOKEN")
assert token

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(
    description="Create a travel itinerary with your chosen location!",
    guild=discord.Object(id=guild_id),
)
async def create(interaction):
  await interaction.response.send_message("Creating travel itenary for (location)...")


@client.event
async def on_ready():
  await tree.sync(guild=discord.Object(id=guild_id))
  print("Ready!")


client.run(token)
