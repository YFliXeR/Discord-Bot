import discord
import os
import datetime
import asyncio
from discord.ext import tasks
from discord import Intents
from dotenv import load_dotenv

load_dotenv(dotenv_path="encrypt.env")

intents = Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

# Dictionary to store saved dates and times along with account names
saved_reminders = {}


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    # Start background task to check for saved dates that are due
    check_saved_dates.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!add7"):
        # Parse input to get date, time, and account name
        input_str = message.content[7:].strip()  # Remove "!add7 " from beginning
        
        datetime_str, account_name = input_str.rsplit(":", 1)
        datetime_obj = datetime.datetime.strptime(datetime_str.strip(),"%d %b, %Y %I:%M%p")
        print(datetime_obj)
      

        # Calculate date 7 days after input date and time
        new_datetime_obj = datetime_obj + datetime.timedelta(days=7)
        new_datetime_str = new_datetime_obj.strftime("%d %b, %Y %I:%M%p")

        # Save reminder date and account name to dictionary
        if account_name not in saved_reminders:
            saved_reminders[account_name] = [new_datetime_obj]
        else:
            saved_reminders[account_name].append(new_datetime_obj)

        await message.channel.send(f"Saved '{new_datetime_str}:{account_name}'")

    # Check for other commands and handle them here


@tasks.loop(minutes=5)
async def check_saved_dates():
    now = datetime.datetime.now()
    for account_name, dates in saved_reminders.items():
        for date in dates:
            if now >= date:
                # Get the member who added the reminder
                member = await client.fetch_user(int(date.strftime('%s')) % 10000)
                if member is not None:
                    await member.send(
                        f"Reminder: {date.strftime('%d %b, %Y %I:%M%p')} for account '{account_name}' is due!"
                    )
                # Remove saved date from dictionary
                saved_reminders[account_name].remove(date)


client.run(os.getenv("TOKEN"))
