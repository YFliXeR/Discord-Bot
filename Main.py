from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
import os
import datetime
from pytz import timezone

load_dotenv(dotenv_path="encrypt.env")

client = commands.Bot(intents=discord.Intents.all(), command_prefix="!")

# Dictionary to store saved dates, times, and account names along with the channel ID where the reminder was added
saved_reminders = {}


@client.event
async def on_ready():
  print("\033[38;2;102;176;239m{0.user}\033[0m Logged in.".format(client))
  check_saved_dates.start()


@client.command(name="sync")
async def _sync(ctx: commands.Context):
  if ctx.author.id in (859233737607086090, 923600698967461898):
    await client.tree.sync()
    await ctx.send("Syncing.")
  else:
    await ctx.send("No.")


@client.tree.command(name="add7", description="adds a reminder")
async def _add7(interaction: discord.Interaction, date_and_time: str,
                account_name: str):
  await interaction.response.defer()
  try:
    datetime_obj = datetime.datetime.strptime(date_and_time.strip(),
                                              "%d %b, %Y %I:%M%p")
  except:
    await interaction.followup.send(
      "Invalid input. Please enter date and time in the format '3 Apr, 2023 10:17pm:account_name'."
    )
    return

  new_datetime_obj = datetime_obj + datetime.timedelta(days=7)
  new_datetime_str = new_datetime_obj.strftime("%d %b, %Y %I:%M%p")

  if account_name not in saved_reminders:
    saved_reminders[account_name] = [(new_datetime_obj, account_name,
                                      interaction.user.id)]
  else:
    saved_reminders[account_name].append(
      (new_datetime_obj, interaction.channel.id, interaction.user.id))

  embed = discord.Embed(
    title="Reminder added",
    description=f"Account: {account_name}",
    color=0x00FF00,
  )
  embed.add_field(name="Date and Time", value=new_datetime_str)
  await interaction.followup.send(embed=embed)


@tasks.loop(minutes=1)
async def check_saved_dates():
  now = datetime.datetime.now(timezone("Egypt"))
  for account_name, dates in saved_reminders.items():
    for date in dates:

      date_obj, channel_id, author_id = date
      date_obj = timezone("Egypt").localize(date_obj)

      if now >= date_obj:
        try:

          member = await client.fetch_user(author_id)
          embed = discord.Embed(
            title="Reminder",
            description=f"Account: {account_name}",
            color=0x00FF00,
          )
          embed.add_field(
            name="Date and Time",
            value=date_obj.strftime("%d %b, %Y %I:%M%p"),
          )

          await member.send(embed=embed)
          saved_reminders[account_name].remove(date)
        except:
          pass


client.run(os.getenv("TOKEN"))
