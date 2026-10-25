import os
import discord
from discord import app_commands
import requests

TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = "https://delta-solver-v2.onrender.com/delta"

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    print('------')

@client.tree.command(name="getkey", description="Generate a Delta key from a Platorelay link")
async def getkey(interaction: discord.Interaction, url: str):
    if "auth.platorelay.com" not in url:
        await interaction.response.send_message("❌ That doesn't look like a Platorelay link.", ephemeral=True)
        return

    await interaction.response.send_message("⏳ Solving checkpoints... (Wait up to 30s if server is asleep)", ephemeral=True)

    try:
        response = requests.get(f"{API_URL}?url={url}", timeout=60)
        data = response.json()

        if "error" in data:
            await interaction.edit_original_response(content=f"❌ Error: {data['error']}")
        else:
            await interaction.edit_original_response(content=f"✅ **Key:**\n```\n{data['key']}\n```")
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ Failed: {e}")

client.run(TOKEN)
