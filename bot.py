import discord
from discord import app_commands
from discord.ui import View, Button
from discord import ButtonStyle
from backend.create_itinerary import create_itinerary
from backend.verify_location import verify_location
from google import genai
from util.apikeys import guild_id, discord_token, gemini_key


guild = discord.Object(id=guild_id)

intents = discord.Intents.default()
bot_client = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot_client)

gemini_client = genai.Client(api_key=gemini_key)

events = {}

@tree.command(
    description="Create a travel itinerary with your chosen location!",
    guild=guild,
)
@app_commands.describe(location="Your travel destination!")
async def create(interaction: discord.Interaction, location: str):
  verified_location = verify_location(gemini_client, location)
  if verified_location is None:
    await interaction.response.send_message(f"{location} is not a valid location!")
    print(f"invalid location: {location}")
    return
  await interaction.response.send_message(f"Creating travel itinerary for {verified_location}...")
  print(f"Creating travel itinerary for {verified_location}...")
  itinerary = create_itinerary(gemini_client, verified_location)
  await interaction.followup.send(itinerary)
  print(f"Travel itinerary for {verified_location} completed.")


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
        return await interaction.response.send_message("You have no events.")

    selected = set()
    view = View(timeout=120)

    for idx, ev in enumerate(user_events):
        label_off = f"[ ] {ev['name']} on {ev['date']}"
        label_on  = f"[x] {ev['name']} on {ev['date']}"
        btn = Button(label=label_off, style=ButtonStyle.secondary)

        async def toggle(inter: discord.Interaction, idx=idx, btn=btn):
            if idx in selected:
                selected.remove(idx)
                btn.label = label_off
            else:
                selected.add(idx)
                btn.label = label_on
            await inter.response.edit_message(view=view)

        btn.callback = toggle
        view.add_item(btn)

    submit = Button(label="Submit", style=ButtonStyle.primary)

    async def on_submit(inter: discord.Interaction):
        if not selected:
            await inter.response.send_message("No events selected.", ephemeral=True)
            return
        choices = "\n".join(
            f"- {user_events[i]['name']} on {user_events[i]['date']}" for i in selected
        )
        await inter.response.send_message(f"You selected:\n{choices}", ephemeral=True)

    submit.callback = on_submit
    view.add_item(submit)

    await interaction.response.send_message("Select events via buttons:", view=view)

@bot_client.event
async def on_ready():
  await tree.sync(guild=guild)
  print("Ready!")


bot_client.run(discord_token)
