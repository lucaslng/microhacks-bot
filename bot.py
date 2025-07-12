import discord
from discord import app_commands
from discord.ui import View, Button
from discord import ButtonStyle
from backend.create_itinerary import create_itinerary
from backend.chat import chat
from backend.gemini import gemini
from backend.verify_location import verify_location
from google import genai
from util.apikeys import guild_id, discord_token, gemini_key


guild = discord.Object(id=guild_id)

intents = discord.Intents.default()
bot_client = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot_client)

gemini_client = genai.Client(api_key=gemini_key)

events = {}
# Store conversation state for each user
conversations = {}

@tree.command(
    description="test",
    guild=guild
)
async def test(interaction: discord.Interaction, what: str):
    response = chat(gemini_client, what)
    await interaction.response.send_message(response)

@tree.command(
    description="Chat with me about your travel itinerary!",
    guild=guild
)
@app_commands.describe(message="Ask me anything about your trip!")
async def chat_command(interaction: discord.Interaction, message: str):
    user_id = str(interaction.user.id)
    
    # Check if user has an active conversation
    if user_id not in conversations or not conversations[user_id].get("active", False):
        await interaction.response.send_message(
            "You don't have an active travel planning session. Use `/create` to start planning a trip first!"
        )
        return
    
    # Get conversation context
    conversation_context = conversations[user_id]
    
    # Get response from chat function
    response = chat(gemini_client, message, conversation_context)
    
    # Check if user wants to end the chat
    if message.lower().strip() in ["i'm satisfied", "im satisfied", "satisfied", "done", "end", "stop"]:
        conversations[user_id]["active"] = False
        await interaction.response.send_message(response)
        await interaction.followup.send("Your chat session has ended. Use `/create` to start planning a new trip")
    else:
        await interaction.response.send_message(response)

@tree.command(
    description="Create a travel itinerary with your chosen location!",
    guild=guild,
)
@app_commands.describe(location="Your travel destination!")
@app_commands.describe(days="The length of your vacation!")
async def create(interaction: discord.Interaction, location: str, days: int):
  verified_location = verify_location(gemini_client, location)
  if verified_location is None:
    await interaction.response.send_message(f"{location} is not a valid location!")
    print(f"invalid location: {location}")
    return
  
  # Defer the response since we'll be sending multiple messages
  await interaction.response.defer()
  
  await interaction.followup.send(f"Creating travel itinerary for {verified_location}...")
  print(f"Creating travel itinerary for {verified_location}...")
  itinerary = create_itinerary(gemini_client, verified_location, days)
  for day in itinerary:
    message = f"# Day {day['day']} - {day['sublocation']}\n\n"
    for activity, description in day['activities'].items():
        message += '## ' + activity + '\n' + description + '\n\n'
    await interaction.followup.send(message)

  print(f"Travel itinerary for {verified_location} completed.")
  
  # Start interactive chat session
  user_id = str(interaction.user.id)
  conversations[user_id] = {
    "location": verified_location,
    "days": days,
    "itinerary": itinerary,
    "active": True
  }
  
  await interaction.followup.send(
    f"Your itinerary for {verified_location} is ready"
    f"Use `/chat <your question>` to ask me anything about your trip, "
  ) 


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

        async def toggle(interaction: discord.Interaction, idx=idx, btn=btn):
            if idx in selected:
                selected.remove(idx)
                btn.label = label_off
            else:
                selected.add(idx)
                btn.label = label_on
            await interaction.response.edit_message(view=view)

        btn.callback = toggle
        view.add_item(btn)

    submit = Button(label="Submit", style=ButtonStyle.primary)

    async def on_submit(interaction: discord.Interaction):
        if not selected:
            await interaction.response.send_message("No events selected.", ephemeral=True)
            return
        choices = "\n".join(
            f"- {user_events[i]['name']} on {user_events[i]['date']}" for i in selected
        )
        await interaction.response.send_message(f"You selected:\n{choices}", ephemeral=True)

    submit.callback = on_submit
    view.add_item(submit)

    await interaction.response.send_message("Select events via buttons:", view=view)

@bot_client.event
async def on_ready():
  await tree.sync(guild=guild)
  print("Ready!")


bot_client.run(discord_token)
