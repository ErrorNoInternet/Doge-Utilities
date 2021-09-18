import os
import io
import sys
import json
import html
import pytz
import time
import math
import extra
import urllib
import base64
import string
import psutil
import random
import asyncio
import disnake
import hashlib
import textwrap
import requests
import datetime
import importlib
import threading
import variables
import functions
import traceback
import contextlib
import simpleeval
import sqlitedict
from PIL import Image
from dateutil import parser

sqlitedict.PICKLE_PROTOCOL = 3
user_cooldowns = {}; message_strikes = {}; last_messages = {}
database = sqlitedict.SqliteDict("database.sql", autocommit=True)

class Command:
    def __init__(self, name, aliases, function, usage, description):
        super().__init__()
        
        self.name = name
        self.aliases = aliases
        self.function = function
        self.usage = usage
        self.description = description

class ContextObject:
    def __init__(self, client, message):
        super().__init__()

        self.bot = client
        self.message = message
        self.author = message.author
        self.guild = message.guild
        self.send = message.channel.send

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
                if key.startswith("mute."):
                    for value in database[key]:
                        try:
                            guild_id = int(key.split(".")[1])
                            user_id = int(value[0])
                            mute_start = float(value[1])
                            duration = float(value[2])
                        except:
                            moderation_data = database[key]
                            moderation_data.remove(value)
                            database[key] = moderation_data
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
                                    moderation_data = database[key]
                                    moderation_data.remove(value)
                                    database[key] = moderation_data
                            except:
                                moderation_data = database[key]
                                moderation_data.remove(value)
                                database[key] = moderation_data
        except Exception as error:
            print(f"Fatal error in manage_muted_members: {error}")
            try:
                moderation_data = database[key]
                moderation_data.remove(value)
                database[key] = moderation_data
            except:
                pass
        await asyncio.sleep(10)

try:
    start_time
except:
    start_time = time.time()
    last_command = time.time(); math_variables = {}
    required_intents = disnake.Intents.default()
    required_intents.members = True
    client = disnake.AutoShardedClient(
        shard_count=variables.shard_count,
        intents=required_intents,
    )
    client.max_messages = 512; snipe_list = {}
    threading.Thread(name="manage_muted_members", target=asyncio.run_coroutine_threadsafe, args=(manage_muted_members(), client.loop, )).start()
    threading.Thread(name="reset_strikes", target=reset_strikes).start()

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

def parse_variables(text):
    text = text.replace("<text>", "hello")
    text = text.replace("<color code>", "#0068DB")
    text = text.replace("<low>", "10"); text = text.replace("<high>", "100")
    text = text.replace("<suggestion>", "Make the bot better")
    text = text.replace("<expression>", "28 + 72")
    text = text.replace("<epoch>", str(round(time.time())))
    text = text.replace("<date>", "2021-01-01 08:00:00")
    text = text.replace("<on/off>", "on")
    text = text.replace("<encode/decode>", "encode")
    text = text.replace("<role>", "@Members")
    text = text.replace("<user>", "531392146767347712")
    text = text.replace("<messages>", "5")
    text = text.replace("<type>", "sha256")
    text = text.replace("<page>", "2")
    text = text.replace("<timezone>", "America/Denver")
    text = text.replace("<currency>", "usd")
    text = text.replace("<amount>", "8")
    text = text.replace("<nickname>", "Wumpus")
    text = text.replace("<minutes>", "2")
    text = text.replace("<enable/disable>", "enable")
    text = text.replace("<item>", "apple")
    text = text.replace("<repository>", "ErrorNoInternet/Doge-Utilities")
    text = text.replace("<project>", "disnake")
    return text

def reload_data():
    modules = [
        os,
        io,
        sys,
        json,
        html,
        pytz,
        time,
        math,
        extra,
        urllib,
        base64,
        string,
        psutil,
        random,
        asyncio,
        disnake,
        hashlib,
        textwrap,
        requests,
        datetime,
        importlib,
        threading,
        variables,
        functions,
        traceback,
        contextlib,
        simpleeval,
        sqlitedict,
    ]
    time_list = []
    for module in modules:
        start_time = time.time()
        for i in range(2):
            importlib.reload(module)
        end_time = time.time()
        time_list.append(end_time - start_time)
    
    total_time = sum(time_list); longest = [0, None]
    for length in time_list:
        if length > longest[0]:
            longest[0] = length; longest[1] = modules[time_list.index(length)]
    if round(total_time, 1) == 1.0:
        total_time = 1
    return f"Successfully reloaded all modules in **{round(total_time, 1)} {'second' if round(total_time, 1) == 1 else 'seconds'}**\nAverage: **{round(total_time/len(time_list), 2)} {'second' if round(total_time, 1) == 1 else 'seconds'}**, Longest: `{longest[1].__name__}` at **{round(longest[0], 2)} {'second' if round(total_time, 1) == 1 else 'seconds'}**"

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

async def currency_command(message, prefix):
    parts = message.content.split(" ")
    if len(parts) == 4:
        try:
            amount = float(parts[1].replace(",", "").replace(" ", "")); input_currency = parts[2].lower(); output_currency = parts[3].lower()
            url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{input_currency}/{output_currency}.json"
            response = requests.get(url).json(); value = response[output_currency] * amount
            embed = disnake.Embed(title="Currency Conversion", description=f"**{round(amount, 6):,} {input_currency.upper()}** = **{round(value, 6):,} {output_currency.upper()}**", color=variables.embed_color)
            await message.channel.send(embed=embed)
            add_cooldown(message.author.id, "currency", 5)
        except:
            await message.channel.send("Unable to convert currency"); return
    elif len(parts) == 2 and parts[1].lower() == "list":
        response = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies.json").json()
        output = ""
        for key in response.keys():
            output += f"{key}: {response[key]}\n"
        segments = [output[i: i + 1000] for i in range(0, len(output), 1000)]
        pager = CustomPager(
            timeout=60, length=1, prefix=f"```\n", suffix="```", color=variables.embed_color, title="Currency List", entries=segments,
        )
        await pager.start(ContextObject(client, message))
        add_cooldown(message.author.id, "currency", 5)
    else:
        await message.channel.send(f"The syntax is `{prefix}currency <input> <amount> <output>`"); return

async def ping_command(message, prefix):
    embed = disnake.Embed(title="Pong :ping_pong:", description=f"Latency: **{round(client.latency * 1000, 1)} ms**", color=variables.embed_color)
    await message.channel.send(embed=embed)

async def tests_command(message, prefix):
    add_cooldown(message.author.id, "tests", variables.large_number)
    description = """
:grey_question: `Code Integrity`
:grey_question: `Bot Status`
:grey_question: `Task Threads`
:grey_question: `Bot Version`
:grey_question: `Raid Protection`
:grey_question: `User Lookup`
:grey_question: `Cooldown System`
:grey_question: `Image Library`
    """
    embed = disnake.Embed(title="Doge Tests", description=description, color=variables.embed_color)
    old_message = await message.channel.send(embed=embed)

    lines = description.split("\n"); tests = []
    for line in lines:
        if ":" in line:
            tests.append(line)
    for test in tests:
        description = description.replace(test, test.replace(":grey_question:", ":hourglass_flowing_sand:"))
        embed = disnake.Embed(title="Doge Tests", description=description, color=variables.embed_color)
        await old_message.edit(embed=embed)
        description = description.replace(":hourglass_flowing_sand:", ":grey_question:")

        name = test.split(":grey_question: ")[1].replace("`", "")
        if name == "Code Integrity":
            try:
                for i in range(10):
                    reload_data()
                description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Bot Status":
            try:
                for i in range(100):
                    process = psutil.Process(os.getpid())
                    memory_usage = process.memory_info().rss / 1000000
                    if memory_usage >= 250:
                        description = description.replace(test, test.replace(":grey_question:", ":orange_square:")); continue
                    if round(psutil.cpu_percent()) >= 80 or (client.latency * 1000) >= 800:
                        description = description.replace(test, test.replace(":grey_question:", ":yellow_square:")); continue

                    description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Task Threads":
            try:
                if threading.active_count() >= 3:
                    description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
                else:
                    description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Bot Version":
            try:
                for i in range(10):
                    file_size = 0
                    for object in os.listdir():
                        try:
                            file = open(object, "rb")
                            file_size += len(file.read()); file.close()
                        except:
                            pass
                description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Raid Protection":
            try:
                for i in range(20):
                    server_roles = {}; server_channels = {}
                    for guild in client.guilds:
                        server_channels[guild.id] = guild.channels
                        server_roles[guild.id] = guild.roles
                description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "User Lookup":
            try:
                for i in range(3):
                    guild = random.choice(client.guilds)
                    member = random.choice(guild.members)
                    headers = {"Authorization": "Bot " + os.getenv("TOKEN")}
                    url = "https://discord.com/api/users/" + str(member.id)
                    requests.get(url, headers=headers)
                description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Cooldown System":
            try:
                for i in range(50):
                    add_cooldown(message.author.id, "test-command", 60)
                    if round(get_cooldown(message.author.id, "test-command")) == 60:
                        description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
                    else:
                        description = description.replace(test, test.replace(":grey_question:", ":yellow_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Image Library":
            try:
                for i in range(10):
                    if generate_color(f"({random.randint(0, 256)}, {random.randint(0, 256)}, {random.randint(0, 256)})") == 1:
                        description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
                    else:
                        description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
            
        embed = disnake.Embed(title="Doge Tests", description=description, color=variables.embed_color)
        await old_message.edit(embed=embed)
    add_cooldown(message.author.id, "tests", 300)

async def status_command(message, prefix):
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
    embed.add_field(name="Bot Latency", value="```" + f"{round(client.get_shard(message.guild.shard_id).latency * 1000, 1)} ms" + "```")
    embed.add_field(name="CPU Usage", value="```" + f"{psutil.cpu_percent()}%" + "```")
    embed.add_field(name="RAM Usage", value="```" + f"{round(memory_usage, 1)} MB{' (nice)' if round(memory_usage, 1) == 69.0 else ''}" + "```")
    embed.add_field(name="Thread Count", value="```" + str(threading.active_count()) + "```")
    embed.add_field(name="Joined Guilds", value="```" + str(len(client.guilds)) + "```")
    embed.add_field(name="Active Shards", value="```" + str(client.shards[0].shard_count) + "```")
    embed.add_field(name="Member Count", value="```" + str(member_count) + "```")
    embed.add_field(name="Channel Count", value="```" + str(channel_count) + "```")
    embed.add_field(name="Command Count", value="```" + str(len(command_list)) + "```")
    embed.add_field(name="Disnake Version", value="```" + disnake.__version__ + "```")
    embed.add_field(name="Bot Version", value="```" + f"{variables.version_number}.{variables.build_number}" + "```")
    embed.add_field(name="Bot Uptime", value="```" + uptime + "```")

    await message.channel.send(embed=embed)
    add_cooldown(message.author.id, "status", 5)

async def support_command(message, prefix):
    embed = disnake.Embed(title="Support Server", description=f"You can join Doge Utilities's official server [here]({variables.support_server_invite})", color=variables.embed_color)
    await message.channel.send(embed=embed)

async def version_command(message, prefix):
    file_size = 0
    for object in os.listdir():
        try:
            file = open(object, "rb")
            file_size += len(file.read()); file.close()
        except:
            pass
    embed = disnake.Embed(title="Bot Version", description=f"Version: **{variables.version_number}**\nBuild: **{variables.build_number}**\nPython: **{sys.version.split(' ')[0]}**\nDisnake: **{disnake.__version__}**\nSize: **{round(file_size / 1000)} KB**", color=variables.embed_color)
    await message.channel.send(embed=embed)
    add_cooldown(message.author.id, "version", 5)

async def invite_command(message, prefix):
    guild_member = True
    if message.author == message.guild.owner:
        guild_member = False

    class CommandView(disnake.ui.View):
        def __init__(self):
            super().__init__()

            self.clicked = False
            self.add_item(
                disnake.ui.Button(
                    label="Support Server",
                    url=variables.support_server_invite,
                )
            )
            self.add_item(
                disnake.ui.Button(
                    label="Invite Link",
                    url=f"https://discord.com/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=applications.commands%20bot",
                )
            )

        @disnake.ui.button(label="Leave Server", style=disnake.ButtonStyle.red, disabled=guild_member)
        async def leave_server(self, _, interaction):
            if interaction.author == message.author:
                if self.clicked:
                    await interaction.response.send_message("Leaving server...", ephemeral=True)
                    await message.guild.leave()
                else:
                    self.clicked = True
                    await interaction.response.send_message(
                        "Are you sure you want me to leave this server? Please press the button again to confirm.",
                        ephemeral=True,
                    )
            else:
                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
    await message.channel.send("Here's the link to invite me to another server", view=CommandView())

async def prefix_command(message, prefix):
    new_prefix = message.content.split(" ")
    if message.author.guild_permissions.administrator or message.author.id in variables.permission_override:
        if len(new_prefix) == 2:
            new_prefix = new_prefix[1]

            class CommandView(disnake.ui.View):
                def __init__(self):
                    super().__init__()

                @disnake.ui.button(label="Yes", style=disnake.ButtonStyle.green)
                async def confirm_change(self, _, interaction):
                    if interaction.author != message.author:
                        await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                        return

                    database[f"prefix.{message.guild.id}"] = new_prefix
                    await old_message.edit(content=f"This server's prefix has been set to `{new_prefix}`", view=None)
                    self.stop()

                @disnake.ui.button(label="No", style=disnake.ButtonStyle.green)
                async def reject_change(self, _, interaction):
                    if interaction.author != message.author:
                        await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                        return

                    await old_message.edit(content=f"Prefix change request cancelled", view=None)
                    self.stop()
            old_message = await message.channel.send(
                f"Are you sure you want to change this server's prefix to `{new_prefix}`?",
                view=CommandView(),
            )
        else:
            await message.channel.send(f"The syntax is `{prefix}prefix <new prefix>`")
    else:
        await message.channel.send(variables.no_permission_text)

async def setup_banned_command(message, prefix):
    if message.author.guild_permissions.manage_roles or message.author.id in variables.permission_override:
        pass
    else:
        await message.channel.send(variables.no_permission_text); return

    roles = message.guild.roles
    for role in roles:
        if role.name == "Banned":
            await message.channel.send("The **Banned** role already exists in this guild")
            return
    old_message = await message.channel.send("Generating the **Banned** role for the current guild...")
    try:
        banned_role = await message.guild.create_role(name="Banned")
        guild_roles = len(message.guild.roles); retry_count = 0
        while True:
            if retry_count > 100:
                break
            try:
                await banned_role.edit(position=guild_roles - retry_count)
                break
            except:
                retry_count += 1
        for channel in message.guild.channels:
            try:
                await channel.set_permissions(banned_role, view_channel=False, connect=False, change_nickname=False, add_reactions=False)
            except:
                pass
    except:
        await old_message.edit(content=f"Unable to generate the **Banned** role for this guild")
        return
    await old_message.edit(content=f"Successfully generated the **Banned** role for this guild")
    add_cooldown(message.author.id, "setup", 60)

async def setup_muted_command(message, prefix):
    if message.author.guild_permissions.manage_roles or message.author.id in variables.permission_override:
        pass
    else:
        await message.channel.send(variables.no_permission_text); return

    roles = message.guild.roles
    for role in roles:
        if role.name == "Muted":
            await message.channel.send("The **Muted** role already exists in this guild")
            return
    old_message = await message.channel.send("Generating the **Muted** role for the current guild...")
    try:
        muted_role = await message.guild.create_role(name="Muted")
        guild_roles = len(message.guild.roles); retry_count = 0
        while True:
            if retry_count > 100:
                break
            try:
                await muted_role.edit(position=guild_roles - retry_count)
                break
            except:
                retry_count += 1
        for channel in message.guild.channels:
            try:
                await channel.set_permissions(muted_role, send_messages=False)
            except:
                try:
                    await channel.set_permissions(muted_role, connect=False)
                except:
                    pass
    except:
        await old_message.edit(f"Unable to generate the **Muted** role for this guild")
        return
    await old_message.edit(f"Successfully generated the **Muted** role for this guild")
    add_cooldown(message.author.id, "setup", 60)

async def random_command(message, prefix):
    arguments = message.content.split(" "); high_number = 0; low_number = 0
    try:
        if len(arguments) == 2:
            high_number = float(arguments[1])
        elif len(arguments) == 3:
            low_number = float(arguments[1])
            high_number = float(arguments[2])
        else:
            await message.channel.send(f"The syntax is `{prefix}random <low> <high>`")
            return
    except:
        await message.channel.send("Please enter a valid number")
        return
    try:
        random_number = round(random.uniform(low_number, high_number), 2)
    except:
        await message.channel.send("The lower number is larger than the higher number")
        return
    add_cooldown(message.author.id, "random", 20)
    button_text = "Generate Number"

    class CommandView(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.uses = 0

        @disnake.ui.button(label=button_text, style=disnake.ButtonStyle.gray)
        async def generate_number(self, _, interaction):
            if interaction.author != message.author:
                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if self.uses < 5:
                self.uses += 1
                random_number = round(random.uniform(low_number, high_number), 2)
                await old_message.edit(content=f"Your random number is **{random_number}**")
            else:
                new_view = disnake.ui.View()
                new_view.add_item(disnake.ui.Button(label=button_text, style=disnake.ButtonStyle.gray, disabled=True))
                await old_message.edit(view=new_view)
                await interaction.response.send_message("You have generated **5 numbers** already. Please re-run the command to continue.", ephemeral=True)
                self.stop()
    old_message = await message.channel.send(f"Your random number is **{random_number}**", view=CommandView())

async def execute_command(message, prefix):
    if message.author.id == variables.bot_owner:
        try:
            output_language = ""
            length = len(prefix+"execute ")
            if len(message.content) >= length:
                code = message.content[length:]
            else:
                await message.channel.send("No code specified")
                return
            if code.startswith("```python"):
                code = code[9:]
            if code.startswith("```py"):
                code = code[5:]
            if code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            code = code.replace("run_coroutine", "asyncio.run_coroutine_threadsafe")
            if "#python" in code:
                output_language = "py"
            if "#go" in code:
                output_language = "go"

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
                pager = CustomPager(
                    timeout=120, length=1, prefix=f"```{output_language}\n", suffix="```", color=variables.embed_color, title=f"Code Output ({len(segments)} pages)", entries=segments,
                )
                await pager.start(ContextObject(client, message))
            else:
                await message.channel.send(output)
        except Exception as error:
            if not "empty message" in str(error):
                await message.channel.send("`Error: " + str(error) + "`")
                await message.add_reaction("❌")
            else:
                await message.add_reaction("✅")
            return
    else:
        await message.add_reaction("🚫")

async def reload_command(message, prefix):
    if message.author.id == variables.bot_owner:
        embed = disnake.Embed(title="Reload", description=reload_data(), color=disnake.Color.green())
        await message.channel.send(embed=embed)
    else:
        await message.add_reaction("🚫")

async def disconnect_members_command(message, prefix):
    if message.author.guild_permissions.administrator or message.author.id in variables.permission_override:
        old_message = await message.channel.send("Disconnecting all members from voice channels...")
        add_cooldown(message.author.id, "disconnect-members", variables.large_number); members = 0; failed = 0

        for channel in message.guild.channels:
            if type(channel) == disnake.channel.voice_channel:
                for member in channel.members:
                    try:
                        await member.edit(voice_channel=None); members += 1
                    except:
                        failed += 1
        await old_message.edit(f"Successfully disconnected **{members}/{members + failed} {'member' if members == 1 else 'members'}** from voice channels")
    else:
        await message.channel.send(variables.no_permission_text)
    add_cooldown(message.author.id, "disconnect-members", 20)

async def suggest_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        add_cooldown(message.author.id, "suggest", variables.large_number)
        arguments.pop(0); text = " ".join(arguments)
        old_message = await message.channel.send("Sending your suggestion...")
        for user_iD in variables.message_managers:
            member = None
            for guild in client.guilds:
                try:
                    member = await guild.fetch_member(user_iD)
                    break
                except:
                    continue
            if member:
                try:
                    await member.send(f"**{message.author.name}#{message.author.discriminator}** **(**`{member.id}`**)** **has sent a suggestion:**\n{text}")
                except:
                    pass
        await old_message.edit("Your suggestion has been successfully sent")
    else:
        await message.channel.send(f"The syntax is `{prefix}suggest <text>`")
    add_cooldown(message.author.id, "suggest", 300)

async def autorole_command(message, prefix):
    if message.author.guild_permissions.administrator or message.author.id in variables.permission_override:
        message.content = message.content.replace("<", "").replace("@", "").replace("!", "").replace("&", "").replace(">", "")
        arguments = message.content.split(" ")
        if len(arguments) > 1:
            arguments.pop(0)
            role_list = arguments; role_found = False
            for role in message.guild.roles:
                for role_iD in role_list:
                    try:
                        if role.id == int(role_iD):
                            role_found = True
                            break
                    except:
                        await message.channel.send("That role is not found in this server")
                        return
            if not role_found:
                await message.channel.send("That role is not found in this server")
                return
            database[f"autorole.{message.guild.id}"] = role_list; role_string = ""
            for role in role_list:
                role_string += "<@&" + role + "> "
            await message.channel.send(embed=disnake.Embed(title="Autorole", description=f"This server's autorole has been set to {role_string}", color=variables.embed_color))
        else:
            try:
                role_list = database[f"autorole.{message.guild.id}"]; role_string = ""
                for role in role_list:
                    role_string += "<@&" + role + "> "
                await message.channel.send(embed=disnake.Embed(title="Autorole", description=f"This server's autorole is {role_string}", color=variables.embed_color))
            except:
                await message.channel.send(f"This server does not have autorole configured")
    else:
        await message.channel.send(variables.no_permission_text)
    add_cooldown(message.author.id, "autorole", 5)

async def shards_command(message, prefix):
    pages = {}; current_page = 1; page_limit = 20; current_item = 0; index = 1
    try:
        current_page = int(message.content.split(prefix + "shards ")[1])
    except:
        pass
    for shard in client.shards:
        current_server = ""
        shard_guilds = 0
        shard_members = 0
        for guild in client.guilds:
            if guild.shard_id == shard:
                shard_guilds += 1
                shard_members += guild.member_count
                if guild.id == message.guild.id:
                    current_server = "**"
        temporary_text = f"{current_server}Shard `{client.shards[shard].id}` - `{round(client.shards[shard].latency * 1000, 2)} ms` (`{shard_guilds}` guilds, `{shard_members}` members){current_server}\n"
        if index > page_limit:
            index = 0
            current_item += 1
        try:
            pages[current_item] += temporary_text
        except:
            pages[current_item] = f"Shard Count: `{len(client.shards)}`, Current Shard: `{message.guild.shard_id}`\n\n"
            pages[current_item] += temporary_text
        index += 1
    try:
        help_page = pages[current_page - 1]
    except:
        help_page = "That page doesn't exist"
        current_page = 0
    embed = disnake.Embed(title="Doge Shards", description=help_page, color=variables.embed_color, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f"Viewing shards page {current_page} of {len(pages)}")
    await message.channel.send(embed=embed)
    add_cooldown(message.author.id, "shards", 5)

async def lookup_command(message, prefix):
    user_iD = message.content.split(" ")
    if len(user_iD) != 2:
        user_iD.append(str(message.author.id))

    user_iD = user_iD[1]
    user_iD = user_iD.replace("<", ""); user_iD = user_iD.replace("@", "")
    user_iD = user_iD.replace("!", ""); user_iD = user_iD.replace(">", "")
    headers = {"Authorization": "Bot " + os.getenv("TOKEN")}
    url = "https://discord.com/api/users/" + user_iD
    response = requests.get(url, headers=headers).json()
    if "10013" not in str(response):
        try:
            response["public_flags"]
        except:
            await message.channel.send("Please enter a valid user ID"); return
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
        embed.add_field(name="Creation Time", value=f"<t:{round(((int(response['id']) >> 22) + 1420070400000) / 1000)}:R>")
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
    await message.channel.send(embed=embed)
    add_cooldown(message.author.id, "lookup", 6)

async def permissions_command(message, prefix):
    user_iD = message.content.split(" ")
    if len(user_iD) != 2:
        user_iD.append(str(message.author.id))
    user_iD = user_iD[1]
    user_iD = user_iD.replace("<", ""); user_iD = user_iD.replace("@", "")
    user_iD = user_iD.replace("!", ""); user_iD = user_iD.replace(">", "")
    
    target_user = None
    try:
        target_user = await message.guild.fetch_member(int(user_iD))
    except:
        pass
        if str(user.id) == user_iD:
            target_user = user
    if target_user == None:
        await message.channel.send("Unable to find user"); return
    
    permission_list = ""
    for permission in target_user.guild_permissions:
        if permission[1] == True:
            permission_list += f":white_check_mark: `{permission[0]}`\n"
        else:
            permission_list += f":x: `{permission[0]}`\n"
    if target_user == message.author.guild.owner:
        permission_list += f":white_check_mark: `owner`\n"
    else:
        permission_list += f":x: `owner`\n"

    embed = disnake.Embed(title="User Permissions", description=f"Permissions for **{target_user.name}#{target_user.discriminator}**\n\n" + permission_list, color=variables.embed_color)
    await message.channel.send(embed=embed)
    add_cooldown(message.author.id, "permissions", 3)

async def raid_protection_command(message, prefix):
    if message.author.guild_permissions.administrator or message.author.id in variables.permission_override:
        try:
            setting = message.content.split(prefix + "raid-protection ")[1]
        except:
            try:
                current_setting = database[f"{message.author.guild.id}.raid-protection"]
                if current_setting:
                    await message.channel.send("This server's raid protection is turned **on**")
                else:
                    await message.channel.send("This server's raid protection is turned **off**")
            except:
                await message.channel.send("This server's raid protection is turned **off**")
            return
        if setting.lower() == "on":
            database[f"{message.author.guild.id}.raid-protection"] = True
            await message.channel.send("This server's raid protection has been turned **on**")
            return
        elif setting.lower() == "off":
            database[f"{message.author.guild.id}.raid-protection"] = False
            await message.channel.send("This server's raid protection has been turned **off**")
            return
        else:
            await message.channel.send("Please specify a valid setting (on/off)")
            return
    else:
        await message.channel.send(variables.no_permission_text)

async def epoch_date_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); text = " ".join(arguments)
        try:
            date = functions.epoch_to_date(int(text)); embed = disnake.Embed(color=variables.embed_color)
            embed.add_field(name="Epoch", value="`" + text + "`"); embed.add_field(name="Date", value=date, inline=False)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Invalid timestamp"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}epoch-date <epoch>`")

async def date_epoch_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); text = " ".join(arguments)
        try:
            epoch = functions.date_to_epoch(text); embed = disnake.Embed(color=variables.embed_color)
            embed.add_field(name="Date", value=text); embed.add_field(name="Epoch", value="`" + str(epoch) + "`", inline=False)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Invalid date"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}date-epoch <date>`")

async def hash_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 2:
        arguments.pop(0); hash_type = arguments[0]; arguments.pop(0); text = " ".join(arguments)
        try:
            output_hash = hash_text(hash_type, text); embed = disnake.Embed(color=variables.embed_color)
            embed.add_field(name="Text", value=text); embed.add_field(name=f"Hash ({hash_type})", value="`" + output_hash + "`", inline=False)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Invalid hash type"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}hash <type> <text>`")
    add_cooldown(message.author.id, "hash", 5)

async def base64Command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 2:
        arguments.pop(0); action_type = arguments[0]; arguments.pop(0); text = " ".join(arguments)
        try:
            if action_type.lower() == "encode":
                output_code = base64.b64encode(text.encode("utf-8")).decode("utf-8")
                embed = disnake.Embed(color=variables.embed_color)
                embed.add_field(name="Text", value=text); embed.add_field(name="Base64", value="`" + output_code + "`", inline=False)
            elif action_type.lower() == "decode":
                output_text = base64.b64decode(text.encode("utf-8")).decode("utf-8")
                embed = disnake.Embed(color=variables.embed_color)
                embed.add_field(name="Base64", value="`" + text + "`"); embed.add_field(name="Text", value=output_text, inline=False)
            else:
                embed = disnake.Embed(title="Base64", description="Unknown action. Please use `encode` or `decode`.", color=variables.embed_color)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Unable to process command"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}base64 <action> <text>`")
    add_cooldown(message.author.id, "base64", 5)

async def binary_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 2:
        arguments.pop(0); action_type = arguments[0]; arguments.pop(0); text = " ".join(arguments)
        try:
            if action_type.lower() == "encode":
                output_code = ' '.join(format(ord(letter), '08b') for letter in text)
                embed = disnake.Embed(color=variables.embed_color)
                embed.add_field(name="Text", value=text); embed.add_field(name="Binary", value="`" + output_code + "`", inline=False)
            elif action_type.lower() == "decode":
                output_text = ""
                for letter in text.split():
                    number = int(letter, 2)
                    output_text += chr(number)
                embed = disnake.Embed(color=variables.embed_color)
                embed.add_field(name="Binary", value="`" + text + "`"); embed.add_field(name="Text", value=output_text, inline=False)
            else:
                embed = disnake.Embed(title="Binary", description="Unknown action. Please use `encode` or `decode`.", color=variables.embed_color)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Unable to process command"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}binary <action> <text>`")
    add_cooldown(message.author.id, "binary", 5)

async def calculate_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); expression = ' '.join(arguments)
        if expression.startswith("`"):
            expression = expression[1:]
        if expression.endswith("`"):
            expression = expression[:-1]
        answer = evaluate_expression(expression); embed = disnake.Embed(color=variables.embed_color)
        embed.add_field(name="Expression", value="`" + expression + "`"); embed.add_field(name="Result", value="`" + answer + "`", inline=False)
        await message.channel.send(embed=embed)
    else:
        await message.channel.send(f"The syntax is `{prefix}calculate <expression>`")
    add_cooldown(message.author.id, "calculate", 3)

async def clear_command(message, prefix):
    if message.author.guild_permissions.administrator or message.author.id in variables.permission_override:
        try:
            count = int(message.content.split(prefix + "clear ")[1])
        except:
            await message.channel.send("Please specify a valid number")
            return
        if count > 500:
            class CommandView(disnake.ui.View):
                def __init__(self):
                    super().__init__()

                @disnake.ui.button(label="Yes", style=disnake.ButtonStyle.green)
                async def confirm(self, _, interaction):
                    if interaction.author != message.author:
                        await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                        return

                    try:    
                        await message.channel.purge(limit=count + 1)
                    except:
                        await message.channel.send("Unable to delete messages")
                    await interaction.response.send_message(
                        content=f"Successfully deleted more than **500 messages** in this channel",
                        ephemeral=True,
                    )
                    self.stop()

                @disnake.ui.button(label="No", style=disnake.ButtonStyle.green)
                async def reject(self, _, interaction):
                    if interaction.author != message.author:
                        await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                        return

                    await old_message.edit(content=f"Operation cancelled", view=None)
                    self.stop()
                
            old_message = await message.channel.send(
                f"Are you sure you want to clear more than **500 messages** in this channel?",
                view=CommandView()
            )
    else:
        await message.channel.send(variables.no_permission_text)
    add_cooldown(message.author.id, "clear", 10)

async def wide_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); new_text = ""; text = " ".join(arguments)
        for letter in text:
            new_text += letter + " "
        await message.channel.send(new_text.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}wide <text>`")
    add_cooldown(message.author.id, "wide", 3)

async def unwide_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); new_text = ""; text = " ".join(arguments); space_character = False
        for letter in text.replace("   ", "  "):
            if letter == " ":
                if space_character:
                    new_text += " "
                space_character = True
            else:
                space_character = False
                new_text += letter
        await message.channel.send(new_text.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}unwide <text>`")
    add_cooldown(message.author.id, "unwide", 3)

async def spoiler_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); new_text = ""; text = " ".join(arguments)
        for letter in text:
            new_text += "||" + letter + "||"
        await message.channel.send(new_text.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}spoiler <text>`")
    add_cooldown(message.author.id, "spoiler", 3)

async def cringe_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); new_text = ""; text = " ".join(arguments)
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
        await message.channel.send(new_text.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}cringe <text>`")
    add_cooldown(message.author.id, "cringe", 3)

async def reverse_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); new_text = ""; text = " ".join(arguments)
        new_text = text[::-1]; await message.channel.send(new_text.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}reverse <text>`")
    add_cooldown(message.author.id, "reverse", 3)

async def corrupt_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); new_text = ""; text = " ".join(arguments)
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
        await message.channel.send(new_text.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}reverse <text>`")
    add_cooldown(message.author.id, "corrupt", 3)

async def color_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); text = " ".join(arguments)
        colors = functions.generate_color(text)
        if colors == 1:
            await message.channel.send("Invalid color code"); return
        else:
            hex_color = colors[0]; rgb_color = colors[1]
            embed = disnake.Embed(color=int("0x" + hex_color[1:], 16))
            embed.set_image(url="attachment://color.png")
            embed.add_field(name="Hex", value=hex_color)
            embed.add_field(name="RGB", value=str(rgb_color), inline=True)
        await message.channel.send(embed=embed, file=disnake.File("images/color.png"))
    else:
        await message.channel.send(f"The syntax is `{prefix}color <color code>`")
    add_cooldown(message.author.id, "color", 3)

async def vote_command(message, prefix):
    embed = disnake.Embed(title="Vote Link", description="You can upvote Doge Utilities on [top.gg](https://top.gg/bot/854965721805226005/vote), [discordbotlist](https://discordbotlist.com/bots/doge-utilities/upvote), or on [botsfordiscord](https://discords.com/bots/bot/854965721805226005/vote)", color=variables.embed_color)
    await message.channel.send(embed=embed)

async def time_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        try:
            arguments.pop(0); text = " ".join(arguments)
            if text.lower() == "list" or text.lower() == "help":
                output = ""
                for timezone in pytz.all_timezones:
                    output += timezone + "\n"
                segments = [output[i: i + 1000] for i in range(0, len(output), 1000)]
                pager = CustomPager(
                    timeout=60, color=variables.embed_color,
                    length=1, prefix="```\n", suffix="```",
                    title=f"Timezone List", entries=segments,
                )
                await pager.start(ContextObject(client, message))
            elif text.lower() == "epoch" or text.lower() == "unix":
                embed = disnake.Embed(title="Time", description=f"Current epoch time: **{round(time.time())}**", color=variables.embed_color)
                await message.channel.send(embed=embed)
            else:
                user_timezone = pytz.timezone(text.replace(" ", "_"))
                now = datetime.datetime.now(user_timezone)
                embed = disnake.Embed(title="Time", description=f"Information for **{text.replace(' ', '_')}**\n\nTime: **{str(now.time()).split('.')[0]}**\nDate: **{now.date()}**\nWeekday: **{variables.weekdays[now.weekday() + 1]}**", color=variables.embed_color)
                await message.channel.send(embed=embed)
        except KeyError:
            text = "_".join(arguments)
            for timezone in pytz.all_timezones:
                try:
                    city = timezone.split("/")[1]
                    if text.lower() == city.lower():
                        user_timezone = pytz.timezone(timezone); now = datetime.datetime.now(user_timezone)
                        embed = disnake.Embed(title="Time", description=f"Information for **{timezone}**\n\nTime: **{str(now.time()).split('.')[0]}**\nDate: **{now.date()}**\nWeekday: **{variables.weekdays[now.weekday() + 1]}**", color=variables.embed_color)
                        await message.channel.send(embed=embed); return
                except:
                    pass
            embed = disnake.Embed(title="Time", description=f"That timezone was not found", color=variables.embed_color)
            await message.channel.send(embed=embed); return
    else:
        await message.channel.send(f"The syntax is `{prefix}time <timezone>`")
    add_cooldown(message.author.id, "time", 3)

async def nickname_command(message, prefix):
    if message.author.guild_permissions.manage_nicknames or message.author.id in variables.permission_override:
        arguments = message.content.split(" ")
        if len(arguments) >= 3:
            arguments.pop(0); user_iD = arguments[0]; arguments.pop(0); nickname = ' '.join(arguments)
            try:
                user_iD = int(user_iD.replace("<", "").replace(">", "").replace("@", "").replace("!", ""))
                member = await message.guild.fetch_member(user_iD)
            except:
                await message.channel.send("Please mention a valid user!"); return
            try:
                await member.edit(nick=nickname); add_cooldown(message.author.id, "nickname", 5)
                await message.channel.send(f"Successfully updated **{member.name}#{member.discriminator}**'s nickname to **{nickname}**"); return
            except:
                await message.channel.send("Unable to change user nickname"); return
            await message.channel.send("Unable to find user"); return
        else:
            await message.channel.send(f"The syntax is `{prefix}nickname <user> <nickname>`")
    else:
        await message.channel.send(variables.no_permission_text)

async def stackoverflow_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        try:
            stackoverflow_parameters = {
                "order": "desc",
                "sort": "activity",
                "site": "stackoverflow"
            }
            arguments.pop(0); text = ' '.join(arguments)
            stackoverflow_parameters["q"] = text; parameters = stackoverflow_parameters
            response = requests.get(url="https://api.stackexchange.com/2.2/search/advanced", params=parameters).json()
            if not response["items"]:
                embed = disnake.Embed(title="StackOverflow", description=f"No search results found for **{text}**", color=disnake.Color.red())
                await message.channel.send(embed=embed); return
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
            await message.channel.send(embed=embed)
        except disnake.HTTPException:
            await message.channel.send("The search result is too long!"); return
        except:
            await message.channel.send("Unable to search for item"); return
        add_cooldown(message.author.id, "stackoverflow", 10)
    else:
        await message.channel.send(f"The syntax is `{prefix}stackoverflow <text>`")

async def source_command(message, prefix):
    description = "You can find my code [here](https://github.com/error_no_internet/Doge-Utilities)\n"
    response = requests.get("https://api.github.com/repos/error_no_internet/Doge-Utilities").json()
    description += f"Open Issues: **{response['open_issues']}**, Forks: **{response['forks']}**\nStargazers: **{response['stargazers_count']}**, Watchers: **{response['subscribers_count']}**"
    embed = disnake.Embed(title="Source Code", description=description, color=variables.embed_color)
    embed.set_thumbnail(url=client.user.avatar); await message.channel.send(embed=embed)
    add_cooldown(message.author.id, "source", 20)

async def uptime_command(message, prefix):
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
    await message.channel.send(embed=embed)

async def donate_command(message, prefix):
    embed = disnake.Embed(title="Donate", description=":moneybag: Bitcoin: `bc1qer5es59d62pvwdhaplgyltzd63kyyd0je2fhjm`\n:dog: Dogecoin: `D5Gy8ADPTbz_gLD3qvpv4Zk_nNr_pMNk_yX49j`", color=variables.embed_color)
    await message.channel.send(embed=embed)

async def doge_command(message, prefix):
    embed = disnake.Embed(color=variables.embed_color)
    embed.set_image(url=client.user.avatar); await message.channel.send(embed=embed)

async def guilds_command(message, prefix):
    if message.author.id == variables.bot_owner:
        await message.channel.send(str(len(client.guilds)))
    else:
        await message.add_reaction("🚫")

async def smiley_command(message, prefix):
    if prefix == "=" or prefix == ";":
        await message.channel.send(f"**{prefix}D**")

async def about_command(message, prefix):
    await message.channel.send(embed=disnake.Embed(title="About", description=f"I was created by **Zenderking** (`{variables.bot_owner}`/<@{variables.bot_owner}>)", color=variables.embed_color))

async def blacklist_command(message, prefix):
    if message.author.id == variables.bot_owner:
        arguments = message.content.split(" ")
        if len(arguments) >= 2:
            if arguments[1] == "list":
                blacklisted_users = []
                blacklist_file = open("blacklist.json", "r"); raw_array = json.load(blacklist_file); blacklist_file.close()
                for user in raw_array:
                    blacklisted_users.append(str(user))
                embed = disnake.Embed(title="Blacklisted Users", description="\n".join(blacklisted_users) if "\n".join(blacklisted_users) != "" else "There are no blacklisted users", color=variables.embed_color)
                await message.channel.send(embed=embed)
            if arguments[1] == "add":
                if len(arguments) == 3:
                    try:
                        user_iD = int(arguments[2].replace("<@", "").replace("!", "").replace(">", ""))
                    except:
                        await message.channel.send("Please enter a valid user ID"); return
                    blacklist_file = open("blacklist.json", "r")
                    blacklisted_users = json.load(blacklist_file); blacklist_file.close()
                    blacklisted_users.append(user_iD)
                    blacklist_file = open("blacklist.json", "w")
                    json.dump(blacklisted_users, blacklist_file)
                    blacklist_file.close()
                    await message.channel.send("Successfully added user to blacklist")
                else:
                    await message.channel.send(f"The syntax is `{prefix}blacklist <add/remove/list> <user>`"); return
            if arguments[1] == "remove":
                if len(arguments) == 3:
                    try:
                        user_iD = int(arguments[2].replace("<@", "").replace("!", "").replace(">", ""))
                    except:
                        await message.channel.send("Please enter a valid user ID"); return
                    blacklist_file = open("blacklist.json", "r")
                    blacklisted_users = json.load(blacklist_file)
                    blacklist_file.close()
                    try:
                        blacklisted_users.remove(user_iD)
                    except:
                        pass
                    blacklist_file = open("blacklist.json", "w")
                    json.dump(blacklisted_users, blacklist_file)
                    blacklist_file.close()
                    await message.channel.send("Successfully removed user from blacklist")
                else:
                    await message.channel.send(f"The syntax is `{prefix}blacklist <add/remove/list> <user>`"); return
        else:
            await message.channel.send(f"The syntax is `{prefix}blacklist <add/remove/list> <user>`"); return
    else:
        await message.add_reaction("🚫")

async def meme_command(message, prefix):
    response = requests.get("https://meme-api.herokuapp.com/gimme").json()
    description = f"Posted by **{response['author']}** in **{response['subreddit']}** (**{response['ups']}** upvotes)"
    embed = disnake.Embed(title=response["title"], url=response["post_link"], description=description, color=variables.embed_color)
    embed.set_image(url=response["url"]); add_cooldown(message.author.id, "meme", 5); await message.channel.send(embed=embed)

async def unmute_command(message, prefix):
    if message.author.guild_permissions.manage_roles or message.author.guild_permissions.administrator:
        pass
    else:
        await message.channel.send(variables.no_permission_text); return

    arguments = message.content.split(" ")
    if len(arguments) == 2:
        try:
            user_iD = int(arguments[1].replace("<@", "").replace(">", "").replace("!", ""))
            member = await message.guild.fetch_member(user_iD)
        except:
            await message.channel.send("Please enter a valid user ID"); return
        mute_role = None; exists = False
        for role in message.guild.roles:
            if "mute" in role.name.lower():
                mute_role = role; exists = True
        if exists:
            try:
                await member.remove_roles(mute_role)
            except:
                pass
        await message.channel.send(f"Successfully unmuted **{member}**")
    else:
        await message.channel.send(f"The syntax is `{prefix}unmute <user>`"); return

async def mute_command(message, prefix):
    if message.author.guild_permissions.manage_roles or message.author.guild_permissions.administrator or message.author.id in variables.permission_override:
        pass
    else:
        await message.channel.send(variables.no_permission_text); return

    arguments = message.content.split(" ")
    if len(arguments) >= 2:
        mute_role = None; exists = False
        for role in message.guild.roles:
            if "mute" in role.name.lower():
                mute_role = role; exists = True
        if not exists:
            await setup_muted_command(message, prefix)
        mute_role = None; exists = False
        for role in message.guild.roles:
            if "mute" in role.name.lower():
                mute_role = role; exists = True
        if not exists:
            await message.channel.send("Unable to find mute role"); return
        try:
            user_iD = int(arguments[1].replace("<@", "").replace(">", "").replace("!", ""))
            member = await message.guild.fetch_member(user_iD)
        except:
            await message.channel.send("Please enter a valid user ID"); return
    if len(arguments) == 2:
        try:
            await member.add_roles(mute_role)
        except:
            await message.channel.send(f"Unable to mute **{member}**"); return
        await message.channel.send(f"Successfully muted **{member}** permanently")
    elif len(arguments) == 3:
        try:
            duration = float(arguments[2])
        except:
            await message.channel.send("Please enter a valid duration (in minutes)"); return
        try:
            moderation_data = database["mute." + str(message.guild.id)]
        except:
            database["mute." + str(message.guild.id)] = []
            moderation_data = database["mute." + str(message.guild.id)]
        try:
            await member.add_roles(mute_role); moderation_data.append([user_iD, time.time(), duration])
            database["mute." + str(message.guild.id)] = moderation_data
        except:
            await message.channel.send(f"Unable to mute **{member}**"); return
        await message.channel.send(f"Successfully muted **{member}** for **{duration if round(duration) != 1 else round(duration)} {'minute' if round(duration) == 1 else 'minutes'}**")
    else:
        await message.channel.send(f"The syntax is `{prefix}mute <user> <duration>`"); return

async def insults_command(message, prefix):
    if message.author.guild_permissions.manage_messages:
        pass
    else:
        await message.channel.send(variables.no_permission_text); return

    arguments = message.content.split(" ")
    if len(arguments) >= 2:
        if arguments[1] == "list":
            try:
                insults_data = database[f"insults.list.{message.guild.id}"]
            except:
                insults_data = []
                database[f"insults.list.{message.guild.id}"] = []
            embed = disnake.Embed(title="Insults List", description="There are no swear words configured for your server" if insults_data == [] else '\n'.join(insults_data), color=variables.embed_color)
            await message.channel.send(embed=embed)
        elif arguments[1] == "filter" or arguments[1] == "status":
            try:
                current_status = database[f"insults.toggle.{message.guild.id}"]
            except:
                current_status = False
            await message.channel.send(f"The insults filter is currently **{'enabled' if current_status else 'disabled'}**")
        elif arguments[1] == "enable":
            database[f"insults.toggle.{message.guild.id}"] = True
            await message.channel.send("The insults filter has been successfully **enabled**")
        elif arguments[1] == "disable":
            database[f"insults.toggle.{message.guild.id}"] = False
            await message.channel.send("The insults filter has been successfully **disabled**")
        elif arguments[1] == "add":
            if len(arguments) != 3:
                await message.channel.send(f"The syntax is `{prefix}insults add <word>`"); return
            try:
                insults_data = database[f"insults.list.{message.guild.id}"]
            except:
                insults_data = []
                database[f"insults.list.{message.guild.id}"] = []
            if len(insults_data) >= 50:
                await message.channel.send("You have reached the limit of **50 words**"); return
            insults_data.append(arguments[2])
            database[f"insults.list.{message.guild.id}"] = insults_data
            await message.channel.send(f"Successfully added **{arguments[2]}** to your insults list")
        elif arguments[1] == "remove" or arguments[1] == "delete":
            if len(arguments) != 3:
                await message.channel.send(f"The syntax is `{prefix}insults remove <word>`"); return
            try:
                insults_data = database[f"insults.list.{message.guild.id}"]
            except:
                insults_data = []
                database[f"insults.list.{message.guild.id}"] = []
            try:
                insults_data.remove(arguments[2])
            except:
                await message.channel.send("That word does not exist in the insults filter"); return
            database[f"insults.list.{message.guild.id}"] = insults_data
            await message.channel.send(f"Successfully removed **{arguments[2]}** from the insults list")
    else:
        await message.channel.send(f"The syntax is `{prefix}insults <add/remove/enable/disable/list/status>`"); return

async def links_command(message, prefix):
    if not message.author.guild_permissions.administrator:
        await message.channel.send(variables.no_permission_text); return
        
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        if arguments[1] == "enable":
            database[f"links.toggle.{message.guild.id}"] = True
            await message.channel.send("The links filter has been successfully **enabled**")
        elif arguments[1] == "disable":
            database[f"links.toggle.{message.guild.id}"] = False
            await message.channel.send("The links filter has been successfully **disabled**")
        elif arguments[1] == "status" or arguments[1] == "filter":
            value = False
            try:
                value = database[f"links.toggle.{message.guild.id}"]
            except:
                pass
            await message.channel.send(f"The links filter is currently **{'enabled' if value else 'disabled'}**")
    else:
        await message.channel.send(f"The syntax is `{prefix}links <enable/disable/status>`"); return

async def spamming_command(message, prefix):
    if not message.author.guild_permissions.administrator:
        await message.channel.send(variables.no_permission_text); return
        
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        if arguments[1] == "enable":
            database[f"spamming.toggle.{message.guild.id}"] = True
            await message.channel.send("The spam filter has been successfully **enabled**")
        elif arguments[1] == "disable":
            database[f"spamming.toggle.{message.guild.id}"] = False
            await message.channel.send("The spam filter has been successfully **disabled**")
        elif arguments[1] == "set":
            if len(arguments) > 2:
                try:
                    limit = int(arguments[2])
                except:
                    await message.channel.send("Please enter a valid number!"); return
            database[f"spamming.limit.{message.guild.id}"] = limit
            await message.channel.send(f"The spam filter limit has been set to **{limit} {'message' if limit == 1 else 'messages'}** per **15 seconds**")
        elif arguments[1] == "status" or arguments[1] == "filter" or arguments[1] == "limit":
            value = False
            try:
                value = database[f"spamming.toggle.{message.guild.id}"]
            except:
                pass
            limit = 6
            try:
                limit = database[f"spamming.limit.{message.guild.id}"]
            except:
                pass
            await message.channel.send(f"The spam filter is currently **{'enabled' if value else 'disabled'}** (limit is **{limit}**)")
    else:
        await message.channel.send(f"The syntax is `{prefix}spamming <enable/disable/set/status>`"); return

async def welcome_command(message, prefix):
    if not message.author.guild_permissions.administrator:
        await message.channel.send(variables.no_permission_text); return
        
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        if arguments[1] == "enable":
            try:
                database[f"welcome.text.{message.guild.id}"]
            except:
                await message.channel.send(f"Please set a welcome message with `{prefix}welcome set <text>` first"); return
            try:
                channel_iD = database[f"welcome.channel.{message.guild.id}"]
                found = False
                for channel in message.guild.channels:
                    if channel.id == channel_iD:
                        found = True
                if not found:
                    raise Exception("unable to find channel")
            except:
                await message.channel.send(f"Please set a welcome channel with `{prefix}welcome channel <channel>` first"); return

            database[f"welcome.toggle.{message.guild.id}"] = True
            await message.channel.send("Welcome messages have been successfully **enabled**")
        elif arguments[1] == "disable":
            database[f"welcome.toggle.{message.guild.id}"] = False
            await message.channel.send("Welcome messages have been successfully **disabled**")
        elif arguments[1] == "set" or arguments[1] == "text":
            text = ""
            if len(arguments) > 2:
                for i in range(2):
                    arguments.pop(0)
                text = ' '.join(arguments)
            else:
                await message.channel.send(f"The syntax is `{prefix}welcome set <text>`"); return
            database[f"welcome.text.{message.guild.id}"] = text
            await message.channel.send(f"The welcome message has been set to\n```\n{text}```\n" + "Variables like `{user}`, `{user_iD}`, `{discriminator}`, and `{members}` are also supported")
        elif arguments[1] == "channel":
            channel_iD = 0
            if len(arguments) > 2:
                try:
                    channel_iD = int(arguments[2].replace("<#", "").replace("!", "").replace(">", ""))
                except:
                    await message.channel.send("That channel does not exist in this server"); return
            else:
                await message.channel.send(f"The syntax is `{prefix}welcome channel <channel>`"); return
            database[f"welcome.channel.{message.guild.id}"] = channel_iD
            await message.channel.send(f"The welcome channel for this server has been set to <#{channel_iD}>")
        elif arguments[1] == "status" or arguments[1] == "filter" or arguments[1] == "limit":
            value = False
            try:
                value = database[f"welcome.toggle.{message.guild.id}"]
            except:
                pass
            text = "There is nothing here..."
            try:
                text = database[f"welcome.text.{message.guild.id}"]
            except:
                pass
            channel_iD = "**#unknown-channel**"
            try:
                channel_iD = "<#" + str(database[f"welcome.channel.{message.guild.id}"]) + ">"
            except:
                pass
            await message.channel.send(f"Welcome messages are currently **{'enabled' if value else 'disabled'}** and set to {channel_iD}\n```\n{text}```")
    else:
        await message.channel.send(f"The syntax is `{prefix}welcome <enable/disable/channel/set/status>`"); return

async def leave_command(message, prefix):
    if not message.author.guild_permissions.administrator:
        await message.channel.send(variables.no_permission_text); return
        
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        if arguments[1] == "enable":
            try:
                database[f"leave.text.{message.guild.id}"]
            except:
                await message.channel.send(f"Please set a leave message with `{prefix}leave set <text>` first"); return
            try:
                channel_iD = database[f"leave.channel.{message.guild.id}"]
                found = False
                for channel in message.guild.channels:
                    if channel.id == channel_iD:
                        found = True
                if not found:
                    raise Exception("unable to find channel")
            except:
                await message.channel.send(f"Please set a leave channel with `{prefix}leave channel <channel>` first"); return

            database[f"leave.toggle.{message.guild.id}"] = True
            await message.channel.send("Leave messages have been successfully **enabled**")
        elif arguments[1] == "disable":
            database[f"leave.toggle.{message.guild.id}"] = False
            await message.channel.send("Leave messages have been successfully **disabled**")
        elif arguments[1] == "set" or arguments[1] == "text":
            text = ""
            if len(arguments) > 2:
                for i in range(2):
                    arguments.pop(0)
                text = ' '.join(arguments)
            else:
                await message.channel.send(f"The syntax is `{prefix}leave set <text>`"); return
            database[f"leave.text.{message.guild.id}"] = text
            await message.channel.send(f"The leave message has been set to\n```\n{text}```\n" + "Variables like `{user}`, `{user_iD}`, `{discriminator}`, and `{members}` are also supported")
        elif arguments[1] == "channel":
            channel_iD = 0
            if len(arguments) > 2:
                try:
                    channel_iD = int(arguments[2].replace("<#", "").replace("!", "").replace(">", ""))
                except:
                    await message.channel.send("That channel does not exist in this server"); return
            else:
                await message.channel.send(f"The syntax is `{prefix}leave channel <channel>`"); return
            database[f"leave.channel.{message.guild.id}"] = channel_iD
            await message.channel.send(f"The leave channel for this server has been set to <#{channel_iD}>")
        elif arguments[1] == "status" or arguments[1] == "filter" or arguments[1] == "limit":
            value = False
            try:
                value = database[f"leave.toggle.{message.guild.id}"]
            except:
                pass
            text = "There is nothing here..."
            try:
                text = database[f"leave.text.{message.guild.id}"]
            except:
                pass
            channel_iD = "**#unknown-channel**"
            try:
                channel_iD = "<#" + str(database[f"leave.channel.{message.guild.id}"]) + ">"
            except:
                pass
            await message.channel.send(f"Leave messages are currently **{'enabled' if value else 'disabled'}** and set to {channel_iD}\n```\n{text}```")
    else:
        await message.channel.send(f"The syntax is `{prefix}leave <enable/disable/channel/set/status>`"); return

async def snipe_command(message, prefix):
    add_cooldown(message.author.id, "snipe", 1)
    arguments = message.content.split(" ")
    if len(arguments) == 1:
        try:
            random_message = random.choice(snipe_list[message.guild.id])
            message_author = random_message[0]
            message_author_avatar = random_message[1]; channel_name = random_message[2]
            message_sent_time = random_message[3]; message_data = random_message[4]
            embed = disnake.Embed(description=message_data, color=variables.embed_color, timestamp=message_sent_time)
            embed.set_author(name=message_author, icon_url=message_author_avatar); embed.set_footer(text=f"Sent in #{channel_name}")
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("There is nothing to snipe!")
    elif len(arguments) > 1:
        if arguments[1] == "enable":
            if not message.author.guild_permissions.administrator:
                await message.channel.send(variables.no_permission_text); return

            database[f"snipe.{message.guild.id}"] = True
            await message.channel.send("Snipe has been **enabled** for this server")
        elif arguments[1] == "disable":
            if not message.author.guild_permissions.administrator:
                await message.channel.send(variables.no_permission_text); return

            database[f"snipe.{message.guild.id}"] = False
            await message.channel.send("Snipe has been **disabled** for this server")
        elif arguments[1] == "clear":
            if not message.author.guild_permissions.administrator:
                await message.channel.send(variables.no_permission_text); return

            snipe_list[message.guild.id] = []
            await message.channel.send("The snipe list for this server has been successfully cleared")
        elif arguments[1] == "status":
            value = False
            try:
                value = database[f"snipe.{message.guild.id}"]
            except:
                pass
            await message.channel.send(f"Snipe is currently **{'enabled' if value else 'disabled'}** for this server")

async def joke_command(message, prefix):
    add_cooldown(message.author.id, "joke", 3)
    response = requests.get("http://random-joke-api.herokuapp.com/random").json()
    embed = disnake.Embed(description=f"Here's a `{response['type']}` joke:\n{response['setup']} **{response['punchline']}**", color=variables.embed_color)
    await message.channel.send(embed=embed)

async def members_command(message, prefix):
    users = 0; bots = 0
    for member in message.guild.members:
        if member.bot:
            bots += 1
        else:
            users += 1
    embed = disnake.Embed(
        title="Guild Members",
        description=f"User accounts: **{users}**\nBot accounts: **{bots}**\nTotal members: **{users + bots}**",
        color=variables.embed_color
    )
    await message.channel.send(embed=embed)

async def github_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) == 2:
        try:
            arguments[1] = arguments[1].split("github.com/")[1]
        except:
            pass
        response = requests.get(f"https://api.github.com/repos/{arguments[1]}").json()
        try:
            if response["message"] == "Not Found":
                await message.channel.send("That GitHub repository was not found"); return
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
        await message.channel.send(embed=embed)
        add_cooldown(message.author.id, "github", 5)
    else:
        await message.channel.send(f"The syntax is `{prefix}github <repository>`")

async def choose_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) >= 2:
        arguments.pop(0)
        random_item = random.choice(' '.join(arguments).replace(", ", ",").split(","))
        await message.channel.send(f"I choose **{random_item}**")
    else:
        await message.channel.send(f"The syntax is `{prefix}choose <item>, <item>`")

async def trivia_command(message, prefix):
    add_cooldown(message.author.id, "trivia", 10)
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
            for button in old_message.components[0].children:
                style = disnake.ButtonStyle.red
                if chosen_answer == button.label:
                    style = disnake.ButtonStyle.blurple
                if correct_answer == button.label:
                    style = disnake.ButtonStyle.green
                new_view.add_item(disnake.ui.Button(label=button.label, style=style, disabled=True))
            await old_message.edit(view=new_view)
            self.stop()
        
        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_1(self, button, interaction):
            if interaction.author != message.author:
                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if button.label == correct_answer:
                await interaction.response.send_message("Correct answer!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Wrong answer... The correct answer was **{correct_answer}**.", ephemeral=True)
            await self.close(button.label)

        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_2(self, button, interaction):
            if interaction.author != message.author:
                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if button.label == correct_answer:
                await interaction.response.send_message("Correct answer!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Wrong answer... The correct answer was **{correct_answer}**.", ephemeral=True)
            await self.close(button.label)

        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_3(self, button, interaction):
            if interaction.author != message.author:
                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if button.label == correct_answer:
                await interaction.response.send_message("Correct answer!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Wrong answer... The correct answer was **{correct_answer}**.", ephemeral=True)
            await self.close(button.label)

        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_4(self, button, interaction):
            if interaction.author != message.author:
                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                return

            if button.label == correct_answer:
                await interaction.response.send_message("Correct answer!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Wrong answer... The correct answer was **{correct_answer}**.", ephemeral=True)
            await self.close(button.label)

    embed = disnake.Embed(
        description=description,
        color=variables.embed_color,
    )
    old_message = await message.channel.send(embed=embed, view=CommandView())

async def pypi_command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) == 2:
        response = requests.get(f"https://pypi.org/pypi/{arguments[1]}/json/")
        if response.status_code == 404:
            await message.channel.send("That package was not found")
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
        await message.channel.send(embed=embed)
        add_cooldown(message.author.id, "pypi", 5)
    else:
        await message.channel.send(f"The syntax is `{prefix}pypi <project>`")
        return

async def discriminator_command(message, prefix):
    arguments = message.content.split(" ")
    discriminator = message.author.discriminator
    members = []
    if len(arguments) > 1:
        arguments[1] = arguments[1].replace("#", "")
        try:
            int(arguments[1])
            if len(arguments[1]) != 4:
                raise Exception("invalid discriminator")
        except:
            await message.channel.send("That is not a valid discriminator!")
            return
        discriminator = arguments[1]

    for member in client.get_all_members():
        if member.discriminator == discriminator:
            if str(member) not in members:
                members.append(str(member))
    new_line = "\n"
    if members == []:
        await message.channel.send("There are no other users with the same discriminator")
        return

    output = "\n".join(members)
    segments = [output[i: i + 1000] for i in range(0, len(output), 1000)]
    pager = CustomPager(
        timeout=60, length=1, prefix=f"```\n", suffix="```", color=variables.embed_color, title="Discriminator", entries=segments,
    )
    await pager.start(ContextObject(client, message))
    add_cooldown(message.author.id, "discriminator", 5)

async def help_command(message, prefix):
    pages = {}; current_page = 1; page_limit = 12; current_item = 0; index = 1; page_arguments = False
    try:
        current_page = int(message.content.split(" ")[1])
        page_arguments = True
    except:
        try:
            current_page = message.content.split(" ")[1]
        except:
            page_arguments = True
            pass
    if page_arguments:
        for command in command_list:
            if command.name in hidden_commands:
                continue
            temporary_text = f"`{prefix}{command.usage}` - {command.description}\n"
            if index > page_limit:
                index = 0
                current_item += 1
            try:
                pages[current_item] += temporary_text
            except:
                pages[current_item] = temporary_text
            index += 1
        try:
            help_page = pages[current_page - 1]
        except:
            help_page = "That page doesn't exist or wasn't found"
            current_page = 0
        embed = disnake.Embed(title="Doge Commands", description=help_page, color=variables.embed_color, timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"Viewing help page {current_page} of {len(pages)}")
        await message.channel.send(embed=embed); add_cooldown(message.author.id, "help", 1.5)
    else:
        for command in command_list:
            if command.name in hidden_commands:
                continue
            if command.name == current_page:
                command_arguments = command.usage.split(" "); command_arguments.pop(0)
                command_arguments = ' '.join(command_arguments)
                if command_arguments == "":
                    command_arguments = "None"
                command_example = prefix + parse_variables(command.usage)
                additional_arguments = ""
                if command_arguments != "None":
                    additional_arguments = f"\nAdditional arguments: `{command_arguments}`"
                command = f"Command: `{prefix}{command.name}`{additional_arguments}\nUsage example: `{command_example}`\n\n**{command.description}**"
                embed = disnake.Embed(title="Doge Commands", description=command, color=variables.embed_color, timestamp=datetime.datetime.utcnow())
                embed.set_footer(text=f"Viewing command help page")
                await message.channel.send(embed=embed); return
        embed = disnake.Embed(title="Doge Commands", description="That command doesn't exist or wasn't found", color=variables.embed_color, timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"Viewing command help page")
        await message.channel.send(embed=embed); add_cooldown(message.author.id, "help", 1.5)

def epoch_to_date(epoch):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(epoch))

def date_to_epoch(timestamp):
    timestamp = timestamp.replace("Today", str(datetime.datetime.utcnow().date()))
    timestamp = timestamp.replace("/", "-")
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

def evaluate_expression(expression):
    expression = expression.replace("^", "**")

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

async def send_user_message(user_iD, message):
    for guild in client.guilds:
        try:
            member = await guild.fetch_member(int(user_iD))
            await member.send(message); return
        except:
            continue

async def on_member_join(member):
    try:
        autoroles = database[f"autorole.{member.guild.id}"]
        for role in member.guild.roles:
            for role_iD in autoroles:
                if int(role_iD) == role.id:
                    await member.add_roles(role)
    except:
        pass
    try:
        if database[f"welcome.toggle.{member.guild.id}"]:
            welcome_message = database[f"welcome.text.{member.guild.id}"]
            welcome_channel = database[f"welcome.channel.{member.guild.id}"]
            for channel in member.guild.channels:
                if welcome_channel == channel.id:
                    welcome_message = welcome_message.replace("{user}", member.name)
                    welcome_message = welcome_message.replace("{user_iD}", str(member.id))
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
        if database[f"leave.toggle.{member.guild.id}"]:
            leave_message = database[f"leave.text.{member.guild.id}"]
            leave_channel = database[f"leave.channel.{member.guild.id}"]
            for channel in member.guild.channels:
                if leave_channel == channel.id:
                    leave_message = leave_message.replace("{user}", member.name)
                    leave_message = leave_message.replace("{user_iD}", str(member.id))
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
                    embed = disnake.Embed(
                        title="Hello there",
                        color=variables.embed_color,
                        description="Thank you for inviting me to your server! My name is **Doge Utilities**, and I am a Discord utility bot that can help you with all sorts of tasks. My default prefix is `=`, if you would like to change this, simply type `=prefix <new prefix>` and click the \"Yes\" button. To see the help page (or list of commands), type `=help`. I have a **lot** of commands, so you might have to do `=help 2` or `=help 3` to see more commands that can't fit on a single page. Some of the most used tools that I have are `=raid-protection`, `=setup-muted`, `=setup-banned`, `=autorole`, `=lookup`, `=mute`, `=color`, `=permissions`, and `=insults`. Feel free to try them out! If you have issues or need help with a few commands, please join the [official support server](https://discord.gg/3Tp7R8FUs_c). Once again, thank you for inviting Doge Utilities!"
                    )
                    await entry.user.send(embed=embed)
                    break
    except:
        pass

async def on_message_delete(message, *arguments):
    if len(arguments) > 0:
        await on_message(arguments[0])
        if message.author.bot:
            return
    
    if not message.guild:
        return

    value = True
    try:
        value = database[f"snipe.{message.guild.id}"]
    except:
        pass
    if not value:
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
            datetime.datetime.utcnow(),
            message_data,
        ])
        snipe_list[message.guild.id] = snipes

async def on_message(message):
    try:
        if message.author.bot:
            return

        if message.guild:
            prefix = "="
            try:
                prefix = database[f"prefix.{message.guild.id}"]
            except:
                database[f"prefix.{message.guild.id}"] = "="
        else:
            return

        if message.content == f"<@{client.user.id}>" or message.content == f"<@!{client.user.id}>":
            await message.channel.send(f"My prefix here is `{prefix}`")
            last_command = open("last-command", "w")
            last_command.write(str(round(time.time()))); last_command.close()
            return

        if not message.author.guild_permissions.administrator:
            if message.author.id not in variables.permission_override:
                try:
                    if database[f"insults.toggle.{message.guild.id}"]:
                        insults = database[f"insults.list.{message.guild.id}"]
                        for word in insults:
                            if word.lower() in message.content.lower():
                                await message.delete()
                                await message.author.send(f"Please do not use that word (**{word.lower()}**)!")
                                return
                except:
                    pass
                try:
                    if database[f"links.toggle.{message.guild.id}"]:
                        link_regexes = ["http://", "https://", "www.", "discord.gg/"]
                        for regex in link_regexes:
                            if regex in message.content.lower():
                                await message.delete()
                                await message.author.send("Please do not put links in your message!")
                                return
                except:
                    pass
                try:
                    if "spam" not in message.channel.name:
                        if database[f"spamming.toggle.{message.guild.id}"]:
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
                                    strike_limit = database[f"spamming.limit.{message.guild.id}"]
                                except:
                                    pass
                                if strike_limit > 30:
                                    strike_limit = 30
                                if strikes >= strike_limit:
                                    await message.delete()
                                    await message.author.send("Stop spamming!")
                                    return
                except:
                    pass
        last_messages[message.author.id] = time.time()

        if message.content.startswith(prefix) and len(message.content) > 1:
            last_command = open("last-command", "w")
            last_command.write(str(round(time.time()))); last_command.close()
        else:
            return

        for command in command_list:
            call_command = False
            if len(command.aliases) > 0:
                for alias in command.aliases:
                    if " " not in message.content:
                        if message.content == f"{prefix}{alias}":
                            message.content = f"{prefix}{command.name}"
                    else:
                        message.content = message.content.replace(f"{prefix}{alias} ", f"{prefix}{command.name} ")
            if message.content.startswith(prefix + command.name):
                call_command = True

            if call_command:
                blacklist_file = open("blacklist.json", "r")
                blacklisted_users = json.load(blacklist_file)
                blacklist_file.close()
                if message.author.id in blacklisted_users:
                    await message.reply("You are banned from using Doge Utilities"); return

                await message.channel.trigger_typing()
                if get_cooldown(message.author.id, command.name) > 0:
                    cooldown_string = generate_cooldown(command.name, get_cooldown(message.author.id, command.name))
                    embed = disnake.Embed(title="Command Cooldown", description=cooldown_string, color=variables.embed_color)
                    await message.channel.send(embed=embed); return
                await command.function(message, prefix); return
    except disnake.errors.Forbidden:
        await message.author.send("I do not have the required permissions!")
    except disnake.errors.InteractionResponded:
        await message.channel.send("That interaction is already used!")
    except Exception as error:
        if "50035" in str(error):
            await message.channel.send("Message too long to be sent!"); return

        escaped_character = '\`'
        for user_iD in variables.message_managers:
            member = None
            for guild in client.guilds:
                try:
                    member = await guild.fetch_member(user_iD)
                    break
                except:
                    continue
            if member:
                try:
                    await member.send(f"**{message.author.name}#{message.author.discriminator}** (**`{message.author.id}`**) has ran into an error in **{message.author.guild.name}** (**`{message.author.guild.id}`**):\n\n**Message:**\n```\n{message.content.replace('`', escaped_character)}\n```**Error:**\n```\n{str(''.join(traceback.format_exception(error, error, error.__traceback__))).replace('`', escaped_character)}\n```")
                except:
                    pass

        embed = disnake.Embed(title="Bot Error", description=f"Uh oh! Doge Utilities has ran into an error!\nThis error has been sent to our bot creators.\n```\n{error}\n```", color=disnake.Color.red(), timestamp=datetime.datetime.utcnow())
        embed.set_footer(text="Doge Utilities error report"); await message.reply(embed=embed); return "error"

hidden_commands = ["execute", "reload", "guilds", "D", "blacklist", "about"]
command_list = [
    Command("D", [], smiley_command, "D", "=D"),
    Command("about", ["owner"], about_command, "about", "System Command"),
    Command("execute", [], execute_command, "execute <code>", "System Command"),
    Command("reload", [], reload_command, "reload", "System Command"),
    Command("guilds", ["servers"], guilds_command, "guilds", "System Command"),
    Command("blacklist", [], blacklist_command, "blacklist <add/remove/list>", "System Command"),
    Command("help", ["h", "commands"], help_command, "help", "Displays a help page for Doge Utilities"),
    Command("ping", ["pong"], ping_command, "ping", "Display the bot's current latency"),
    Command("status", ["stats"], status_command, "status", "Show the bot's current statistics"),
    Command("support", ["report"], support_command, "support", "Display the official Discord server for Doge"),
    Command("tests", [], tests_command, "tests", "Run a series of tests to diagnose Doge"),
    Command("source", ["src"], source_command, "source", "Display a link to Doge Utilities' code"),
    Command("uptime", [], uptime_command, "uptime", "Display Doge Utilities' current uptime"),
    Command("vote", ["upvote"], vote_command, "vote", "Display a link to upvote Doge Utilities"),
    Command("donate", [], donate_command, "donate", "Donate to the creators of Doge Utilities"),
    Command("version", ["ver"], version_command, "version", "Display the bot's current version"),
    Command("prefix", ["setprefix", "changeprefix"], prefix_command, "prefix", "Change the bot's prefix on this server"),
    Command("invite", ["inv"], invite_command, "invite", "Invite this bot to another server"),
    Command("doge", ["dog"], doge_command, "doge", "D O G E"),
    Command("shards", [], shards_command, "shards <page>", "View information about Doge's shards"),
    Command("setup-muted", [], setup_muted_command, "setup-muted", "Generate a role that mutes members"),
    Command("setup-banned", [], setup_banned_command, "setup-banned", "Generate a role that disables access to channels"),
    Command("random", ["rand"], random_command, "random <low> <high>", "Generate a random number within the range"),
    Command("disconnect-members", ["disconnect-users"], disconnect_members_command, "disconnect-members", "Disconnect all the members in voice channels"),
    Command("suggest", [], suggest_command, "suggest <suggestion>", "Send a suggestion to the bot creators"),
    Command("autorole", [], autorole_command, "autorole <role>", "Change the role that is automatically given to users"),
    Command("lookup", ["ui", "userinfo"], lookup_command, "lookup <user>", "Display profile information for the specified user"),
    Command("clear", ["purge"], clear_command, "clear <messages>", "Delete the specified amount of messages"),
    Command("raid-protection", ["raidp"], raid_protection_command, "raid-protection <on/off>", "Toggle server's raid protection"),
    Command("wide", [], wide_command, "wide <text>", "Add spaces to every character in the text"),
    Command("unwide", [], unwide_command, "unwide <text>", "Remove spaces from every character in the text"),
    Command("cringe", [], cringe_command, "cringe <text>", "Randomly change the cases of the text"),
    Command("spoiler", [], spoiler_command, "spoiler <text>", "Add spoilers to every character in the text"),
    Command("reverse", [], reverse_command, "reverse <text>", "Reverse the specified text (last character first)"),
    Command("corrupt", [], corrupt_command, "corrupt <text>", "Make the specified text appear to be corrupted"),
    Command("epoch-date", ["unix-date"], epoch_date_command, "epoch-date <epoch>", "Convert an epoch timestamp into a date"),
    Command("base64", ["b64"], base64Command, "base64 <encode/decode> <text>", "Convert the text to/from base64"),
    Command("date-epoch", ["date-unix"], date_epoch_command, "date-epoch <date>", "Covert a date into an epoch timestamp"),
    Command("hash", [], hash_command, "hash <type> <text>", "Hash the text object with the specified type"),
    Command("meme", [], meme_command, "meme", "Search for a meme on Reddit and display it in an embed"),
    Command("snipe", [], snipe_command, "snipe <enable/disable>", "Restore and bring deleted messages back to life"),
    Command("calculate", ["calc"], calculate_command, "calculate <expression>", "Calculate the specified math expression"),
    Command("color", ["colour"], color_command, "color <color code>", "Display information about the color code"),
    Command("permissions", ["perms"], permissions_command, "permissions <user>", "Display the permissions for the specified user"),
    Command("time", ["date"], time_command, "time <timezone>", "Display the current time for the specified timezone"),
    Command("binary", ["bin"], binary_command, "binary <encode/decode> <text>", "Convert the text to/from binary"),
    Command("nickname", ["nick"], nickname_command, "nickname <user> <nickname>", "Change or update a user's nickname"),
    Command("currency", ["cur"], currency_command, "currency <amount> <currency> <currency>", "Convert currencies"),
    Command("stackoverflow", ["so"], stackoverflow_command, "stackoverflow <text>", "Search for code help on StackOverflow"),
    Command("mute", [], mute_command, "mute <user> <minutes>", "Mute the specified member for the specified duration"),
    Command("unmute", [], unmute_command, "unmute <user>", "Unmute the specified member on the current guild"),
    Command("github", ["gh", "repo", "git"], github_command, "github <repository>", "Display information about a GitHub repository"),
    Command("insults", [], insults_command, "insults <add/remove/enable/disable/list>", "Modify the insults filter"),
    Command("links", [], links_command, "links <enable/disable>", "Enable or disable the link/advertisement filter"),
    Command("spam", [], spamming_command, "spamming <enable/disable/set>", "Enable or disable the spam filter"),
    Command("welcome", [], welcome_command, "welcome <enable/disable/channel/set>", "Modify the welcome messages"),
    Command("leave", [], leave_command, "leave <enable/disable/channel/set>", "Modify the leave messages"),
    Command("choose", [], choose_command, "choose <item>, <item>", "Choose a random item from the specified list"),
    Command("pypi", ["pip"], pypi_command, "pypi <project>", "Display information about a package on PyPi"),
    Command("discriminator", ["discrim"], discriminator_command, "discriminator", "Display other users with the same discriminator"),
    Command("joke", ["dadjoke"], joke_command, "joke", "Display a funny random joke from a random category"),
    Command("members", ["users"], members_command, "members", "Display information about this guild's members"),
    Command("trivia", ["quiz"], trivia_command, "trivia", "Display a random trivia question from a random category"),
]
