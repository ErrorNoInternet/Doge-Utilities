import os
import io
import sys
import json
import html
import pytz
import time
import math
import redis
import extra
import server
import base64
import string
import psutil
import random
import asyncio
import disnake
import hashlib
import requests
import datetime
import textwrap
import converter
import threading
import variables
import traceback
import simpleeval
import contextlib
import googletrans
from PIL import Image
from typing import List
from dateutil import parser
from disnake.ext import commands
from disnake.ext.commands import Param

user_cooldowns = {}; message_strikes = {}; last_messages = {}
database = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"],
)

class FakeResponse:
    def __init__(self, user):
        self.user = user
        self.sent_message = None

    async def defer(self, ephemeral=None):
        self.sent_message = await self.user.send("I am thinking...")
    
    async def send_message(self, content=None, embed=None, view=None, ephemeral=None):
        self.sent_message = await self.user.send(content=content, embed=embed, view=view)

    async def edit_message(self, content=None, embed=None, view=None):
        await self.sent_message.edit(content=content, embed=embed, view=view)

class FakeInteraction:
    def __init__(self, user):
        self.author = user
        self.guild = None
        if type(user) == disnake.Member:
            self.guild = user.guild
        self.response = FakeResponse(user)

    async def edit_original_message(self, content=None, embed=None, view=None):
        await self.response.edit_message(content=content, embed=embed, view=view)

class MessagePaginator:
    def __init__(self, title, segments, color=0x000000, prefix="", suffix=""):
        self.embeds = []
        self.current_page = 1
        
        for segment in segments:
            self.embeds.append(
                disnake.Embed(
                    title=title,
                    color=color,
                    description=prefix + segment + suffix,
                )
            )

    async def start(self, message):
        class PaginatorView(disnake.ui.View):
            def __init__(this):
                super().__init__()
                this.add_item(
                    disnake.ui.Button(label=f"Page {self.current_page}/{len(self.embeds)}", style=disnake.ButtonStyle.gray, disabled=True)
                )

            @disnake.ui.button(label=variables.first_button_text, style=disnake.ButtonStyle.blurple, disabled=True if len(self.embeds) == 1 else False)
            async def first_button(this, _, interaction):
                if interaction.author != message.author:
                    await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                    return

                self.current_page = 1
                await old_message.edit(embed=self.embeds[self.current_page-1], view=PaginatorView())

            @disnake.ui.button(label=variables.previous_button_text, style=disnake.ButtonStyle.blurple, disabled=True if len(self.embeds) == 1 else False)
            async def previous_button(this, _, interaction):
                if interaction.author != message.author:
                    await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                    return

                self.current_page -= 1
                if self.current_page < 1:
                    self.current_page = len(self.embeds)
                await old_message.edit(embed=self.embeds[self.current_page-1], view=PaginatorView())

            @disnake.ui.button(label=variables.next_button_text, style=disnake.ButtonStyle.blurple, disabled=True if len(self.embeds) == 1 else False)
            async def next_button(this, _, interaction):
                if interaction.author != message.author:
                    await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                    return

                self.current_page += 1
                if self.current_page > len(self.embeds):
                    self.current_page = 1
                await old_message.edit(embed=self.embeds[self.current_page-1], view=PaginatorView())

            @disnake.ui.button(label=variables.last_button_text, style=disnake.ButtonStyle.blurple, disabled=True if len(self.embeds) == 1 else False)
            async def last_button(this, _, interaction):
                if interaction.author != message.author:
                    await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                    return

                self.current_page = len(self.embeds)
                await old_message.edit(embed=self.embeds[self.current_page-1], view=PaginatorView())
        old_message = await message.channel.send(embed=self.embeds[0], view=PaginatorView())

class Paginator:
    def __init__(self, title, segments, color=0x000000, prefix="", suffix="", target_page=1, timeout=180):
        self.embeds = []
        self.current_page = target_page
        self.timeout = timeout

        for segment in segments:
            self.embeds.append(
                disnake.Embed(
                    title=title,
                    color=color,
                    description=prefix + segment + suffix,
                )
            )

        if self.current_page > len(self.embeds) or self.current_page < 1:
            self.current_page = 1

        class PaginatorView(disnake.ui.View):
            def __init__(this, interaction):
                super().__init__()
                
                this.timeout = self.timeout
                this.interaction = interaction
                this.add_item(
                    disnake.ui.Button(label=f"Page {self.current_page}/{len(self.embeds)}", style=disnake.ButtonStyle.gray, disabled=True)
                )

            @disnake.ui.button(label=variables.first_button_text, style=disnake.ButtonStyle.blurple, disabled=True if len(self.embeds) == 1 else False)
            async def first_button(this, _, button_interaction):
                if button_interaction.author != this.interaction.author:
                    await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                    return

                self.current_page = 1
                await this.interaction.edit_original_message(embed=self.embeds[self.current_page-1], view=self.view(this.interaction))

            @disnake.ui.button(label=variables.previous_button_text, style=disnake.ButtonStyle.blurple, disabled=True if len(self.embeds) == 1 else False)
            async def previous_button(this, _, button_interaction):
                if button_interaction.author != this.interaction.author:
                    await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                    return

                self.current_page -= 1
                if self.current_page < 1:
                    self.current_page = len(self.embeds)
                await this.interaction.edit_original_message(embed=self.embeds[self.current_page-1], view=self.view(this.interaction))

            @disnake.ui.button(label=variables.next_button_text, style=disnake.ButtonStyle.blurple, disabled=True if len(self.embeds) == 1 else False)
            async def next_button(this, _, button_interaction):
                if button_interaction.author != this.interaction.author:
                    await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                    return

                self.current_page += 1
                if self.current_page > len(self.embeds):
                    self.current_page = 1
                await this.interaction.edit_original_message(embed=self.embeds[self.current_page-1], view=self.view(this.interaction))

            @disnake.ui.button(label=variables.last_button_text, style=disnake.ButtonStyle.blurple, disabled=True if len(self.embeds) == 1 else False)
            async def last_button(this, _, button_interaction):
                if button_interaction.author != this.interaction.author:
                    await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                    return

                self.current_page = len(self.embeds)
                await this.interaction.edit_original_message(embed=self.embeds[self.current_page-1], view=self.view(this.interaction))
        self.view = PaginatorView

    async def start(self, interaction):
        await interaction.response.send_message(embed=self.embeds[self.current_page-1], view=self.view(interaction))

def reset_strikes():
    global message_strikes
    while True:
        time.sleep(15)
        message_strikes = {}

async def manage_muted_members():
    await asyncio.sleep(10)
    while True:
        try:
            for key in database.keys():
                if key.decode("utf-8").startswith("mute."):
                    database_value = json.loads(database[key])
                    if database_value == []:
                        del database[key]
                    for value in database_value:
                        try:
                            guild_id = int(key.decode("utf-8").split(".")[1])
                            user_id = int(value[0])
                            mute_start = float(value[1])
                            duration = float(value[2])
                        except:
                            moderation_data = json.loads(database[key])
                            moderation_data.remove(value)
                            database[key] = json.dumps(moderation_data)
                            continue
                        if (time.time() / 60) > ((mute_start / 60) + duration):
                            try:
                                mute_role = None; target_guild = None
                                for guild in client.guilds:
                                    if guild.id == guild_id:
                                        target_guild = guild
                                member = await target_guild.fetch_member(user_id)
                                for role in target_guild.roles:
                                    if "mute" in role.name.lower():
                                        mute_role = role
                                if mute_role:
                                    try:
                                        await member.remove_roles(mute_role)
                                    except:
                                        pass
                                    moderation_data = json.loads(database[key])
                                    moderation_data.remove(value)
                                    database[key] = json.dumps(moderation_data)
                            except:
                                moderation_data = json.loads(database[key])
                                moderation_data.remove(value)
                                database[key] = json.dumps(moderation_data)
        except Exception as error:
            print(f"Fatal error in manage_muted_members: {error}")
            try:
                moderation_data = json.loads(database[key])
                moderation_data.remove(value)
                database[key] = json.dunps(moderation_data)
            except:
                pass
        await asyncio.sleep(10)

async def manage_reminders():
    await asyncio.sleep(10)
    while True:
        try:
            for key in database.keys():
                if key.decode("utf-8").startswith("reminders."):
                    database_value = json.loads(database[key])
                    if database_value == []:
                        del database[key]
                    for value in database_value:
                        try:
                            user_id = int(key.decode("utf-8").split(".")[1])
                            start_time = value[0]
                            duration = value[1]
                            text = value[2]
                        except:
                            reminder_data = json.loads(database[key])
                            reminder_data.remove(value)
                            database[key] = json.dumps(reminder_data)
                            continue
                        if time.time() >= (start_time + duration):
                            try:
                                sent = False
                                for guild in client.guilds:
                                    for member in guild.members:
                                        if member.id == user_id:
                                            if not sent:
                                                sent = True
                                                await member.send(f"**Reminder:** {text}")
                                reminder_data = json.loads(database[key])
                                reminder_data.remove(value)
                                database[key] = json.dumps(reminder_data)
                            except:
                                reminder_data = json.loads(database[key])
                                reminder_data.remove(value)
                                database[key] = json.dumps(reminder_data)
        except Exception as error:
            print(f"Fatal error in manage_reminders: {error}")
            try:
                reminder_data = json.loads(database[key])
                reminder_data.remove(value)
                database[key] = json.dumps(reminder_data)
            except:
                pass
        await asyncio.sleep(10)

def manage_blacklist():
    global blacklisted_users
    while True:
        try:
            blacklisted_users = json.loads(database["blacklist"])
        except:
            database["blacklist"] = json.dumps([])
        time.sleep(30)

start_time = time.time()
last_command = time.time()
blacklisted_users = []
snipe_list = {}
math_variables = {}
required_intents = disnake.Intents.default()
required_intents.members = True
client = commands.AutoShardedBot(
    variables.prefix,
    shard_count=variables.shard_count,
    intents=required_intents,
    test_guilds=variables.test_guilds,
)
client.max_messages = 2048
threading.Thread(
    name="manage_muted_members",
    target=asyncio.run_coroutine_threadsafe,
    args=(manage_muted_members(), client.loop, ),
).start()
threading.Thread(
    name="manage_reminders",
    target=asyncio.run_coroutine_threadsafe,
    args=(manage_reminders(), client.loop, ),
).start()
threading.Thread(name="reset_strikes", target=reset_strikes).start()
threading.Thread(name="blacklist_manager", target=manage_blacklist).start()
threading.Thread(name="web_server", target=server.run).start()
help_paginator = Paginator(
    title="Getting Started",
    color=variables.embed_color,
    timeout=None,
    segments=[variables.help_text[i: i + 1000] for i in range(0, len(variables.help_text), 1000)],
)

async def select_status():
    client_status = disnake.Status.online; status_type = random.choice(variables.status_types)
    if status_type == "Playing":
        status_text = random.choice(variables.status1).replace("[users]", str(len(list(client.get_all_members())))).replace("[servers]", str(len(client.guilds)))
        await client.change_presence(status=client_status, activity=disnake.Activity(type=disnake.ActivityType.playing, name=status_text))
    elif status_type == "Watching":
        status_text = random.choice(variables.status2).replace("[users]", str(len(list(client.get_all_members())))).replace("[servers]", str(len(client.guilds)))
        await client.change_presence(status=client_status, activity=disnake.Activity(type=disnake.ActivityType.watching, name=status_text))
    elif status_type == "Listening":
        status_text = random.choice(variables.status3).replace("[users]", str(len(list(client.get_all_members())))).replace("[servers]", str(len(client.guilds)))
        await client.change_presence(status=client_status, activity=disnake.Activity(type=disnake.ActivityType.listening, name=status_text))
    elif status_type == "Competing":
        status_text = random.choice(variables.status4).replace("[users]", str(len(list(client.get_all_members())))).replace("[servers]", str(len(client.guilds)))
        await client.change_presence(status=client_status, activity=disnake.Activity(type=disnake.ActivityType.competing, name=status_text))

def clean(text):
    text = text.replace("@everyone", "everyone")
    text = text.replace("@here", "here")
    return text

def remove_mention(user):
    user = user.replace("<", "")
    user = user.replace("@", "")
    user = user.replace("!", "")
    user = user.replace(">", "")
    return user

def get_cooldown(id, command):
    try:
        cooldown = user_cooldowns[f"{id}.{command}"]
        future_time = cooldown[0] + cooldown[1]
        if future_time - time.time() < 0:
            return 0
        else:
            return future_time - time.time()
    except:
        return 0

def add_cooldown(id, command, cooldown_time):
    user_cooldowns[f"{id}.{command}"] = [time.time(), cooldown_time]

def generate_cooldown(command, cooldown_time):
    cooldown_unit = "seconds"
    if cooldown_time >= 60:
        cooldown_unit = "minutes"
        cooldown_time = cooldown_time / 60
        if cooldown_time >= 60:
            cooldown_unit = "hours"
            cooldown_time = cooldown_time / 60
            if cooldown_time >= 24:
                cooldown_unit = "days"
                cooldown_time = cooldown_time / 24
                if cooldown_time >= 30.4:
                    cooldown_unit = "months"
                    cooldown_time = cooldown_time / 30.4
                    if cooldown_time >= 12:
                        cooldown_unit = "years"
                        cooldown_time = cooldown_time / 12

    cooldown_time = round(cooldown_time, 1)
    if str(cooldown_time).endswith(".0"):
        cooldown_time = round(cooldown_time)
    if cooldown_time == 1:
        cooldown_unit = cooldown_unit[:-1]
    if str(cooldown_time) == "inf":
        cooldown_time = "for an"
        cooldown_unit = "eternity"
    return f"Please wait **{cooldown_time} {cooldown_unit}** before using the `{command}` command again"

@client.before_message_command_invoke
async def message_command_handler(interaction):
    if interaction.author.id in blacklisted_users:
        await interaction.response.send_message("You are banned from using Doge Utilities!", ephemeral=True)
        return

    if not interaction.guild:
        await interaction.response.send_message("Please use Doge Utilities in a server for the best experience!")
        return

@client.before_user_command_invoke
async def user_command_handler(interaction):
    if interaction.author.id in blacklisted_users:
        await interaction.response.send_message("You are banned from using Doge Utilities!", ephemeral=True)
        return

    if not interaction.guild:
        await interaction.response.send_message("Please use Doge Utilities in a server for the best experience!")
        return

@client.before_slash_command_invoke
async def slash_command_handler(interaction):
    if interaction.author.id in blacklisted_users:
        await interaction.response.send_message("You are banned from using Doge Utilities!", ephemeral=True)
        return

    if not interaction.guild:
        await interaction.response.send_message("Please use Doge Utilities in a server for the best experience!")
        return

    if interaction.data.name in variables.owner_commands and interaction.author.id not in variables.bot_owners:
        await interaction.response.send_message("You are not the owner of Doge Utilities!", ephemeral=True)
        return

    if get_cooldown(interaction.author.id, interaction.data.name) > 0:
        cooldown_string = generate_cooldown(interaction.data.name, get_cooldown(interaction.author.id, interaction.data.name))
        embed = disnake.Embed(title="Command Cooldown", description=cooldown_string, color=variables.embed_color)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    variables.last_command = time.time()

@client.slash_command(name="help", description="Get started with Doge Utilities")
async def help_command(interaction):
    await help_paginator.start(interaction)
    add_cooldown(interaction.author.id, "help", 60)

@client.slash_command(name="currency", description="Convert currencies")
async def currency_command(_):
    pass

@currency_command.sub_command(name="convert", description="Convert amounts from one currency to another")
async def currency_convert_command(
        interaction,
        amount: float = Param(description="The amount (for the input currency)"),
        input_currency: str = Param(name="input-currency", description="The input currency"),
        output_currency: str = Param(name="output-currency", description="The output currency"),
    ):
    try:
        input_currency = input_currency.lower().strip()
        output_currency = output_currency.lower().strip()
        url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{input_currency}/{output_currency}.json"
        response = requests.get(url).json(); value = response[output_currency] * amount
        embed = disnake.Embed(title="Currency Conversion", description=f"**{round(amount, 6):,} {input_currency.upper()}** = **{round(value, 6):,} {output_currency.upper()}**", color=variables.embed_color)
        await interaction.response.send_message(embed=embed)
        add_cooldown(interaction.author.id, "currency", 5)
    except:
        await interaction.response.send_message("Unable to convert currency", ephemeral=True)

@currency_command.sub_command(name="list", description="List all the available currencies")
async def currency_list_command(interaction):
    response = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies.json").json()
    output = ""
    for key in response.keys():
        output += f"{key}: {response[key]}\n"
    segments = [output[i: i + 1000] for i in range(0, len(output), 1000)]
    pager = Paginator(
        prefix=f"```\n", suffix="```", color=variables.embed_color, title="Currency List", segments=segments,
    )
    await pager.start(interaction)
    add_cooldown(interaction.author.id, "currency", 5)

@client.slash_command(name="ping", description="Display the bot's current latency")
async def ping_command(interaction):
    embed = disnake.Embed(
        title="Pong :ping_pong:",
        description=f"Latency: **{round(client.latency * 1000, 1)} ms**",
        color=variables.embed_color
    )
    await interaction.response.send_message(embed=embed)

@client.slash_command(name="links", description="Get links for Doge Utilities")
async def links_command(_):
    pass

@links_command.sub_command(name="support", description="Display the official Discord server for Doge")
async def support_command(interaction):
    await interaction.response.send_message(f"Doge Utilities support server: {variables.support_server_invite}")

@links_command.sub_command(name="invite", description="Invite this bot to another server")
async def invite_command(interaction):
    guild_member = True
    if interaction.author == interaction.guild.owner:
        guild_member = False

    class CommandView(disnake.ui.View):
        def __init__(self):
            super().__init__()

            self.clicked = False
            self.add_item(
                disnake.ui.Button(
                    label="Invite Link",
                    url=variables.bot_invite_link,
                )
            )

        @disnake.ui.button(label="Leave Server", style=disnake.ButtonStyle.red, disabled=guild_member)
        async def leave_server(self, _, button_interaction):
            if button_interaction.author == interaction.author:
                if self.clicked:
                    await button_interaction.response.send_message("Leaving server...", ephemeral=True)
                    await button_interaction.guild.leave()
                else:
                    self.clicked = True
                    await button_interaction.response.send_message(
                        "Are you sure you want me to leave this server? Please press the button again to confirm.",
                        ephemeral=True,
                    )
            else:
                await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
    await interaction.response.send_message("Here is Doge Utilities' invite link", view=CommandView())

@links_command.sub_command(name="vote", description="Get links to vote for the bot")
async def vote_command(interaction):
    vote_view = disnake.ui.View()
    vote_view.add_item(disnake.ui.Button(label="top.gg", url="https://top.gg/bot/854965721805226005/vote"))
    vote_view.add_item(disnake.ui.Button(label="discordbotlist", url="https://discordbotlist.com/bots/doge-utilities/upvote"))
    vote_view.add_item(disnake.ui.Button(label="discords", url="https://discords.com/bots/bot/854965721805226005/vote"))
    await interaction.response.send_message("You can vote for me on these sites", view=vote_view)

@links_command.sub_command(name="source", description="Get the link to Doge's source code")
async def source_command(interaction):
    description = "You can find my code [here](https://github.com/ErrorNoInternet/Doge-Utilities)"
    try:
        response = requests.get("https://api.github.com/repos/ErrorNoInternet/Doge-Utilities").json()
        description += f"\nActive Issues: **{response['open_issues']}**, Forks: **{response['forks']}**\nStargazers: **{response['stargazers_count']}**, Watchers: **{response['subscribers_count']}**"
    except:
        pass
    embed = disnake.Embed(title="Source Code", description=description, color=variables.embed_color)
    embed.set_thumbnail(url=client.user.avatar)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "source", 10)

@links_command.sub_command(name="website", description="Get links to the bot's website")
async def website_command(interaction):
    view = disnake.ui.View()
    view.add_item(disnake.ui.Button(label="Website", url=os.environ["WEBSITE_URL"]))
    view.add_item(disnake.ui.Button(label="Dashboard", url=os.environ["WEBSITE_URL"] + "/web/authenticate"))
    await interaction.response.send_message("Here are the links to my website", view=view)

@client.slash_command(name="get", description="Get information about the bot")
async def get_command(_):
    pass

@get_command.sub_command(name="shards", description="Get information about Doge Utilities' shards")
async def shards_command(interaction):
    pages = {}; current_page = 1; page_limit = 20; current_item = 0; index = 1
    for shard in client.shards:
        current_server = ""
        shard_guilds = 0
        shard_members = 0
        for guild in client.guilds:
            if guild.shard_id == shard:
                shard_guilds += 1
                shard_members += guild.member_count
                if guild.id == interaction.guild.id:
                    current_server = "**"
        temporary_text = f"{current_server}Shard `{client.shards[shard].id}` - `{round(client.shards[shard].latency * 1000, 2)} ms` (`{shard_guilds}` guilds, `{shard_members}` members){current_server}\n"
        if index > page_limit:
            index = 0
            current_item += 1
        try:
            pages[current_item] += temporary_text
        except:
            pages[current_item] = f"Shard Count: `{len(client.shards)}`, Current Shard: `{interaction.guild.shard_id}`\n\n"
            pages[current_item] += temporary_text
        index += 1
    pager = Paginator(title="Doge Shards", segments=pages.values(), target_page=current_page, color=variables.embed_color)
    await pager.start(interaction)
    add_cooldown(interaction.author.id, "shards", 3)

@get_command.sub_command(name="status", description="Display the bot's current statistics")
async def status_command(interaction):
    member_count = 0; channel_count = 0; uptime = ""
    for guild in client.guilds:
        member_count += guild.member_count
        channel_count += len(guild.channels)
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1000000
    seconds_time = time.time() - start_time
    minutes_time = seconds_time / 60
    hours_time = minutes_time / 60
    days_time = hours_time / 24
    seconds_time = seconds_time % 60
    minutes_time = minutes_time % 60
    hours_time = hours_time % 24
    if days_time >= 1:
        uptime += str(math.floor(days_time)) + "d "
    if hours_time >= 1:
        uptime += str(math.floor(hours_time)) + "hr "
    if minutes_time >= 1:
        uptime += str(math.floor(minutes_time)) + "m "
    if seconds_time >= 1:
        uptime += str(math.floor(seconds_time)) + "s "
    if uptime == "":
        uptime = "Unknown"
    else:
        uptime = uptime.split(" ")
        uptime = " ".join(uptime[:3])
    
    embed = disnake.Embed(color=variables.embed_color)
    embed.add_field(name="Bot Latency", value="```" + f"{round(client.get_shard(interaction.guild.shard_id).latency * 1000, 1)} ms" + "```")
    embed.add_field(name="CPU Usage", value="```" + f"{psutil.cpu_percent()}%" + "```")
    embed.add_field(name="RAM Usage", value="```" + f"{round(memory_usage, 1)} MB" + "```")
    embed.add_field(name="Thread Count", value="```" + str(threading.active_count()) + "```")
    embed.add_field(name="Joined Guilds", value="```" + str(len(client.guilds)) + "```")
    embed.add_field(name="Active Shards", value="```" + str(client.shards[0].shard_count) + "```")
    embed.add_field(name="Member Count", value="```" + str(member_count) + "```")
    embed.add_field(name="Channel Count", value="```" + str(channel_count) + "```")
    embed.add_field(name="Command Count", value="```" + str(len(client.slash_commands)) + "```")
    embed.add_field(name="Disnake Version", value="```" + disnake.__version__ + "```")
    embed.add_field(name="Bot Version", value="```" + f"{variables.version_number}.{variables.build_number}" + "```")
    embed.add_field(name="Bot Uptime", value="```" + uptime + "```")
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "status", 3)

@get_command.sub_command(name="version", description="Display the bot's current version")
async def version_command(interaction):
    file_size = 0
    for object in os.listdir():
        try:
            file = open(object, "rb")
            file_size += len(file.read()); file.close()
        except:
            pass
    embed = disnake.Embed(title="Bot Version", description=f"Version: **{variables.version_number}**\nBuild: **{variables.build_number}**\nPython: **{sys.version.split(' ')[0]}**\nDisnake: **{disnake.__version__}**\nSize: **{round(file_size / 1000)} KB**", color=variables.embed_color)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "version", 5)

@get_command.sub_command(name="uptime", description="Get Doge Utilities' current uptime")
async def uptime_command(interaction):
    seconds_time = time.time() - start_time
    minutes_time = seconds_time / 60
    hours_time = minutes_time / 60
    days_time = hours_time / 24
    seconds_time = seconds_time % 60
    minutes_time = minutes_time % 60
    hours_time = hours_time % 24
    uptime = ""
    if days_time >= 1:
        uptime += str(math.floor(days_time)) + "d "
    if hours_time >= 1:
        uptime += str(math.floor(hours_time)) + "hr "
    if minutes_time >= 1:
        uptime += str(math.floor(minutes_time)) + "m "
    if seconds_time >= 1:
        uptime += str(math.floor(seconds_time)) + "s "
    if uptime == "":
        uptime = "Unknown"
    embed = disnake.Embed(title="Bot Uptime", description=f"Doge has been running for **{uptime}**", color=variables.embed_color)
    await interaction.response.send_message(embed=embed)

@client.slash_command(name="setup", description="Setup mute and ban roles in your server")
async def setup_command(_):
    pass

@setup_command.sub_command(name="banned", description="Setup a 'Banned' role in your server")
async def setup_banned_command(interaction):
    if interaction.author.guild_permissions.manage_roles or interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(variables.no_permission_text); return

    roles = interaction.guild.roles
    for role in roles:
        if role.name == "Banned":
            await interaction.response.send_message("The **Banned** role already exists in this guild")
            return
    await interaction.response.send_message("Generating the **Banned** role for the current guild...")
    try:
        banned_role = await interaction.guild.create_role(name="Banned")
        guild_roles = len(interaction.guild.roles); retry_count = 0
        while True:
            if retry_count > 100:
                break
            try:
                await banned_role.edit(position=guild_roles - retry_count)
                break
            except:
                retry_count += 1
        for channel in interaction.guild.channels:
            try:
                await channel.set_permissions(banned_role, view_channel=False, connect=False, change_nickname=False, add_reactions=False)
            except:
                pass
    except:
        await interaction.edit_original_message(content=f"Unable to generate the **Banned** role for this guild")
        return
    await interaction.edit_original_message(content=f"Successfully generated the **Banned** role for this guild")
    add_cooldown(interaction.author.id, "setup", 30)

@setup_command.sub_command(name="muted", description="Setup a 'Muted' role in your server")
async def setup_muted_command(interaction):
    if interaction.author.guild_permissions.manage_roles or interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(variables.no_permission_text); return

    roles = interaction.guild.roles
    for role in roles:
        if role.name == "Muted":
            await interaction.response.send_message("The **Muted** role already exists in this guild")
            return
    await interaction.response.send_message("Generating the **Muted** role for the current guild...")
    try:
        muted_role = await interaction.guild.create_role(name="Muted")
        guild_roles = len(interaction.guild.roles); retry_count = 0
        while True:
            if retry_count > 100:
                break
            try:
                await muted_role.edit(position=guild_roles - retry_count)
                break
            except:
                retry_count += 1
        for channel in interaction.guild.channels:
            try:
                if type(channel) == disnake.channel.TextChannel:
                    await channel.set_permissions(muted_role, send_messages=False)
                elif type(channel) == disnake.channel.VoiceChannel:
                    await channel.set_permissions(muted_role, connect=False)
            except:
                pass
    except:
        await interaction.edit_original_message(content=f"Unable to generate the **Muted** role for this guild")
        return
    await interaction.edit_original_message(content=f"Successfully generated the **Muted** role for this guild")
    add_cooldown(interaction.author.id, "setup", 30)

@client.slash_command(name="random", description="Generate a random number between the range")
async def random_command(
        interaction,
        low_number: float = Param(name="low", description="The lower number"),
        high_number: float = Param(0, name="high", description="The higher number"),
    ):
    if low_number != 0 and high_number == 0:
        high_number = low_number
        low_number = 0
    random_number = round(random.uniform(low_number, high_number), 2)
    button_text = "Generate Number"

    class CommandView(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.uses = 0

        @disnake.ui.button(label=button_text, style=disnake.ButtonStyle.gray)
        async def generate_number(self, _, button_interaction):
            if button_interaction.author != interaction.author:
                await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if self.uses < 5:
                self.uses += 1
                random_number = round(random.uniform(low_number, high_number), 2)
                await interaction.edit_original_message(content=f"Your random number is **{random_number}**")
            else:
                new_view = disnake.ui.View()
                new_view.add_item(disnake.ui.Button(label=button_text, style=disnake.ButtonStyle.gray, disabled=True))
                await interaction.edit_original_message(view=new_view)
                await button_interaction.response.send_message("You have generated **5 numbers** already. Please re-run the command to continue.", ephemeral=True)
                self.stop()
    await interaction.response.send_message(f"Your random number is **{random_number}**", view=CommandView())
    add_cooldown(interaction.author.id, "random", 10)

@client.slash_command(name="disconnect-members", description="Disconnect all members from all voice channels")
async def disconnect_members_command(interaction):
    if interaction.author.guild_permissions.administrator or interaction.author.id in variables.permission_override:
        await interaction.response.send_message("Disconnecting all members from voice channels...")
        members = 0; failed = 0

        for channel in interaction.guild.channels:
            if type(channel) == disnake.channel.VoiceChannel:
                for member in channel.members:
                    try:
                        await member.edit(voice_channel=None)
                        members += 1
                    except:
                        failed += 1
        await interaction.edit_original_message(content=f"Successfully disconnected **{members}/{members + failed} {'member' if members == 1 else 'members'}** from voice channels")
        add_cooldown(interaction.author.id, "disconnect-members", 30)
    else:
        await interaction.response.send_message(variables.no_permission_text)

@client.slash_command(name="suggest", description="Send a suggestion to the bot creators")
async def suggest_command(
        interaction,
        suggestion: str = Param(description="The suggestion you want to send"),
    ):
    await interaction.response.send_message("Sending your suggestion...", ephemeral=True)
    class SuggestionView(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.timeout = None

        @disnake.ui.button(label="Accept", style=disnake.ButtonStyle.green)
        async def accept_button(self, _, button_interaction):
            await interaction.author.send(f"The suggestion you sent ({suggestion[:20].strip()}...) has been **accepted** by **{button_interaction.author}**")
            await button_interaction.response.send_message("Accepted successfully")
            self.stop()

        @disnake.ui.button(label="Reject", style=disnake.ButtonStyle.red)
        async def reject_button(self, _, button_interaction):
            await interaction.author.send(f"The suggestion you sent ({suggestion[:20].strip()}...) has been **rejected** by **{button_interaction.author}**")
            await button_interaction.response.send_message("Rejected successfully")
            self.stop()

    for user_id in variables.message_managers:
        sent = False
        for guild in client.guilds:
            for member in guild.members:
                if not sent:
                    if member.id == user_id:
                        sent = True
                        try:
                            await member.send(f"**{interaction.author.name}#{interaction.author.discriminator}** (`{interaction.author.id}`) **has sent a suggestion**\n{suggestion}", view=SuggestionView())
                        except:
                            pass
    await interaction.edit_original_message(content="Your suggestion has been successfully sent")
    add_cooldown(interaction.author.id, "suggest", 300)

@client.slash_command(name="autorole", description="Manage automatically assigned roles")
async def autorole_command(_):
    pass

@autorole_command.sub_command(name="disable", description="Disable autorole in your server")
async def disable_autorole_command(interaction):
    if not interaction.author.guild_permissions.manage_roles and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return

    del database[f"autorole.{interaction.guild.id}"]
    await interaction.response.send_message("Autorole has been **disabled** for this server")

@autorole_command.sub_command(name="list", description="List all the automatically assigned roles")
async def list_autorole_command(interaction):
    if not interaction.author.guild_permissions.manage_roles and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return

    try:
        role_list = json.loads(database[f"autorole.{interaction.guild.id}"])
        role_string = ""
        for role in role_list:
            role_string += "<@&" + role + "> "
        await interaction.response.send_message(embed=disnake.Embed(title="Autorole", description=f"This server's autorole is {role_string}", color=variables.embed_color))
    except:
        await interaction.response.send_message(f"This server does not have autorole configured")

@autorole_command.sub_command(name="set", description="Change the automatically assigned roles")
async def set_autorole_command(
        interaction,
        role1: disnake.Role = Param(description="A role you want to automatically assign"),
        role2: disnake.Role = Param(0, description="A role you want to automatically assign"),
        role3: disnake.Role = Param(0, description="A role you want to automatically assign"),
        role4: disnake.Role = Param(0, description="A role you want to automatically assign"),
        role5: disnake.Role = Param(0, description="A role you want to automatically assign"),
    ):
    if not interaction.author.guild_permissions.manage_roles and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    
    role_list = []
    if role1 != 0:
        role_list.append(str(role1.id))
    if role2 != 0:
        role_list.append(str(role2.id))
    if role3 != 0:
        role_list.append(str(role3.id))
    if role4 != 0:
        role_list.append(str(role4.id))
    if role5 != 0:
        role_list.append(str(role5.id))
    database[f"autorole.{interaction.guild.id}"] = json.dumps(role_list)
    role_string = ""
    for role in role_list:
        role_string += f"<@&{role}> "
    await interaction.response.send_message(
        embed=disnake.Embed(
            title="Autorole",
            description=f"This server's autorole has been set to {role_string}",
            color=variables.embed_color,
        )
    )

@client.slash_command(name="lookup", description="Find a user on Discord")
async def lookup_command(
        interaction,
        user: str = Param(0, description="The ID of the target user")
    ):
    if user == 0:
        user = str(interaction.author.id)
    user = remove_mention(user)
    headers = {"Authorization": "Bot " + os.environ["TOKEN"]}
    url = "https://discord.com/api/users/" + user
    response = requests.get(url, headers=headers).json()
    if "10013" not in str(response):
        try:
            response["public_flags"]
        except:
            await interaction.response.send_message("Please mention a valid user!", ephemeral=True)
            return
        badges = ""
        for flag in variables.public_flags:
            if response['public_flags'] & int(flag) == int(flag):
                if variables.public_flags[flag] != "None":
                    try:
                        badges += variables.badge_list[variables.public_flags[flag]]
                    except:
                        raise Exception(f"unable to find badge: {variables.public_flags[flag]}")
        bot_value = False
        try:
            bot_value = response["bot"]
        except:
            pass
        system_value = False
        try:
            system_value = response["system"]
        except:
            pass
        embed = disnake.Embed(color=int(hex(response['accent_color']), 16) if response['accent_color'] else 0x000000)
        embed.add_field(name="User ID", value=f"`{response['id']}`")
        embed.add_field(name="Tag", value=f"`{response['username']}#{response['discriminator']}`")
        embed.add_field(name="Creation Time", value=f"<t:{parse_snowflake(int(response['id']))}:R>")
        embed.add_field(name="Public Flags", value=f"`{response['public_flags']}` {badges}")
        embed.add_field(name="Bot User", value=f"`{bot_value}`")
        embed.add_field(name="System User", value=f"`{system_value}`")

        if response['avatar'] == None:
            avatar_url = f"https://cdn.discordapp.com/embed/avatars/{int(response['discriminator']) % 5}.png"
        else:
            if response['avatar'].startswith("a_"):
                avatar_url = f"https://cdn.discordapp.com/avatars/{response['id']}/{response['avatar']}.gif?size=512"
            else:
                avatar_url = f"https://cdn.discordapp.com/avatars/{response['id']}/{response['avatar']}.webp?size=512"
        embed.set_thumbnail(url=avatar_url)

        if response['banner'] != None:
            if response['banner'].startswith("a_"):
                banner_url = f"https://cdn.discordapp.com/banners/{response['id']}/{response['banner']}.gif?size=1024"
            else:
                banner_url = f"https://cdn.discordapp.com/banners/{response['id']}/{response['banner']}.webp?size=1024"
            embed.set_image(url=banner_url)
    else:
        embed = disnake.Embed(title="Unknown User", description="Unable to find the specified user", color=variables.embed_color)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "lookup", 5)

@client.user_command(name="Lookup User")
async def user_lookup_command(interaction):
    await lookup_command(interaction, str(interaction.target.id))

@client.slash_command(name="permissions", description="Check the permissions of a specified member")
async def permissions_command(
        interaction,
        member: disnake.Member = Param(0, name="member", description="The member you want to check permissions for"),
    ):
    if member == 0:
        member = interaction.author
    
    permission_list = build_permissions(interaction.author)
    embed = disnake.Embed(title="User Permissions", description=f"Permissions for **{member.name}#{member.discriminator}**\n\n" + permission_list, color=variables.embed_color)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "permissions", 3)

@client.user_command(name="View Permissions")
async def user_permissions_command(interaction):
    permission_list = build_permissions(interaction.target)
    embed = disnake.Embed(title="User Permissions", description=f"Permissions for **{interaction.target.name}#{interaction.target.discriminator}**\n\n" + permission_list, color=variables.embed_color)
    await interaction.response.send_message(embed=embed)

@client.slash_command(name="raid-protection", description="Change the raid protection settings")
async def raid_protection_command(_):
    pass

@raid_protection_command.sub_command(name="status", description="See the current setting for raid protection")
async def raid_protection_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return

    try:
        current_setting = json.loads(database[f"{interaction.guild.id}.raid-protection"])
        if current_setting:
            await interaction.response.send_message("This server's raid protection is turned **on**")
        else:
            await interaction.response.send_message("This server's raid protection is turned **off**")
    except:
        await interaction.response.send_message("This server's raid protection is turned **off**")

@raid_protection_command.sub_command(name="enable", description="Enable raid protection for this server")
async def raid_protection_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return

    database[f"{interaction.guild.id}.raid-protection"] = 1
    await interaction.response.send_message("This server's raid protection has been turned **on**")

@raid_protection_command.sub_command(name="disable", description="Disable raid protection for this server")
async def raid_protection_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return

    database[f"{interaction.guild.id}.raid-protection"] = 0
    await interaction.response.send_message("This server's raid protection has been turned **off**")

@client.slash_command(name="epoch-date", description="Convert unix timestamps to dates")
async def epoch_date_command(
        interaction,
        text: str = Param(name="timestamp", description="The unix timestamp"),
    ):
    try:
        date = epoch_to_date(int(text)); embed = disnake.Embed(color=variables.embed_color)
        embed.add_field(name="Epoch", value="`" + text + "`"); embed.add_field(name="Date", value=date, inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Invalid unix timestamp")
        return
        
@client.slash_command(name="date-epoch", description="Convert dates to unix timestamps")
async def date_epoch_command(
        interaction,
        text: str = Param(name="date", description="The date")
    ):
    try:
        epoch = date_to_epoch(text); embed = disnake.Embed(color=variables.embed_color)
        embed.add_field(name="Date", value=text); embed.add_field(name="Epoch", value="`" + str(epoch) + "`", inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Invalid date")
        return

@client.slash_command(name="hash", description="Hash text using different algorithms")
async def hash_command(
        interaction,
        hash_type: str = Param(name="algorithm", description="The type of the output hash (md5, sha256, etc)"),
        text: str = Param(description="The text you want to hash"),
    ):
    try:
        hash_type = hash_type.strip()
        text = text.strip()
        output_hash = hash_text(hash_type, text)
        embed = disnake.Embed(color=variables.embed_color)
        embed.add_field(name="Text", value=text)
        embed.add_field(name=f"Hash ({hash_type})", value="`" + output_hash + "`", inline=False)
        await interaction.response.send_message(embed=embed)
        add_cooldown(interaction.author.id, "hash", 5)
    except:
        await interaction.response.send_message("Invalid hash type")
        return

@client.slash_command(name="base64", description="Encode and decode base64")
async def base64_command(_):
    pass

@base64_command.sub_command(name="encode", description="Encode text to base64")
async def base64_encode_command(
        interaction,
        text: str = Param(description="The text you want to encode"),
    ):
    try:
        output_code = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        embed = disnake.Embed(color=variables.embed_color)
        embed.add_field(name="Text", value=text); embed.add_field(name="Base64", value="`" + output_code + "`", inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Unable to encode the specified text")
    add_cooldown(interaction.author.id, "base64", 5)

@base64_command.sub_command(name="decode", description="Decode text from base64")
async def base64_decode_command(
        interaction,
        text: str = Param(description="The text you want to decode"),
    ):
    try:
        output_text = base64.b64decode(text.encode("utf-8")).decode("utf-8")
        embed = disnake.Embed(color=variables.embed_color)
        embed.add_field(name="Base64", value="`" + text + "`"); embed.add_field(name="Text", value=output_text, inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Unable to decode the specified text")
    add_cooldown(interaction.author.id, "base64", 5)

@client.slash_command(name="binary", description="Encode and decode binary")
async def binary_command(_):
    pass

@binary_command.sub_command(name="encode", description="Encode text to binary")
async def binary_encode_command(
        interaction,
        text: str = Param(description="The text you want to encode"),
    ):
    try:
        output_code = ' '.join(format(ord(letter), '08b') for letter in text)
        embed = disnake.Embed(color=variables.embed_color)
        embed.add_field(name="Text", value=text)
        embed.add_field(name="Binary", value="`" + output_code + "`", inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Unable to encode the specified text")
        return
    add_cooldown(interaction.author.id, "binary", 5)

@binary_command.sub_command(name="decode", description="Decode text from binary")
async def binary_decode_command(
        interaction,
        text: str = Param(description="The text you want to decode"),
    ):
    try:
        output_text = ""
        for letter in text.split():
            number = int(letter, 2)
            output_text += chr(number)
        embed = disnake.Embed(color=variables.embed_color)
        embed.add_field(name="Binary", value="`" + text + "`")
        embed.add_field(name="Text", value=output_text, inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Unable to decode the specified text")
        return
    add_cooldown(interaction.author.id, "binary", 5)

@client.slash_command(name="calculate", description="Evaluate a math expression")
async def calculate_command(
        interaction,
        expression: str = Param(description="The math expression you want to evaluate")
    ):
    if expression.startswith("`"):
        expression = expression[1:]
    if expression.endswith("`"):
        expression = expression[:-1]
    answer = evaluate_expression(expression); embed = disnake.Embed(color=variables.embed_color)
    embed.add_field(name="Expression", value="`" + expression + "`")
    embed.add_field(name="Result", value="`" + answer + "`", inline=False)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "calculate", 3)

@client.slash_command(name="clear", description="Delete the specified amount of messages")
async def clear_command(
        interaction,
        count: int = Param(description="The amount of messages you want to delete"),
    ):
    if interaction.author.guild_permissions.administrator or interaction.author.id in variables.permission_override:
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.channel.purge(limit=count)
        except:
            await interaction.edit_original_message(content="Unable to clear messages")
            return
        await interaction.edit_original_message(content=f"Successfully deleted **{count} {'message' if count == 1 else 'messages'}**")
    else:
        await interaction.response.send_message(variables.no_permission_text)
    add_cooldown(interaction.author.id, "clear", 10)

@client.slash_command(name="text", description="Change what text looks like")
async def text_command(_):
    pass

@text_command.sub_command(name="wide", description="Make text appear to be wider")
async def wide_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):

    new_text = ""
    for letter in text:
        new_text += letter + " "
    await interaction.response.send_message(clean(new_text))
    add_cooldown(interaction.author.id, "wide", 3)

@text_command.sub_command(name="unwide", description="Un-wide the specified text")
async def unwide_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):

    new_text = ""
    space_character = False
    for letter in text.replace("   ", "  "):
        if letter == " ":
            if space_character:
                new_text += " "
            space_character = True
        else:
            space_character = False
            new_text += letter
    await interaction.response.send_message(clean(new_text))
    add_cooldown(interaction.author.id, "unwide", 3)

@text_command.sub_command(name="spoiler", description="Add spoilers to every single character")
async def spoiler_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    new_text = ""
    for letter in text:
        new_text += "||" + letter + "||"
    await interaction.response.send_message(clean(new_text))
    add_cooldown(interaction.author.id, "spoiler", 3)

@text_command.sub_command(name="cringe", description="Make the text look CrInGY")
async def cringe_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    new_text = ""
    for letter in text:
        case = random.randint(1, 2)
        if case == 1:
            if letter.upper() == letter:
                new_text += letter.lower()
            else:
                new_text += letter.upper()
        else:
            if letter.upper() == letter:
                new_text += letter.upper()
            else:
                new_text += letter.lower()
    await interaction.response.send_message(clean(new_text))
    add_cooldown(interaction.author.id, "cringe", 3)

@text_command.sub_command(name="reverse", description="Reverse the specified text")
async def reverse_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    new_text = text[::-1]
    await interaction.response.send_message(clean(new_text))
    add_cooldown(interaction.author.id, "reverse", 3)

@text_command.sub_command(name="corrupt", description="Make the text appear to be corrupted")
async def corrupt_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    new_text = ""
    for letter in text:
        switch = random.randint(0, 100)
        if switch > 95:
            new_text += text[random.randint(0, len(text) - 1)]
        else:
            number = random.randint(0, 100)
            if number > 80:
                new_text += random.choice(["0", "1"])
            else:
                new_text += letter
                punctuation = random.choice([True, False, False, False, False])
                if punctuation:
                    new_text += string.punctuation[random.randint(0, len(string.punctuation) - 1)]
    await interaction.response.send_message(clean(new_text))
    add_cooldown(interaction.author.id, "corrupt", 3)

@client.slash_command(name="color", description="Visualize a color code")
async def color_command(
        interaction,
        color_code: str = Param(name="color", description="The color code you want to visualize"),
    ):
    colors = generate_color(color_code)
    if colors == 1:
        await interaction.response.send_message("Invalid color code")
        return
    else:
        hex_color = colors[0]; rgb_color = colors[1]
        embed = disnake.Embed(color=int("0x" + hex_color[1:], 16))
        embed.set_image(url="attachment://color.png")
        embed.add_field(name="Hex", value=hex_color)
        embed.add_field(name="RGB", value=str(rgb_color), inline=True)
    await interaction.response.send_message(embed=embed, file=disnake.File("images/color.png"))
    add_cooldown(interaction.author.id, "color", 3)

@client.slash_command(name="time", description="Get the time information about a specific region")
async def time_command(
        interaction,
        region: str = Param(description="The target region")
    ):
    region = region.strip()
    try:
        if region.lower() == "list" or region.lower() == "help":
            output = ""
            for timezone in pytz.all_timezones:
                output += timezone + "\n"
            segments = [output[i: i + 1000] for i in range(0, len(output), 1000)]
            pager = Paginator(
                color=variables.embed_color,
                prefix="```\n", suffix="```",
                title=f"Timezone List", segments=segments,
            )
            await pager.start(interaction)
        elif region.lower() == "epoch" or region.lower() == "unix":
            embed = disnake.Embed(title="Time", description=f"Current epoch time: **{round(time.time())}**", color=variables.embed_color)
            await interaction.response.send_message(embed=embed)
        else:
            user_timezone = pytz.timezone(region.replace(" ", "_"))
            now = datetime.datetime.now(user_timezone)
            embed = disnake.Embed(title="Time", description=f"Information for **{region.replace(' ', '_')}**\n\nTime: **{str(now.time()).split('.')[0]}**\nDate: **{now.date()}**\nWeekday: **{variables.weekdays[now.weekday() + 1]}**", color=variables.embed_color)
            await interaction.response.send_message(embed=embed)
    except KeyError:
        for timezone in pytz.all_timezones:
            try:
                city = timezone.split("/")[1]
                if region.replace(" ", "_").lower() == city.lower():
                    user_timezone = pytz.timezone(timezone); now = datetime.datetime.now(user_timezone)
                    embed = disnake.Embed(title="Time", description=f"Information for **{timezone}**\n\nTime: **{str(now.time()).split('.')[0]}**\nDate: **{now.date()}**\nWeekday: **{variables.weekdays[now.weekday() + 1]}**", color=variables.embed_color)
                    await interaction.response.send_message(embed=embed); return
            except:
                pass
        embed = disnake.Embed(title="Time", description=f"That timezone was not found", color=variables.embed_color)
        await interaction.response.send_message(embed=embed); return
    add_cooldown(interaction.author.id, "time", 3)

@client.slash_command(name="nickname", description="Change a member's nickname")
async def nickname_command(
        interaction,
        nickname: str = Param(description="The new nickname"),
        member: disnake.Member = Param(0, description="The target member"),
    ):
    if member != 0:
        if not interaction.author.guild_permissions.manage_nicknames and interaction.author.id not in variables.permission_override:
            await interaction.response.send_message(variables.no_permission_text)
            return
    else:
        member = interaction.author

    try:        
        await member.edit(nick=nickname)
        await interaction.response.send_message(f"Successfully updated **{member.name}#{member.discriminator}**'s nickname to **{nickname}**")
        add_cooldown(interaction.author.id, "nickname", 5)
    except:
        await interaction.response.send_message(f"Unable to change **{member.name}#{member.discriminator}**'s nickname"); return

@client.slash_command(name="stackoverflow", description="Look for something on StackOverflow")
async def stackoverflow_command(
        interaction,
        text: str = Param(description="The search query"),
    ):
    await interaction.response.defer()
    try:
        stackoverflow_parameters = {
            "order": "desc",
            "sort": "activity",
            "site": "stackoverflow"
        }
        stackoverflow_parameters["q"] = text
        parameters = stackoverflow_parameters
        response = requests.get(url="https://api.stackexchange.com/2.2/search/advanced", params=parameters).json()
        if not response["items"]:
            embed = disnake.Embed(title="StackOverflow", description=f"No search results found for **{text}**", color=disnake.Color.red())
            await interaction.edit_original_message(embed=embed); return
        final_results = response["items"][:5]
        embed = disnake.Embed(title="StackOverflow", description=f"Here are the top **{len(final_results)}** results for **{text}**", color=variables.embed_color)
        for result in final_results:
            tags = ""
            for tag in result['tags'][:4]:
                tags += f"`{tag}`, "
            embed.add_field(
                name = html.unescape(result["title"]),
                value = (
                    f"Views: `{result['view_count']}`, "
                    f"Score: `{result['score']}`, "
                    f"Answers: `{result['answer_count']}` "
                    f"([link to post]({result['link']}))\n"
                    f"Tags: {tags[:-2]}"
                ),
                inline = False
            )
        await interaction.edit_original_message(embed=embed)
    except disnake.HTTPException:
        await interaction.edit_original_message(content="The search result is too long!"); return
    except:
        await interaction.edit_original_message(content="Unable to search for item"); return
    add_cooldown(interaction.author.id, "stackoverflow", 10)

@client.slash_command(name="blacklist", description="Owner Command")
async def blacklist_command(_):
    pass

@blacklist_command.sub_command(name="list", description="Owner Command")
async def blacklist_list_command(interaction):
    blacklisted_users = []
    raw_array = json.loads(database["blacklist"])
    for user in raw_array:
        blacklisted_users.append(f"{user} (<@{user}>)")
    embed = disnake.Embed(title="Blacklisted Users", description="\n".join(blacklisted_users) if "\n".join(blacklisted_users) != "" else "There are no blacklisted users", color=variables.embed_color)
    await interaction.response.send_message(embed=embed)

@blacklist_command.sub_command(name="add", description="Owner Command")    
async def blacklist_add_command(
        interaction,
        user: str = Param(description="Owner Command"),
    ):
    try:
        user_id = int(remove_mention(user))
    except:
        await interaction.response.send_message("Please mention a valid user!", ephemeral=True)
        return
    current_users = json.loads(database["blacklist"])
    current_users.append(user_id)
    database["blacklist"] = json.dumps(current_users)
    await interaction.response.send_message("Successfully added user to blacklist")

@blacklist_command.sub_command(name="remove", description="Owner Command")
async def blacklist_remove_command(
        interaction,
        user: str = Param(description="Owner Command"),
    ):
    try:
        user_id = int(remove_mention(user))
    except:
        await interaction.response.send_message("Please mention a valid user!", ephemeral=True)
        return
    current_users = json.loads(database["blacklist"])
    try:
        current_users.remove(user_id)
    except:
        pass
    database["blacklist"] = json.dumps(current_users)
    await interaction.response.send_message("Successfully removed user from blacklist")

@client.slash_command(name="game", description="Start a fun game")
async def game_command(_):
    pass

@game_command.sub_command(name="tictactoe", description="Start a TicTacToe game")
async def tictactoe_command(interaction):
    class TicTacToeButton(disnake.ui.Button['TicTacToe']):
        def __init__(self, x: int, y: int):
            super().__init__(style=disnake.ButtonStyle.secondary, label='\u200b', row=y)
            self.x = x
            self.y = y

        async def callback(self, button_interaction: disnake.MessageInteraction):
            assert self.view is not None
            view: TicTacToe = self.view
            state = view.board[self.y][self.x]
            if state in (view.X, view.O):
                return

            if button_interaction.author.id not in players:
                await button_interaction.response.send_message("You are not a part of that TicTacToe game!")
                return

            if view.current_player == view.X:
                if button_interaction.author.id != players[0]:
                    await button_interaction.response.send_message("It is not your turn!", ephemeral=True)
                    return

                self.style = disnake.ButtonStyle.danger
                self.label = 'X'
                self.disabled = True
                view.board[self.y][self.x] = view.X
                view.current_player = view.O
                content = f"It is now <@{players[1]}>'s (O) turn"
            else:
                if button_interaction.author.id != players[1]:
                    await button_interaction.response.send_message("It is not your turn!", ephemeral=True)
                    return

                self.style = disnake.ButtonStyle.success
                self.label = 'O'
                self.disabled = True
                view.board[self.y][self.x] = view.O
                view.current_player = view.X
                content = f"It is now <@{players[0]}>'s (X) turn"

            winner = view.check_board_winner()
            if winner is not None:
                if winner == view.X:
                    content = f'X (<@{players[0]}>) won!'
                elif winner == view.O:
                    content = f'O (<@{players[1]}>) won!'
                else:
                    content = "It's a tie!"

                for child in view.children:
                    child.disabled = True
                view.stop()
            await button_interaction.response.edit_message(content=content, view=view)

    class TicTacToe(disnake.ui.View):
        children: List[TicTacToeButton]
        X = -1
        O = 1
        Tie = 2

        def __init__(self):
            super().__init__()
            self.current_player = self.X
            self.board = [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]

            for x in range(3):
                for y in range(3):
                    self.add_item(TicTacToeButton(x, y))

        def check_board_winner(self):
            for across in self.board:
                value = sum(across)
                if value == 3:
                    return self.O
                elif value == -3:
                    return self.X

            for line in range(3):
                value = self.board[0][line] + self.board[1][line] + self.board[2][line]
                if value == 3:
                    return self.O
                elif value == -3:
                    return self.X

            diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
            if diag == 3:
                return self.O
            elif diag == -3:
                return self.X

            diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
            if diag == 3:
                return self.O
            elif diag == -3:
                return self.X

            if all(i != 0 for row in self.board for i in row):
                return self.Tie
            return None

    players = []
    class GameChecker(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.timeout = 300

        @disnake.ui.button(label="Player 1", style=disnake.ButtonStyle.blurple)
        async def player_one(self, button, button_interaction):
            if button_interaction.author.id not in players:
                players.append(button_interaction.author.id)
                await button_interaction.response.send_message("Successfully joined the game!", ephemeral=True)
            else:
                await button_interaction.response.send_message("You have already joined the game!", ephemeral=True)
                return
            if len(players) == 2:
                await interaction.edit_original_message(content=f"It's your turn, <@{players[0]}>!", view=TicTacToe())
                self.stop()
                return
            
            button.label = button_interaction.author.name
            button.disabled = True
            await interaction.edit_original_message(view=self)

        @disnake.ui.button(label="Player 2", style=disnake.ButtonStyle.blurple)
        async def player_two(self, button, button_interaction):
            if button_interaction.author.id not in players:
                players.append(button_interaction.author.id)
                await button_interaction.response.send_message("Successfully joined the game!", ephemeral=True)
            else:
                await button_interaction.response.send_message("You have already joined the game!", ephemeral=True)
                return
            if len(players) == 2:
                await interaction.edit_original_message(content=f"It's your turn, <@{players[0]}>!", view=TicTacToe())
                self.stop()
                return

            button.label = button_interaction.author.name
            button.disabled = True
            await interaction.edit_original_message(view=self)

    await interaction.response.send_message("Click to join the TicTacToe game", view=GameChecker())
    add_cooldown(interaction.author.id, "game", 3)

@game_command.sub_command(name="trivia", description="Start a trivia game")
async def trivia_command(interaction):
    await interaction.response.defer()
    url = f"https://opentdb.com/api.php?amount=1&type=multiple&category={random.randint(9, 33)}&difficulty={random.choice(['easy', 'medium', 'hard'])}"
    response = requests.get(url).json()
    description = f"**{html.unescape(response['results'][0]['question'])}**\nCategory: `{response['results'][0]['category']}` (**{response['results'][0]['difficulty']}** difficulty)"
    answers = response['results'][0]['incorrect_answers']
    answers.append(response['results'][0]['correct_answer'])
    correct_answer = html.unescape(response['results'][0]['correct_answer'])

    class CommandView(disnake.ui.View):
        def __init__(self):
            super().__init__()

        async def close(self, chosen_answer):
            new_view = disnake.ui.View()
            original_message = await interaction.original_message()
            for button in original_message.components[0].children:
                style = disnake.ButtonStyle.red
                if chosen_answer == button.label:
                    style = disnake.ButtonStyle.gray
                if correct_answer == button.label:
                    style = disnake.ButtonStyle.green
                new_view.add_item(disnake.ui.Button(label=button.label, style=style, disabled=True))
            await interaction.edit_original_message(view=new_view)
            self.stop()
        
        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_1(self, button, button_interaction):
            if button_interaction.author != button_interaction.author:
                await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if button.label == correct_answer:
                await button_interaction.response.send_message("Correct answer!", ephemeral=True)
            else:
                await button_interaction.response.send_message(f"Wrong answer... The correct answer was **{correct_answer}**.", ephemeral=True)
            await self.close(button.label)

        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_2(self, button, button_interaction):
            if button_interaction.author != button_interaction.author:
                await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if button.label == correct_answer:
                await button_interaction.response.send_message("Correct answer!", ephemeral=True)
            else:
                await button_interaction.response.send_message(f"Wrong answer... The correct answer was **{correct_answer}**.", ephemeral=True)
            await self.close(button.label)

        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_3(self, button, button_interaction):
            if button_interaction.author != button_interaction.author:
                await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if button.label == correct_answer:
                await button_interaction.response.send_message("Correct answer!", ephemeral=True)
            else:
                await button_interaction.response.send_message(f"Wrong answer... The correct answer was **{correct_answer}**.", ephemeral=True)
            await self.close(button.label)

        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_4(self, button, button_interaction):
            if button_interaction.author != button_interaction.author:
                await button_interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if button.label == correct_answer:
                await button_interaction.response.send_message("Correct answer!", ephemeral=True)
            else:
                await button_interaction.response.send_message(f"Wrong answer... The correct answer was **{correct_answer}**.", ephemeral=True)
            await self.close(button.label)

    embed = disnake.Embed(
        description=description,
        color=variables.embed_color,
    )
    await interaction.edit_original_message(embed=embed, view=CommandView())
    add_cooldown(interaction.author.id, "game", 3)

@client.slash_command(name="fetch", description="Fetch something fun")
async def fetch_command(_):
    pass

@fetch_command.sub_command(name="meme", description="Fetch a random meme from Reddit")
async def meme_command(interaction):
    await interaction.response.defer()
    response = requests.get("https://meme-api.herokuapp.com/gimme").json()
    description = f"Posted by **{response['author']}** in **{response['subreddit']}** (**{response['ups']}** upvotes)"
    embed = disnake.Embed(title=response["title"], url=response["postLink"], description=description, color=variables.embed_color)
    embed.set_image(url=response["url"])
    await interaction.edit_original_message(embed=embed)
    add_cooldown(interaction.author.id, "fetch", 3)

@fetch_command.sub_command(name="joke", description="Fetch a random joke")
async def joke_command(interaction):
    await interaction.response.defer()
    response = requests.get("http://random-joke-api.herokuapp.com/random").json()
    embed = disnake.Embed(description=f"Here's a `{response['type']}` joke:\n{response['setup']} **{response['punchline']}**", color=variables.embed_color)
    await interaction.edit_original_message(embed=embed)
    add_cooldown(interaction.author.id, "fetch", 3)

@fetch_command.sub_command(name="quote", description="Fetch an inspirational quote")
async def quote_command(interaction):
    await interaction.response.defer()
    try:
        response = json.loads(requests.get("https://zenquotes.io/api/random").content)[0]
        await interaction.edit_original_message(content=f'"{response["q"]}"\n\n\t\t\t\t**- {response["a"]}**')
        add_cooldown(interaction.author.id, "fetch", 3)
    except:
        await interaction.edit_original_message(content="Unable to fetch quote")

@client.slash_command(name="unmute", description="Unmute the specified member")
async def unmute_command(
        interaction,
        member: disnake.Member = Param(description="The member you want to unmute"),
    ):
    if interaction.author.guild_permissions.manage_roles or interaction.author.guild_permissions.administrator or interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(variables.no_permission_text); return

    mute_role = None; exists = False
    for role in interaction.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if exists:
        try:
            await member.remove_roles(mute_role)
        except:
            await interaction.response.send_message(f"Unable to unmute **{member}**")
            return
    await interaction.response.send_message(f"Successfully unmuted **{member}**")

@client.slash_command(name="mute", description="Mute a specified member on your server")
async def mute_command(
        interaction,
        member: disnake.Member = Param(description="The member you want to mute"),
        duration: float = Param(0, name="minutes", description="The target duration"),
    ):
    if interaction.author.guild_permissions.manage_roles or interaction.author.guild_permissions.administrator or interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(variables.no_permission_text)
        return

    mute_role = None; exists = False
    for role in interaction.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if not exists:
        await setup_muted_command(interaction)
    mute_role = None; exists = False
    for role in interaction.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if not exists:
        await interaction.response.send_message("Unable to find mute role")
        return

    if duration == 0:
        try:
            await member.add_roles(mute_role)
        except:
            await interaction.response.send_message(f"Unable to mute **{member}**"); return
        await interaction.response.send_message(f"Successfully muted **{member}** permanently")
    else:
        if duration > 43200:
            await interaction.response.send_message("The specified duration is too long!"); return
        if duration < 0:
            await interaction.response.send_message("No negative numbers please!"); return
        try:
            moderation_data = json.loads(database["mute." + str(interaction.guild.id)])
        except:
            database["mute." + str(interaction.guild.id)] = json.dumps([])
            moderation_data = json.loads(database["mute." + str(interaction.guild.id)])
        try:
            await member.add_roles(mute_role)
            moderation_data.append([member.id, time.time(), duration])
            database["mute." + str(interaction.guild.id)] = json.dumps(moderation_data)
        except:
            await interaction.response.send_message(f"Unable to mute **{member}**"); return
        await interaction.response.send_message(f"Successfully muted **{member}** for **{duration if round(duration) != 1 else round(duration)} {'minute' if round(duration) == 1 else 'minutes'}**")

@client.user_command(name="Mute Member")
async def user_mute_command(interaction):
    mute_role = None; exists = False
    for role in interaction.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if not exists:
        await setup_muted_command(interaction)
    mute_role = None; exists = False
    for role in interaction.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if not exists:
        await interaction.response.send_message("Unable to find mute role")
        return
    try:
        await interaction.target.add_roles(mute_role)
        await interaction.response.send_message(f"Successfully muted **{interaction.target}**")
    except:
        await interaction.response.send_message(f"Unable to mute **{interaction.target}**")

@client.user_command(name="Unmute Member")
async def user_unmute_command(interaction):
    mute_role = None; exists = False
    for role in interaction.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if exists:
        try:
            await interaction.target.remove_roles(mute_role)
            await interaction.response.send_message(f"Successfully unmuted **{interaction.target}**")
        except:
            await interaction.response.send_message(f"Unable to unmute **{interaction.target}**")
    else:
        await interaction.response.send_message(f"Unable to unmute **{interaction.target}**")

@client.slash_command(name="filter", description="Manage the auto-moderation filters")
async def filter_command(_):
    pass

@filter_command.sub_command_group(name="insults", description="Manage the insults filter")
async def insults_command(_):
    pass

@insults_command.sub_command(name="list", description="List all the words in the insults filter")
async def insults_list_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    try:
        insults_data = json.loads(database[f"insults.list.{interaction.guild.id}"])
    except:
        insults_data = []
    embed = disnake.Embed(title="Insults List", description="There are no swear words configured for your server" if insults_data == [] else '\n'.join(insults_data), color=variables.embed_color)
    await interaction.response.send_message(embed=embed)

@insults_command.sub_command(name="status", description="See the current status of the insults filter")
async def insults_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    try:
        current_status = json.loads(database[f"insults.toggle.{interaction.guild.id}"])
    except:
        current_status = False
    await interaction.response.send_message(f"The insults filter is currently **{'enabled' if current_status else 'disabled'}**")

@insults_command.sub_command(name="enable", description="Enable the insults filter")
async def insults_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"insults.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("The insults filter has been successfully **enabled**")

@insults_command.sub_command(name="disable", description="Disable the insults filter")
async def insults_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"insults.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("The insults filter has been successfully **disabled**")

@insults_command.sub_command(name="add", description="Add a word to the insults filter")
async def insults_add_command(
        interaction,
        word: str = Param(description="The word you want to add"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    try:
        insults_data = json.loads(database[f"insults.list.{interaction.guild.id}"])
    except:
        insults_data = []
        database[f"insults.list.{interaction.guild.id}"] = json.dumps([])
    if len(insults_data) >= 20:
        await interaction.response.send_message("You can only add up to **20 words**!")
        return
    insults_data.append(word)
    database[f"insults.list.{interaction.guild.id}"] = json.dumps(insults_data)
    await interaction.response.send_message(f"Successfully added **{word}** to your insults list")

@insults_command.sub_command(name="remove", description="Remove a word from the insults filter")
async def insults_remove_command(
        interaction,
        word: str = Param(description="The word you want to remove")
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    try:
        insults_data = json.loads(database[f"insults.list.{interaction.guild.id}"])
    except:
        insults_data = []
        database[f"insults.list.{interaction.guild.id}"] = json.dumps([])
    try:
        insults_data.remove(word)
    except:
        await interaction.response.send_message("That word does not exist in the insults filter"); return
    database[f"insults.list.{interaction.guild.id}"] = json.dumps(insults_data)
    await interaction.response.send_message(f"Successfully removed **{word}** from the insults list")

@filter_command.sub_command_group(name="links", description="Manage the links filter")
async def links_filter_command(_):
    pass

@links_filter_command.sub_command(name="enable", description="Enable the links filter")
async def links_filter_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"links.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("The links filter has been successfully **enabled**")

@links_filter_command.sub_command(name="disable", description="Disable the links filter")
async def links_filter_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"links.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("The links filter has been successfully **disabled**")

@links_filter_command.sub_command(name="status", description="See the current status of the links filter")
async def links_filter_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    value = False
    try:
        value = json.loads(database[f"links.toggle.{interaction.guild.id}"])
    except:
        pass
    await interaction.response.send_message(f"The links filter is currently **{'enabled' if value else 'disabled'}**")

@filter_command.sub_command_group(name="spam", description="Manage the spam filter")
async def spam_command(_):
    pass

@spam_command.sub_command(name="enable", description="Enable the spam filter")
async def spam_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"spamming.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("The spam filter has been successfully **enabled**")

@spam_command.sub_command(name="disable", description="Disable the spam filter")
async def spam_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"spamming.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("The spam filter has been successfully **disabled**")

@spam_command.sub_command(name="set", description="Set the limit for the spam filter")
async def spam_set_command(
        interaction,
        limit: int = Param(description="The limit you want to set"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"spamming.limit.{interaction.guild.id}"] = limit
    await interaction.response.send_message(f"The spam filter limit has been set to **{limit} {'message' if limit == 1 else 'messages'}** per **15 seconds**")

@spam_command.sub_command(name="status", description="See the current status for the spam filter")
async def spam_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    value = 0
    try:
        value = json.loads(database[f"spamming.toggle.{interaction.guild.id}"])
    except:
        pass
    limit = 6
    try:
        limit = json.loads(database[f"spamming.limit.{interaction.guild.id}"])
    except:
        pass
    await interaction.response.send_message(f"The spam filter is currently **{'enabled' if value else 'disabled'}** (limit is **{limit}**)")

@client.slash_command(name="greetings", description="Manage welcome and leave messages")
async def greetings_command(_):
    pass

@greetings_command.sub_command_group(name="leave", description="Manage leave messages")
async def leave_command(_):
    pass

@leave_command.sub_command(name="enable", description="Enable leave messages")
async def leave_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    try:
        database[f"leave.text.{interaction.guild.id}"]
    except:
        await interaction.response.send_message(f"Please set a leave message first")
        return
    try:
        channel_id = json.loads(database[f"leave.channel.{interaction.guild.id}"])
        found = False
        for channel in interaction.guild.channels:
            if channel.id == channel_id:
                found = True
        if not found:
            raise Exception("unable to find channel")
    except:
        await interaction.response.send_message(f"Please set a leave channel first"); return

    database[f"leave.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("Leave messages have been successfully **enabled**")

@leave_command.sub_command(name="disable", description="Disable leave messages")
async def leave_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"leave.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("Leave messages have been successfully **disabled**")

@leave_command.sub_command(name="text", description="Change the leave message text")
async def leave_text_command(
        interaction,
        text: str = Param(description="The leave message text"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"leave.text.{interaction.guild.id}"] = text
    await interaction.response.send_message(f"The leave message has been set to\n```\n{text}```\n" + "Variables like `{user}`, `{user_id}`, `{discriminator}`, and `{members}` are also supported!")
    try:
        database[f"leave.text.{interaction.guild.id}"]
        database[f"leave.channel.{interaction.guild.id}"]
        database[f"leave.toggle.{interaction.guild.id}"] = 1
    except:
        pass

@leave_command.sub_command(name="channel", description="Change the leave message channel")
async def leave_channel_command(
        interaction,
        channel: disnake.channel.TextChannel = Param(description="The leave channel"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"leave.channel.{interaction.guild.id}"] = channel.id
    await interaction.response.send_message(f"The leave channel for this server has been set to <#{channel.id}>")
    try:
        database[f"leave.text.{interaction.guild.id}"]
        database[f"leave.channel.{interaction.guild.id}"]
        database[f"leave.toggle.{interaction.guild.id}"] = 1
    except:
        pass

@leave_command.sub_command(name="status", description="See the current status of the leave message")
async def leave_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    value = False
    try:
        value = json.loads(database[f"leave.toggle.{interaction.guild.id}"])
    except:
        pass
    text = "There is nothing here..."
    try:
        text = database[f"leave.text.{interaction.guild.id}"].decode("utf-8")
    except:
        pass
    channel_id = "**#unknown-channel**"
    try:
        channel_id = "<#" + database[f"leave.channel.{interaction.guild.id}"].decode("utf-8") + ">"
    except:
        pass
    await interaction.response.send_message(f"Leave messages are currently **{'enabled' if value else 'disabled'}** and set to {channel_id}\n```\n{text}```")

@greetings_command.sub_command_group(name="welcome", description="Manage welcome messages")
async def welcome_command(_):
    pass

@welcome_command.sub_command(name="enable", description="Enable welcome messages")
async def welcome_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    try:
        database[f"welcome.text.{interaction.guild.id}"]
    except:
        await interaction.response.send_message(f"Please set a welcome message first")
        return
    try:
        channel_id = json.loads(database[f"welcome.channel.{interaction.guild.id}"])
        found = False
        for channel in interaction.guild.channels:
            if channel.id == channel_id:
                found = True
        if not found:
            raise Exception("unable to find channel")
    except:
        await interaction.response.send_message(f"Please set a welcome channel first"); return

    database[f"welcome.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("Welcome messages have been successfully **enabled**")

@welcome_command.sub_command(name="disable", description="Disable welcome messages")
async def welcome_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"welcome.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("Welcome messages have been successfully **disabled**")

@welcome_command.sub_command(name="text", description="Change the welcome message text")
async def welcome_text_command(
        interaction,
        text: str = Param(description="The welcome message text"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"welcome.text.{interaction.guild.id}"] = text
    await interaction.response.send_message(f"The welcome message has been set to\n```\n{text}```\n" + "Variables like `{user}`, `{user_id}`, `{discriminator}`, and `{members}` are also supported!")
    try:
        database[f"welcome.text.{interaction.guild.id}"]
        database[f"welcome.channel.{interaction.guild.id}"]
        database[f"welcome.toggle.{interaction.guild.id}"] = 1
    except:
        pass

@welcome_command.sub_command(name="channel", description="Change the welcome message channel")
async def welcome_channel_command(
        interaction,
        channel: disnake.channel.TextChannel = Param(description="The welcome channel"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    database[f"welcome.channel.{interaction.guild.id}"] = channel.id
    await interaction.response.send_message(f"The welcome channel for this server has been set to <#{channel.id}>")
    try:
        database[f"welcome.text.{interaction.guild.id}"]
        database[f"welcome.channel.{interaction.guild.id}"]
        database[f"welcome.toggle.{interaction.guild.id}"] = 1
    except:
        pass

@welcome_command.sub_command(name="status", description="See the current status of the welcome message")
async def welcome_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(variables.no_permission_text)
        return
    value = False
    try:
        value = json.loads(database[f"welcome.toggle.{interaction.guild.id}"])
    except:
        pass
    text = "There is nothing here..."
    try:
        text = database[f"welcome.text.{interaction.guild.id}"].decode("utf-8")
    except:
        pass
    channel_id = "**#unknown-channel**"
    try:
        channel_id = "<#" + database[f"welcome.channel.{interaction.guild.id}"].decode("utf-8") + ">"
    except:
        pass
    await interaction.response.send_message(f"Welcome messages are currently **{'enabled' if value else 'disabled'}** and set to {channel_id}\n```\n{text}```")

@client.slash_command(name="snipe", description="Bring deleted messages back to life")
async def snipe_command(interaction):
    try:
        random_message = random.choice(snipe_list[interaction.guild.id])
        message_author = random_message[0]
        message_author_avatar = random_message[1]
        channel_name = random_message[2]
        message_sent_time = random_message[3]
        message_data = random_message[4]
        embed = disnake.Embed(description=message_data, color=variables.embed_color, timestamp=message_sent_time)
        embed.set_author(name=message_author, icon_url=message_author_avatar); embed.set_footer(text=f"Sent in #{channel_name}")
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("There is nothing to snipe!")

@client.slash_command(name="server", description="View information about this server")
async def server_command(_):
    pass

@server_command.sub_command(name="members", description="Count the members in this server")
async def server_members_command(interaction):
    users = 0
    bots = 0
    for member in interaction.guild.members:
        if member.bot:
            bots += 1
        else:
            users += 1
    embed = disnake.Embed(
        title="Guild Members",
        description=f"User accounts: **{users}**\nBot accounts: **{bots}**\nTotal members: **{users + bots}**",
        color=variables.embed_color
    )
    await interaction.response.send_message(embed=embed)

@server_command.sub_command(name="information", description="View information about this server")
async def server_information_command(interaction):
    users = 0
    bots = 0
    administrators = 0
    for member in interaction.guild.members:
        if member.guild_permissions.administrator:
            administrators += 1
        if member.bot:
            bots += 1
        else:
            users += 1
    text_channels = 0
    voice_channels = 0
    categories = 0
    for channel in interaction.guild.channels:
        if type(channel) == disnake.channel.TextChannel:
            text_channels += 1
        elif type(channel) == disnake.channel.VoiceChannel:
            voice_channels += 1
        elif type(channel) == disnake.channel.CategoryChannel:
            categories += 1
    server_bans = "?"
    try:
        server_bans = len(await interaction.guild.bans())
    except:
        pass
    server_invites = "?"
    try:
        server_invites = len(await interaction.guild.invites())
    except:
        pass

    embed = disnake.Embed(color=variables.embed_color)
    if interaction.guild.icon != None:
        embed.set_thumbnail(url=interaction.guild.icon)
    if interaction.guild.banner != None:
        embed.set_image(url=interaction.guild.banner)
    embed.add_field(name="Server ID", value=f"`{interaction.guild.id}`")
    embed.add_field(name="Server Region", value=f"{interaction.guild.region}")
    embed.add_field(name="Creation Time", value=f"<t:{parse_snowflake(interaction.guild.id)}:R>")
    embed.add_field(name="Server Owner", value=f"`{interaction.guild.owner.id}`")
    embed.add_field(name="Channels", value=f"{text_channels + voice_channels + categories:,}")
    embed.add_field(name="Roles", value=f"{len(interaction.guild.roles):,}")
    embed.add_field(name="Categories", value=f"{categories:,}")
    embed.add_field(name="Text Channels", value=f"{text_channels:,}")
    embed.add_field(name="Voice Channels", value=f"{voice_channels:,}")
    embed.add_field(name="Threads", value=f"{len(await interaction.guild.active_threads()):,}")
    embed.add_field(name="Emojis", value=f"{len(interaction.guild.emojis):,}")
    embed.add_field(name="Stickers", value=f"{len(interaction.guild.stickers):,}")
    embed.add_field(name="Administrators", value=f"{administrators:,}")
    embed.add_field(name="Users", value=f"{users:,}")
    embed.add_field(name="Bots", value=f"{bots:,}")
    embed.add_field(name="Bans", value=f"{server_bans:,}")
    embed.add_field(name="Members", value=f"{users + bots:,}")
    embed.add_field(name="Max Members", value=f"{interaction.guild.max_members:,}")
    embed.add_field(name="Invites", value=f"{server_invites:,}")
    embed.add_field(name="Boosters", value=f"{len(interaction.guild.premium_subscribers):,}")
    embed.add_field(name="Boost Level", value=f"{interaction.guild.premium_tier:,}")
    if interaction.guild.description:
        embed.add_field(name="Description", value=interaction.guild.description)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "server", 3)

@client.slash_command(name="github", description="Fetch a repository on GitHub")
async def github_command(
        interaction,
        repository: str = Param(description="The repository you want to fetch"),
    ):
    response = requests.get(f"https://api.github.com/repos/{repository.strip()}").json()
    try:
        if response["message"] == "Not Found":
            await interaction.response.send_message("That GitHub repository was not found"); return
    except:
        pass
    embed = disnake.Embed(color=variables.embed_color)
    embed.add_field(name="Repository", value=f"[URL]({response['html_url']})")
    embed.add_field(name="Owner", value=f"{response['owner']['login']}")
    embed.add_field(name="Name", value=f"{response['name']}")
    embed.add_field(name="Language", value=f"{response['language']}")
    embed.add_field(name="Issues", value=f"{response['open_issues']:,}")
    embed.add_field(name="Watchers", value=f"{response['subscribers_count']:,}")
    embed.add_field(name="Stars", value=f"{response['stargazers_count']:,}")
    embed.add_field(name="Forks", value=f"{response['forks']:,}")
    embed.add_field(name="License", value=f"{response['license']['name'] if response['license'] != None else 'None'}")
    embed.add_field(name="Size", value=f"{round(response['size']/1000, 2):,} MB")
    embed.add_field(name="Branch", value=f"{response['default_branch']}")
    embed.add_field(name="Forked", value=f"{response['fork']}")
    embed.add_field(name="Archived", value=f"{response['archived']}")
    embed.add_field(name="Created", value=f"<t:{str(parser.isoparse(response['created_at']).timestamp()).split('.')[0]}:d>")
    embed.add_field(name="Updated", value=f"<t:{str(parser.isoparse(response['updated_at']).timestamp()).split('.')[0]}:d>")
    embed.add_field(name="Description", value=f"{response['description']}")
    embed.set_thumbnail(url=response["owner"]["avatar_url"])
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "github", 5)

@client.slash_command(name="choose", description="Choose a random item from the list")
async def choose_command(
        interaction,
        item1: str = Param(description="An item"),
        item2: str = Param(description="An item"),
        item3: str = Param("", description="An item"),
        item4: str = Param("", description="An item"),
        item5: str = Param("", description="An item"),
        item6: str = Param("", description="An item"),
        item7: str = Param("", description="An item"),
        item8: str = Param("", description="An item"),
        item9: str = Param("", description="An item"),
        item10: str = Param("", description="An item"),
    ):
    items = []
    if item1 != "":
        items.append(item1)
    if item2 != "":
        items.append(item2)
    if item3 != "":
        items.append(item3)
    if item4 != "":
        items.append(item4)
    if item5 != "":
        items.append(item5)
    if item6 != "":
        items.append(item6)
    if item7 != "":
        items.append(item7)
    if item8 != "":
        items.append(item8)
    if item9 != "":
        items.append(item9)
    if item10 != "":
        items.append(item10)
    random_item = random.choice(items)
    await interaction.response.send_message(f"I choose **{random_item}**")

@client.slash_command(name="pypi", description="Fetch a project on PyPi")
async def pypi_command(
        interaction,
        project: str = Param(description="The PyPi project that you want to search"),
    ):
    response = requests.get(f"https://pypi.org/pypi/{project}/json/")
    if response.status_code == 404:
        await interaction.response.send_message("That package was not found")
        return
    response = response.json()
    size_unit = "bytes"; size = response["urls"][len(response["urls"])-1]["size"]
    if size > 1000:
        size_unit = "KB"
        size = size / 1000
        if size > 1000:
            size_unit = "MB"
            size = size / 1000
    embed = disnake.Embed(color=variables.embed_color)
    embed.add_field(name="Project", value=f"[URL]({response['info']['package_url']})")
    embed.add_field(name="Homepage", value=f"[URL]({response['info']['home_page']})")
    embed.add_field(name="Owner", value=response["info"]["author"] if response["info"]["author"] != "" else "None")
    embed.add_field(name="Name", value=response["info"]["name"])
    embed.add_field(name="Version", value=response["info"]["version"])
    embed.add_field(name="License", value=response["info"]["license"] if response["info"]["license"] != "" else "None")
    embed.add_field(name="Yanked", value=response["info"]["yanked"])
    embed.add_field(name="Size", value=f"{round(size, 2)} {size_unit}")
    embed.add_field(name="Updated", value=f"<t:{str(parser.isoparse(response['urls'][len(response['urls'])-1]['upload_time_iso_8601']).timestamp()).split('.')[0]}:d>")
    embed.add_field(name="Summary", value=response["info"]["summary"])
    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/oQNoEyWKGK4hHgW0x-sijvshBVYPzZ8g7zrARhLbHJU/https/cdn.discordapp.com/emojis/766274397257334814.png?width=115&height=100")
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "pypi", 5)

@client.slash_command(name="discriminator", description="Find users with the same discriminator")
async def discriminator_command(
        interaction,
        discriminator: str = Param(0, description="The discriminator to look for"),
    ):
    if discriminator == 0:
        discriminator = interaction.author.discriminator

    members = []
    discriminator = discriminator.replace("#", "")
    try:
        int(discriminator)
        if len(discriminator) != 4:
            raise Exception("invalid discriminator")
    except:
        await interaction.response.send_message("That is not a valid discriminator!", ephemeral=True)
        return

    for member in client.get_all_members():
        if member.discriminator == discriminator:
            if str(member) not in members:
                members.append(str(member))
    new_line = "\n"
    if members == []:
        await interaction.response.send_message("There are no other users with the same discriminator")
        return

    output = "\n".join(members)
    segments = [output[i: i + 1000] for i in range(0, len(output), 1000)]
    pager = Paginator(
        prefix=f"```\n", suffix="```", color=variables.embed_color, title="Discriminator", segments=segments,
    )
    await pager.start(interaction)
    add_cooldown(interaction.author.id, "discriminator", 5)

@client.slash_command(name="kick", description="Kick a member from your server")
async def kick_command(
        interaction,
        member: disnake.Member = Param(description="The member you want to kick"),
        reason: str = Param("Not specified", description="The reason for kicking the member"),
    ):
    if interaction.author.guild_permissions.kick_members or interaction.author.id in variables.permission_override:
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(
                embed=disnake.Embed(
                    color=variables.embed_color,
                    description=f":white_check_mark: **{member}** has been **successfully kicked**",
                )
            )
        except:
            await interaction.response.send_message(
                embed=disnake.Embed(
                    color=variables.embed_color,
                    description=f":x: Unable to kick **{member}**",
                )
            )
    else:
        await interaction.response.send_message(variables.no_permission_text)

@client.slash_command(name="ban", description="Ban a specified member from your server")
async def ban_command(
        interaction,
        member: str = Param(description="The ID of the member you want to ban"),
        reason: str = Param("Not specified", description="The reason for banning the member"),
    ):
    if interaction.author.guild_permissions.ban_members or interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(variables.no_permission_text)
        return

    try:
        user_id = int(remove_mention(member))
    except:
        await interaction.response.send_message("Please mention a valid user!", ephemeral=True)
        return

    found = False
    for member in interaction.guild.members:
        if member.id == user_id:
            found = True
            try:
                await member.ban(reason=reason, delete_message_days=0)
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        color=variables.embed_color,
                        description=f":white_check_mark: **{member}** has been **successfully banned**",
                    )
                )
            except:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        color=variables.embed_color,
                        description=f":x: Unable to ban **{member}**",
                    )
                )
    if not found:
        try:
            try:
                user = await client.fetch_user(user_id)
            except:
                await interaction.response.send_message("Unable to find the specified user")
                return
            await interaction.guild.ban(user, reason=reason, delete_message_days=0)
            await interaction.response.send_message(
                embed=disnake.Embed(
                    color=variables.embed_color,
                    description=f":white_check_mark: **{user}** has been **successfully banned**",
                )
            )
        except:
            await interaction.response.send_message(
                embed=disnake.Embed(
                    color=variables.embed_color,
                    description=f":x: Unable to ban **{user}**",
                )
            )

@client.slash_command(name="unban", description="Unban a specified member from your server")
async def unban_command(
        interaction,
        member: str = Param(description="The member you want to unban"),
    ):
    if interaction.author.guild_permissions.ban_members or interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(variables.no_permission_text)
        return

    try:
        user_id = int(remove_mention(member))
        user = await client.fetch_user(user_id)
    except:
        await interaction.response.send_message("Please mention a valid user!", ephemeral=True)
        return
    try:
        await interaction.guild.unban(user)
        await interaction.response.send_message(
            embed=disnake.Embed(
                color=variables.embed_color,
                description=f":white_check_mark: **{user}** has been **successfully unbanned**",
            )
        )
    except:
        await interaction.response.send_message(
            embed=disnake.Embed(
                color=variables.embed_color,
                description=f":x: Unable to unban **{user}**",
            )
        )

@client.slash_command(name="convert", description="Convert amounts to different units")
async def convert_command(
        interaction,
        amount: float = Param(description="The amount (for the input unit)"),
        input_unit: str = Param(name="input-unit", description="The input unit"),
        output_unit: str = Param(name="output-unit", description="The output unit"),
    ):
    input_unit = input_unit.strip()
    output_unit = output_unit.strip()
    data = converter.convert(amount, input_unit, output_unit)
    if data["error"] == 404:
        await interaction.response.send_message("That input/output pair is not supported")
        return
    description = f"**{round(amount, 6):,} {data['input_abbreviation']}** = **{round(data['result'], 6):,} {data['output_abbreviation']}**\n\n**Unit abbreviations:**\n`{data['input_abbreviation']}` = `{data['input_unit']}`, `{data['output_abbreviation']}` = `{data['output_unit']}`"
    embed = disnake.Embed(
        title="Conversion",
        color=variables.embed_color,
        description=description,
    )
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "convert", 3)

@client.slash_command(name="translate", description="Translate text to different languages")
async def translate_command(
        interaction,
        language: str = Param(description="The language you want to translate to"),
        text: str = Param(description="The text you want to translate"),
    ):
    await interaction.response.defer()
    try:
        translator = googletrans.Translator()
        result = translator.translate(text, dest=language.strip())
        embed = disnake.Embed(color=variables.embed_color)
        source_language = googletrans.LANGUAGES[result.src.lower()].title().replace("(", "").replace(")", "")
        destination_language = googletrans.LANGUAGES[result.dest.lower()].title().replace("(", "").replace(")", "")
        embed.add_field(name=f"Original Text ({source_language})", value=text, inline=False)
        embed.add_field(name=f"Translated Text ({destination_language})", value=result.text)
        await interaction.edit_original_message(embed=embed)
        add_cooldown(interaction.author.id, "translate", 5)
    except Exception as error:
        await interaction.edit_original_message(content=f"There was an error while trying to translate the specified text: `{error}`")

@client.message_command(name="Translate (English)")
async def message_translate_command(interaction):
    await interaction.response.defer(ephemeral=True) 
    try:
        text = interaction.target.content
        if text == "":
            await interaction.edit_original_message(content="That message does not have any text!")
            return
        translator = googletrans.Translator()
        result = translator.translate(text, dest="en")
        embed = disnake.Embed(color=variables.embed_color)
        source_language = googletrans.LANGUAGES[result.src.lower()].title().replace("(", "").replace(")", "")
        destination_language = googletrans.LANGUAGES[result.dest.lower()].title().replace("(", "").replace(")", "")
        embed.add_field(name=f"Original Text ({source_language})", value=text, inline=False)
        embed.add_field(name=f"Translated Text ({destination_language})", value=result.text)
        await interaction.edit_original_message(embed=embed)
        add_cooldown(interaction.author.id, "translate", 5)
    except Exception as error:
        await interaction.edit_original_message(content=f"There was an error while trying to translate the specified text: `{error}`")

@client.slash_command(name="definition", description="Find the definition of a word")
async def definition_command(
        interaction,
        word: str = Param(description="The word you want to find the definition of"),
        language: str = Param("en", description="The word's language"),
    ):
    await interaction.response.defer()
    language = language.strip().lower()
    reversed_languages = {value: key for key, value in googletrans.LANGUAGES.items()}
    if language in reversed_languages.keys():
        language = reversed_languages[language]
    response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/{language}/{word.strip()}").json()
    try:
        if response["title"] == "No Definitions Found":
            await interaction.edit_original_message(content="That word was not found in the dictionary")
            return
    except:
        pass
    phonetic = "unknown"
    try:
        phonetic = response[0]['phonetic']
    except:
        pass
    origin = "unknown"
    try:
        origin = response[0]['origin'].replace(" .", ".").replace(" )", ")")
    except:
        pass
    description = f"**Word:** {response[0]['word']} ({phonetic})\n**Origin:** {origin}"
    for meaning in response[0]['meanings']:
        synonyms = ', '.join(meaning['definitions'][0]['synonyms'][:3])
        if synonyms == "":
            synonyms = "none"
        example = "none"
        try:
            example = meaning['definitions'][0]['example'].replace(response[0]['word'], '__' + response[0]['word'] + '__')
        except:
            pass
        description += f"\n\n**Type:** {meaning['partOfSpeech']}\n**Definition:** {meaning['definitions'][0]['definition']}\n**Example:** {example}\n**Synonyms:** {synonyms}"
    embed = disnake.Embed(title="Definition", description=description, color=variables.embed_color)
    await interaction.edit_original_message(embed=embed)
    add_cooldown(interaction.author.id, "definition", 5)

@client.slash_command(name="remind", description="Remind yourself about something")
async def remind_command(_):
    pass

@remind_command.sub_command(name="list", description="See all your active reminders")
async def remind_list_command(interaction):
    try:
        current_reminders = json.loads(database[f"reminders.{interaction.author.id}"])
    except:
        current_reminders = []
    text = ""
    for reminder in current_reminders:
        end_time = reminder[0] + reminder[1]
        text += f"**Time:** <t:{round(end_time)}:R>\n**Text:** {reminder[2]}\n\n"
    if text == "":
        text = "You have no reminders"
    embed = disnake.Embed(title="Reminders", description=text, color=variables.embed_color)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "remind", 10)

@remind_command.sub_command(name="add", description="Add a new reminder")
async def remind_add_command(
        interaction,
        duration: float = Param(name="minutes", description="The duration of the reminder"),
        text: str = Param(description="The name of the reminder"),
    ):
    if len(text) > 200:
        await interaction.response.send_message("The specified text is too long!")
        return
    if duration > 10080:
        await interaction.response.send_message("The specified duration is too long!")
        return
    if duration < 0:
        await interaction.response.send_message("No negative numbers please!")
        return
    try:
        current_reminders = json.loads(database[f"reminders.{interaction.author.id}"])
    except:
        current_reminders = []
    if len(current_reminders) >= 5:
        await interaction.response.send_message("You already have **5 reminders**!")
        return
    current_reminders.append([time.time(), duration*60, text])
    database[f"reminders.{interaction.author.id}"] = json.dumps(current_reminders)
    await interaction.response.send_message(f"You will be reminded in **{duration if round(duration) != 1 else round(duration)} {'minute' if round(duration) == 1 else 'minutes'}**")

def epoch_to_date(epoch):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))

def date_to_epoch(timestamp):
    timestamp = timestamp.replace("Today", str(datetime.datetime.now().date()))
    timestamp = timestamp.replace("/", "-")
    if timestamp.count(" ") == 0:
        if timestamp.count("-") == 2:
            timestamp += " 00:00:00"
    date = timestamp.split(" ")[0]; time = timestamp.split(" ")[1]
    date_parts = date.split("-"); time_parts = time.split(":")
    for i in range(len(date_parts)):
        date_parts[i] = int(date_parts[i])
    for i in range(len(time_parts)):
        time_parts[i] = int(time_parts[i])
    year = date_parts[0]; month = date_parts[1]; day = date_parts[2]
    hour = time_parts[0]; minute = time_parts[1]; second = time_parts[2]
    epoch = datetime.datetime(year, month, day, hour, minute, second).timestamp()
    return int(epoch)

def hash_text(hash_type, input_text):
    hasher = hashlib.new(hash_type)
    hasher.update(input_text.encode("utf-8"))
    return hasher.hexdigest()

def get_variable(name):
    try:
        return math_variables[name]
    except:
        return 0

def set_variable(name, value):
    math_variables[name] = value
    return 0

def build_permissions(member):
    permission_list = ""
    for permission in member.guild_permissions:
        if permission[1] == True:
            permission_list += f":white_check_mark: `{permission[0]}`\n"
        else:
            permission_list += f":x: `{permission[0]}`\n"
    return permission_list

def parse_snowflake(id):
    return round(((id >> 22) + 1420070400000) / 1000)

def evaluate_expression(expression):
    expression = expression.replace("^", "**")
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")

    math_functions = {
        "boo": "Boo!",
        "pi": math.pi,
        "π": math.pi,
        "len": lambda x: len(x),
        "sqrt": lambda x: math.sqrt(x),
        "cbrt": lambda x: x ** (1. / 3),
        "square": lambda x: x * x,
        "cube": lambda x: x * x * x,
        "random": lambda x, y: random.randint(x, y),
        "ord": lambda character: ord(character),
        "int": lambda value: int(value),
        "str": lambda value: str(value),
        "float": lambda value: float(value),
        "chr": lambda value: chr(value),
        "get": lambda name: get_variable(name),
        "set": lambda name, value: set_variable(name, value),
        "bin": lambda value: bin(value),
        "hex": lambda value: hex(value),
    }

    try:
        answer = str(simpleeval.simple_eval(expression, functions=math_functions))
    except:
        answer = "Unknown Answer"
    return answer

def rgb_to_hex(rgb_color):
    for value in rgb_color:
        if value >= 0 and value <= 255:
            pass
        else:
            raise Exception("invalid RGB color code")
    return '#%02x%02x%02x' % rgb_color

def generate_color(color_code):
    image_width = 180; image_height = 80
    if color_code.lower().startswith("rgb"):
        color_code = color_code[3:]
    if len(color_code) == 8 and color_code.startswith("0x"):
        color_code = color_code[2:]
        color_code = "#" + color_code
    if len(color_code) == 6:
        text = True
        for letter in color_code.lower():
            if letter not in string.ascii_lowercase:
                text = False
        if not text:
            color_code = "#" + color_code
    
    if not color_code.startswith("#") and not color_code.count(",") == 2:
        try:
            color_code = color_code.replace(" ", "_")
            color_code = str(eval("disnake.Color." + color_code + "()"))
        except:
            pass

    if color_code.startswith("#") and len(color_code) == 7:
        try:
            image = Image.new("RGB", (image_width, image_height), color_code)
            image.save("images/color.png"); value = color_code.lstrip('#'); length = len(value)
            rgb_color = tuple(int(value[i:i+length//3], 16) for i in range(0, length, length//3))
            return (color_code, rgb_color)
        except:
            return 1
    elif color_code.count(",") == 2 and "(" in color_code and ")" in color_code:
        try:
            color_code = color_code.replace("(", ""); color_code = color_code.replace(")", "")
            color_code = color_code.replace(", ", ","); rgb_color = tuple(map(int, color_code.split(',')))
            color_code = rgb_to_hex(rgb_color); image = Image.new("RGB", (image_width, image_height), color_code)
            image.save("images/color.png"); return (color_code, rgb_color)
        except:
            return 1
    else:
        return 1

async def send_user_message(user_id, message):
    for guild in client.guilds:
        try:
            member = await guild.fetch_member(int(user_id))
            await member.send(message); return
        except:
            continue

async def send_vote_message(user_id):
    for guild in client.guilds:
        for member in guild.members:
            if str(member.id) == user_id:
                class CommandView(disnake.ui.View):
                    def __init__(self):
                        super().__init__()
                        self.timeout = None

                    @disnake.ui.button(label="Add a reminder", style=disnake.ButtonStyle.green)
                    async def add_reminder(self, _, interaction):
                        duration = 43200
                        text = "Don't forget to vote for me!"
                        try:
                            current_reminders = json.loads(database[f"reminders.{user_id}"])
                        except:
                            current_reminders = []
                        exists = False
                        for reminder in current_reminders:
                            if reminder[1] == duration and reminder[2] == text:
                                exists = True
                        if exists:
                            await interaction.response.send_message("A reminder already exists!")
                            self.stop()
                            return
                        current_reminders.append([time.time(), duration, text])
                        database[f"reminders.{user_id}"] = json.dumps(current_reminders)
                        await interaction.response.send_message("A **12 hour reminder** has been successfully added!")
                        self.stop()
                await member.send(variables.vote_message, view=CommandView())
                return

async def on_member_join(member):
    try:
        autoroles = json.loads(database[f"autorole.{member.guild.id}"])
        for role in member.guild.roles:
            for role_id in autoroles:
                if role_id == str(role.id):
                    await member.add_roles(role)
    except:
        pass
    try:
        if json.loads(database[f"welcome.toggle.{member.guild.id}"]):
            welcome_message = database[f"welcome.text.{member.guild.id}"].decode("utf-8")
            welcome_channel = database[f"welcome.channel.{member.guild.id}"].decode("utf-8")
            for channel in member.guild.channels:
                if welcome_channel == str(channel.id):
                    welcome_message = welcome_message.replace("{user}", member.name)
                    welcome_message = welcome_message.replace("{user_id}", str(member.id))
                    welcome_message = welcome_message.replace("{user.id}", str(member.id))
                    welcome_message = welcome_message.replace("{user_id}", str(member.id))
                    welcome_message = welcome_message.replace("{discriminator}", member.discriminator)
                    welcome_message = welcome_message.replace("{members}", str(member.guild.member_count))
                    welcome_message = welcome_message.replace("{server}", member.guild.name)
                    await channel.send(welcome_message)
    except:
        pass

async def on_member_remove(member):
    try:
        if json.loads(database[f"leave.toggle.{member.guild.id}"]):
            leave_message = database[f"leave.text.{member.guild.id}"].decode("utf-8")
            leave_channel = database[f"leave.channel.{member.guild.id}"].decode("utf-8")
            for channel in member.guild.channels:
                if leave_channel == str(channel.id):
                    leave_message = leave_message.replace("{user}", member.name)
                    leave_message = leave_message.replace("{user_id}", str(member.id))
                    leave_message = leave_message.replace("{user.id}", str(member.id))
                    leave_message = leave_message.replace("{user_id}", str(member.id))
                    leave_message = leave_message.replace("{discriminator}", member.discriminator)
                    leave_message = leave_message.replace("{members}", str(member.guild.member_count))
                    leave_message = leave_message.replace("{server}", member.guild.name)
                    await channel.send(leave_message)
    except:
        pass

async def on_guild_join(guild):
    try:
        async for entry in guild.audit_logs(limit=10):
            if entry.action == disnake.AuditLogAction.bot_add:
                if entry.target.id == client.user.id:
                    await help_paginator.start(FakeInteraction(entry.user))
                    break
    except:
        pass

async def on_message_delete(message, *_):
    if not message.guild or message.author.bot:
        return

    try:
        snipes = snipe_list[message.guild.id]
    except:
        snipes = []
        snipe_list[message.guild.id] = []
    while len(snipes) >= 10:
        random_snipe = random.choice(snipes)
        snipes.remove(random_snipe)

    message_data = message.content
    if message_data == "":
        if len(message.embeds) > 0:
            message_data = message.embeds[0].description
    if message_data != "" or type(message_data) != disnake.Embed.Empty:
        snipes.append([
            f"{message.author.name}#{message.author.discriminator}",
            message.author.avatar,
            message.channel.name,
            datetime.datetime.now(),
            message_data,
        ])
        snipe_list[message.guild.id] = snipes

async def on_message(message):
    if message.author.bot or not message.guild:
        return

    prefix = variables.prefix
    if message.content == f"<@{client.user.id}>" or message.content == f"<@!{client.user.id}>":
        await message.channel.send(embed=disnake.Embed(title="New Prefix", description=f"My prefix here is `/` (slash commands)\nIf you do not see any slash commands, make sure the bot is invited with [this link]({variables.bot_invite_link})", color=variables.embed_color))
        return
    
    if message.content.startswith(f"<@{client.user.id}> "):
        message.content = message.content.replace(f"<@{client.user.id}> ", prefix, 1)
    if message.content.startswith(f"<@!{client.user.id}> "):
        message.content = message.content.replace(f"<@!{client.user.id}> ", prefix, 1)
    if message.content.startswith(f"<@{client.user.id}>"):
        message.content = message.content.replace(f"<@{client.user.id}>", prefix, 1)
    if message.content.startswith(f"<@!{client.user.id}>"):
        message.content = message.content.replace(f"<@!{client.user.id}>", prefix, 1)

    if not message.author.guild_permissions.administrator:
        if message.author.id not in variables.permission_override:
            try:
                if json.loads(database[f"insults.toggle.{message.guild.id}"]):
                    insults = json.loads(database[f"insults.list.{message.guild.id}"])
                    for word in insults:
                        if word.lower() in message.content.lower():
                            await message.delete()
                            await message.author.send(f"Please do not use that word (**{word.lower()}**)!")
                            return
            except:
                pass
            try:
                if json.loads(database[f"links.toggle.{message.guild.id}"]):
                    link_regexes = ["http://", "https://", "www.", "discord.gg/"]
                    for regex in link_regexes:
                        if regex in message.content.lower().replace(" ", ""):
                            await message.delete()
                            await message.author.send("Please do not put links in your message!")
                            return
            except:
                pass
            try:
                if "spam" not in message.channel.name:
                    if json.loads(database[f"spamming.toggle.{message.guild.id}"]):
                        try:
                            last_message_time = last_messages[message.author.id]
                        except:
                            last_message_time = 0
                        if (time.time() - last_message_time) < 15:
                            try:
                                strikes = message_strikes[message.author.id]
                            except:
                                strikes = 0
                            message_strikes[message.author.id] = strikes + 1
                            strike_limit = 6
                            try:
                                strike_limit = json.loads(database[f"spamming.limit.{message.guild.id}"])
                            except:
                                pass
                            if strike_limit > 20:
                                strike_limit = 20
                            if strikes >= strike_limit:
                                await message.delete()
                                await message.author.send("Stop spamming!")
                                return
            except:
                pass
    last_messages[message.author.id] = time.time()
    
    if message.content.startswith(prefix) and len(message.content) > 1 and message.author.id not in variables.bot_owners:
        await message.channel.send("We have migrated to slash commands!", embed=disnake.Embed(title="New Prefix", description=f"My prefix here is `/` (slash commands)\nIf you do not see any slash commands, make sure the bot is invited with [this link]({variables.bot_invite_link})", color=variables.embed_color))
        return

    if message.content.startswith(prefix+"execute"):
        length = len(prefix+"execute ")
        if len(message.content) >= length:
            code = message.content[length:]
        else:
            await message.channel.send("No code specified")
            return
        output_language = ""
        codeblock = "```"
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```py"):
            code = code[5:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        if "#python" in code:
            output_language = "py"
        if "#golang" in code:
            output_language = "go"
        if "#clang" in code:
            output_language = "c"
        if "#cs" in code:
            output_language = "cs"
        if "#cpp" in code:
            output_language = "cpp"
        if "#java" in code:
            output_language = "java"
        if "#raw" in code:
            output_language = ""
            codeblock = ""

        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                if "#globals" in code:
                    exec(f"async def run_code():\n{textwrap.indent(code, '   ')}", globals())
                    await globals()["run_code"]()
                else:
                    dictionary = dict(locals(), **globals())
                    exec(f"async def run_code():\n{textwrap.indent(code, '   ')}", dictionary, dictionary)
                    await dictionary["run_code"]()

                output = stdout.getvalue()
        except Exception as error:
            output = "`" + str(error) + "`"
        
        output = output.replace(os.getenv("TOKEN"), "<token>")
        segments = [output[i: i + 2000] for i in range(0, len(output), 2000)]
        if len(output) > 2001:
            output = output.replace("`", "\`")
            pager = MessagePaginator(
                prefix=f"{codeblock}{output_language}\n", 
                suffix=codeblock, 
                color=variables.embed_color, 
                title=f"Code Output", 
                segments=segments,
            )
            await pager.start(message)
        elif len(output.strip()) == 0:
            await message.add_reaction("✅")
        else:
            await message.channel.send(output)

async def on_slash_command_error(interaction, error):
    error_text = str(error)
    if error_text.startswith("InteractionResponded:") or error_text.startswith("Command raised an exception: InteractionResponded:"):
        return

    if type(error) == disnake.errors.Forbidden:
        await interaction.author.send("I do not have the required permissions!")
    else:
        if "50035" in str(error):
            try:
                await interaction.response.send_message("Message too long to be sent!")
            except:
                try:
                    await interaction.edit_original_message(content="Message too long to be sent!")
                except:
                    await interaction.channel.send("Message too long to be sent!")
            return

        escaped_character = '\`'
        permissions = 0
        for user in interaction.guild.members:
            if user.id == client.user.id:
                permissions = user.guild_permissions.value
        interaction_data = "/" + interaction.data.name + " "
        for option in interaction.data.options:
            interaction_data += option.name
            if option.value != "" and option.value != None:
                interaction_data += f":{option.value}"
            interaction_data += " "
            for sub_option in option.options:
                if sub_option.value != "" and sub_option.value != None:
                    interaction_data += f"{sub_option.name}:{sub_option.value}"
                else:
                    interaction_data += f"{sub_option.name}"
        formatted_error = str(''.join(traceback.format_exception(error, error, error.__traceback__)))
        formatted_error = formatted_error.replace("`", escaped_character)
        codeblock = "```\n"
        if len(formatted_error) > 2000:
            codeblock = ""
        output = f"**{interaction.author.name}#{interaction.author.discriminator}** (`{interaction.author.id}`) has ran into an error in **{interaction.author.guild.name}** (`{interaction.author.guild.id}`)\n\n**Command:**\n```\n{interaction_data.replace('`', escaped_character)}```**Permissions:**\n```\n{permissions}```**Error:**\n{codeblock}{formatted_error}{codeblock}"
        segments = [output[i: i + 2000] for i in range(0, len(output), 2000)]
        for user_id in variables.message_managers:
            sent = False
            for guild in client.guilds:
                for member in guild.members:
                    if member.id == user_id:
                        try:
                            if not sent:
                                pager = Paginator(
                                    color=disnake.Color.red(), title="Error Report", segments=segments, timeout=None,
                                )
                                await pager.start(FakeInteraction(member))
                                sent = True
                        except Exception as new_error:
                            print(f"Unable to send error: {new_error}")

        embed = disnake.Embed(title="Bot Error", description=f"Uh oh! Doge Utilities has ran into an error!\nThis error has been sent to our bot creators.\n```\n{error}\n```", color=disnake.Color.red(), timestamp=datetime.datetime.now())
        embed.set_footer(text="Doge Utilities error report")
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            try:
                await interaction.edit_original_message(embed=embed)
            except:
                await interaction.channel.send(embed=embed)
