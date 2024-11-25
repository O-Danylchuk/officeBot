import discord
import asyncio
from discord.ext import commands, tasks
from discord.ui import Button, View
from dotenv import load_dotenv
from datetime import datetime, time, timedelta
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("Discord token is not set. Please set it in the .env file.")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

STATUS = False
office_schedule = { "today": {}, "tomorrow": {} }


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    reset_status.start()

@tasks.loop(hours=24)
async def reset_status():
    now = datetime.now()
    reset_time = time(20, 0)
    wait_time = (datetime.combine(now.date(), reset_time) - now).total_seconds()

    if wait_time < 0:  # If the reset time has passed today, wait until tomorrow
        wait_time += 24 * 60 * 60

    await asyncio.sleep(wait_time)
    global STATUS
    STATUS = False
    print("Status reset to False at 8:00 PM.")

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
async def schedule(ctx, person: str, day: str, start_time: str, end_time: str):
    """
    Add or update the office schedule for a person.
    Usage: !schedule <person> <today/tomorrow> <start_time> <end_time>
    Example: !schedule Alice today 09:00 17:00
    """
    if day.lower() not in ["today", "tomorrow"]:
        await ctx.send("❌ Day must be 'today' or 'tomorrow' (this will be expanded in the near future).")
        return

    try:
        start = datetime.strptime(start_time, "%H:%M").time()
        end = datetime.strptime(end_time, "%H:%M").time()
    except ValueError:
        await ctx.send("❌ Time format must be HH:MM (24-hour format).")
        return

    office_schedule[day.lower()][person] = {"start": start, "end": end}
    await ctx.send(f"✅ Schedule set for {person} on {day}: {start_time} to {end_time}")

@bot.command()
async def show_schedule(ctx, day: str):
    """
    Show the office schedule for today or tomorrow.
    Usage: !show_schedule <today/tomorrow>
    Example: !show_schedule today
    """
    if day.lower() not in ["today", "tomorrow"]:
        await ctx.send("❌ Day must be 'today' or 'tomorrow' (this will be expanded in the near future).")
        return

    schedule = office_schedule[day.lower()]
    if not schedule:
        await ctx.send(f"❌ No schedules found for {day}.")
        return

    response = f"📅 **Office Schedule for {day.capitalize()}:**\n"
    for person, times in schedule.items():
        response += f"- {person}: {times['start'].strftime('%H:%M')} to {times['end'].strftime('%H:%M')}\n"

    await ctx.send(response)

@bot.command()
async def clear_schedule(ctx, day: str):
    """
    Clear the schedule for today or tomorrow.
    Usage: !clear_schedule <today/tomorrow>
    """
    if day.lower() not in ["today", "tomorrow"]:
        await ctx.send("❌ Day must be 'today' or 'tomorrow'.")
        return

    office_schedule[day.lower()] = {}
    await ctx.send(f"✅ Cleared all schedules for {day}.")

@bot.command()
async def office(ctx):
    """
    See if there are any people in office right now.
    Usage: !office
    """
    if office_schedule["today"]:
        now = datetime.now().time()
        await ctx.send(f"time for now: {now}")
        for person, times in office_schedule["today"].items():
            if times["start"] <= now <= times["end"]:
                await ctx.send(f"✅ {person} is in the office!")
                return

    await ctx.send("❌ The office is empty!")

@bot.command()
async def help(ctx):
    """
    Show the help message.
    Usage: !help
    """
    response = (
        "**📖 Help Menu**\n\n"
        "Here are the available commands:\n"
        "1. `!officeSet` - Set the office status (People in office or no one).\n"
        "2. `!office` - Check if there are people in the office.\n"
        "3. `!schedule <person> <today/tomorrow> <start_time> <end_time>` - Add or update a person's office schedule.\n"
        "   - Example: `!schedule Alice today 09:00 17:00`\n"
        "4. `!show_schedule <today/tomorrow>` - Show office schedules for today or tomorrow.\n"
        "   - Example: `!show_schedule today`\n"
        "5. `!clear_schedule <today/tomorrow>` - Clear all schedules for today or tomorrow.\n"
        "   - Example: `!clear_schedule tomorrow`\n"
        "6. `!help` - Show this help message.\n\n"
    )
    await ctx.send(response)

bot.run(TOKEN)
