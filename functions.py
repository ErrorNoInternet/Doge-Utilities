if __name__ == "__main__":
    exit()

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
import discord
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
import discord_components
from dateutil import parser
from discord.ext import buttons

if not os.path.exists("databases"):
    os.mkdir("databases")
userCooldowns = {}; messageStrikes = {}; lastMessages = {}
prefixDatabase = sqlitedict.SqliteDict("databases/prefixDatabase.sql", autocommit=True)
autoroleDatabase = sqlitedict.SqliteDict("databases/autoroleDatabase.sql", autocommit=True)
settingsDatabase = sqlitedict.SqliteDict("databases/settingsDatabase.sql", autocommit=True)
moderationDatabase = sqlitedict.SqliteDict("databases/moderationDatabase.sql", autocommit=True)

class Command(object):
    def __init__(self, name, aliases, function, usage, description):
        super().__init__()
        
        self.name = name
        self.aliases = aliases
        self.function = function
        self.usage = usage
        self.description = description

class ContextObject(object):
    def __init__(self, client, message):
        super().__init__()

        self.bot = client
        self.message = message
        self.author = message.author
        self.guild = message.guild
        self.send = message.channel.send

class CustomPager(buttons.Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

def resetStrikes():
    global messageStrikes
    while True:
        time.sleep(15)
        messageStrikes = {}

async def manageMutedMembers():
    await asyncio.sleep(10)
    while True:
        try:
            for key in moderationDatabase.keys():
                if key.startswith("mute."):
                    for value in moderationDatabase[key]:
                        try:
                            guildID = int(key.split(".")[1])
                            userID = int(value[0])
                            muteStart = float(value[1])
                            duration = float(value[2])
                        except:
                            moderationData = moderationDatabase[key]
                            moderationData.remove(value)
                            moderationDatabase[key] = moderationData
                        if (time.time() / 60) > ((muteStart / 60) + duration):
                            try:
                                muteRole = None; targetGuild = None
                                for guild in client.guilds:
                                    if guild.id == guildID:
                                        targetGuild = guild
                                member = await targetGuild.fetch_member(userID)
                                for role in targetGuild.roles:
                                    if "mute" in role.name.lower():
                                        muteRole = role
                                if muteRole:
                                    try:
                                        await member.remove_roles(muteRole)
                                    except:
                                        pass
                                    moderationData = moderationDatabase[key]
                                    moderationData.remove(value)
                                    moderationDatabase[key] = moderationData
                            except:
                                moderationData = moderationDatabase[key]
                                moderationData.remove(value)
                                moderationDatabase[key] = moderationData
        except Exception as error:
            print(f"Fatal error in manageMutedMembers: {error}")
            try:
                moderationData = moderationDatabase[key]
                moderationData.remove(value)
                moderationDatabase[key] = moderationData
            except:
                pass
        await asyncio.sleep(10)

try:
    startTime
except:
    startTime = time.time()
    lastCommand = time.time(); mathVariables = {}
    requiredIntents = discord.Intents.default()
    requiredIntents.members = True
    client = discord.AutoShardedClient(
        shard_count=variables.shardCount,
        intents=requiredIntents,
    )
    client.max_messages = 512; snipeList = {}
    threading.Thread(target=asyncio.run_coroutine_threadsafe, args=(manageMutedMembers(), client.loop, )).start()
    threading.Thread(target=resetStrikes).start()

async def selectStatus():
    clientStatus = discord.Status.online; statusType = random.choice(variables.statusTypes)
    if statusType == "Playing":
        statusText = random.choice(variables.status1)
        await client.change_presence(status=clientStatus, activity=discord.Activity(type=discord.ActivityType.playing, name=statusText))
    elif statusType == "Watching":
        statusText = random.choice(variables.status2)
        await client.change_presence(status=clientStatus, activity=discord.Activity(type=discord.ActivityType.watching, name=statusText))
    elif statusType == "Listening":
        statusText = random.choice(variables.status3)
        await client.change_presence(status=clientStatus, activity=discord.Activity(type=discord.ActivityType.listening, name=statusText))
    elif statusType == "Competing":
        statusText = random.choice(variables.status4)
        await client.change_presence(status=clientStatus, activity=discord.Activity(type=discord.ActivityType.competing, name=statusText))

def parseVariables(text):
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
    return text

def reloadData():
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
        discord,
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
        discord_components
    ]
    timeList = []
    for module in modules:
        startTime = time.time()
        for i in range(2):
            importlib.reload(module)
        endTime = time.time()
        timeList.append(endTime - startTime)
    
    totalTime = sum(timeList); longest = [0, None]
    for length in timeList:
        if length > longest[0]:
            longest[0] = length; longest[1] = modules[timeList.index(length)]
    if round(totalTime, 1) == 1.0:
        totalTime = 1
    return f"Successfully reloaded all modules in **{round(totalTime, 1)} {'second' if round(totalTime, 1) == 1 else 'seconds'}**\nAverage: **{round(totalTime/len(timeList), 2)} {'second' if round(totalTime, 1) == 1 else 'seconds'}**, Longest: `{longest[1].__name__}` at **{round(longest[0], 2)} {'second' if round(totalTime, 1) == 1 else 'seconds'}**"

def getCooldown(id, command):
    try:
        cooldown = userCooldowns[f"{id}.{command}"]
        futureTime = cooldown[0] + cooldown[1]
        if futureTime - time.time() < 0:
            return 0
        else:
            return futureTime - time.time()
    except:
        return 0

def addCooldown(id, command, cooldownTime):
    userCooldowns[f"{id}.{command}"] = [time.time(), cooldownTime]

def generateCooldown(command, cooldownTime):
    cooldownUnit = "seconds"
    if cooldownTime >= 60:
        cooldownUnit = "minutes"
        cooldownTime = cooldownTime / 60
        if cooldownTime >= 60:
            cooldownUnit = "hours"
            cooldownTime = cooldownTime / 60
            if cooldownTime >= 24:
                cooldownUnit = "days"
                cooldownTime = cooldownTime / 24
                if cooldownTime >= 30.4:
                    cooldownUnit = "months"
                    cooldownTime = cooldownTime / 30.4
                    if cooldownTime >= 12:
                        cooldownUnit = "years"
                        cooldownTime = cooldownTime / 12

    cooldownTime = round(cooldownTime, 1)
    if str(cooldownTime).endswith(".0"):
        cooldownTime = round(cooldownTime)
    if cooldownTime == 1:
        cooldownUnit = cooldownUnit[:-1]
    if str(cooldownTime) == "inf":
        cooldownTime = "for an"
        cooldownUnit = "eternity"
    return f"Please wait **{cooldownTime} {cooldownUnit}** before using the `{command}` command again"

async def currencyCommand(message, prefix):
    parts = message.content.split(" ")
    if len(parts) == 4:
        try:
            amount = float(parts[1].replace(",", "").replace(" ", "")); inputCurrency = parts[2].lower(); outputCurrency = parts[3].lower()
            url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{inputCurrency}/{outputCurrency}.json"
            response = requests.get(url).json(); value = response[outputCurrency] * amount
            embed = discord.Embed(title="Currency Convert", description=f"**{round(amount, 6):,} {inputCurrency.upper()}** = **{round(value, 6):,} {outputCurrency.upper()}**", color=variables.embedColor)
            await message.channel.send(embed=embed)
            addCooldown(message.author.id, "currency", 5)
        except:
            await message.channel.send("Unable to convert currency"); return
    elif len(parts) == 2 and parts[1].lower() == "list":
        response = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies.json").json()
        output = ""
        for key in response.keys():
            output += f"{key}: {response[key]}\n"
        segments = [output[i: i + 1000] for i in range(0, len(output), 1000)]
        pager = CustomPager(
            timeout=60, length=1, prefix=f"```\n", suffix="```", color=variables.embedColor, title="Currency List", entries=segments
        )
        await pager.start(ContextObject(client, message))
        addCooldown(message.author.id, "currency", 5)
    else:
        await message.channel.send(f"The syntax is `{prefix}currency <input> <amount> <output>`"); return

async def pingCommand(message, prefix):
    embed = discord.Embed(title="Pong :ping_pong:", description=f"Latency: **{round(client.latency * 1000, 1)} ms**", color=variables.embedColor)
    await message.channel.send(embed=embed)

async def testsCommand(message, prefix):
    addCooldown(message.author.id, "tests", variables.largeNumber)
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
    embed = discord.Embed(title="Doge Tests", description=description, color=variables.embedColor)
    oldMessage = await message.channel.send(embed=embed)

    lines = description.split("\n"); tests = []
    for line in lines:
        if ":" in line:
            tests.append(line)
    for test in tests:
        description = description.replace(test, test.replace(":grey_question:", ":hourglass_flowing_sand:"))
        embed = discord.Embed(title="Doge Tests", description=description, color=variables.embedColor)
        await oldMessage.edit(embed=embed)
        description = description.replace(":hourglass_flowing_sand:", ":grey_question:")

        name = test.split(":grey_question: ")[1].replace("`", "")
        if name == "Code Integrity":
            try:
                for i in range(20):
                    reloadData()
                description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Bot Status":
            try:
                for i in range(200):
                    process = psutil.Process(os.getpid())
                    memoryUsage = process.memory_info().rss / 1000000
                    if memoryUsage > 100 and memoryUsage < 200:
                        description = description.replace(test, test.replace(":grey_question:", ":yellow_square:")); continue
                    if memoryUsage > 200:
                        description = description.replace(test, test.replace(":grey_question:", ":orange_square:")); continue
                    if round(psutil.cpu_percent()) == 100 or (client.latency * 1000) > 200:
                        description = description.replace(test, test.replace(":grey_question:", ":yellow_square:")); continue

                    description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Task Threads":
            try:
                if threading.active_count() >= 5:
                    description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
                else:
                    description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Bot Version":
            try:
                for i in range(20):
                    fileSize = 0
                    for object in os.listdir():
                        try:
                            file = open(object, "rb")
                            fileSize += len(file.read()); file.close()
                        except:
                            pass
                description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Raid Protection":
            try:
                for i in range(30):
                    serverRoles = {}; serverChannels = {}
                    for guild in client.guilds:
                        serverChannels[guild.id] = guild.channels
                        serverRoles[guild.id] = guild.roles
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
                for i in range(300):
                    addCooldown(message.author.id, "test-command", 60)
                    if round(getCooldown(message.author.id, "test-command")) == 60:
                        description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
                    else:
                        description = description.replace(test, test.replace(":grey_question:", ":yellow_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
        elif name == "Image Library":
            try:
                for i in range(150):
                    if generateColor(f"({random.randint(0, 256)}, {random.randint(0, 256)}, {random.randint(0, 256)})") == 1:
                        description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
                    else:
                        description = description.replace(test, test.replace(":grey_question:", ":green_square:"))
            except:
                description = description.replace(test, test.replace(":grey_question:", ":red_square:"))
            
        embed = discord.Embed(title="Doge Tests", description=description, color=variables.embedColor)
        await oldMessage.edit(embed=embed)
    addCooldown(message.author.id, "tests", 60)

async def statusCommand(message, prefix):
    memberCount = 0; channelCount = 0; uptime = ""
    for guild in client.guilds:
        memberCount += guild.member_count
        channelCount += len(guild.channels)
    process = psutil.Process(os.getpid())
    memoryUsage = process.memory_info().rss / 1000000
    secondsTime = time.time() - startTime
    minutesTime = secondsTime / 60
    hoursTime = minutesTime / 60
    daysTime = hoursTime / 24
    secondsTime = secondsTime % 60
    minutesTime = minutesTime % 60
    hoursTime = hoursTime % 24
    if daysTime >= 1:
        uptime += str(math.floor(daysTime)) + "d "
    if hoursTime >= 1:
        uptime += str(math.floor(hoursTime)) + "hr "
    if minutesTime >= 1:
        uptime += str(math.floor(minutesTime)) + "m "
    if secondsTime >= 1:
        uptime += str(math.floor(secondsTime)) + "s "
    if uptime == "":
        uptime = "Unknown"
    
    embed = discord.Embed(color=variables.embedColor)
    embed.add_field(name="Bot Latency", value="```" + f"{round(client.get_shard(message.guild.shard_id).latency * 1000, 1)} ms" + "```")
    embed.add_field(name="CPU Usage", value="```" + f"{psutil.cpu_percent()}%" + "```")
    embed.add_field(name="RAM Usage", value="```" + f"{round(memoryUsage, 1)} MB{' (nice)' if round(memoryUsage, 1) == 69.0 else ''}" + "```")
    embed.add_field(name="Thread Count", value="```" + str(threading.active_count()) + "```")
    embed.add_field(name="Joined Guilds", value="```" + str(len(client.guilds)) + "```")
    embed.add_field(name="Active Shards", value="```" + str(client.shards[0].shard_count) + "```")
    embed.add_field(name="Member Count", value="```" + str(memberCount) + "```")
    embed.add_field(name="Channel Count", value="```" + str(channelCount) + "```")
    embed.add_field(name="Command Count", value="```" + str(len(commandList)) + "```")
    embed.add_field(name="Discord Version", value="```" + discord.__version__ + "```")
    embed.add_field(name="Bot Version", value="```" + f"{variables.versionNumber}.{variables.buildNumber}" + "```")
    embed.add_field(name="Bot Uptime", value="```" + uptime + "```")

    await message.channel.send(embed=embed)
    addCooldown(message.author.id, "status", 5)

async def supportCommand(message, prefix):
    embed = discord.Embed(title="Support Server", description=f"You can join Doge Utilities's official server [here](https://discord.gg/3Tp7R8FUsC)", color=variables.embedColor)
    await message.channel.send(embed=embed)

async def versionCommand(message, prefix):
    fileSize = 0
    for object in os.listdir():
        try:
            file = open(object, "rb")
            fileSize += len(file.read()); file.close()
        except:
            pass
    embed = discord.Embed(title="Bot Version", description=f"Version: **{variables.versionNumber}**\nBuild: **{variables.buildNumber}**\nPython: **{sys.version.split(' ')[0]}**\nDiscord: **{discord.__version__}**\nSize: **{round(fileSize / 1000)} KB**", color=variables.embedColor)
    await message.channel.send(embed=embed)
    addCooldown(message.author.id, "version", 5)

async def inviteCommand(message, prefix):
    guildMember = True
    if message.author == message.guild.owner:
        guildMember = False
    await message.channel.send("Here's the link to invite me to another server",
        components=[[
            discord_components.Button(style=discord_components.ButtonStyle.URL, label="Invite Link", url="https://discord.com/oauth2/authorize?client_id=854965721805226005&permissions=8&&scope=bot"),
            discord_components.Button(style=discord_components.ButtonStyle.red, label="Leave Server", disabled=guildMember)
    ]])
    result = await client.wait_for("button_click", check = lambda item: item.component.label == "Leave Server")
    if result.channel == message.channel:
        if result.author == message.author:
            await result.respond(type=4, content="Are you sure you want me to leave this server? Please press the button again to confirm.")
            result = await client.wait_for("button_click", check = lambda item: item.component.label == "Leave Server")
            if result.channel == message.channel:
                if result.author == message.author:
                    if result.author == message.guild.owner:
                        await result.respond(type=4, content="Leaving server...")
                        await message.guild.leave()
        else:
            await result.respond(type=4, content="You are not the sender of the command!")

async def prefixCommand(message, prefix):
    newPrefix = message.content.split(" ")
    if message.author.guild_permissions.administrator or message.author.id in variables.permissionOverride:
        if len(newPrefix) == 2:
            newPrefix = newPrefix[1]
            if " " in newPrefix:
                await message.channel.send("Please do not put spaces in the bot's prefix")
                return
            oldMessage = await message.channel.send(
                f"Are you sure you want to change this server's prefix to `{newPrefix}`?",
                components=[[
                    discord_components.Button(style=discord_components.ButtonStyle.green, label="Yes"),
                    discord_components.Button(style=discord_components.ButtonStyle.green, label="No")
                ]]
            )
            result = await client.wait_for("button_click")
            if result.message.id == oldMessage.id:
                if result.component.label == "No":
                    await result.respond(type=4, content="Operation cancelled")
                else:
                    prefixDatabase[message.guild.id] = newPrefix
                    await oldMessage.edit(content=f"This server's prefix has been set to `{newPrefix}`", components=[])
                    await result.respond(type=4, content=f"Successfully changed server prefix")
            else:
                await result.respond(type=4, content="You are not the sender of the command!")
        else:
            await message.channel.send(f"The syntax is `{prefix}prefix <new prefix>`")
    else:
        await message.channel.send("You do not have permission to use this command")

async def setupBannedCommand(message, prefix):
    if message.author.guild_permissions.manage_roles or message.author.id in variables.permissionOverride:
        pass
    else:
        await message.channel.send("You do not have permission to use this command"); return

    roles = message.guild.roles
    for role in roles:
        if role.name == "Banned":
            await message.channel.send("The **Banned** role already exists in this guild")
            return
    oldMessage = await message.channel.send("Generating the **Banned** role for the current guild...")
    try:
        bannedRole = await message.guild.create_role(name="Banned")
        guildRoles = len(message.guild.roles); retryCount = 0
        while True:
            if retryCount > 100:
                break
            try:
                await bannedRole.edit(position=guildRoles - retryCount)
                break
            except:
                retryCount += 1
        for channel in message.guild.channels:
            try:
                await channel.set_permissions(bannedRole, view_channel=False, connect=False, change_nickname=False, add_reactions=False)
            except:
                pass
    except:
        await oldMessage.edit(content=f"Unable to generate the **Banned** role for this guild")
        return
    await oldMessage.edit(content=f"Successfully generated the **Banned** role for this guild")
    addCooldown(message.author.id, "setup", 120)

async def setupMutedCommand(message, prefix):
    if message.author.guild_permissions.manage_roles or message.author.id in variables.permissionOverride:
        pass
    else:
        await message.channel.send("You do not have permission to use this command"); return

    roles = message.guild.roles
    for role in roles:
        if role.name == "Muted":
            await message.channel.send("The **Muted** role already exists in this guild")
            return
    oldMessage = await message.channel.send("Generating the **Muted** role for the current guild...")
    try:
        mutedRole = await message.guild.create_role(name="Muted")
        guildRoles = len(message.guild.roles); retryCount = 0
        while True:
            if retryCount > 100:
                break
            try:
                await mutedRole.edit(position=guildRoles - retryCount)
                break
            except:
                retryCount += 1
        for channel in message.guild.channels:
            try:
                await channel.set_permissions(mutedRole, send_messages=False)
            except:
                try:
                    await channel.set_permissions(mutedRole, connect=False)
                except:
                    pass
    except:
        await oldMessage.edit(f"Unable to generate the **Muted** role for this guild")
        return
    await oldMessage.edit(f"Successfully generated the **Muted** role for this guild")
    addCooldown(message.author.id, "setup", 120)

async def randomCommand(message, prefix):
    arguments = message.content.split(" "); highNumber = 0; lowNumber = 0
    try:
        if len(arguments) == 2:
            highNumber = float(arguments[1])
        elif len(arguments) == 3:
            lowNumber = float(arguments[1])
            highNumber = float(arguments[2])
        else:
            await message.channel.send(f"The syntax is `{prefix}random <low> <high>`")
            return
    except:
        await message.channel.send("Please enter a valid number")
        return
    try:
        randomNumber = round(random.uniform(lowNumber, highNumber), 2)
    except:
        await message.channel.send("The lower number is larger than the higher number")
        return
    addCooldown(message.author.id, "random", 30)
    buttonText = "Generate Number"
    oldMessage = await message.channel.send(
            f"Your random number is **{randomNumber}**",
            components=[
                discord_components.Button(style=discord_components.ButtonStyle.gray, label=buttonText)
    ]); uses = 0
    while uses < 5:
        result = await client.wait_for("button_click", check = lambda item: item.component.label == buttonText)
        if result.channel == message.channel:
            if result.author == message.author:
                randomNumber = round(random.uniform(lowNumber, highNumber), 2)
                displayText = "uses"; uses += 1
                if 5 - uses == 1: displayText = "use"
                await oldMessage.edit(content=f"Your random number is **{randomNumber}**")
                await result.respond(content=f"Successfully generated a new number ({5 - uses} {displayText} left)")
            else:
                await result.respond(type=4, content="You are not the sender of this command!")
    await oldMessage.edit(components=[[discord_components.Button(style=discord_components.ButtonStyle.gray, label=buttonText, disabled=True)]])

async def executeCommand(message, prefix):
    if message.author.id == variables.botOwner:
        try:
            outputLanguage = ""
            code = message.content.split(prefix + "execute;")[1]
            if code.startswith("```python"):
                code = code[9:]
            if code.startswith("```py"):
                code = code[5:]
            if code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            code = code.replace("runCoroutine", "asyncio.run_coroutine_threadsafe")
            if "#python" in code:
                outputLanguage = "py"
            if "#go" in code:
                outputLanguage = "go"

            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    if "#globals" in code:
                        exec(f"async def runCode():\n{textwrap.indent(code, '   ')}", globals())
                        await globals()["runCode"]()
                    else:
                        dictionary = dict(locals(), **globals())
                        exec(f"async def runCode():\n{textwrap.indent(code, '   ')}", dictionary, dictionary)
                        await dictionary["runCode"]()

                    output = stdout.getvalue()
            except Exception as error:
                output = "`" + str(error) + "`"
            
            output = output.replace(os.getenv("TOKEN"), "<token>")
            segments = [output[i: i + 2000] for i in range(0, len(output), 2000)]
            if len(output) > 2001:
                output = output.replace("`", "\`")
                pager = CustomPager(
                    timeout=120, length=1, prefix=f"```{outputLanguage}\n", suffix="```", color=variables.embedColor, title=f"Code Output ({len(segments)} pages)", entries=segments
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

async def reloadCommand(message, prefix):
    if message.author.id == variables.botOwner:
        embed = discord.Embed(title="Reload", description=reloadData(), color=discord.Color.green())
        await message.channel.send(embed=embed)
    else:
        await message.add_reaction("🚫")

async def disconnectMembersCommand(message, prefix):
    if message.author.guild_permissions.administrator or message.author.id in variables.permissionOverride:
        oldMessage = await message.channel.send("Disconnecting all members from voice channels...")
        addCooldown(message.author.id, "disconnect-members", variables.largeNumber); members = 0; failed = 0

        for channel in message.guild.channels:
            if type(channel) == discord.channel.VoiceChannel:
                for member in channel.members:
                    try:
                        await member.edit(voice_channel=None); members += 1
                    except:
                        failed += 1
        await oldMessage.edit(f"Successfully disconnected **{members}/{members + failed} {'member' if members == 1 else 'members'}** from voice channels")
    else:
        await message.channel.send("You do not have permission to use this command")
    addCooldown(message.author.id, "disconnect-members", 20)

async def suggestCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        addCooldown(message.author.id, "suggest", variables.largeNumber)
        arguments.pop(0); text = " ".join(arguments)
        oldMessage = await message.channel.send("Sending your suggestion...")
        for userID in variables.messageManagers:
            member = None
            for guild in client.guilds:
                try:
                    member = await guild.fetch_member(userID)
                    break
                except:
                    continue
            if member:
                try:
                    await member.send(f"**{message.author.name}#{message.author.discriminator}** **(**`{member.id}`**)** **has sent a suggestion:**\n{text}")
                except:
                    pass
        await oldMessage.edit("Your suggestion has been successfully sent")
    else:
        await message.channel.send(f"The syntax is `{prefix}suggest <text>`")
    addCooldown(message.author.id, "suggest", 300)

async def autoroleCommand(message, prefix):
    if message.author.guild_permissions.administrator or message.author.id in variables.permissionOverride:
        message.content = message.content.replace("<", "").replace("@", "").replace("!", "").replace("&", "").replace(">", "")
        arguments = message.content.split(" ")
        if len(arguments) > 1:
            arguments.pop(0)
            roleList = arguments; roleFound = False
            for role in message.guild.roles:
                for roleID in roleList:
                    try:
                        if role.id == int(roleID):
                            roleFound = True
                            break
                    except:
                        await message.channel.send("That role is not found in this server")
                        return
            if not roleFound:
                await message.channel.send("That role is not found in this server")
                return
            autoroleDatabase[message.guild.id] = roleList; roleString = ""
            for role in roleList:
                roleString += "<@&" + role + "> "
            await message.channel.send(embed=discord.Embed(title="Autorole", description=f"This server's autorole has been changed to {roleString}", color=variables.embedColor))
        else:
            try:
                roleList = autoroleDatabase[message.guild.id]; roleString = ""
                for role in roleList:
                    roleString += "<@&" + role + "> "
                await message.channel.send(embed=discord.Embed(title="Autorole", description=f"This server's autorole is {roleString}", color=variables.embedColor))
            except:
                await message.channel.send(f"This server does not have autorole configured")
    else:
        await message.channel.send("You do not have permission to use this command")
    addCooldown(message.author.id, "autorole", 5)

async def shardsCommand(message, prefix):
    pages = {}; currentPage = 1; pageLimit = 20; currentItem = 0; index = 1
    try:
        currentPage = int(message.content.split(prefix + "shards ")[1])
    except:
        pass
    for shard in client.shards:
        currentServer = ""
        shardGuilds = 0
        shardMembers = 0
        for guild in client.guilds:
            if guild.shard_id == shard:
                shardGuilds += 1
                shardMembers += guild.member_count
                if guild.id == message.guild.id:
                    currentServer = "**"
        temporaryText = f"{currentServer}Shard `{client.shards[shard].id}` - `{round(client.shards[shard].latency * 1000, 2)} ms` (`{shardGuilds}` guilds, `{shardMembers}` members){currentServer}\n"
        if index > pageLimit:
            index = 0
            currentItem += 1
        try:
            pages[currentItem] += temporaryText
        except:
            pages[currentItem] = f"Shard Count: `{len(client.shards)}`, Current Shard: `{message.guild.shard_id}`\n\n"
            pages[currentItem] += temporaryText
        index += 1
    try:
        helpPage = pages[currentPage - 1]
    except:
        helpPage = "That page doesn't exist"
        currentPage = 0
    embed = discord.Embed(title="Doge Shards", description=helpPage, color=variables.embedColor, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f"Viewing shards page {currentPage} of {len(pages)}")
    await message.channel.send(embed=embed)
    addCooldown(message.author.id, "shards", 5)

async def lookupCommand(message, prefix):
    userID = message.content.split(" ")
    if len(userID) != 2:
        userID.append(str(message.author.id))

    userID = userID[1]
    userID = userID.replace("<", ""); userID = userID.replace("@", "")
    userID = userID.replace("!", ""); userID = userID.replace(">", "")
    headers = {"Authorization": "Bot " + os.getenv("TOKEN")}
    url = "https://discord.com/api/users/" + userID
    response = requests.get(url, headers=headers).json()
    if "10013" not in str(response):
        try:
            response["public_flags"]
        except:
            await message.channel.send("Please enter a valid user ID"); return
        badges = ""
        for flag in variables.publicFlags:
            if response['public_flags'] & int(flag) == int(flag):
                if variables.publicFlags[flag] != "None":
                    try:
                        badges += variables.badgeList[variables.publicFlags[flag]]
                    except:
                        raise Exception(f"unable to find badge: {variables.publicFlags[flag]}")
        botValue = False
        try:
            botValue = response["bot"]
        except:
            pass
        systemValue = False
        try:
            systemValue = response["system"]
        except:
            pass
        embed = discord.Embed(color=int(hex(response['accent_color']), 16) if response['accent_color'] else 0x000000)
        embed.add_field(name="User ID", value=f"`{response['id']}`")
        embed.add_field(name="Tag", value=f"`{response['username']}#{response['discriminator']}`")
        embed.add_field(name="Creation Time", value=f"<t:{round(((int(response['id']) >> 22) + 1420070400000) / 1000)}:R>")
        embed.add_field(name="Public Flags", value=f"`{response['public_flags']}` {badges}")
        embed.add_field(name="Bot User", value=f"`{botValue}`")
        embed.add_field(name="System User", value=f"`{systemValue}`")

        if response['avatar'] == None:
            avatarURL = f"https://cdn.discordapp.com/embed/avatars/{int(response['discriminator']) % 5}.png"
        else:
            if response['avatar'].startswith("a_"):
                avatarURL = f"https://cdn.discordapp.com/avatars/{response['id']}/{response['avatar']}.gif?size=512"
            else:
                avatarURL = f"https://cdn.discordapp.com/avatars/{response['id']}/{response['avatar']}.webp?size=512"
        embed.set_thumbnail(url=avatarURL)

        if response['banner'] != None:
            if response['banner'].startswith("a_"):
                bannerURL = f"https://cdn.discordapp.com/banners/{response['id']}/{response['banner']}.gif?size=1024"
            else:
                bannerURL = f"https://cdn.discordapp.com/banners/{response['id']}/{response['banner']}.webp?size=1024"
            embed.set_image(url=bannerURL)
    else:
        embed = discord.Embed(title="Unknown User", description="Unable to find the specified user", color=variables.embedColor)
    await message.channel.send(embed=embed)
    addCooldown(message.author.id, "lookup", 6)

async def permissionsCommand(message, prefix):
    userID = message.content.split(" ")
    if len(userID) != 2:
        userID.append(str(message.author.id))
    userID = userID[1]
    userID = userID.replace("<", ""); userID = userID.replace("@", "")
    userID = userID.replace("!", ""); userID = userID.replace(">", "")
    
    targetUser = None
    try:
        targetUser = await message.guild.fetch_member(int(userID))
    except:
        pass
        if str(user.id) == userID:
            targetUser = user
    if targetUser == None:
        await message.channel.send("Unable to find user"); return
    
    permissionList = ""
    for permission in targetUser.guild_permissions:
        if permission[1] == True:
            permissionList += f":white_check_mark: `{permission[0]}`\n"
        else:
            permissionList += f":x: `{permission[0]}`\n"
    if targetUser == message.author.guild.owner:
        permissionList += f":white_check_mark: `owner`\n"
    else:
        permissionList += f":x: `owner`\n"

    embed = discord.Embed(title="User Permissions", description=f"Permissions for **{targetUser.name}#{targetUser.discriminator}**\n\n" + permissionList, color=variables.embedColor)
    await message.channel.send(embed=embed)
    addCooldown(message.author.id, "permissions", 3)

async def raidProtectionCommand(message, prefix):
    if message.author.guild_permissions.administrator or message.author.id in variables.permissionOverride:
        try:
            setting = message.content.split(prefix + "raid-protection ")[1]
        except:
            try:
                currentSetting = settingsDatabase[f"{message.author.guild.id}|raid-protection"]
                if currentSetting:
                    await message.channel.send("This server's raid protection is turned **on**")
                else:
                    await message.channel.send("This server's raid protection is turned **off**")
            except:
                await message.channel.send("This server's raid protection is turned **off**")
            return
        if setting.lower() == "on":
            settingsDatabase[f"{message.author.guild.id}|raid-protection"] = True
            await message.channel.send("This server's raid protection has been turned **on**")
            return
        elif setting.lower() == "off":
            settingsDatabase[f"{message.author.guild.id}|raid-protection"] = False
            await message.channel.send("This server's raid protection has been turned **off**")
            return
        else:
            await message.channel.send("Please specify a valid setting (on/off)")
            return
    else:
        await message.channel.send("You do not have permission to use this command")

async def epochDateCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); text = " ".join(arguments)
        try:
            date = functions.epochToDate(int(text)); embed = discord.Embed(color=variables.embedColor)
            embed.add_field(name="Epoch", value="`" + text + "`"); embed.add_field(name="Date", value=date, inline=False)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Invalid timestamp"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}epoch-date <epoch>`")

async def dateEpochCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); text = " ".join(arguments)
        try:
            epoch = functions.dateToEpoch(text); embed = discord.Embed(color=variables.embedColor)
            embed.add_field(name="Date", value=text); embed.add_field(name="Epoch", value="`" + str(epoch) + "`", inline=False)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Invalid date"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}date-epoch <date>`")

async def hashCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 2:
        arguments.pop(0); hashType = arguments[0]; arguments.pop(0); text = " ".join(arguments)
        try:
            outputHash = hashText(hashType, text); embed = discord.Embed(color=variables.embedColor)
            embed.add_field(name="Text", value=text); embed.add_field(name=f"Hash ({hashType})", value="`" + outputHash + "`", inline=False)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Invalid hash type"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}hash <type> <text>`")
    addCooldown(message.author.id, "hash", 5)

async def base64Command(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 2:
        arguments.pop(0); actionType = arguments[0]; arguments.pop(0); text = " ".join(arguments)
        try:
            if actionType == "encode":
                outputCode = base64.b64encode(text.encode("utf-8")).decode("utf-8")
                embed = discord.Embed(color=variables.embedColor)
                embed.add_field(name="Text", value=text); embed.add_field(name="Base64", value="`" + outputCode + "`", inline=False)
            elif actionType == "decode":
                outputText = base64.b64decode(text.encode("utf-8")).decode("utf-8")
                embed = discord.Embed(color=variables.embedColor)
                embed.add_field(name="Base64", value="`" + text + "`"); embed.add_field(name="Text", value=outputText, inline=False)
            else:
                embed = discord.Embed(title="Base64", description="Unknown action. Please use `encode` or `decode`.", color=variables.embedColor)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Unable to process command"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}base64 <action> <text>`")
    addCooldown(message.author.id, "base64", 5)

async def binaryCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 2:
        arguments.pop(0); actionType = arguments[0]; arguments.pop(0); text = " ".join(arguments)
        try:
            if actionType == "encode":
                outputCode = ' '.join(format(ord(letter), '08b') for letter in text)
                embed = discord.Embed(color=variables.embedColor)
                embed.add_field(name="Text", value=text); embed.add_field(name="Binary", value="`" + outputCode + "`", inline=False)
            elif actionType == "decode":
                outputText = ""
                for letter in text.split():
                    number = int(letter, 2)
                    outputText += chr(number)
                embed = discord.Embed(color=variables.embedColor)
                embed.add_field(name="Binary", value="`" + text + "`"); embed.add_field(name="Text", value=outputText, inline=False)
            else:
                embed = discord.Embed(title="Binary", description="Unknown action. Please use `encode` or `decode`.", color=variables.embedColor)
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("Unable to process command"); return
    else:
        await message.channel.send(f"The syntax is `{prefix}binary <action> <text>`")
    addCooldown(message.author.id, "binary", 5)

async def calculateCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); expression = ' '.join(arguments)
        if expression.startswith("`"):
            expression = expression[1:]
        if expression.endswith("`"):
            expression = expression[:-1]
        answer = evaluateExpression(expression); embed = discord.Embed(color=variables.embedColor)
        embed.add_field(name="Expression", value="`" + expression + "`"); embed.add_field(name="Result", value="`" + answer + "`", inline=False)
        await message.channel.send(embed=embed)
    else:
        await message.channel.send(f"The syntax is `{prefix}calculate <expression>`")
    addCooldown(message.author.id, "calculate", 3)

async def clearCommand(message, prefix):
    if message.author.guild_permissions.administrator or message.author.id in variables.permissionOverride:
        try:
            count = int(message.content.split(prefix + "clear ")[1])
        except:
            await message.channel.send("Please specify a valid number")
            return
        if count > 500:
            await message.channel.send(
                f"Are you sure you want to clear more than **500 messages** in this channel?",
                components=[[
                    discord_components.Button(style=discord_components.ButtonStyle.green, label="Yes"),
                    discord_components.Button(style=discord_components.ButtonStyle.green, label="No")
                ]]
            )
            result = await client.wait_for("button_click")
            if result.channel == message.channel:
                if result.author == message.author:
                    if result.component.label == "No":
                        await result.respond(type=4, content="Operation cancelled")
                        return
                    else:
                        await result.respond(type=4, content=f"Deleting more than 500 messages in this channel...")
                else:
                    await result.respond(type=4, content="You are not the sender of the command!")
        try:    
            await message.channel.purge(limit=count + 1)
        except:
            await message.channel.send("Unable to delete messages")
    else:
        await message.channel.send("You do not have permission to use this command")
    addCooldown(message.author.id, "clear", 10)

async def wideCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); newText = ""; text = " ".join(arguments)
        for letter in text:
            newText += letter + " "
        await message.channel.send(newText.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}wide <text>`")
    addCooldown(message.author.id, "wide", 3)

async def unwideCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); newText = ""; text = " ".join(arguments); spaceCharacter = False
        for letter in text.replace("   ", "  "):
            if letter == " ":
                if spaceCharacter:
                    newText += " "
                spaceCharacter = True
            else:
                spaceCharacter = False
                newText += letter
        await message.channel.send(newText.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}unwide <text>`")
    addCooldown(message.author.id, "unwide", 3)

async def spoilerCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); newText = ""; text = " ".join(arguments)
        for letter in text:
            newText += "||" + letter + "||"
        await message.channel.send(newText.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}spoiler <text>`")
    addCooldown(message.author.id, "spoiler", 3)

async def cringeCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); newText = ""; text = " ".join(arguments)
        for letter in text:
            case = random.randint(1, 2)
            if case == 1:
                if letter.upper() == letter:
                    newText += letter.lower()
                else:
                    newText += letter.upper()
            else:
                if letter.upper() == letter:
                    newText += letter.upper()
                else:
                    newText += letter.lower()
        await message.channel.send(newText.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}cringe <text>`")
    addCooldown(message.author.id, "cringe", 3)

async def reverseCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); newText = ""; text = " ".join(arguments)
        newText = text[::-1]; await message.channel.send(newText.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}reverse <text>`")
    addCooldown(message.author.id, "reverse", 3)

async def corruptCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); newText = ""; text = " ".join(arguments)
        for letter in text:
            switch = random.randint(0, 100)
            if switch > 95:
                newText += text[random.randint(0, len(text) - 1)]
            else:
                number = random.randint(0, 100)
                if number > 80:
                    newText += random.choice(["0", "1"])
                else:
                    newText += letter
                    punctuation = random.choice([True, False, False, False, False])
                    if punctuation:
                        newText += string.punctuation[random.randint(0, len(string.punctuation) - 1)]
        await message.channel.send(newText.replace("@everyone", "everyone"))
    else:
        await message.channel.send(f"The syntax is `{prefix}reverse <text>`")
    addCooldown(message.author.id, "corrupt", 3)

async def colorCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        arguments.pop(0); text = " ".join(arguments)
        colors = functions.generateColor(text)
        if colors == 1:
            await message.channel.send("Invalid color code"); return
        else:
            hexColor = colors[0]; rgbColor = colors[1]
            embed = discord.Embed(color=int("0x" + hexColor[1:], 16))
            embed.set_image(url="attachment://color.png")
            embed.add_field(name="Hex", value=hexColor)
            embed.add_field(name="RGB", value=str(rgbColor), inline=True)
        await message.channel.send(embed=embed, file=discord.File("images/color.png"))
    else:
        await message.channel.send(f"The syntax is `{prefix}color <color code>`")
    addCooldown(message.author.id, "color", 3)

async def voteCommand(message, prefix):
    embed = discord.Embed(title="Vote Link", description="You can upvote Doge Utilities on [top.gg](https://top.gg/bot/854965721805226005/vote), [discordbotlist](https://discordbotlist.com/bots/doge-utilities/upvote), or on [botsfordiscord](https://discords.com/bots/bot/854965721805226005/vote)", color=variables.embedColor)
    await message.channel.send(embed=embed)

async def timeCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        try:
            arguments.pop(0); text = " ".join(arguments)
            if text.lower() == "list":
                output = ""
                for timezone in pytz.all_timezones:
                    output += timezone + "\n"
                segments = [output[i: i + 1000] for i in range(0, len(output), 1000)]
                pager = CustomPager(
                    timeout=60, color=variables.embedColor,
                    length=1, prefix="```\n", suffix="```",
                    title=f"Timezone List", entries=segments
                )
                await pager.start(ContextObject(client, message))
            elif text.lower() == "epoch" or text.lower() == "unix":
                embed = discord.Embed(title="Time", description=f"Current epoch time: **{round(time.time())}**", color=variables.embedColor)
                await message.channel.send(embed=embed)
            else:
                userTimezone = pytz.timezone(text.replace(" ", "_"))
                now = datetime.datetime.now(userTimezone)
                embed = discord.Embed(title="Time", description=f"Information for **{text.replace(' ', '_')}**\n\nTime: **{str(now.time()).split('.')[0]}**\nDate: **{now.date()}**\nDay: **{variables.weekdays[now.weekday() + 1]}**", color=variables.embedColor)
                await message.channel.send(embed=embed)
        except KeyError:
            text = "_".join(arguments)
            for timezone in pytz.all_timezones:
                try:
                    city = timezone.split("/")[1]
                    if text.lower() == city.lower():
                        userTimezone = pytz.timezone(timezone); now = datetime.datetime.now(userTimezone)
                        embed = discord.Embed(title="Time", description=f"Information for **{timezone}**\n\nTime: **{str(now.time()).split('.')[0]}**\nDate: **{now.date()}**\nDay: **{variables.weekdays[now.weekday() + 1]}**", color=variables.embedColor)
                        await message.channel.send(embed=embed); return
                except:
                    pass
            embed = discord.Embed(title="Time", description=f"That timezone was not found\nUse `{prefix}time list` to get a list of timezones", color=variables.embedColor)
            await message.channel.send(embed=embed); return
    else:
        await message.channel.send(f"The syntax is `{prefix}time <timezone>`")
    addCooldown(message.author.id, "time", 3)

async def nicknameCommand(message, prefix):
    if message.author.guild_permissions.manage_nicknames:
        arguments = message.content.split(" ")
        if len(arguments) >= 3:
            arguments.pop(0); userID = arguments[0]; arguments.pop(0); nickname = ' '.join(arguments)
            try:
                userID = int(userID.replace("<", "").replace(">", "").replace("@", "").replace("!", ""))
                member = await message.guild.fetch_member(userID)
            except:
                await message.channel.send("Please mention a valid user!"); return
            try:
                await member.edit(nick=nickname); addCooldown(message.author.id, "nickname", 5)
                await message.channel.send(f"Successfully updated **{member.name}#{member.discriminator}**'s nickname to **{nickname}**"); return
            except:
                await message.channel.send("Unable to change user nickname"); return
            await message.channel.send("Unable to find user"); return
        else:
            await message.channel.send(f"The syntax is `{prefix}nickname <user> <nickname>`")
    else:
        await message.channel.send("You do not have permission to use this command")

async def stackoverflowCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        try:
            stackoverflowParameters = {
                "order": "desc",
                "sort": "activity",
                "site": "stackoverflow"
            }
            arguments.pop(0); text = ' '.join(arguments)
            stackoverflowParameters["q"] = text; parameters = stackoverflowParameters
            response = requests.get(url="https://api.stackexchange.com/2.2/search/advanced", params=parameters).json()
            if not response["items"]:
                embed = discord.Embed(title="StackOverflow", description=f"No search results found for **{text}**", color=discord.Color.red())
                await message.channel.send(embed=embed); return
            finalResults = response["items"][:5]
            embed = discord.Embed(title="StackOverflow", description=f"Here are the top **{len(finalResults)}** results for **{text}**", color=variables.embedColor)
            for result in finalResults:
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
        except discord.HTTPException:
            await message.channel.send("The search result is too long!"); return
        except:
            await message.channel.send("Unable to search for item"); return
        addCooldown(message.author.id, "stackoverflow", 10)
    else:
        await message.channel.send(f"The syntax is `{prefix}stackoverflow <text>`")

async def sourceCommand(message, prefix):
    description = "You can find my code [here](https://github.com/ErrorNoInternet/Doge-Utilities)\n"
    response = requests.get("https://api.github.com/repos/ErrorNoInternet/Doge-Utilities").json()
    description += f"Open Issues: **{response['open_issues']}**, Forks: **{response['forks']}**\nStargazers: **{response['stargazers_count']}**, Watchers: **{response['subscribers_count']}**"
    embed = discord.Embed(title="Source Code", description=description, color=variables.embedColor)
    embed.set_thumbnail(url=client.user.avatar_url); await message.channel.send(embed=embed)
    addCooldown(message.author.id, "source", 20)

async def donateCommand(message, prefix):
    embed = discord.Embed(title="Donate", description=":moneybag: Bitcoin: `bc1qer5es59d62pvwdhaplgyltzd63kyyd0je2fhjm`\n:dog: Dogecoin: `D5Gy8ADPTbzGLD3qvpv4ZkNNrPMNkYX49j`", color=variables.embedColor)
    await message.channel.send(embed=embed)

async def dogeCommand(message, prefix):
    embed = discord.Embed(color=variables.embedColor)
    embed.set_image(url=client.user.avatar_url); await message.channel.send(embed=embed)

async def guildsCommand(message, prefix):
    if message.author.id == variables.botOwner:
        await message.channel.send(str(len(client.guilds)))
    else:
        await message.add_reaction("🚫")

async def smileyCommand(message, prefix):
    if prefix == "=" or prefix == ";":
        await message.channel.send(f"**{prefix}D**")

async def blacklistCommand(message, prefix):
    if message.author.id == variables.botOwner:
        arguments = message.content.split(" ")
        if len(arguments) >= 2:
            if arguments[1] == "list":
                blacklistedUsers = []
                blacklistFile = open("blacklist.json", "r"); rawArray = json.load(blacklistFile); blacklistFile.close()
                for user in rawArray:
                    blacklistedUsers.append(str(user))
                embed = discord.Embed(title="Blacklisted Users", description="\n".join(blacklistedUsers) if "\n".join(blacklistedUsers) != "" else "There are no blacklisted users", color=variables.embedColor)
                await message.channel.send(embed=embed)
            if arguments[1] == "add":
                if len(arguments) == 3:
                    try:
                        userID = int(arguments[2].replace("<@", "").replace("!", "").replace(">", ""))
                    except:
                        await message.channel.send("Please enter a valid user ID"); return
                    blacklistFile = open("blacklist.json", "r")
                    blacklistedUsers = json.load(blacklistFile); blacklistFile.close()
                    blacklistedUsers.append(userID)
                    blacklistFile = open("blacklist.json", "w")
                    json.dump(blacklistedUsers, blacklistFile)
                    blacklistFile.close()
                    await message.channel.send("Successfully added user to blacklist")
                else:
                    await message.channel.send(f"The syntax is `{prefix}blacklist <add/remove/list> <user>`"); return
            if arguments[1] == "remove":
                if len(arguments) == 3:
                    try:
                        userID = int(arguments[2].replace("<@", "").replace("!", "").replace(">", ""))
                    except:
                        await message.channel.send("Please enter a valid user ID"); return
                    blacklistFile = open("blacklist.json", "r")
                    blacklistedUsers = json.load(blacklistFile)
                    blacklistFile.close()
                    try:
                        blacklistedUsers.remove(userID)
                    except:
                        pass
                    blacklistFile = open("blacklist.json", "w")
                    json.dump(blacklistedUsers, blacklistFile)
                    blacklistFile.close()
                    await message.channel.send("Successfully removed user from blacklist")
                else:
                    await message.channel.send(f"The syntax is `{prefix}blacklist <add/remove/list> <user>`"); return
        else:
            await message.channel.send(f"The syntax is `{prefix}blacklist <add/remove/list> <user>`"); return
    else:
        await message.add_reaction("🚫")

async def memeCommand(message, prefix):
    response = requests.get("https://meme-api.herokuapp.com/gimme").json()
    description = f"Posted by **{response['author']}** in **{response['subreddit']}** (**{response['ups']}** upvotes)"
    embed = discord.Embed(title=response["title"], url=response["postLink"], description=description, color=variables.embedColor)
    embed.set_image(url=response["url"]); addCooldown(message.author.id, "meme", 5); await message.channel.send(embed=embed)

async def unmuteCommand(message, prefix):
    if message.author.guild_permissions.manage_roles or message.author.guild_permissions.administrator:
        pass
    else:
        await message.channel.send("You do not have permission to use this command"); return

    arguments = message.content.split(" ")
    if len(arguments) == 2:
        try:
            userID = int(arguments[1].replace("<@", "").replace(">", "").replace("!", ""))
            member = await message.guild.fetch_member(userID)
        except:
            await message.channel.send("Please enter a valid user ID"); return
        muteRole = None; exists = False
        for role in message.guild.roles:
            if "mute" in role.name.lower():
                muteRole = role; exists = True
        if exists:
            try:
                await member.remove_roles(muteRole)
            except:
                pass
        await message.channel.send(f"Successfully unmuted **{member}**")
    else:
        await message.channel.send(f"The syntax is `{prefix}unmute <user>`"); return

async def muteCommand(message, prefix):
    if message.author.guild_permissions.manage_roles or message.author.guild_permissions.administrator:
        pass
    else:
        await message.channel.send("You do not have permission to use this command"); return

    arguments = message.content.split(" ")
    if len(arguments) >= 2:
        muteRole = None; exists = False
        for role in message.guild.roles:
            if "mute" in role.name.lower():
                muteRole = role; exists = True
        if not exists:
            await setupMutedCommand(message, prefix)
        muteRole = None; exists = False
        for role in message.guild.roles:
            if "mute" in role.name.lower():
                muteRole = role; exists = True
        if not exists:
            await message.channel.send("Unable to find mute role"); return
        try:
            userID = int(arguments[1].replace("<@", "").replace(">", "").replace("!", ""))
            member = await message.guild.fetch_member(userID)
        except:
            await message.channel.send("Please enter a valid user ID"); return
    if len(arguments) == 2:
        try:
            await member.add_roles(muteRole)
        except:
            await message.channel.send(f"Unable to mute **{member}**"); return
        await message.channel.send(f"Successfully muted **{member}** permanently")
    elif len(arguments) == 3:
        try:
            duration = float(arguments[2])
        except:
            await message.channel.send("Please enter a valid duration (in minutes)"); return
        try:
            moderationData = moderationDatabase["mute." + str(message.guild.id)]
        except:
            moderationDatabase["mute." + str(message.guild.id)] = []
            moderationData = moderationDatabase["mute." + str(message.guild.id)]
        try:
            await member.add_roles(muteRole); moderationData.append([userID, time.time(), duration])
            moderationDatabase["mute." + str(message.guild.id)] = moderationData
        except:
            await message.channel.send(f"Unable to mute **{member}**"); return
        await message.channel.send(f"Successfully muted **{member}** for **{duration if round(duration) != 1 else round(duration)} {'minute' if round(duration) == 1 else 'minutes'}**")
    else:
        await message.channel.send(f"The syntax is `{prefix}mute <user> <duration>`"); return

async def insultsCommand(message, prefix):
    if message.author.guild_permissions.manage_messages:
        pass
    else:
        await message.channel.send("You do not have permission to use this command"); return

    arguments = message.content.split(" ")
    if len(arguments) >= 2:
        if arguments[1] == "list":
            try:
                insultsData = moderationDatabase[f"insults.list.{message.guild.id}"]
            except:
                insultsData = []
                moderationDatabase[f"insults.list.{message.guild.id}"] = []
            embed = discord.Embed(title="Insults List", description="There are no swear words configured for your server" if insultsData == [] else '\n'.join(insultsData), color=variables.embedColor)
            await message.channel.send(embed=embed)
        elif arguments[1] == "filter" or arguments[1] == "status":
            try:
                currentStatus = moderationDatabase[f"insults.toggle.{message.guild.id}"]
            except:
                currentStatus = False
            await message.channel.send(f"The insults filter is currently **{'enabled' if currentStatus else 'disabled'}**")
        elif arguments[1] == "enable":
            moderationDatabase[f"insults.toggle.{message.guild.id}"] = True
            await message.channel.send("The insults filter has been successfully **enabled**")
        elif arguments[1] == "disable":
            moderationDatabase[f"insults.toggle.{message.guild.id}"] = False
            await message.channel.send("The insults filter has been successfully **disabled**")
        elif arguments[1] == "add":
            if len(arguments) != 3:
                await message.channel.send(f"The syntax is `{prefix}insults add <word>`"); return
            try:
                insultsData = moderationDatabase[f"insults.list.{message.guild.id}"]
            except:
                insultsData = []
                moderationDatabase[f"insults.list.{message.guild.id}"] = []
            if len(insultsData) >= 50:
                await message.channel.send("You have reached the limit of **50 words**"); return
            insultsData.append(arguments[2])
            moderationDatabase[f"insults.list.{message.guild.id}"] = insultsData
            await message.channel.send(f"Successfully added **{arguments[2]}** to your insults list")
        elif arguments[1] == "remove" or arguments[1] == "delete":
            if len(arguments) != 3:
                await message.channel.send(f"The syntax is `{prefix}insults remove <word>`"); return
            try:
                insultsData = moderationDatabase[f"insults.list.{message.guild.id}"]
            except:
                insultsData = []
                moderationDatabase[f"insults.list.{message.guild.id}"] = []
            try:
                insultsData.remove(arguments[2])
            except:
                await message.channel.send("That word does not exist in the insults filter"); return
            moderationDatabase[f"insults.list.{message.guild.id}"] = insultsData
            await message.channel.send(f"Successfully removed **{arguments[2]}** from the insults list")
    else:
        await message.channel.send(f"The syntax is `{prefix}insults <add/remove/enable/disable/list/status>`"); return

async def linksCommand(message, prefix):
    if not message.author.guild_permissions.administrator:
        await message.channel.send("You do not have permission to use this command"); return
        
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        if arguments[1] == "enable":
            moderationDatabase[f"links.toggle.{message.guild.id}"] = True
            await message.channel.send("The links filter has been successfully **enabled**")
        elif arguments[1] == "disable":
            moderationDatabase[f"links.toggle.{message.guild.id}"] = False
            await message.channel.send("The links filter has been successfully **disabled**")
        elif arguments[1] == "status" or arguments[1] == "filter":
            value = False
            try:
                value = moderationDatabase[f"links.toggle.{message.guild.id}"]
            except:
                pass
            await message.channel.send(f"The links filter is currently **{'enabled' if value else 'disabled'}**")
    else:
        await message.channel.send(f"The syntax is `{prefix}links <enable/disable/status>`"); return

async def spammingCommand(message, prefix):
    if not message.author.guild_permissions.administrator:
        await message.channel.send("You do not have permission to use this command"); return
        
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        if arguments[1] == "enable":
            moderationDatabase[f"spamming.toggle.{message.guild.id}"] = True
            await message.channel.send("The spam filter has been successfully **enabled**")
        elif arguments[1] == "disable":
            moderationDatabase[f"spamming.toggle.{message.guild.id}"] = False
            await message.channel.send("The spam filter has been successfully **disabled**")
        elif arguments[1] == "set":
            if len(arguments) > 2:
                try:
                    limit = int(arguments[2])
                except:
                    await message.channel.send("Please enter a valid number!"); return
            moderationDatabase[f"spamming.limit.{message.guild.id}"] = limit
            await message.channel.send(f"The spam filter limit has been set to **{limit} {'message' if limit == 1 else 'messages'}** per **15 seconds**")
        elif arguments[1] == "status" or arguments[1] == "filter" or arguments[1] == "limit":
            value = False
            try:
                value = moderationDatabase[f"spamming.toggle.{message.guild.id}"]
            except:
                pass
            limit = 6
            try:
                limit = moderationDatabase[f"spamming.limit.{message.guild.id}"]
            except:
                pass
            await message.channel.send(f"The spam filter is currently **{'enabled' if value else 'disabled'}** (limit is **{limit}**)")
    else:
        await message.channel.send(f"The syntax is `{prefix}spamming <enable/disable/set/status>`"); return

async def welcomeCommand(message, prefix):
    if not message.author.guild_permissions.administrator:
        await message.channel.send("You do not have permission to use this command"); return
        
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        if arguments[1] == "enable":
            try:
                moderationDatabase[f"welcome.text.{message.guild.id}"]
            except:
                await message.channel.send(f"Please set a welcome message with `{prefix}welcome set <text>` first"); return
            try:
                channelID = moderationDatabase[f"welcome.channel.{message.guild.id}"]
                found = False
                for channel in message.guild.channels:
                    if channel.id == channelID:
                        found = True
                if not found:
                    raise Exception("unable to find channel")
            except:
                await message.channel.send(f"Please set a welcome channel with `{prefix}welcome channel <channel>` first"); return

            moderationDatabase[f"welcome.toggle.{message.guild.id}"] = True
            await message.channel.send("Welcome messages have been successfully **enabled**")
        elif arguments[1] == "disable":
            moderationDatabase[f"welcome.toggle.{message.guild.id}"] = False
            await message.channel.send("Welcome messages have been successfully **disabled**")
        elif arguments[1] == "set" or arguments[1] == "text":
            text = ""
            if len(arguments) > 2:
                for i in range(2):
                    arguments.pop(0)
                text = ' '.join(arguments)
            else:
                await message.channel.send(f"The syntax is `{prefix}welcome set <text>`"); return
            moderationDatabase[f"welcome.text.{message.guild.id}"] = text
            await message.channel.send(f"The welcome message has been set to\n```\n{text}```\n" + "Variables like `{user}`, `{userID}`, `{discriminator}`, and `{members}` are also supported")
        elif arguments[1] == "channel":
            channelID = 0
            if len(arguments) > 2:
                try:
                    channelID = int(arguments[2].replace("<#", "").replace("!", "").replace(">", ""))
                except:
                    await message.channel.send("That channel does not exist in this server"); return
            else:
                await message.channel.send(f"The syntax is `{prefix}welcome channel <channel>`"); return
            moderationDatabase[f"welcome.channel.{message.guild.id}"] = channelID
            await message.channel.send(f"The welcome channel for this server has been set to <#{channelID}>")
        elif arguments[1] == "status" or arguments[1] == "filter" or arguments[1] == "limit":
            value = False
            try:
                value = moderationDatabase[f"welcome.toggle.{message.guild.id}"]
            except:
                pass
            text = "There is nothing here..."
            try:
                text = moderationDatabase[f"welcome.text.{message.guild.id}"]
            except:
                pass
            channelID = "**#unknown-channel**"
            try:
                channelID = "<#" + str(moderationDatabase[f"welcome.channel.{message.guild.id}"]) + ">"
            except:
                pass
            await message.channel.send(f"Welcome messages are currently **{'enabled' if value else 'disabled'}** and set to {channelID}\n```\n{text}```")
    else:
        await message.channel.send(f"The syntax is `{prefix}welcome <enable/disable/channel/set/status>`"); return

async def leaveCommand(message, prefix):
    if not message.author.guild_permissions.administrator:
        await message.channel.send("You do not have permission to use this command"); return
        
    arguments = message.content.split(" ")
    if len(arguments) > 1:
        if arguments[1] == "enable":
            try:
                moderationDatabase[f"leave.text.{message.guild.id}"]
            except:
                await message.channel.send(f"Please set a leave message with `{prefix}leave set <text>` first"); return
            try:
                channelID = moderationDatabase[f"leave.channel.{message.guild.id}"]
                found = False
                for channel in message.guild.channels:
                    if channel.id == channelID:
                        found = True
                if not found:
                    raise Exception("unable to find channel")
            except:
                await message.channel.send(f"Please set a leave channel with `{prefix}leave channel <channel>` first"); return

            moderationDatabase[f"leave.toggle.{message.guild.id}"] = True
            await message.channel.send("Leave messages have been successfully **enabled**")
        elif arguments[1] == "disable":
            moderationDatabase[f"leave.toggle.{message.guild.id}"] = False
            await message.channel.send("Leave messages have been successfully **disabled**")
        elif arguments[1] == "set" or arguments[1] == "text":
            text = ""
            if len(arguments) > 2:
                for i in range(2):
                    arguments.pop(0)
                text = ' '.join(arguments)
            else:
                await message.channel.send(f"The syntax is `{prefix}leave set <text>`"); return
            moderationDatabase[f"leave.text.{message.guild.id}"] = text
            await message.channel.send(f"The leave message has been set to\n```\n{text}```\n" + "Variables like `{user}`, `{userID}`, `{discriminator}`, and `{members}` are also supported")
        elif arguments[1] == "channel":
            channelID = 0
            if len(arguments) > 2:
                try:
                    channelID = int(arguments[2].replace("<#", "").replace("!", "").replace(">", ""))
                except:
                    await message.channel.send("That channel does not exist in this server"); return
            else:
                await message.channel.send(f"The syntax is `{prefix}leave channel <channel>`"); return
            moderationDatabase[f"leave.channel.{message.guild.id}"] = channelID
            await message.channel.send(f"The leave channel for this server has been set to <#{channelID}>")
        elif arguments[1] == "status" or arguments[1] == "filter" or arguments[1] == "limit":
            value = False
            try:
                value = moderationDatabase[f"leave.toggle.{message.guild.id}"]
            except:
                pass
            text = "There is nothing here..."
            try:
                text = moderationDatabase[f"leave.text.{message.guild.id}"]
            except:
                pass
            channelID = "**#unknown-channel**"
            try:
                channelID = "<#" + str(moderationDatabase[f"leave.channel.{message.guild.id}"]) + ">"
            except:
                pass
            await message.channel.send(f"Leave messages are currently **{'enabled' if value else 'disabled'}** and set to {channelID}\n```\n{text}```")
    else:
        await message.channel.send(f"The syntax is `{prefix}leave <enable/disable/channel/set/status>`"); return

async def snipeCommand(message, prefix):
    addCooldown(message.author.id, "snipe", 1)
    arguments = message.content.split(" ")
    if len(arguments) == 1:
        try:
            randomMessage = random.choice(snipeList[message.guild.id])
            messageAuthor = f"{randomMessage[0]}#{randomMessage[1]}"
            messageAuthorAvatar = randomMessage[2]; channelName = randomMessage[3]
            messageSentTime = randomMessage[4]; messageData = randomMessage[5]
            embed = discord.Embed(description=messageData, color=variables.embedColor, timestamp=messageSentTime)
            embed.set_author(name=messageAuthor, icon_url=messageAuthorAvatar); embed.set_footer(text=f"Sent in #{channelName}")
            await message.channel.send(embed=embed)
        except:
            await message.channel.send("There is nothing to snipe!")
    elif len(arguments) > 1:
        if arguments[1] == "enable":
            if not message.author.guild_permissions.administrator:
                await message.channel.send("You do not have permission to use this command"); return

            settingsDatabase[f"snipe|{message.guild.id}"] = True
            await message.channel.send("Snipe has been **enabled** for this server")
        elif arguments[1] == "disable":
            if not message.author.guild_permissions.administrator:
                await message.channel.send("You do not have permission to use this command"); return

            settingsDatabase[f"snipe|{message.guild.id}"] = False
            await message.channel.send("Snipe has been **disabled** for this server")
        elif arguments[1] == "clear":
            if not message.author.guild_permissions.administrator:
                await message.channel.send("You do not have permission to use this command"); return

            snipeList[message.guild.id] = []
            await message.channel.send("The snipe list for this server has been successfully cleared")
        elif arguments[1] == "status":
            value = False
            try:
                value = settingsDatabase[f"snipe|{message.guild.id}"]
            except:
                pass
            await message.channel.send(f"Snipe is currently **{'enabled' if value else 'disabled'}** for this server")

async def jokeCommand(message, prefix):
    addCooldown(message.author.id, "joke", 3)
    response = requests.get("https://official-joke-api.appspot.com/random_joke").json()
    embed = discord.Embed(description=f"Here's a `{response['type']}` joke:\n{response['setup']} **{response['punchline']}**", color=variables.embedColor)
    await message.channel.send(embed=embed)

async def membersCommand(message, prefix):
    users = 0; bots = 0
    for member in message.guild.members:
        if member.bot:
            bots += 1
        else:
            users += 1
    embed = discord.Embed(
        title="Guild Members",
        description=f"User accounts: **{users}**\nBot accounts: **{bots}**\nTotal members: **{users + bots}**",
        color=variables.embedColor
    )
    await message.channel.send(embed=embed)

async def githubCommand(message, prefix):
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
        embed = discord.Embed(color=variables.embedColor)
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
        embed.add_field(name="Date", value=f"<t:{str(parser.isoparse(response['created_at']).timestamp()).split('.')[0]}:d>")
        embed.add_field(name="Description", value=f"{response['description']}")
        embed.set_thumbnail(url=response["owner"]["avatar_url"])
        await message.channel.send(embed=embed)
        addCooldown(message.author.id, "github", 8)
    else:
        await message.channel.send(f"The syntax is `{prefix}github <repository>`")

async def chooseCommand(message, prefix):
    arguments = message.content.split(" ")
    if len(arguments) >= 2:
        arguments.pop(0)
        randomItem = random.choice(' '.join(arguments).replace(", ", ",").split(","))
        await message.channel.send(f"I choose **{randomItem}**")
    else:
        await message.channel.send(f"The syntax is `{prefix}choose <item>, <item>`")

async def triviaCommand(message, prefix):
    addCooldown(message.author.id, "trivia", 12)
    url = f"https://opentdb.com/api.php?amount=1&type=multiple&category={random.randint(9, 33)}&difficulty={random.choice(['easy', 'medium', 'hard'])}"
    response = requests.get(url).json()
    description = f"**{html.unescape(response['results'][0]['question'])}**\nCategory: `{response['results'][0]['category']}` (**{response['results'][0]['difficulty']}** difficulty)"
    answers = response['results'][0]['incorrect_answers']
    answers.append(response['results'][0]['correct_answer'])
    correctAnswer = html.unescape(response['results'][0]['correct_answer'])
    buttons = [[]]
    for i in range(len(answers)):
        answer = html.unescape(random.choice(answers)); answers.remove(answer)
        buttons[0].append(discord_components.Button(style=discord_components.ButtonStyle.gray, label=answer))
    embed = discord.Embed(
        description=description,
        color=variables.embedColor,
    )
    oldMessage = await message.channel.send(embed=embed, components=buttons)
    while True:
        result = await client.wait_for("button_click")
        if result.channel == message.channel:
            if result.author == message.author:
                if result.component.label == correctAnswer:
                    await result.respond(type=4, content="Correct answer!")
                else:
                    await result.respond(type=4, content=f"Incorrect answer... The correct answer was **{correctAnswer}**.")
                newButtons = [[]]
                for oldButton in buttons[0]:
                    if oldButton.label == correctAnswer:
                        newButton = discord_components.Button(style=discord_components.ButtonStyle.green, label=oldButton.label, disabled=True)
                    else:
                        newButton = discord_components.Button(style=discord_components.ButtonStyle.red, label=oldButton.label, disabled=True)
                    newButtons[0].append(newButton)
                await oldMessage.edit(embed=embed, components=newButtons)
                break
            else:
                await result.respond(type=4, content="You are not the sender of the command!")

async def helpCommand(message, prefix):
    pages = {}; currentPage = 1; pageLimit = 10; currentItem = 0; index = 1; pageArguments = False
    try:
        currentPage = int(message.content.split(" ")[1])
        pageArguments = True
    except:
        try:
            currentPage = message.content.split(" ")[1]
        except:
            pageArguments = True
            pass
    if pageArguments:
        for command in commandList:
            if command.name in hiddenCommands:
                continue
            temporaryText = f"`{prefix}{command.usage}` - {command.description}\n"
            if index > pageLimit:
                index = 0
                currentItem += 1
            try:
                pages[currentItem] += temporaryText
            except:
                pages[currentItem] = temporaryText
            index += 1
        try:
            helpPage = pages[currentPage - 1]
        except:
            helpPage = "That page doesn't exist or wasn't found"
            currentPage = 0
        embed = discord.Embed(title="Doge Commands", description=helpPage, color=variables.embedColor, timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"Viewing help page {currentPage} of {len(pages)}")
        await message.channel.send(embed=embed); addCooldown(message.author.id, "help", 1.5)
    else:
        for command in commandList:
            if command.name in hiddenCommands:
                continue
            if command.name == currentPage:
                commandArguments = command.usage.split(" "); commandArguments.pop(0)
                commandArguments = ' '.join(commandArguments)
                if commandArguments == "":
                    commandArguments = "None"
                commandExample = prefix + parseVariables(command.usage)
                additionalArguments = ""
                if commandArguments != "None":
                    additionalArguments = f"\nAdditional arguments: `{commandArguments}`"
                command = f"Command: `{prefix}{command.name}`{additionalArguments}\nUsage example: `{commandExample}`\n\n**{command.description}**"
                embed = discord.Embed(title="Doge Commands", description=command, color=variables.embedColor, timestamp=datetime.datetime.utcnow())
                embed.set_footer(text=f"Viewing command help page")
                await message.channel.send(embed=embed); return
        embed = discord.Embed(title="Doge Commands", description="That command doesn't exist or wasn't found", color=variables.embedColor, timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"Viewing command help page")
        await message.channel.send(embed=embed); addCooldown(message.author.id, "help", 1.5)

def epochToDate(epoch):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))

def dateToEpoch(timestamp):
    timestamp = timestamp.replace("Today", str(datetime.datetime.now().date()))
    date = timestamp.split(" ")[0]; time = timestamp.split(" ")[1]
    dateParts = date.split("-"); timeParts = time.split(":")
    for i in range(len(dateParts)):
        dateParts[i] = int(dateParts[i])
    for i in range(len(timeParts)):
        timeParts[i] = int(timeParts[i])
    year = dateParts[0]; month = dateParts[1]; day = dateParts[2]
    hour = timeParts[0]; minute = timeParts[1]; second = timeParts[2]
    epoch = datetime.datetime(year, month, day, hour, minute, second).timestamp()
    return int(epoch)

def hashText(hashType, inputText):
    hasher = hashlib.new(hashType)
    hasher.update(inputText.encode("utf-8"))
    return hasher.hexdigest()

def getVariable(name):
    try:
        return mathVariables[name]
    except:
        return 0

def setVariable(name, value):
    mathVariables[name] = value

def evaluateExpression(expression):
    expression = expression.replace("^", "**")

    mathFunctions = {
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
        "get": lambda name: getVariable(name),
        "set": lambda name, value: setVariable(name, value)
    }

    try:
        answer = str(simpleeval.simple_eval(expression, functions=mathFunctions))
    except:
        answer = "Unknown Answer"
    return answer

def rgbToHex(rgbColor):
    for value in rgbColor:
        if value >= 0 and value <= 255:
            pass
        else:
            raise Exception("invalid RGB color code")
    return '#%02x%02x%02x' % rgbColor

def generateColor(colorCode):
    imageWidth = 180; imageHeight = 80
    colorCode = colorCode.replace("rgb", "")
    if len(colorCode) == 8 and colorCode.startswith("0x"):
        colorCode = colorCode[2:]
        colorCode = "#" + colorCode
    if len(colorCode) == 6:
        colorCode = "#" + colorCode
    
    if not colorCode.startswith("#") and not colorCode.count(",") == 2:
        try:
            colorCode = colorCode.replace(" ", "_")
            colorCode = str(eval("discord.Color." + colorCode + "()"))
        except:
            pass

    if colorCode.startswith("#") and len(colorCode) == 7:
        try:
            image = Image.new("RGB", (imageWidth, imageHeight), colorCode)
            image.save("images/color.png"); value = colorCode.lstrip('#'); length = len(value)
            rgbColor = tuple(int(value[i:i+length//3], 16) for i in range(0, length, length//3))
            return (colorCode, rgbColor)
        except:
            return 1
    elif colorCode.count(",") == 2 and "(" in colorCode and ")" in colorCode:
        try:
            colorCode = colorCode.replace("(", ""); colorCode = colorCode.replace(")", "")
            colorCode = colorCode.replace(", ", ","); rgbColor = tuple(map(int, colorCode.split(',')))
            colorCode = rgbToHex(rgbColor); image = Image.new("RGB", (imageWidth, imageHeight), colorCode)
            image.save("images/color.png"); return (colorCode, rgbColor)
        except:
            return 1
    else:
        return 1

async def sendUserMessage(userID, message):
    for guild in client.guilds:
        try:
            member = await guild.fetch_member(int(userID))
            await member.send(message); return
        except:
            continue

async def on_member_join(member):
    try:
        autoroles = autoroleDatabase[member.guild.id]
        for role in member.guild.roles:
            for roleID in autoroles:
                if int(roleID) == role.id:
                    await member.add_roles(role)
    except:
        pass
    try:
        if moderationDatabase[f"welcome.toggle.{member.guild.id}"]:
            welcomeMessage = moderationDatabase[f"welcome.text.{member.guild.id}"]
            welcomeChannel = moderationDatabase[f"welcome.channel.{member.guild.id}"]
            for channel in member.guild.channels:
                if welcomeChannel == channel.id:
                    welcomeMessage = welcomeMessage.replace("{user}", member.name)
                    welcomeMessage = welcomeMessage.replace("{userID}", str(member.id))
                    welcomeMessage = welcomeMessage.replace("{user.id}", str(member.id))
                    welcomeMessage = welcomeMessage.replace("{user_id}", str(member.id))
                    welcomeMessage = welcomeMessage.replace("{discriminator}", member.discriminator)
                    welcomeMessage = welcomeMessage.replace("{members}", str(member.guild.member_count))
                    welcomeMessage = welcomeMessage.replace("{server}", member.guild.name)
                    await channel.send(welcomeMessage)
    except:
        pass

async def on_member_remove(member):
    try:
        if moderationDatabase[f"leave.toggle.{member.guild.id}"]:
            leaveMessage = moderationDatabase[f"leave.text.{member.guild.id}"]
            leaveChannel = moderationDatabase[f"leave.channel.{member.guild.id}"]
            for channel in member.guild.channels:
                if leaveChannel == channel.id:
                    leaveMessage = leaveMessage.replace("{user}", member.name)
                    leaveMessage = leaveMessage.replace("{userID}", str(member.id))
                    leaveMessage = leaveMessage.replace("{user.id}", str(member.id))
                    leaveMessage = leaveMessage.replace("{user_id}", str(member.id))
                    leaveMessage = leaveMessage.replace("{discriminator}", member.discriminator)
                    leaveMessage = leaveMessage.replace("{members}", str(member.guild.member_count))
                    leaveMessage = leaveMessage.replace("{server}", member.guild.name)
                    await channel.send(leaveMessage)
    except:
        pass

async def on_guild_join(guild):
    try:
        async for entry in guild.audit_logs(limit=10):
            if entry.action == discord.AuditLogAction.bot_add:
                if entry.target.id == client.user.id:
                    embed = discord.Embed(
                        title="Hello there",
                        color=variables.embedColor,
                        description="Thank you for inviting me to your server! My name is **Doge Utilities**, and I am a Discord utility bot that can help you with all sorts of tasks. My default prefix is `=`, if you would like to change this, simply type `=prefix <new prefix>` and click the \"Yes\" button. To see the help page (or list of commands), type `=help`. I have a **lot** of commands, so you might have to do `=help 2` or `=help 3` to see more commands that can't fit on a single page. Some of the most used tools that I have are `=raid-protection`, `=setup-muted`, `=setup-banned`, `=autorole`, `=lookup`, `=mute`, `=color`, `=permissions`, and `=insults`. Feel free to try them out! If you have issues or need help with a few commands, please join the [official support server](https://discord.gg/3Tp7R8FUsC). Once again, thank you for inviting Doge Utilities!"
                    )
                    await entry.user.send(embed=embed)
                    break
    except:
        pass

async def on_message_delete(message, *arguments):
    if len(arguments) > 0:
        await on_message(arguments[0])

    if not message.guild:
        return

    value = True
    try:
        value = settingsDatabase[f"snipe|{message.guild.id}"]
    except:
        pass
    if not value:
        return

    try:
        snipes = snipeList[message.guild.id]
    except:
        snipes = []
        snipeList[message.guild.id] = []
    while len(snipes) >= 10:
        randomSnipe = random.choice(snipes)
        snipes.remove(randomSnipe)

    messageData = message.content
    if messageData == "":
        if len(message.embeds) > 0:
            messageData = message.embeds[0].description
    if messageData != "" or messageData != discord.Embed.Empty:
        snipes.append([
            message.author.name,
            message.author.discriminator,
            message.author.avatar_url,
            message.channel.name,
            datetime.datetime.utcnow(),
            messageData,
        ])
        snipeList[message.guild.id] = snipes

async def on_message(message):
    try:
        if message.author.bot:
            return

        if message.guild:
            prefix = "="
            try:
                prefix = prefixDatabase[message.guild.id]
            except:
                prefixDatabase[message.guild.id] = "="
        else:
            return

        if message.content == f"<@{client.user.id}>" or message.content == f"<@!{client.user.id}>":
            await message.channel.send(f"My prefix here is `{prefix}`")
            lastCommand = open("last-command", "w")
            lastCommand.write(str(round(time.time()))); lastCommand.close()
            return

        if not message.author.guild_permissions.administrator:
            try:
                if moderationDatabase[f"insults.toggle.{message.guild.id}"]:
                    insults = moderationDatabase[f"insults.list.{message.guild.id}"]
                    for word in insults:
                        if word.lower() in message.content.lower():
                            await message.delete()
                            await message.author.send(f"Please do not use that word (**{word.lower()}**)!")
                            return
            except:
                pass
            try:
                if moderationDatabase[f"links.toggle.{message.guild.id}"]:
                    linkRegexes = ["http://", "https://", "www.", "discord.gg/"]
                    for regex in linkRegexes:
                        if regex in message.content.lower():
                            await message.delete()
                            await message.author.send("Please do not put links in your message!")
                            return
            except:
                pass
            try:
                if "spam" not in message.channel.name:
                    if moderationDatabase[f"spamming.toggle.{message.guild.id}"]:
                        try:
                            lastMessageTime = lastMessages[message.author.id]
                        except:
                            lastMessageTime = 0
                        if (time.time() - lastMessageTime) < 15:
                            try:
                                strikes = messageStrikes[message.author.id]
                            except:
                                strikes = 0
                            messageStrikes[message.author.id] = strikes + 1
                            strikeLimit = 6
                            try:
                                strikeLimit = moderationDatabase[f"spamming.limit.{message.guild.id}"]
                            except:
                                pass
                            if strikeLimit > 30:
                                strikeLimit = 30
                            if strikes >= strikeLimit:
                                await message.delete()
                                await message.author.send("Stop spamming!")
                                return
            except:
                pass
        lastMessages[message.author.id] = time.time()

        if message.content.startswith(prefix) and len(message.content) > 1:
            lastCommand = open("last-command", "w")
            lastCommand.write(str(round(time.time()))); lastCommand.close()
        else:
            return

        blacklistFile = open("blacklist.json", "r")
        blacklistedUsers = json.load(blacklistFile)
        blacklistFile.close()
        if message.author.id in blacklistedUsers:
            await message.reply("You are banned from using Doge Utilities"); return

        for command in commandList:
            callCommand = False
            if len(command.aliases) > 0:
                for alias in command.aliases:
                    if " " not in message.content:
                        if message.content == f"{prefix}{alias}":
                            message.content = f"{prefix}{command.name}"
                    else:
                        message.content = message.content.replace(f"{prefix}{alias} ", f"{prefix}{command.name} ")
            if message.content.startswith(prefix + command.name):
                callCommand = True

            if callCommand:
                await message.channel.trigger_typing()
                if getCooldown(message.author.id, command.name) > 0:
                    cooldownString = generateCooldown(command.name, getCooldown(message.author.id, command.name))
                    embed = discord.Embed(title="Command Cooldown", description=cooldownString, color=variables.embedColor)
                    await message.channel.send(embed=embed); return
                await command.function(message, prefix); return
    except Exception as error:
        if "50035" in str(error):
            await message.channel.send("Message too long to be sent!"); return
        elif "Interaction is unknown" in str(error):
            await message.channel.send("That interaction is already used!"); return

        escapedCharacter = '\`'
        for userID in variables.messageManagers:
            member = None
            for guild in client.guilds:
                try:
                    member = await guild.fetch_member(userID)
                    break
                except:
                    continue
            if member:
                try:
                    await member.send(f"**{message.author.name}#{message.author.discriminator}** (**`{message.author.id}`**) has ran into an error in **{message.author.guild.name}** (**`{message.author.guild.id}`**):\n\n**Message:**\n```\n{message.content.replace('`', escapedCharacter)}\n```**Error:**\n```\n{str(''.join(traceback.format_exception(error, error, error.__traceback__))).replace('`', escapedCharacter)}\n```")
                except:
                    pass

        embed = discord.Embed(title="Bot Error", description=f"Uh oh! Doge Utilities has ran into an error!\nThis error has been sent to our bot creators.\n```\n{error}\n```", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        embed.set_footer(text="Doge Utilities error report"); await message.reply(embed=embed); return "error"

hiddenCommands = ["execute;", "reload", "guilds", "D", "blacklist"]
commandList = [
    Command("D", [], smileyCommand, "D", "=D"),
    Command("execute;", [], executeCommand, "execute;<code>", "System Command"),
    Command("reload", [], reloadCommand, "reload", "System Command"),
    Command("guilds", ["servers"], guildsCommand, "guilds", "System Command"),
    Command("blacklist", [], blacklistCommand, "blacklist <add/remove/list>", "System Command"),
    Command("help", ["h", "commands"], helpCommand, "help", "Displays a help page for Doge Utilities"),
    Command("ping", ["pong"], pingCommand, "ping", "Display the bot's current latency"),
    Command("status", ["stats"], statusCommand, "status", "Show the bot's current statistics"),
    Command("support", [], supportCommand, "support", "Display the official Discord server for Doge"),
    Command("tests", [], testsCommand, "tests", "Run a series of tests to diagnose Doge"),
    Command("source", ["src"], sourceCommand, "source", "Display a link to Doge Utilities' code"),
    Command("vote", ["upvote"], voteCommand, "vote", "Display a link to upvote Doge Utilities"),
    Command("donate", [], donateCommand, "donate", "Donate to the creators of Doge Utilities"),
    Command("version", ["ver"], versionCommand, "version", "Display the bot's current version"),
    Command("prefix", ["setprefix", "changeprefix"], prefixCommand, "prefix", "Change the bot's prefix on this server"),
    Command("doge", ["dog"], dogeCommand, "doge", "D O G E"),
    Command("invite", ["inv"], inviteCommand, "invite", "Invite this bot to another server"),
    Command("shards", [], shardsCommand, "shards <page>", "View information about Doge's shards"),
    Command("setup-muted", [], setupMutedCommand, "setup-muted", "Generate a role that mutes members"),
    Command("setup-banned", [], setupBannedCommand, "setup-banned", "Generate a role that disables access to channels"),
    Command("random", ["rand"], randomCommand, "random <low> <high>", "Generate a random number within the range"),
    Command("disconnect-members", ["disconnect-users"], disconnectMembersCommand, "disconnect-members", "Disconnect all the members in voice channels"),
    Command("suggest", [], suggestCommand, "suggest <suggestion>", "Send a suggestion to the bot creators"),
    Command("autorole", [], autoroleCommand, "autorole <role>", "Change the role that is automatically given to users"),
    Command("lookup", ["ui", "userinfo"], lookupCommand, "lookup <user>", "Display profile information for the specified user"),
    Command("clear", ["purge"], clearCommand, "clear <messages>", "Delete the specified amount of messages"),
    Command("raid-protection", ["raidp"], raidProtectionCommand, "raid-protection <on/off>", "Toggle server's raid protection"),
    Command("wide", [], wideCommand, "wide <text>", "Add spaces to every character in the text"),
    Command("unwide", [], unwideCommand, "unwide <text>", "Remove spaces from every character in the text"),
    Command("cringe", [], cringeCommand, "cringe <text>", "Randomly change the cases of the text"),
    Command("spoiler", [], spoilerCommand, "spoiler <text>", "Add spoilers to every character in the text"),
    Command("reverse", [], reverseCommand, "reverse <text>", "Reverse the specified text (last character first)"),
    Command("corrupt", [], corruptCommand, "corrupt <text>", "Make the specified text appear to be corrupted"),
    Command("epoch-date", [], epochDateCommand, "epoch-date <epoch>", "Convert an epoch timestamp into a date"),
    Command("base64", ["b64"], base64Command, "base64 <encode/decode> <text>", "Convert the text to/from base64"),
    Command("date-epoch", [], dateEpochCommand, "date-epoch <date>", "Covert a date into an epoch timestamp"),
    Command("hash", [], hashCommand, "hash <type> <text>", "Hash the text object with the specified type"),
    Command("meme", [], memeCommand, "meme", "Search for a meme on Reddit and display it as an embed"),
    Command("snipe", [], snipeCommand, "snipe <enable/disable>", "Restore and bring deleted messages back to life"),
    Command("calculate", ["calc"], calculateCommand, "calculate <expression>", "Calculate the specified math expression"),
    Command("color", ["colour"], colorCommand, "color <color code>", "Display information about the color code"),
    Command("permissions", ["perms"], permissionsCommand, "permissions <user>", "Display the permissions for the specified user"),
    Command("time", ["date"], timeCommand, "time <timezone>", "Display the current time for the specified timezone"),
    Command("binary", ["bin"], binaryCommand, "binary <encode/decode> <text>", "Convert the text to/from binary"),
    Command("nickname", ["nick"], nicknameCommand, "nickname <user> <nickname>", "Change or update a user's nickname"),
    Command("currency", ["cur"], currencyCommand, "currency <amount> <currency> <currency>", "Convert currencies"),
    Command("stackoverflow", ["so"], stackoverflowCommand, "stackoverflow <text>", "Search for code help on StackOverflow"),
    Command("mute", [], muteCommand, "mute <user> <minutes>", "Mute the specified member for the specified duration"),
    Command("unmute", [], unmuteCommand, "unmute <user>", "Unmute the specified member on the current guild"),
    Command("github", ["gh", "repo", "git"], githubCommand, "github <repository>", "Display information about a GitHub repository"),
    Command("insults", [], insultsCommand, "insults <add/remove/enable/disable/list>", "Modify the insults filter"),
    Command("links", [], linksCommand, "links <enable/disable>", "Enable or disable the link/advertisement filter"),
    Command("spam", [], spammingCommand, "spamming <enable/disable/set>", "Enable or disable the spam filter"),
    Command("welcome", [], welcomeCommand, "welcome <enable/disable/channel/set>", "Modify the welcome messages"),
    Command("leave", [], leaveCommand, "leave <enable/disable/channel/set>", "Modify the leave messages"),
    Command("choose", [], chooseCommand, "choose <item>, <item>", "Choose a random item from the specified list"),
    Command("joke", ["dadjoke"], jokeCommand, "joke", "Display a funny random joke from a random category"),
    Command("members", ["users", "membercount"], membersCommand, "members", "Display information about this guild's members"),
    Command("trivia", ["quiz"], triviaCommand, "trivia", "Display a random trivia question from a random category"),
]
