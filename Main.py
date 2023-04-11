import discord
import os
import datetime
import asyncio
from discord.ext import tasks
from discord import Intents
from dotenv import load_dotenv
from pytz import timezone

load_dotenv(dotenv_path="encrypt.env")

intents = Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

# Dictionary to store saved dates, times, and account names along with the channel ID where the reminder was added
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
    print("new_datetime_obj", new_datetime_obj)
    print("new_datetime_str: " + new_datetime_str)

    # Save reminder date, time, account name, and channel ID to dictionary
    if account_name not in saved_reminders:
      saved_reminders[account_name] = [(new_datetime_obj, account_name,
                                        message.author.id)]
    else:
      saved_reminders[account_name].append(
        (new_datetime_obj, message.channel.id, message.author.id))

    for account_name, dates in saved_reminders.items():
      print(account_name, dates)

    # Create embed with confirmation message
    embed = discord.Embed(title="Reminder added",
                          description=f"Account: {account_name}",
                          color=0x00ff00)
    embed.add_field(name="Date and Time", value=new_datetime_str)
    # Send confirmation as embed
    await message.channel.send(embed=embed)

  # Check for other commands and handle them here


@tasks.loop(minutes=1)
async def check_saved_dates():
  now = datetime.datetime.now(timezone('Egypt'))
  for account_name, dates in saved_reminders.items():
    for date in dates:

      date_obj, channel_id, author_id = date
      # channel = client.get_channel(channel_id)

      date_obj = timezone('Egypt').localize(date_obj)

      # print(date_obj , now)
      if now >= date_obj:
        try:

          member = await client.fetch_user(author_id)
          # Create the embed with the reminder information
          embed = discord.Embed(title="Reminder",
                                description=f"Account: {account_name}",
                                color=0x00ff00)
          embed.add_field(name="Date and Time",
                          value=date_obj.strftime('%d %b, %Y %I:%M%p'))

          # Send the reminder as an embed in a DM to the user
          await member.send(embed=embed)
          saved_reminders[account_name].remove(date)
        except:
          print("")
      #   # Get the channel where the message was sent
      #   channel = client.get_channel(channel_id)
      #   print("channel" + channel)

      #   # Get the member who added the reminder
      #   member = await channel.guild.fetch_member(author_id)
      #   print("member: ", member)

      #   if member is not None:
      #     # Create embed with reminder information
      #     embed = discord.Embed(title="Reminder",
      #                           description=f"Account: {account_name}",
      #                           color=0x00ff00)
      #     embed.add_field(name="Date and Time",
      #                     value=date_obj.strftime('%d %b, %Y %I:%M%p'))
      #     # Send reminder as embed
      #     await channel.send(content=member.mention, embed=embed)
      #     print("embed" + embed)
      #   # Remove saved date from dictionary
      # saved_reminders[account_name].remove(date)


client.run(os.getenv("TOKEN"))
