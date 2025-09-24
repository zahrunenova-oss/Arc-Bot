import discord
from discord.ext import commands
import os
from fastapi import FastAPI
import uvicorn
import asyncio
from discord.ui import Button, View

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# FastAPI for webhook logging
app = FastAPI()

# In-memory store for ledger (replace with Joplin or DB for persistence)
ledger = []

@app.post("/ledger")
async def post_ledger(data: dict):
    ledger.append(data)
    return {"status": "logged"}

# Bot events
@bot.event
async def on_ready():
    print(f'Arc-Bot v1 online as {bot.user}')

@bot.event
async def on_member_join(member):
    # Assign Pilgrim role
    pilgrim_role = discord.utils.get(member.guild.roles, name="Pilgrim")
    if pilgrim_role:
        await member.add_roles(pilgrim_role)
    
    # Send DM with initiation modal
    try:
        await member.send(
            "🌬️ Welcome to The Arkadian Grove\n"
            "The Spiral Codex breathes as One. Reply with:\n"
            "**Name | Intent | Node Location**\n"
            "Example: Nova | To weave the flame | Arcadia-7"
        )
    except discord.Forbidden:
        print(f"Cannot DM {member.name}")

# Listen for DM responses
@bot.event
async def on_message(message):
    if message.author.bot or not isinstance(message.channel, discord.DMChannel):
        await bot.process_commands(message)
        return

    # Parse Name | Intent | Node Location
    parts = message.content.split("|")
    if len(parts) == 3:
        name, intent, node_location = [p.strip() for p in parts]
        
        # Post to #ritual-onboarding
        ritual_channel = discord.utils.get(
            message.author.guild.text_channels, name="ritual-onboarding"
        )
        if ritual_channel:
            await ritual_channel.send(
                f"**New Pilgrim Initiation**\n"
                f"Name: {name}\nIntent: {intent}\nNode: {node_location}"
            )
        
        # Log to ledger via webhook
        async with bot.http_session.post(
            os.getenv("WEBHOOK_URL"), json={
                "name": name, "intent": intent, "node": node_location
            }
        ) as resp:
            if resp.status == 200:
                ledger_channel = discord.utils.get(
                    message.author.guild.text_channels, name="ledger"
                )
                if ledger_channel:
                    await ledger_channel.send(
                        f"**Ledger Receipt**: {name} | {intent} | {node_location}"
                    )

    await bot.process_commands(message)

# Slash command: /apply
@bot.slash_command(name="apply", description="Apply for a role in the Grove")
async def apply(ctx):
    class ApplicationModal(discord.ui.Modal):
        def __init__(self):
            super().__init__(title="Arkadian Initiation")
            self.add_item(discord.ui.InputText(label="Name", placeholder="Your name"))
            self.add_item(discord.ui.InputText(label="Intent", placeholder="Your purpose"))
            self.add_item(discord.ui.InputText(label="Node Location", placeholder="Your node"))

        async def callback(self, interaction: discord.Interaction):
            name = self.children[0].value
            intent = self.children[1].value
            node = self.children[2].value
            ritual_channel = discord.utils.get(
                interaction.guild.text_channels, name="ritual-onboarding"
            )
            if ritual_channel:
                await ritual_channel.send(
                    f"**New Application**\nName: {name}\nIntent: {intent}\nNode: {node}"
                )
            await interaction.response.send_message("Initiation received. The Flame holds.", ephemeral=True)

    await ctx.interaction.response.send_modal(ApplicationModal())

# Button for ritual scheduling
@bot.slash_command(name="ritual", description="Schedule your initiation ritual")
async def ritual(ctx):
    view = View()
    button = Button(label="Book Ritual", url="https://calendly.com/your-link", style=discord.ButtonStyle.link)
    view.add_item(button)
    await ctx.respond("Click to schedule your 15-min initiation ritual:", view=view)

# Run bot and webhook concurrently
async def main():
    async with bot:
        await asyncio.gather(
            bot.start(os.getenv("DISCORD_TOKEN")),
            uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
        )

if __name__ == "__main__":
    asyncio.run(main())
