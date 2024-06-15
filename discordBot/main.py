import datetime
import os
import traceback

import discord
import django
import parsedatetime
import pytz
from discord import app_commands
from discord.ext import commands, tasks
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "discordBot_django.discordBot_django.django_settings")
django.setup()

application = get_wsgi_application()

from discordBot_django.discordBot_django.models import Reminder
from discordBot_django.discordBot_django import django_settings

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

TOKEN = os.environ.get("BOT_TOKEN", None)
if TOKEN is None:
    print(f"did not detect the BOT_TOKEN")

GUILD_ID = os.environ.get("GUILD_ID", None)
if TOKEN is None:
    print(f"did not detect the GUILD_ID")

MY_GUILD = discord.Object(id=GUILD_ID)


def embed_creator(title: str = None, author: discord.Member = None, embed_description: str = '', footer_text: str = ''):
    embed_obj = discord.Embed(title=title)
    author_name = None
    author_icon_url = None
    if author is not None:
        author_name = author.display_name
        author_icon_url = author.display_avatar.url
    embed_obj.set_author(name=author_name, icon_url=author_icon_url)
    embed_obj.description = embed_description
    if footer_text is None:
        embed_obj.set_footer(text=footer_text)
    return embed_obj


class DiscordBotTutorial(commands.Bot):

    async def setup_hook(self) -> None:
        self.my_background_task.start()
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    @tasks.loop(seconds=2)
    async def my_background_task(self):
        if not self.is_ready():
            return
        reminder_channel = discord.utils.get(self.guilds[0].channels, name='bot_testing')
        try:
            reminders = await Reminder.get_expired_reminders()
            for reminder in reminders:
                channel = discord.utils.get(self.guilds[0].channels, id=int(reminder.original_message_channel_id))
                original_message = await channel.fetch_message(reminder.original_message_id)
                author_id = original_message.author.id
                print(f'[Reminders get_messages()] obtained the message of [{original_message.content}] for '
                      f'author with id [{author_id}]')
                e_obj = embed_creator(
                    author=bot.user,
                    embed_description=f"This is your reminder to {original_message.content}",
                    footer_text='Reminder'
                )
                if e_obj is not False:
                    await reminder_channel.send(f'<@{author_id}>', embed=e_obj)
                    print('[Reminders get_messages()] sent off '
                          f'reminder to {author_id} about \"{original_message.content}\"')
                await Reminder.delete_reminder(reminder)
        except Exception as error:
            print('[Reminders get_messages()] Ignoring exception when generating reminder:')
            traceback.print_exception(error)


bot = DiscordBotTutorial(command_prefix='.', description=description, intents=intents)


@bot.tree.command(name="echo", description="repeats what the user said back at them")
@app_commands.describe(string="string to echo")
async def echo(interaction: discord.Interaction, string: str):
    print(
        f"[HealthChecks echo()] echo command detected from {interaction.user} with argument {string}"
    )
    e_obj = embed_creator(
        author=interaction.user,
        embed_description=string
    )
    if e_obj is not False:
        await interaction.response.send_message(embed=e_obj)


@bot.command()
async def remindmein(ctx, *args):
    print(f"remindmein command detected from user {ctx.message.author}")
    parsed_time = ''
    message = ''
    user_specified_timezone = pytz.timezone(django_settings.TIME_ZONE)
    parse_time = True
    for index, value in enumerate(args):
        if parse_time:
            if value == 'to':
                parse_time = False
            else:
                if value in pytz.all_timezones:
                    user_specified_timezone = pytz.timezone(f"{value}")  # Set timezone if user specifies
                parsed_time += f"{value} "
        else:
            message += f"{value} "
    if parsed_time == '':
        print("[Reminders remindmein()] was unable to extract a time")
        e_obj = embed_creator(
            title='RemindMeIn Error',
            author=ctx.me,
            embed_description="unable to extract a time"
        )
        if e_obj is not False:
            await ctx.send(embed=e_obj, reference=ctx.message)
        return
    if message == '':
        print("[Reminders remindmein()] was unable to extract a message")
        e_obj = embed_creator(
            title='RemindMeIn Error',
            author=ctx.me,
            embed_description="Could not detect any reminder message"
        )
        if e_obj is not False:
            await ctx.send(embed=e_obj, reference=ctx.message)
        return
    print(f"[Reminders remindmein()] extracted time is {parsed_time}")
    print(f"[Reminders remindmein()] extracted timezone is {user_specified_timezone}")
    print(f"[Reminders remindmein()] extracted message is {message}")
    current_time = datetime.datetime.now(tz=user_specified_timezone)
    reminder_date, parse_status = parsedatetime.Calendar().parseDT(
        datetimeString=parsed_time,
        sourceTime=current_time,
        tzinfo=user_specified_timezone
    )

    if parse_status == 0:
        print("[Reminders remindmein()] couldn't parse the time")
        e_obj = embed_creator(
            title='RemindMeIn Error',
            author=ctx.me,
            embed_description="Could not parse time!"
        )
        if e_obj is not False:
            await ctx.send(embed=e_obj, reference=ctx.message)
        return
    reminder_obj = Reminder(
        reminder_date=reminder_date.timestamp(), original_message_channel_id=ctx.message.channel.id,
        original_message_id=ctx.message.id
    )
    await Reminder.save_reminder(reminder_obj)
    e_obj = embed_creator(
        author=ctx.me,
        embed_description=reminder_obj.get_countdown(current_time)
    )
    if e_obj is not False:
        await ctx.send(embed=e_obj, reference=ctx.message)
        print("[Reminders remindmein()] reminder has been constructed and sent.")


bot.run(token=TOKEN)
