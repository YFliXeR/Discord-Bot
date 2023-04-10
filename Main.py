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
    input_str = message.content[5:].strip()  # Remove "!add7 " from beginning
    try:
      datetime_str, account_name = input_str.rsplit(":", 1)

      datetime_obj = datetime.datetime.strptime(datetime_str.strip(),
                                                "%d %b, %Y %I:%M%p")
    except:
      await message.channel.send(
        "Invalid input. Please enter date and time in the format '3 Apr, 2023 10:17pm:account_name'."
      )
      return

    # Calculate date 7 days after input date and time
    new_datetime_obj = datetime_obj + datetime.timedelta(days=7)
    new_datetime_str = new_datetime_obj.strftime("%d %b, %Y %I:%M%p")

    # Save reminder date and account name to dictionary
    if account_name not in saved_reminders:
      saved_reminders[account_name] = [(new_datetime_obj, message.channel.id)]
    else:
      saved_reminders[account_name].append(
        (new_datetime_obj, message.channel.id))

    for account_name, dates in saved_reminders.items():
      print(account_name, dates)

    await message.channel.send(f"Saved '{new_datetime_str}:{account_name}'")

  # Check for other commands and handle them here


@tasks.loop(minutes=1)
async def check_saved_dates():
  now = datetime.datetime.now()
  for account_name, dates in saved_reminders.items():
    for date in dates:
      date_obj, channel_id = date
      if now >= date_obj:
        # Get the channel where the message was sent
        channel = client.get_channel(channel_id)

        # Get the member who added the reminder
        member = await channel.guild.fetch_member(int(channel_id))

        if member is not None:
          await channel.send(
            f"{member.mention}, Reminder: {date_obj.strftime('%d %b, %Y %I:%M%p')} for account '{account_name}' is due!"
          )
        # Remove saved date from dictionary
        saved_reminders[account_name].remove(date)


client.run(os.getenv("TOKEN"))
