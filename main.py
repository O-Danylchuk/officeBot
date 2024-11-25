import discord
import asyncio
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
from datetime import datetime, time, 
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("Discord token is not set. Please set it in the .env file.")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

STATUS = False

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def officeSet(ctx):
    global STATUS

    button_yes = Button(style=discord.ButtonStyle.green, label="People in Office")
    button_no = Button(style=discord.ButtonStyle.red, label="No one in Office")

    async def yes_callback(interaction):
        global STATUS
        STATUS = True
        await interaction.response.send_message("✅ There are people in the office!")

    async def no_callback(interaction):
        global STATUS
        STATUS = False
        await interaction.response.send_message("❌ The office is empty!")

    button_yes.callback = yes_callback
    button_no.callback = no_callback

    view = View()
    view.add_item(button_yes)
    view.add_item(button_no)

    await ctx.send("Set office status:", view=view)

@bot.command()
async def office(ctx):
    if STATUS:
        await ctx.send("✅ There are people in the office!")
    else:
        await ctx.send("❌ The office is empty!")

bot.run(TOKEN)
