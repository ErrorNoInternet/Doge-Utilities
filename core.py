import os
import io
import re
import sys
import json
import html
import pytz
import time
import math
import redis
import extra
import qrcode
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
import language
import functions
import converter
import threading
import variables
import traceback
import simpleeval
import contextlib
import googletrans
import disnake_paginator

from PIL import Image
from typing import List
from dateutil import parser
from disnake.ext import commands
from disnake.ext.commands import Param

def get_vote_view(text="Add a reminder"):
    class VoteView(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.timeout = None

        @disnake.ui.button(label=text, style=disnake.ButtonStyle.green, custom_id="vote-reminder-button")
        async def add_reminder(self, button, interaction):
            duration = 43200
            text = functions.get_text(interaction.author.id, "vote_again")
            try:
                current_reminders = json.loads(database[f"reminders.{interaction.author.id}"])
            except:
                current_reminders = []
            exists = False
            for reminder in current_reminders:
                if reminder[1] == duration and reminder[2] == text:
                    exists = True
            if exists:
                await interaction.response.send_message(functions.get_text(interaction.author.id, "vote_reminder_exists"))
                return
            if len(current_reminders) >= 5:
                await interaction.response.send_message(functions.get_text(interaction.author.id, "item_limit").format("5"))
                return
            current_reminders.append([round(time.time()), duration, text])
            database[f"reminders.{interaction.author.id}"] = json.dumps(current_reminders)
            button.disabled = True
            await interaction.message.edit(view=self)
            await interaction.response.send_message(functions.get_text(interaction.author.id, "vote_reminder_added"))
    return VoteView()

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
                                                await member.send(f"**{functions.get_text(member.id, 'reminder')}:** {text}")
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
math_variables = {}
user_cooldowns = {}
message_strikes = {}
last_messages = {}
used_commands = []
ToggleOption = commands.option_enum(["enable", "disable"])
FilterOption = commands.option_enum(list(variables.filters.keys()))
required_intents = disnake.Intents.default()
required_intents.members = True
required_intents.messages = True
client = commands.AutoShardedBot(
    max_messages=2048,
    shard_count=variables.shard_count,
    intents=required_intents,
    test_guilds=variables.test_guilds,
    sync_permissions=True,
)
database = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.getenv("REDIS_PASSWORD"),
)
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
help_paginator = disnake_paginator.ButtonPaginator(
    title="Getting Started",
    color=variables.embed_color(),
    timeout=600,
    segments=[variables.help_text[i: i + 1000] for i in range(0, len(variables.help_text), 1000)],
    invalid_user_function=functions.invalid_user_function,
)

def parse_status_variables(text):
    text = text.replace("[users]", f"{len(list(client.get_all_members())):,}")
    text = text.replace("[servers]", f"{len(client.guilds):,}")
    return text

async def select_status():
    client_status = disnake.Status.online; status_type = random.choice(variables.status_types)
    if status_type == "Playing":
        status_text = parse_status_variables(random.choice(variables.status1))
        await client.change_presence(status=client_status, activity=disnake.Activity(type=disnake.ActivityType.playing, name=status_text))
    elif status_type == "Watching":
        status_text = parse_status_variables(random.choice(variables.status2))
        await client.change_presence(status=client_status, activity=disnake.Activity(type=disnake.ActivityType.watching, name=status_text))
    elif status_type == "Listening":
        status_text = parse_status_variables(random.choice(variables.status3))
        await client.change_presence(status=client_status, activity=disnake.Activity(type=disnake.ActivityType.listening, name=status_text))
    elif status_type == "Competing":
        status_text = parse_status_variables(random.choice(variables.status4))
        await client.change_presence(status=client_status, activity=disnake.Activity(type=disnake.ActivityType.competing, name=status_text))

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

def generate_cooldown(user_id, command, cooldown_time):
    cooldown_text = functions.display_time(user_id, cooldown_time)
    return functions.get_text(user_id, "command_cooldown_description").format(cooldown_text, command)

@client.before_message_command_invoke
async def message_command_handler(interaction):
    if interaction.author.id in blacklisted_users:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "banned_message"), ephemeral=True)
        raise Exception("no permission")

    if not interaction.guild:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "use_in_server"))
        raise Exception("no permission")

@client.before_user_command_invoke
async def user_command_handler(interaction):
    if interaction.author.id in blacklisted_users:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "banned_message"), ephemeral=True)
        raise Exception("no permission")

    if not interaction.guild:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "use_in_server"))
        raise Exception("no permission")

@client.before_slash_command_invoke
async def slash_command_handler(interaction):
    interaction_data = parse_interaction(interaction)
    if used_commands == []:
        used_commands.append(parse_interaction(interaction))
    else:
        if used_commands[len(used_commands)-1] != interaction_data:
            used_commands.append(parse_interaction(interaction))

    if interaction.author.id in blacklisted_users:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "banned_message"), ephemeral=True)
        raise Exception("no permission")

    if not interaction.guild:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "use_in_server"))
        raise Exception("no permission")

    if interaction.data.name in variables.owner_commands and interaction.author.id not in variables.bot_owners:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "not_bot_owner"), ephemeral=True)
        raise Exception("no permission")

    if get_cooldown(interaction.author.id, interaction.data.name) > 0:
        cooldown_string = generate_cooldown(
            interaction.author.id,
            interaction.data.name,
            get_cooldown(interaction.author.id, interaction.data.name),
        )
        embed = disnake.Embed(title=functions.get_text(interaction.author.id, "command_cooldown"), description=cooldown_string, color=variables.embed_color())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        raise Exception("no permission")

    variables.last_command = time.time()
    if interaction.data.name != "afk":
        afk_key = f"afk.{interaction.author.id}".encode("utf-8")
        if afk_key in database.keys():
            del database[afk_key]
            try:
                await interaction.author.send(functions.get_text(interaction.author.id, "afk_removed"))
            except:
                pass
    if interaction.data.name == "text":
        if not interaction.author.guild_permissions.administrator:
            try:
                try:
                    ignored_channels = json.loads(database[f"filter-ignore.{interaction.guild.id}"])
                except:
                    ignored_channels = {"insults": []}
                if interaction.channel.id not in ignored_channels["insults"]:
                    if json.loads(database[f"insults.toggle.{interaction.guild.id}"]):
                        insults = json.loads(database[f"insults.list.{interaction.guild.id}"])
                        for word in insults:
                            if word.lower() in interaction.data.options[0].options[0].value.replace(" ", ""):
                                await interaction.response.send_message(f'Please do not use the word **"{word.lower()}"** in this server!', ephemeral=True)
                                raise Exception("no permission")
            except:
                pass

@client.slash_command(name="help", description="Get started with Doge Utilities")
async def help_command(interaction):
    await help_paginator.start(interaction)
    add_cooldown(interaction.author.id, "help", 30)

@client.slash_command(name="settings", description="Manage")
async def settings_command(_):
    pass

@settings_command.sub_command_group(name="language", description="Set your preferred language (translate, definition, etc)")
async def settings_language_command(_):
    pass

@settings_language_command.sub_command(name="get", description="Get your preferred language")
async def settings_language_get_command(interaction):
    settings = functions.get_settings(interaction.author.id)
    language = settings["language"]
    if language in googletrans.LANGUAGES:
        language = googletrans.LANGUAGES[language]
    await interaction.response.send_message(functions.get_text(interaction.author.id, "current_language_description").format(functions.get_text(interaction.author.id, "language_name")))

async def autocomplete_languages(_, string):
    languages = []
    for language in googletrans.LANGUAGES.values():
        languages.append(language.title())
    return list(filter(lambda language: string.lower() in language.lower(), languages))[:20]

@settings_language_command.sub_command(name="set", description="Set your preferred language")
async def settings_language_set_command(
        interaction,
        language: str = Param(description="Your new preferred language", autocomplete=autocomplete_languages),
    ):
    language = language.lower()
    if language not in googletrans.LANGUAGES.keys() and language not in googletrans.LANGUAGES.values():
        await interaction.response.send_message("The specified language wasn't found!", ephemeral=True)
        return
    language_name = ""
    language_code = ""
    if language in googletrans.LANGUAGES.keys():
        language_name = googletrans.LANGUAGES[language]
        language_code = language
    else:
        language_name = language
        language_code = googletrans.LANGCODES[language]
    settings = functions.get_settings(interaction.author.id)
    settings["language"] = language_code
    functions.set_settings(settings, interaction.author.id)
    default_text = f"Your preferred language has been set to **{language_name.title()}**"
    language_text = default_text
    try:
        del variables.settings_cache[str(interaction.author.id)]
    except:
        pass
    language_name = functions.get_text(interaction.author.id, "language_name")
    if language_name != "English":
        language_text = functions.get_text(interaction.author.id, "language_update").format(language_name)
    await interaction.response.send_message(language_text)

@settings_command.sub_command_group(name="vote-messages", description="Whether or not you want to receive vote messages")
async def settings_vote_command(_):
    pass

@settings_vote_command.sub_command(name="status", description="Check if vote messages are currently enabled or not")
async def settings_vote_status_command(interaction):
    settings = functions.get_settings(interaction.author.id)
    state = f"{functions.get_text(interaction.author.id, 'enabled_lower') if settings['vote_messages'] else functions.get_text(interaction.author.id, 'disabled_lower')}"
    await interaction.response.send_message(f"{functions.get_text(interaction.author.id, 'vote_messages_status').format(state)}")

@settings_vote_command.sub_command(name="enable", description="Enable vote messages")
async def settings_vote_enable_command(interaction):
    settings = functions.get_settings(interaction.author.id)
    settings["vote_messages"] = True
    functions.set_settings(settings, interaction.author.id)
    await interaction.response.send_message(functions.get_text(interaction.author.id, "vote_messages_enabled"))

@settings_vote_command.sub_command(name="disable", description="Disable vote messages")
async def settings_vote_disable_command(interaction):
    settings = functions.get_settings(interaction.author.id)
    settings["vote_messages"] = False
    functions.set_settings(settings, interaction.author.id)
    await interaction.response.send_message(functions.get_text(interaction.author.id, "vote_messages_disabled"))

@client.slash_command(name="embedify", description="Create a custom embed")
async def embedify_command(
        interaction,
        title: str = Param(description="The title of the embed"),
        description: str = Param(description="The description of the embed"),
        color: str = Param(functions.parse_color(variables.embed_color()), description="The color of the embed"),
    ):
    embed_color = variables.embed_color()
    colors = generate_color(color, generate_image=False)
    if colors != 1:
        embed_color = int(colors[0][1:], 16)
    embed = disnake.Embed(title=title, description=description, color=embed_color)
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Your custom embed has been successfully generated!", ephemeral=True)

@client.slash_command(name="reaction-roles", description="Manage the reaction roles")
async def reaction_command(_):
    pass

@reaction_command.sub_command(name="create", description="Create a new reaction role")
async def reaction_create_command(
        interaction,
        message_id: str = Param(name="message-id", description="The ID of the message you want to add reaction roles to"),
        emoji: str = Param(description="The emoji you want to add to the message"),
        role: disnake.Role = Param(description="The role you want to add to users when they add a reaction"),
    ):
    if not interaction.author.guild_permissions.manage_roles and not interaction.author.guild_permissions.administrator:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    if role.position >= interaction.author.top_role.position:
        await interaction.response.send_message("You do not have permission to manage this role!", ephemeral=True)
        return

    if message_id.endswith("/"):
        message_id = message_id[:-1]
    if "discord.com/channels" in message_id:
        segments = message_id.split("/")
        message_id = segments[len(segments)-1]
    try:
        message = await interaction.channel.fetch_message(int(message_id))
    except:
        await interaction.response.send_message("Please enter a valid message ID (that exists in this channel)", ephemeral=True)
        return
    try:
        await message.add_reaction(emoji)
    except:
        await interaction.response.send_message("I can't add that emoji to the message!", ephemeral=True)
        return
    try:
        reaction_roles = json.loads(database[f"reaction-roles.{interaction.guild.id}"])
    except:
        reaction_roles = []
    if len(reaction_roles) >= 20:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "item_limit").format("20"), ephemeral=True)
        return
    reaction_roles.append({"message": message_id, "emoji": emoji, "role": role.id, "channel": interaction.channel.id})
    database[f"reaction-roles.{interaction.guild.id}"] = json.dumps(reaction_roles)
    await interaction.response.send_message("A new reaction role has been successfully created!", ephemeral=True)

def autocomplete_reaction_roles(interaction, string):
    try:
        reaction_roles = json.loads(database[f"reaction-roles.{interaction.guild.id}"])
    except:
        reaction_roles = []
    roles = []
    for reaction_role in reaction_roles:
        roles.append(str(reaction_role["message"]))
    return list(filter(lambda id: string in id, roles))[:20]

@reaction_command.sub_command(name="remove", description="Remove a reaction role from this server")
async def reaction_delete_command(
        interaction,
        message_id: str = Param(
            name="message-id",
            description="The ID of the message you want to remove reaction roles for",
            autocomplete=autocomplete_reaction_roles,
        ),
    ):
    if not interaction.author.guild_permissions.manage_roles and not interaction.author.guild_permissions.administrator:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    try:
        reaction_roles = json.loads(database[f"reaction-roles.{interaction.guild.id}"])
    except:
        reaction_roles = []
    exists = False
    for reaction_role in reaction_roles:
        if str(reaction_role["message"]) == message_id:
            exists = True
            reaction_roles.remove(reaction_role)
            database[f"reaction-roles.{interaction.guild.id}"] = json.dumps(reaction_roles)
            break
    if not exists:
        await interaction.response.send_message("That reaction role wasn't found!", ephemeral=True)
        return
    else:
        await interaction.response.send_message("That reaction role has been successfully deleted!", ephemeral=True)
        return

@reaction_command.sub_command(name="list", description="List all the reaction roles in this server")
async def reaction_list_command(interaction):
    if not interaction.author.guild_permissions.manage_roles and not interaction.author.guild_permissions.administrator:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    try:
        reaction_roles = json.loads(database[f"reaction-roles.{interaction.guild.id}"])
    except:
        reaction_roles = []
    description = ""
    for role in reaction_roles:
        description += f"{role['emoji']} - <@&{role['role']}>: {role['message']} ([message](https://discord.com/channels/{interaction.guild.id}/{role['channel']}/{role['message']}))\n"
    embed = disnake.Embed(title="Reaction Roles", description=description if description != '' else 'There are no reaction roles in this server', color=variables.embed_color())
    await interaction.response.send_message(embed=embed)

@client.slash_command(name="qr", description="Generate a QR code with custom data")
async def qr_command(
        interaction,
        data: str = Param(description="The data you want to encode"),
        border: int = Param(3, description="The size of the QR code's border"),
        foreground: str = Param("black", description="The foreground color of the QR code"),
        background: str = Param("white", description="The background color of the QR code"),
    ):
    await interaction.response.defer()
    if border > 32:
        await interaction.edit_original_message(content=functions.get_text(interaction.author.id, "border_size_too_big"))
        return
    try:
        qr_code = qrcode.QRCode(border=border)
        qr_code.add_data(data)
        image = qr_code.make_image(fill_color=foreground, back_color=background)
        image.save("images/qr.png")

        embed = disnake.Embed(title=functions.get_text(interaction.author.id, "qr_code"), color=variables.embed_color())
        embed.set_image(url="attachment://qr.png")
        await interaction.edit_original_message(embed=embed, file=disnake.File("images/qr.png"))
        add_cooldown(interaction.author.id, "qr", 10)
    except:
        await interaction.edit_original_message(content=functions.get_text(interaction.author.id, "qr_create_failed"))

@client.slash_command(name="currency", description="Convert currencies")
async def currency_command(_):
    pass

def autocomplete_currencies(_, string):
    currencies = [item.upper() for item in list(requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies.json").json().keys())]
    return list(filter(lambda currency: string.lower() in currency.lower(), currencies))[:20]

@currency_command.sub_command(name="convert", description="Convert amounts from one currency to another")
async def currency_convert_command(
        interaction,
        amount: float = Param(description="The amount (for the input currency)"),
        input_currency: str = Param(name="input-currency", description="The input currency", autocomplete=autocomplete_currencies),
        output_currency: str = Param(name="output-currency", description="The output currency", autocomplete=autocomplete_currencies),
    ):
    try:
        input_currency = input_currency.lower().strip()
        output_currency = output_currency.lower().strip()
        url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{input_currency}/{output_currency}.json"
        response = requests.get(url).json(); value = response[output_currency] * amount
        embed = disnake.Embed(title="Currency Conversion", description=f"**{round(amount, 6):,} {input_currency.upper()}** = **{round(value, 6):,} {output_currency.upper()}**", color=variables.embed_color())
        await interaction.response.send_message(embed=embed)
        add_cooldown(interaction.author.id, "currency", 5)
    except:
        await interaction.response.send_message("Unable to convert currency", ephemeral=True)

@currency_command.sub_command(name="list", description="List all the available currencies")
async def currency_list_command(interaction):
    response = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies.json").json()
    output = ""
    for key in response.keys():
        output += f"{key.upper()}: {response[key]}\n"
    segments = [output[i: i + 1000] for i in range(0, len(output), 1000)]
    pager = disnake_paginator.ButtonPaginator(
        prefix=f"```\n", suffix="```", color=variables.embed_color(), title="Currency List", segments=segments,
        invalid_user_function=functions.invalid_user_function,
    )
    await pager.start(interaction)
    add_cooldown(interaction.author.id, "currency", 5)

@client.slash_command(name="ping", description="Display the bot's current latency")
async def ping_command(interaction):
    embed = disnake.Embed(
        title="Pong :ping_pong:",
        description=f"{functions.get_text(interaction.author.id, 'latency')}: **{round(client.latency * 1000, 1)} ms**",
        color=variables.embed_color(),
    )
    await interaction.response.send_message(embed=embed)

@client.slash_command(name="afk", description="Tell other users that you're currently AFK")
async def afk_command(
        interaction,
        message: str = Param(0, description="The reason why you are AFK"),
    ):
    if message == 0:
        message = functions.get_text(interaction.author.id, "i_am_afk")

    try:
        current_status = database[f"afk.{interaction.author.id}"]
    except:
        current_status = None

    if current_status:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "already_afk"), ephemeral=True)
        return
    else:
        if len(message) > 1000:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "text_too_long"), ephemeral=True)
            return

        database[f"afk.{interaction.author.id}"] = json.dumps([round(time.time()), message])
        await interaction.response.send_message(functions.get_text(interaction.author.id, "afk_set").format(functions.remove_mentions(message)))

@client.slash_command(name="links", description="Get links for Doge Utilities")
async def links_command(_):
    pass

@links_command.sub_command(name="support", description="Display the official support server for Doge")
async def support_command(interaction):
    await interaction.response.send_message(f"{functions.get_text(interaction.author.id, 'support_server')}: {variables.support_server_invite}")

@links_command.sub_command(name="invite", description="Invite this bot to another server")
async def invite_command(interaction):
    guild_member = True
    if interaction.author.id == interaction.guild.owner.id:
        guild_member = False

    class CommandView(disnake.ui.View):
        def __init__(self):
            super().__init__()

            self.clicked = False
            self.add_item(
                disnake.ui.Button(
                    label="Invite Link",
                    url=variables.bot_invite_link,
                ),
            )

        async def on_timeout(self):
            for button in self.children:
                button.disabled = True
            await interaction.edit_original_message(view=self)
            return await super().on_timeout()

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
                await button_interaction.response.send_message(functions.get_text(button_interaction.author.id, "not_command_sender"), ephemeral=True)
    await interaction.response.send_message("Here is Doge Utilities' invite link", view=CommandView())

@links_command.sub_command(name="vote", description="Get links to vote for the bot")
async def vote_command(interaction):
    vote_view = disnake.ui.View()
    vote_view.add_item(disnake.ui.Button(label="top.gg", url="https://top.gg/bot/854965721805226005/vote"))
    vote_view.add_item(disnake.ui.Button(label="discordbotlist", url="https://discordbotlist.com/bots/doge-utilities/upvote"))
    vote_view.add_item(disnake.ui.Button(label="discords", url="https://discords.com/bots/bot/854965721805226005/vote"))
    await interaction.response.send_message(functions.get_text(interaction.author.id, "vote_websites"), view=vote_view)

@links_command.sub_command(name="source", description="Get the link to Doge's source code")
async def source_command(interaction):
    description = "You can find my code [here](https://github.com/ErrorNoInternet/Doge-Utilities)"
    try:
        response = requests.get("https://api.github.com/repos/ErrorNoInternet/Doge-Utilities").json()
        description += f"\nActive Issues: **{response['open_issues']}**, Forks: **{response['forks']}**\nStargazers: **{response['stargazers_count']}**, Watchers: **{response['subscribers_count']}**"
    except:
        pass
    embed = disnake.Embed(title="Source Code", description=description, color=variables.embed_color())
    embed.set_thumbnail(url=client.user.avatar)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "source", 10)

@links_command.sub_command(name="website", description="Get links to the bot's website")
async def website_command(interaction):
    view = disnake.ui.View()
    view.add_item(disnake.ui.Button(label=functions.get_text(interaction.author.id, "website"), url=os.environ["WEBSITE_URL"]))
    view.add_item(disnake.ui.Button(label=functions.get_text(interaction.author.id, "dashboard"), url=os.environ["WEBSITE_URL"] + "/web/authenticate"))
    await interaction.response.send_message(functions.get_text(interaction.author.id, "website_links"), view=view)

@client.slash_command(name="get", description="Get information about the bot")
async def get_command(_):
    pass

@get_command.sub_command(name="supporters", description="Get information about Doge Utilities' supporters")
async def supporters_command(interaction):
    users = []
    added = []
    users_string = ""
    for value in variables.supporters.values():
        if type(value) == list:
            for user in value:
                users.append(await client.getch_user(user))
        if type(value) == dict:
            for user in value.values():
                if type(user) == list:
                    for user_id in user:
                        users.append(await client.getch_user(user_id))
                else:
                    users.append(await client.getch_user(user))
    for user in users:
        if user:
            if user.id not in added:
                users_string += f"**{user.name}**, "
                added.append(user.id)
    description = f"Big thanks to {users_string[:-2]}, and a lot more awesome people!"
    embed = disnake.Embed(description=description, color=variables.embed_color())

    developers = []
    for developer in variables.supporters["developers"]:
        user = await client.getch_user(developer)
        if user:
            developers.append(user.name)
    embed.add_field(name="Developers", value="\n".join(developers))

    ideas = []
    for idea in variables.supporters["ideas"]:
        user = await client.getch_user(idea)
        if user:
            ideas.append(user.name)
    embed.add_field(name="Ideas", value="\n".join(ideas))

    translators = []
    for language, translator in variables.supporters["translators"].items():
        translator_users = []
        for user_id in translator:
            user = await client.getch_user(user_id)
            if user:
                translator_users.append(user.name)
        flag = language
        if "-" in flag:
            flag = flag.split("-")[1]
        if flag == "en":
            flag = "us"
        translators.append(f":flag_{flag}: {', '.join(translator_users)}")
    embed.add_field(name="Translators", value="\n".join(translators))
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "get", 3)

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
                shard_members += len(guild.members)
                if guild.id == interaction.guild.id:
                    current_server = "**"
        temporary_text = f"{current_server}{functions.get_text(interaction.author.id, 'shard')} `{client.shards[shard].id}` - `{round(client.shards[shard].latency * 1000, 2)} ms` (`{shard_guilds}` {functions.get_text(interaction.author.id, 'guilds_lower')}, `{shard_members}` {functions.get_text(interaction.author.id, 'members_lower')}){current_server}\n"
        if index > page_limit:
            index = 0
            current_item += 1
        try:
            pages[current_item] += temporary_text
        except:
            pages[current_item] = f"{functions.get_text(interaction.author.id, 'shard_count')}: `{len(client.shards)}`, {functions.get_text(interaction.author.id, 'current_shard')}: `{interaction.guild.shard_id}`\n\n"
            pages[current_item] += temporary_text
        index += 1
    pager = disnake_paginator.ButtonPaginator(
        title=functions.get_text(interaction.author.id, "active_shards"),
        segments=pages.values(),
        target_page=current_page,
        color=variables.embed_color(),
        invalid_user_function=functions.invalid_user_function,
    )
    await pager.start(interaction)
    add_cooldown(interaction.author.id, "get", 3)

@get_command.sub_command(name="status", description="Display the bot's current statistics")
async def status_command(interaction):
    member_count = 0
    channel_count = 0
    uptime = ""
    for guild in client.guilds:
        member_count += len(guild.members)
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
    
    embed = disnake.Embed(color=variables.embed_color())
    embed.add_field(
        name=functions.get_text(interaction.author.id, "latency"),
        value="```" + f"{round(client.get_shard(interaction.guild.shard_id).latency * 1000, 1)} ms" + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "cpu_usage"),
        value="```" + f"{psutil.cpu_percent()}%" + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "ram_usage"),
        value="```" + f"{round(memory_usage, 1)} MB" + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "thread_count"),
        value="```" + str(threading.active_count()) + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "joined_guilds"),
        value="```" + str(len(client.guilds)) + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "active_shards"),
        value="```" + str(len(client.shards)) + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "member_count"),
        value="```" + str(member_count) + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "channel_count"),
        value="```" + str(channel_count) + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "command_count"),
        value="```" + str(len(client.slash_commands)) + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "disnake_version"),
        value="```" + disnake.__version__ + "```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "bot_version"),
        value=f"```{variables.version_number}.{variables.build_number}```",
    )
    embed.add_field(
        name=functions.get_text(interaction.author.id, "bot_uptime"),
        value="```" + uptime.strip() + "```",
    )
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "get", 3)

@get_command.sub_command(name="version", description="Display the bot's current version")
async def version_command(interaction):
    file_size = 0
    for object in os.listdir():
        try:
            file = open(object, "rb")
            file_size += len(file.read()); file.close()
        except:
            pass
    embed = disnake.Embed(title=functions.get_text(interaction.author.id, "bot_version"), description=f"Version: **{variables.version_number}**\nBuild: **{variables.build_number}**\nPython: **{sys.version.split(' ')[0]}**\nDisnake: **{disnake.__version__}**\nSize: **{round(file_size / 1000)} KB**", color=variables.embed_color())
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "get", 3)

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
    embed = disnake.Embed(
        title=functions.get_text(interaction.author.id, "bot_uptime"),
        description=f"{functions.get_text(interaction.author.id, 'uptime_description')} **{uptime}**",
        color=variables.embed_color(),
    )
    await interaction.response.send_message(embed=embed)

@client.slash_command(name="setup", description="Setup mute and ban roles in your server")
async def setup_command(_):
    pass

@setup_command.sub_command(name="banned", description="Setup a 'Banned' role in your server")
async def setup_banned_command(interaction):
    if interaction.author.guild_permissions.manage_roles or interaction.author.id in variables.permission_override or interaction.author.guild_permissions.administrator:
        pass
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    roles = interaction.guild.roles
    for role in roles:
        if role.name == "Banned":
            await interaction.response.send_message("The **Banned** role already exists in this guild")
            return
    await interaction.response.send_message("Generating the **Banned** role for the current guild...")
    try:
        banned_role = await interaction.guild.create_role(name="Banned", permissions=disnake.Permissions(change_nickname=False))
        guild_roles = len(interaction.guild.roles)
        retry_count = 0
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
                await channel.set_permissions(banned_role, view_channel=False)
            except:
                pass
    except:
        await interaction.edit_original_message(content=f"Unable to generate the **Banned** role for this guild")
        return
    await interaction.edit_original_message(content=f"Successfully generated the **Banned** role for this guild")
    add_cooldown(interaction.author.id, "setup", 30)

@setup_command.sub_command(name="muted", description="Setup a 'Muted' role in your server")
async def setup_muted_command(interaction):
    if interaction.author.guild_permissions.manage_roles or interaction.author.id in variables.permission_override or interaction.author.guild_permissions.administrator:
        pass
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    roles = interaction.guild.roles
    for role in roles:
        if role.name == "Muted":
            await interaction.response.send_message("The **Muted** role already exists in this guild")
            return
    await interaction.response.send_message("Generating the **Muted** role for the current guild...")
    try:
        muted_role = await interaction.guild.create_role(name="Muted", permissions=disnake.Permissions(add_reactions=False))
        guild_roles = len(interaction.guild.roles)
        retry_count = 0
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
                try:
                    await channel.set_permissions(muted_role, send_messages=False)
                except:
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
    button_text = functions.get_text(interaction.author.id, "generate_number")

    class CommandView(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.uses = 0

        async def on_timeout(self):
            for button in self.children:
                button.disabled = True
            await interaction.edit_original_message(view=self)
            return await super().on_timeout()

        @disnake.ui.button(label=button_text, style=disnake.ButtonStyle.gray)
        async def generate_number(self, _, button_interaction):
            if button_interaction.author != interaction.author:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "not_command_sender"), ephemeral=True)
                return

            if self.uses < 5:
                self.uses += 1
                random_number = round(random.uniform(low_number, high_number), 2)
                await button_interaction.response.edit_message(content=f"{functions.get_text(interaction.author.id, 'number_prompt')}: **{random_number}**")
            else:
                new_view = disnake.ui.View()
                new_view.add_item(disnake.ui.Button(label=button_text, style=disnake.ButtonStyle.gray, disabled=True))
                await interaction.edit_original_message(view=new_view)
                await button_interaction.response.send_message(
                    functions.get_text(interaction.author.id, "generate_number_limit"),
                    ephemeral=True,
                )
                self.stop()
    await interaction.response.send_message(f"{functions.get_text(interaction.author.id, 'number_prompt')}: **{random_number}**", view=CommandView())
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
        add_cooldown(interaction.author.id, "disconnect-members", 20)
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)

@client.slash_command(name="suggest", description="Send a suggestion to the bot creators")
async def suggest_command(
        interaction,
        suggestion: str = Param(description="The suggestion you want to send"),
    ):
    suggestion = functions.shrink(suggestion, 1500)
    await interaction.response.send_message(functions.get_text(interaction.author.id, "sending_suggestion"), ephemeral=True)
    class SuggestionView(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.timeout = None

        @disnake.ui.button(label="Accept", style=disnake.ButtonStyle.green)
        async def accept_button(self, _, button_interaction):
            try:
                await interaction.author.send(f"The suggestion you sent ({functions.shrink(suggestion, 20)}) has been **accepted** by **{button_interaction.author}**")
            except:
                await button_interaction.response.send_message("Unable to accept")
                return
            await button_interaction.response.send_message("Accepted successfully")
            for button in self.children:
                button.disabled = True
            for original_message in original_messages:
                await original_message.edit(view=self)
            self.stop()

        @disnake.ui.button(label="Reject", style=disnake.ButtonStyle.red)
        async def reject_button(self, _, button_interaction):
            try:
                await interaction.author.send(f"The suggestion you sent ({functions.shrink(suggestion, 20)}) has been **rejected** by **{button_interaction.author}**")
            except:
                await button_interaction.response.send_message("Unable to reject")
                return
            await button_interaction.response.send_message("Rejected successfully")
            for button in self.children:
                button.disabled = True
            for original_message in original_messages:
                await original_message.edit(view=self)
            self.stop()

        @disnake.ui.button(label="Ignore", style=disnake.ButtonStyle.gray)
        async def ignore_button(self, _, button_interaction):
            await button_interaction.response.send_message("Ignored successfully")
            for button in self.children:
                button.disabled = True
            for original_message in original_messages:
                await original_message.edit(view=self)
            self.stop()

    original_messages = []
    for user_id in variables.message_managers:
        sent = False
        for guild in client.guilds:
            for member in guild.members:
                if not sent:
                    if member.id == user_id:
                        sent = True
                        try:
                            original_messages.append(await member.send(f"**{interaction.author.name}#{interaction.author.discriminator}** (`{interaction.author.id}`) **has sent a suggestion**\n{suggestion}", view=SuggestionView()))
                        except:
                            pass
    await interaction.edit_original_message(content=functions.get_text(interaction.author.id, "suggestion_sent"))
    add_cooldown(interaction.author.id, "suggest", 300)

@client.slash_command(name="autorole", description="Manage automatically assigned roles")
async def autorole_command(_):
    pass

@autorole_command.sub_command(name="disable", description="Disable autorole in your server")
async def disable_autorole_command(interaction):
    if not interaction.author.guild_permissions.manage_roles and interaction.author.id not in variables.permission_override and not interaction.author.guild_permissions.administrator:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    del database[f"autorole.{interaction.guild.id}"]
    await interaction.response.send_message("Autorole has been **disabled** for this server")

@autorole_command.sub_command(name="list", description="List all the automatically assigned roles")
async def list_autorole_command(interaction):
    if not interaction.author.guild_permissions.manage_roles and interaction.author.id not in variables.permission_override and not interaction.author.guild_permissions.administrator:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    try:
        role_list = json.loads(database[f"autorole.{interaction.guild.id}"])
        role_string = ""
        for role in role_list:
            role_string += "<@&" + role + "> "
        await interaction.response.send_message(embed=disnake.Embed(title="Autorole", description=f"This server's autorole is {role_string}", color=variables.embed_color()))
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
    if not interaction.author.guild_permissions.manage_roles and interaction.author.id not in variables.permission_override and not interaction.author.guild_permissions.administrator:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
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
            color=variables.embed_color(),
        ),
    )

@client.slash_command(name="lookup", description="Find a user or application on Discord")
async def lookup_command(_):
    pass

@lookup_command.sub_command(name="application", description="Find an application on Discord")
async def lookup_application_command(
        interaction,
        application_id: str = Param(name="application-id", description="The ID of the target application"),
    ):
    response = requests.get(f"https://discord.com/api/v9/applications/{application_id}/rpc").json()
    if "code" in response.keys():
        await interaction.response.send_message("The application you specified wasn't found!", ephemeral=True)
        return
    embed = disnake.Embed(description=response["description"], color=variables.embed_color())
    embed.set_thumbnail(url=f"https://cdn.discordapp.com/app-icons/{response['id']}/{response['icon']}.webp")
    embed.add_field(name="Application Name", value=response["name"])
    embed.add_field(name="Application ID", value="`" + response["id"] + "`")
    embed.add_field(name="Public Bot", value="`" + str(response["bot_public"]) + "`")
    embed.add_field(name="Public Flags", value="`" + str(response["flags"]) + "`")
    embed.add_field(name="Terms of Service", value="None" if "terms_of_service_url" not in response.keys() else f"[Link]({response['terms_of_service_url']})")
    embed.add_field(name="Privacy Policy", value="None" if "privacy_policy_url" not in response.keys() else f"[Link]({response['privacy_policy_url']})")
    embed.add_field(name="Creation Time", value=f"<t:{functions.parse_snowflake(int(response['id']))}:R>")
    embed.add_field(name="Default Invite URL", value="None" if "install_params" not in response.keys() else f"[Link](https://discord.com/oauth2/authorize?client_id={response['id']}&permissions={response['install_params']['permissions']}&scope={'%20'.join(response['install_params']['scopes'])})")
    embed.add_field(name="Custom Invite URL", value="None" if "custom_install_url" not in response.keys() else f"[Link]({response['custom_install_url']})")

    bot_intents = ""
    for application_flag in variables.application_flags:
        if response['flags'] & application_flag == application_flag:
            intent_name = variables.application_flags[application_flag]
            if intent_name.replace(" (unverified)", "") not in bot_intents:
                bot_intents += f"{intent_name}, "
    embed.add_field(name="Intents", value="None" if bot_intents == "" else bot_intents[:-2])

    bot_tags = ""
    if "tags" in response.keys():
        for tag in response['tags']:
            bot_tags += tag + ", "
    embed.add_field(name="Tags", value="None" if bot_tags == "" else bot_tags[:-2], inline=False)

    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "lookup", 5)

@lookup_command.sub_command(name="user", description="Find a user on Discord")
async def lookup_user_command(
        interaction,
        user: disnake.User = Param(default=lambda interaction: interaction.author, description="The ID of the target user"),
    ):
    badges = ""
    for flag in variables.public_flags:
        if user.public_flags.value & int(flag) == int(flag):
            if variables.public_flags[flag] != "None":
                try:
                    badges += variables.badge_list[variables.public_flags[flag]]
                except:
                    raise Exception(f"unable to find badge: {variables.public_flags[flag]}")
    accent_color = 0x000000
    user_object = await client.fetch_user(user.id)
    if user_object.accent_color != None:
        accent_color = user_object.accent_color
    embed = disnake.Embed(color=accent_color)
    embed.add_field(name=functions.get_text(interaction.author.id, "user_id"), value=f"`{user.id}`")
    embed.add_field(name=functions.get_text(interaction.author.id, "user_tag"), value=f"`{user.name}#{user.discriminator}`")
    embed.add_field(name=functions.get_text(interaction.author.id, "creation_time"), value=f"<t:{functions.parse_snowflake(int(user.id))}:R>")
    embed.add_field(name=functions.get_text(interaction.author.id, "public_flags"), value=f"`{user.public_flags.value}` {badges}")
    embed.add_field(name=functions.get_text(interaction.author.id, "bot_user"), value=f"`{user.bot}`")
    embed.add_field(name=functions.get_text(interaction.author.id, "system_user"), value=f"`{user.system}`")
    embed.set_thumbnail(url=user.avatar if user.avatar else user.default_avatar)
    if user_object.banner: embed.set_image(url=user_object.banner)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "lookup", 5)

@client.user_command(name="Lookup User")
async def user_lookup_command(interaction):
    await lookup_command(interaction, str(interaction.target.id))

@client.slash_command(name="permissions", description="Check the permissions of a member or role")
async def permissions_command(_):
    pass

@permissions_command.sub_command(name="member", description="Check the permissions of a member")
async def permissions_member_command(
        interaction,
        member: disnake.Member = Param(default=lambda interaction: interaction.author, description="The member you want to check permissions for"),
    ):
    permission_list = build_member_permissions(member)
    embed = disnake.Embed(title="User Permissions", description=f"Permissions for <@{member.id}>\n\n" + permission_list, color=variables.embed_color())
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "permissions", 3)

@permissions_command.sub_command(name="role", description="Check the permissions of a role")
async def permissions_role_command(
        interaction,
        role: disnake.Role = Param(description="The role you want to check permissions for"),
    ):
    permission_list = build_role_permissions(role)
    embed = disnake.Embed(title="Role Permissions", description=f"Permissions for <@&{role.id}>\n\n" + permission_list, color=variables.embed_color())
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "permissions", 3)

@client.user_command(name="View Permissions")
async def user_permissions_command(interaction):
    permission_list = build_member_permissions(interaction.target)
    embed = disnake.Embed(title="User Permissions", description=f"Permissions for <@{interaction.target.id}>\n\n" + permission_list, color=variables.embed_color())
    await interaction.response.send_message(embed=embed)

@client.slash_command(name="raid-protection", description="Change the raid protection settings")
async def raid_protection_command(_):
    pass

@raid_protection_command.sub_command(name="status", description="See the current setting for raid protection")
async def raid_protection_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    try:
        current_setting = json.loads(database[f"{interaction.guild.id}.raid-protection"])
        if current_setting:
            counter = 0
            if interaction.guild.id in variables.protected_guilds:
                counter = variables.protected_guilds[interaction.guild.id]
            await interaction.response.send_message(f"This server's raid protection is turned **on**\nRaid Protection has saved **{counter} {'object' if counter == 1 else 'objects'}** so far")
        else:
            await interaction.response.send_message("This server's raid protection is turned **off**")
    except:
        await interaction.response.send_message("This server's raid protection is turned **off**")

@raid_protection_command.sub_command(name="enable", description="Enable raid protection for this server")
async def raid_protection_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    database[f"{interaction.guild.id}.raid-protection"] = 1
    await interaction.response.send_message("This server's raid protection has been turned **on**")

@raid_protection_command.sub_command(name="disable", description="Disable raid protection for this server")
async def raid_protection_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    database[f"{interaction.guild.id}.raid-protection"] = 0
    await interaction.response.send_message("This server's raid protection has been turned **off**")

async def autocomplete_algorithms(_, string):
    return list(filter(lambda algorithm: string.lower() in algorithm.lower(), list(hashlib.algorithms_available)))[:20]

@client.slash_command(name="hash", description="Hash text using different algorithms")
async def hash_command(
        interaction,
        hash_type: str = Param(name="algorithm", description="The type of the output hash (md5, sha256, etc)", autocomplete=autocomplete_algorithms),
        text: str = Param(description="The text you want to hash"),
        length: int = Param(None, description="The length of the output hash (for shake_128, shake_256, etc)"),
    ):
    try:
        hash_type = hash_type.strip()
        text = text.strip()
        output_hash = hash_text(hash_type, text, length=length)
        embed = disnake.Embed(color=variables.embed_color())
        embed.add_field(name="Text", value=text)
        embed.add_field(name=f"Hash ({hash_type})", value="`" + output_hash + "`", inline=False)
        await interaction.response.send_message(embed=embed)
        add_cooldown(interaction.author.id, "hash", 3)
    except:
        await interaction.response.send_message("Invalid hash algorithm (or no length specified)", ephemeral=True)
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
        embed = disnake.Embed(color=variables.embed_color())
        embed.add_field(name="Text", value=text); embed.add_field(name="Base64", value="`" + output_code + "`", inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Unable to encode the specified text")
    add_cooldown(interaction.author.id, "base64", 3)

@base64_command.sub_command(name="decode", description="Decode text from base64")
async def base64_decode_command(
        interaction,
        text: str = Param(description="The text you want to decode"),
    ):
    try:
        output_text = base64.b64decode(text.encode("utf-8")).decode("utf-8")
        embed = disnake.Embed(color=variables.embed_color())
        embed.add_field(name="Base64", value="`" + text + "`"); embed.add_field(name="Text", value=output_text, inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Unable to decode the specified text")
    add_cooldown(interaction.author.id, "base64", 3)

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
        embed = disnake.Embed(color=variables.embed_color())
        embed.add_field(name="Text", value=text)
        embed.add_field(name="Binary", value="`" + output_code + "`", inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Unable to encode the specified text")
        return
    add_cooldown(interaction.author.id, "binary", 3)

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
        embed = disnake.Embed(color=variables.embed_color())
        embed.add_field(name="Binary", value="`" + text + "`")
        embed.add_field(name="Text", value=output_text, inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Unable to decode the specified text")
        return
    add_cooldown(interaction.author.id, "binary", 3)

@client.slash_command(name="calculate", description="Evaluate a math expression")
async def calculate_command(
        interaction,
        expression: str = Param(description="The math expression you want to evaluate"),
    ):
    if expression.startswith("`"):
        expression = expression[1:]
    if expression.endswith("`"):
        expression = expression[:-1]
    answer = evaluate_expression(expression)
    if answer == None:
        answer = functions.get_text(interaction.author.id, "unknown_answer")
    embed = disnake.Embed(color=variables.embed_color())
    embed.add_field(name=functions.get_text(interaction.author.id, "expression"), value="`" + expression + "`")
    embed.add_field(name=functions.get_text(interaction.author.id, "result"), value="`" + answer + "`", inline=False)
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "calculate", 3)

@client.slash_command(name="clear", description="Delete the specified amount of messages")
async def clear_command(
        interaction,
        count: int = Param(description="The amount of messages you want to delete"),
        member: disnake.Member = Param(0, description="The member you want to delete messages for"),
        contains: str = Param("", description="Only clear the messages that contain this"),
    ):
    if interaction.author.guild_permissions.manage_messages or interaction.author.id in variables.permission_override:
        await interaction.response.defer(ephemeral=True)

        if count > 1000:
            await interaction.edit_original_message(content=functions.get_text(interaction.author.id, "max_clear_messages"))
            return
        elif count < 0:
            await interaction.edit_original_message(content=functions.get_text(interaction.author.id, "no_negative_numbers"))
            return
        def contains_check(target_message):
            return contains.lower() in target_message.content.lower()
        def member_check(target_message):
            return target_message.author.id == member.id
        contains = contains.strip()
        user_text = None
        contains_text = None
        try:
            if contains != "":
                contains_text = contains

            if member == 0:
                messages = len(await interaction.channel.purge(limit=count, check=contains_check))
            else:
                user_text = member
                def check(target_message):
                    if contains_check(target_message) and member_check(target_message):
                        return True
                    else:
                        return False
                messages = len(await interaction.channel.purge(limit=count, check=check))
        except:
            await interaction.edit_original_message(content=functions.get_text(interaction.author.id, "unable_to_clear"))
            return
        text = ""
        message_label = functions.get_text(interaction.author.id, 'message_lower') if messages == 1 else functions.get_text(interaction.author.id, 'messages_lower')
        if user_text and contains_text:
            text = functions.get_text(interaction.author.id, "cleared_from_contains").format(messages, message_label, member, contains)
        elif user_text:
            text = functions.get_text(interaction.author.id, "cleared_from").format(messages, message_label, member)
        elif contains_text:
            text = functions.get_text(interaction.author.id, "cleared_contains").format(messages, message_label, contains)
        else:
            text = functions.get_text(interaction.author.id, "cleared").format(messages, message_label)
        await interaction.edit_original_message(content=text)
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
    add_cooldown(interaction.author.id, "clear", 5)

@client.slash_command(name="text", description="Change what text looks like")
async def text_command(_):
    pass

@text_command.sub_command(name="italic", description="Make text look italic")
async def italic_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    output = ""
    for letter in text:
        if letter in variables.ascii_characters:
            output += variables.italic_characters[variables.ascii_characters.index(letter)]
    output = functions.remove_mentions(output)
    if output.strip() == "":
        await interaction.response.send_message("I couldn't make your text italic!", ephemeral=True)
    else:
        await interaction.response.send_message(output)
    add_cooldown(interaction.author.id, "text", 3)

@text_command.sub_command(name="bold", description="Make text look bold")
async def bold_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    output = ""
    for letter in text:
        if letter in variables.ascii_characters:
            output += variables.bold_characters[variables.ascii_characters.index(letter)]
    output = functions.remove_mentions(output)
    if output.strip() == "":
        await interaction.response.send_message("I couldn't make your text bold!", ephemeral=True)
    else:
        await interaction.response.send_message(output)
    add_cooldown(interaction.author.id, "text", 3)

@text_command.sub_command(name="scramble", description="Scramble the letters in a sentence")
async def scramble_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    letters = []
    for letter in text:
        letters.append(letter)
    output = ""
    for i in range(len(letters)):
        letter = random.choice(letters)
        output += letter
        letters.remove(letter)
    await interaction.response.send_message(functions.remove_mentions(output))
    add_cooldown(interaction.author.id, "text", 3)

@text_command.sub_command(name="wide", description="Make text appear to be wider")
async def wide_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    new_text = ""
    for letter in text:
        new_text += letter + " "
    await interaction.response.send_message(functions.remove_mentions(new_text))
    add_cooldown(interaction.author.id, "text", 3)

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
    await interaction.response.send_message(functions.remove_mentions(new_text))
    add_cooldown(interaction.author.id, "text", 3)

@text_command.sub_command(name="spoiler", description="Add spoilers to every single character")
async def spoiler_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    new_text = ""
    for letter in text:
        new_text += "||" + letter + "||"
    await interaction.response.send_message(functions.remove_mentions(new_text))
    add_cooldown(interaction.author.id, "text", 3)

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
    await interaction.response.send_message(functions.remove_mentions(new_text))
    add_cooldown(interaction.author.id, "text", 3)

@text_command.sub_command(name="reverse", description="Reverse the specified text")
async def reverse_command(
        interaction,
        text: str = Param(description="The text you want to manipulate"),
    ):
    new_text = text[::-1]
    await interaction.response.send_message(functions.remove_mentions(new_text))
    add_cooldown(interaction.author.id, "text", 3)

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
            if number > 90:
                new_text += random.choice(["0", "1"])
            else:
                new_text += letter
                punctuation = random.choice([True, False, False, False, False])
                if punctuation:
                    new_text += string.punctuation[random.randint(0, len(string.punctuation) - 1)]
    await interaction.response.send_message(functions.remove_mentions(new_text))
    add_cooldown(interaction.author.id, "text", 3)

@client.slash_command(name="color", description="Visualize a color code")
async def color_command(
        interaction,
        color_code: str = Param(name="color", description="The color code you want to visualize"),
    ):
    colors = generate_color(color_code)
    if colors == 1:
        await interaction.response.send_message(f"`{color_code}` is not a valid color code!")
        return
    else:
        hex_color = colors[0]; rgb_color = colors[1]
        embed = disnake.Embed(color=int("0x" + hex_color[1:], 16))
        embed.set_image(url="attachment://color.png")
        embed.add_field(name="Hex", value=hex_color)
        embed.add_field(name="RGB", value=str(rgb_color), inline=True)
    await interaction.response.send_message(embed=embed, file=disnake.File("images/color.png"))
    add_cooldown(interaction.author.id, "color", 3)

async def autocomplete_timezones(_, string):
    timezones = []
    for timezone in pytz.all_timezones:
        timezone = timezone.replace("_", " ")
        timezones.append(timezone)
    return list(filter(lambda timezone: string.lower() in timezone.lower(), timezones))[:20]

@client.slash_command(name="time", description="Convert unit timestamps and get time information")
async def time_command(_):
    pass

@time_command.sub_command(name="epoch-date", description="Convert unix timestamps to dates")
async def epoch_date_command(
        interaction,
        text: str = Param(name="timestamp", description="The unix timestamp"),
    ):
    try:
        date = epoch_to_date(int(text)); embed = disnake.Embed(color=variables.embed_color())
        embed.add_field(name="Epoch", value="`" + text + "`"); embed.add_field(name="Date", value=date, inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Invalid unix timestamp")
        return
        
@time_command.sub_command(name="date-epoch", description="Convert dates to unix timestamps")
async def date_epoch_command(
        interaction,
        text: str = Param(name="date", description="The date"),
    ):
    try:
        epoch = date_to_epoch(text); embed = disnake.Embed(color=variables.embed_color())
        embed.add_field(name="Date", value=text); embed.add_field(name="Epoch", value="`" + str(epoch) + "`", inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Invalid date")
        return

@time_command.sub_command(name="get", description="Get the time information about a specific region")
async def time_get_command(
        interaction,
        region: str = Param(description="The region you want to check the time for", autocomplete=autocomplete_timezones),
    ):
    region = region.strip()
    try:
        if region.lower() == "list" or region.lower() == "help":
            output = ""
            for timezone in pytz.all_timezones:
                output += timezone + "\n"
            segments = disnake_paginator.split(output, 1000)
            pager = disnake_paginator.ButtonPaginator(
                color=variables.embed_color(),
                prefix="```\n", suffix="```",
                title=f"Timezone List", segments=segments,
                invalid_user_function=functions.invalid_user_function,
            )
            await pager.start(interaction)
        elif region.lower() == "epoch" or region.lower() == "unix":
            embed = disnake.Embed(title="Time", description=f"Current epoch time: **{round(time.time())}**", color=variables.embed_color())
            await interaction.response.send_message(embed=embed)
        else:
            user_timezone = pytz.timezone(region.replace(" ", "_"))
            now = datetime.datetime.now(user_timezone)
            region_name = region.replace("_", " ")
            for timezone in pytz.all_timezones:
                if timezone.lower().replace("_", " ") == region_name.lower():
                    region_name = timezone.replace("_", " ")
            embed = disnake.Embed(title=functions.get_text(interaction.author.id, 'current_time'), description=f"{functions.get_text(interaction.author.id, 'time_description')} **{region_name}**\n\n{functions.get_text(interaction.author.id, 'current_time')}: **{str(now.time()).split('.')[0]}**\n{functions.get_text(interaction.author.id, 'current_date')}: **{now.date()}**\n{functions.get_text(interaction.author.id, 'weekday')}: **{functions.get_text(interaction.author.id, 'weekdays')[now.weekday()]}**", color=variables.embed_color())
            await interaction.response.send_message(embed=embed)
    except KeyError:
        for timezone in pytz.all_timezones:
            try:
                city = timezone.split("/")[1]
                if region.replace(" ", "_").lower() == city.lower():
                    user_timezone = pytz.timezone(timezone)
                    now = datetime.datetime.now(user_timezone)
                    embed = disnake.Embed(title=functions.get_text(interaction.author.id, 'current_time'), description=f"{functions.get_text(interaction.author.id, 'time_description')} **{timezone.replace('_', ' ')}**\n\n{functions.get_text(interaction.author.id, 'current_time')}: **{str(now.time()).split('.')[0]}**\n{functions.get_text(interaction.author.id, 'current_date')}: **{now.date()}**\n{functions.get_text(interaction.author.id, 'weekday')}: **{functions.get_text(interaction.author.id, 'weekdays')[now.weekday()]}**", color=variables.embed_color())
                    await interaction.response.send_message(embed=embed)
                    return
            except:
                pass
        embed = disnake.Embed(title="Time", description=f"That timezone was not found", color=variables.embed_color())
        await interaction.response.send_message(embed=embed)
        return
    add_cooldown(interaction.author.id, "time", 3)

@client.slash_command(name="nickname", description="Change a member's nickname")
async def nickname_command(
        interaction,
        nickname: str = Param(description="The new nickname"),
        member: disnake.Member = Param(default=lambda interaction: interaction.author, description="The target member"),
    ):
    if member.id != interaction.author.id:
        if not interaction.author.guild_permissions.manage_nicknames and interaction.author.id not in variables.permission_override:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
            return

    try:
        if member.id == interaction.author.id:
            if not member.guild_permissions.change_nickname:
                await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
                return
        else:
            if member.top_role.position >= interaction.author.top_role.position:
                await interaction.response.send_message(f"You do not have permission to edit **{member}**'s nickname!", ephemeral=True)
                return
        variables.updated_members.append(member.id)
        await member.edit(nick=nickname)
        nicknameString = f'**"{nickname}"**'
        await interaction.response.send_message(f"Successfully updated **{member.name}#{member.discriminator}**'s nickname to {nicknameString}")
        add_cooldown(interaction.author.id, "nickname", 3)
    except:
        if member.id in variables.updated_members:
            variables.updated_members.remove(member.id)
        await interaction.response.send_message(f"Unable to change **{member.name}#{member.discriminator}**'s nickname", ephemeral=True)
        return

@client.slash_command(name="channel", description="Manage the current channel")
async def channel_command(_):
    pass

@channel_command.sub_command(name="lock", description="Lock the current channel")
async def channel_lock_command(interaction):
    if not interaction.author.guild_permissions.manage_channels and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    except:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "unable_to_lock").format(interaction.channel.mention), ephemeral=True)
        return
    await interaction.response.send_message(functions.get_text(interaction.author.id, "channel_locked").format(interaction.channel.mention), ephemeral=True)

@channel_command.sub_command(name="unlock", description="Unlock the current channel")
async def channel_unlock_command(interaction):
    if not interaction.author.guild_permissions.manage_channels and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    except:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "unable_to_unlock").format(interaction.channel.mention), ephemeral=True)
        return
    await interaction.response.send_message(functions.get_text(interaction.author.id, "channel_unlocked").format(interaction.channel.mention), ephemeral=True)

@channel_command.sub_command(name="slowmode", description="Change this channel's slowmode")
async def channel_slowmode_command(
        interaction,
        seconds: int = Param(description="The new slowmode of this channel"),
    ):
    if not interaction.author.guild_permissions.manage_channels and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    if seconds > 21600 or seconds < 0:
        await interaction.response.send_message("Please enter a valid slowmode between **0** (no slowmode) and **21600** (6 hours)", ephemeral=True)
        return
    try:
        variables.updated_channels.append(interaction.channel.id)
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(f"This channel's slowmode has been set to **{seconds} {'second' if seconds == 1 else 'seconds'}**")
    except:
        await interaction.response.send_message("I was unable to change this channel's slowmode", ephemeral=True)

@client.slash_command(name="search", description="Search for something on the internet")
async def search_command(_):
    pass

async def autocomplete_youtube(_, string):
    response = requests.get(f"https://youtube.com/results?search_query={string}")
    raw_results = []
    items = response.content.decode("utf-8").split(",")
    for item in items:
        if item.startswith('"title":{"runs":[{"text":') and item.endswith('"}]'):
            raw_results.append(item.split('"title":{"runs":[{"text":"')[1].split('"}]')[0])
    search_results = []
    for result in raw_results:
        result = result.replace('\\"', "\"")
        if len(result) > 100:
            result = functions.shrink(result, 100)
        search_results.append(result)
    return search_results[:20]

@search_command.sub_command(name="youtube", description="Look for a video on YouTube")
async def youtube_command(
        interaction,
        query: str = Param(description="The search query", autocomplete=autocomplete_youtube),
    ):
    await interaction.response.defer()
    response = requests.get(f"https://youtube.com/results?search_query={query}")
    try:
        search_results = re.findall(r'/watch\?v=(.{11})', response.text)
    except:
        await interaction.edit_original_message(content="I couldn't find that video on YouTube")
        return
    if not search_results:
        await interaction.edit_original_message(content="I couldn't find that video on YouTube")
        return
    await interaction.edit_original_message(content=f"Here's the video I found: https://youtube.com/watch?v={search_results[0]}")
    add_cooldown(interaction.author.id, "search", 10)

@search_command.sub_command(name="stackoverflow", description="Look for something on StackOverflow")
async def stackoverflow_command(
        interaction,
        text: str = Param(name="query", description="The search query"),
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
            embed = disnake.Embed(title="StackOverflow", description=f'No search results found for **"{text}"**', color=disnake.Color.red())
            await interaction.edit_original_message(embed=embed)
            return
        final_results = response["items"][:5]
        embed = disnake.Embed(
            title="StackOverflow",
            description=f'Here are the **top {len(final_results)}** results for **"{text}"**',
            color=variables.embed_color(),
        )
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
                inline = False,
            )
        await interaction.edit_original_message(embed=embed)
    except disnake.HTTPException:
        await interaction.edit_original_message(content="The search result is too long!", ephemeral=True)
        return
    except:
        await interaction.edit_original_message(content="Unable to search for item", ephemeral=True)
        return
    add_cooldown(interaction.author.id, "search", 10)

@client.slash_command(name="execute", description="Execute code on Doge Utilities", default_permission=False)
async def execute_command(
        interaction,
        code: str = Param(description="The code you want to execute"),
        codeblock: ToggleOption = Param("enable", description="Whether or not you want a codeblock"),
        ephemeral: ToggleOption = Param("disable", description="Whether or not you want the output to be ephemeral"),
    ):
    if code.startswith("```python"):
        code = code[9:]
    if code.startswith("```py"):
        code = code[5:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    if code.startswith("`") and code.endswith("`"):
        code = code[1:-1]
    if codeblock == "enable":
        codeblock = "```"
    else:
        codeblock = ""
    if ephemeral == "enable":
        ephemeral = True
    else:
        ephemeral = False
    await interaction.response.defer(ephemeral=ephemeral)

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
    output = output.replace(os.getenv("TOKEN"), "<TOKEN>")

    if len(output) > 2000:
        output = output.replace("`", "\`")
        segments = disnake_paginator.split(output)
        pager = disnake_paginator.ButtonPaginator(
            prefix=f"{codeblock}\n", 
            suffix=codeblock, 
            color=variables.embed_color(), 
            title=f"Code Output", 
            segments=segments,
            invalid_user_function=functions.invalid_user_function,
        )
        await interaction.edit_original_message(view=pager.view(interaction), embed=pager.embeds[0])
    elif len(output.strip()) == 0:
        await interaction.edit_original_message(content=":white_check_mark:")
    else:
        await interaction.edit_original_message(content=output)

@client.slash_command(name="blacklist", description="Manage Doge Utilities' blacklist", default_permission=False)
async def blacklist_command(_):
    pass

@blacklist_command.sub_command(name="list", description="List all the blacklisted users")
async def blacklist_list_command(interaction):
    blacklisted_users = []
    raw_array = json.loads(database["blacklist"])
    for user in raw_array:
        user_tag = await client.getch_user(user)
        if user_tag == None:
            user_tag = "unknown"
        blacklisted_users.append(f"{user} (**{user_tag}**)")
    embed = disnake.Embed(title="Blacklisted Users", description="\n".join(blacklisted_users) if "\n".join(blacklisted_users) != "" else "There are no blacklisted users", color=variables.embed_color())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@blacklist_command.sub_command(name="add", description="Add a user to the blacklist")    
async def blacklist_add_command(
        interaction,
        user: str = Param(description="The user you want to add to the blacklist"),
    ):
    try:
        user_id = int(functions.remove_mentions(user))
    except:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "mention_valid_user"), ephemeral=True)
        return
    current_users = json.loads(database["blacklist"])
    if user_id in current_users:
        await interaction.response.send_message("That user is already in the blacklist!", ephemeral=True)
        return
    current_users.append(user_id)
    database["blacklist"] = json.dumps(current_users)
    await interaction.response.send_message(f"Successfully added `{user_id}` to the blacklist", ephemeral=True)

@blacklist_command.sub_command(name="remove", description="Remove a user from the blacklist")
async def blacklist_remove_command(
        interaction,
        user: str = Param(description="The user you want to remove from the blacklist"),
    ):
    try:
        user_id = int(functions.remove_mentions(user))
    except:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "mention_valid_user"), ephemeral=True)
        return
    current_users = json.loads(database["blacklist"])
    if user_id not in current_users:
        await interaction.response.send_message("That user is not in the blacklist!", ephemeral=True)
        return
    current_users.remove(user_id)
    database["blacklist"] = json.dumps(current_users)
    await interaction.response.send_message(f"Successfully removed `{user_id}` from the blacklist", ephemeral=True)

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
                await button_interaction.response.send_message(functions.get_text(button_interaction.author.id, "not_in_game"), ephemeral=True)
                return

            if view.current_player == view.X:
                if button_interaction.author.id != players[0]:
                    await button_interaction.response.send_message(functions.get_text(button_interaction.author.id, "wrong_turn"), ephemeral=True)
                    return

                self.style = disnake.ButtonStyle.danger
                self.label = 'X'
                self.disabled = True
                view.board[self.y][self.x] = view.X
                view.current_player = view.O
                content = f"It is now <@{players[1]}>'s (O) turn"
            else:
                if button_interaction.author.id != players[1]:
                    await button_interaction.response.send_message(functions.get_text(button_interaction.author.id, "wrong_turn"), ephemeral=True)
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
                    content = f'<@{players[0]}> (X) won!'
                elif winner == view.O:
                    content = f'<@{players[1]}> (O) won!'
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

        async def on_timeout(self):
            for button in self.children:
                button.disabled = True
            await interaction.edit_original_message(view=self)
            return await super().on_timeout()

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
    class GameLauncher(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.timeout = 300

        async def on_timeout(self):
            for button in self.children:
                button.disabled = True
            await interaction.edit_original_message(view=self)
            return await super().on_timeout()

        @disnake.ui.button(label=functions.get_text(interaction.author.id, "player_one"), style=disnake.ButtonStyle.blurple)
        async def player_one(self, button, button_interaction):
            button.label = button_interaction.author.name
            button.disabled = True

            if button_interaction.author.id not in players:
                players.append(button_interaction.author.id)
                await button_interaction.response.send_message(functions.get_text(button_interaction.author.id, "joined_game"), ephemeral=True)
            else:
                await button_interaction.response.send_message(functions.get_text(button_interaction.author.id, "already_joined"), ephemeral=True)
                return
            if len(players) == 2:
                await interaction.edit_original_message(view=self, content=functions.get_text(interaction.author.id, "game_starts_in_three"))
                await asyncio.sleep(3)
                await interaction.edit_original_message(content=f"It's your turn, <@{players[0]}>!", view=TicTacToe())
                self.stop()
                return
            await interaction.edit_original_message(view=self)

        @disnake.ui.button(label=functions.get_text(interaction.author.id, "player_two"), style=disnake.ButtonStyle.blurple)
        async def player_two(self, button, button_interaction):
            button.label = button_interaction.author.name
            button.disabled = True

            if button_interaction.author.id not in players:
                players.append(button_interaction.author.id)
                await button_interaction.response.send_message(functions.get_text(button_interaction.author.id, "joined_game"), ephemeral=True)
            else:
                await button_interaction.response.send_message(functions.get_text(button_interaction.author.id, "already_joined"), ephemeral=True)
                return
            if len(players) == 2:
                await interaction.edit_original_message(view=self, content=functions.get_text(interaction.author.id, "game_starts_in_three"))
                await asyncio.sleep(3)
                await interaction.edit_original_message(content=f"It's your turn, <@{players[0]}>!", view=TicTacToe())
                self.stop()
                return
            await interaction.edit_original_message(view=self)

    await interaction.response.send_message(functions.get_text(interaction.author.id, "join_tictactoe"), view=GameLauncher())
    add_cooldown(interaction.author.id, "game", 20)

@game_command.sub_command(name="trivia", description="Start a trivia game")
async def trivia_command(interaction):
    await interaction.response.defer()
    url = f"https://opentdb.com/api.php?amount=1&type=multiple&category={random.randint(9, 32)}&difficulty={random.choice(['easy', 'medium', 'hard'])}"
    response = requests.get(url).json()
    description = f"**{html.unescape(response['results'][0]['question'])}**\nCategory: `{response['results'][0]['category']}` (**{response['results'][0]['difficulty']}** difficulty)"
    answers = response['results'][0]['incorrect_answers']
    answers.append(response['results'][0]['correct_answer'])
    correct_answer = html.unescape(response['results'][0]['correct_answer'])

    class CommandView(disnake.ui.View):
        def __init__(self):
            super().__init__()

        async def on_timeout(self):
            for button in self.children:
                button.disabled = True
            await interaction.edit_original_message(view=self)
            return await super().on_timeout()

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
            if interaction.author != button_interaction.author:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "not_command_sender"), ephemeral=True)
                return

            if button.label == correct_answer:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "correct_answer"), ephemeral=True)
            else:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "wrong_answer").format(correct_answer), ephemeral=True)
            await self.close(button.label)

        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_2(self, button, button_interaction):
            if interaction.author != button_interaction.author:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "not_command_sender"), ephemeral=True)
                return

            if button.label == correct_answer:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "correct_answer"), ephemeral=True)
            else:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "wrong_answer").format(correct_answer), ephemeral=True)
            await self.close(button.label)

        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_3(self, button, button_interaction):
            if interaction.author != button_interaction.author:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "not_command_sender"), ephemeral=True)
                return

            if button.label == correct_answer:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "correct_answer"), ephemeral=True)
            else:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "wrong_answer").format(correct_answer), ephemeral=True)
            await self.close(button.label)

        answer = random.choice(answers); answers.remove(answer)
        @disnake.ui.button(label=html.unescape(answer), style=disnake.ButtonStyle.gray)
        async def trivia_response_4(self, button, button_interaction):
            if interaction.author != button_interaction.author:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "not_command_sender"), ephemeral=True)
                return

            if button.label == correct_answer:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "correct_answer"), ephemeral=True)
            else:
                await button_interaction.response.send_message(functions.get_text(interaction.author.id, "wrong_answer").format(correct_answer), ephemeral=True)
            await self.close(button.label)

    embed = disnake.Embed(
        description=description,
        color=variables.embed_color(),
    )
    await interaction.edit_original_message(embed=embed, view=CommandView())
    add_cooldown(interaction.author.id, "game", 3)

@client.slash_command(name="fetch", description="Fetch something from the internet")
async def fetch_command(_):
    pass

@fetch_command.sub_command(name="minecraft-server", description="Fetch a Minecraft server")
async def fetch_minecraft_server_command(
        interaction,
        server_ip: str = Param(name="server-ip", description="The IP of the Minecraft server"),
    ):
    await interaction.response.defer()
    try:
        server = functions.minepinger(server_ip)
    except Exception as error:
        error = str(error)
        if error == "[Errno -2] Name or service not known":
            error = "Name or service not known"
        elif error == "[Errno 104] Connection reset by peer":
            error = "Connection reset by peer"
        elif error == "[Errno 111] Connection refused":
            error = "Connection refused"
        elif error == "[Errno -5] No address associated with hostname":
            error = "No address associated with hostname"
        elif error == "timed out":
            error = "Connection timed out"
        elif error == "'socket' object has no attribute 'read'" or error == "Expecting value: line 1 column 1 (char 0)":
            error = "Not a valid Minecraft server"
        elif error == "connect(): port must be 0-65535.":
            error = "Port must be from 0 to 65535"
        elif "invalid literal" in error:
            error = "Invalid port specified"
        embed = disnake.Embed(title=functions.get_text(interaction.author.id, "unable_to_connect"), description=error, color=disnake.Color.red())
        await interaction.edit_original_message(embed=embed)
        return

    if type(server['description']) == str:
        server_description = server['description']
    else:
        server_description = server['description']['text']
        try:
            for segment in server['description']['extra']:
                bold = False
                if "bold" in segment.keys():
                    bold = segment['bold']
                italic = False
                if "italic" in segment.keys():
                    italic = segment['italic']
                underlined = False
                if "underlined" in segment.keys():
                    underlined = segment['underlined']
                text = segment["text"]
                if bold:
                    text = "**" + text + "**"
                if italic:
                    text = "_" + text + "_"
                if underlined:
                    text = "__" + text + "__"
                server_description += text
                server_description = server_description.replace("****", "")
        except:
            pass
    server_players = ""
    try:
        for player in server['players']['sample']:
          server_players += f"**{player['name']}**, "
    except:
        pass
    if server_players == "":
        server_players = functions.get_text(interaction.author.id, "unknown_upper")
    else:
        server_players = server_players[:-2]

    description = f"`{server_ip}` (**{server['version']['name']}**, **v{server['version']['protocol']}**)\n{server_description}\n\n**{functions.get_text(interaction.author.id, 'players')}** (**{server['players']['online']}**/**{server['players']['max']}**)**:** {functions.shrink(server_players, 1500)}"
    image = False
    if "favicon" in server.keys():
        try:
            file = open("images/icon.png", "wb+")
            file.write(base64.b64decode(server['favicon'][22:]))
            file.close()
            image = True
        except:
            pass
    embed = disnake.Embed(title=functions.get_text(interaction.author.id, "minecraft_server"), description=description, color=disnake.Color.green())
    if image: embed.set_thumbnail(url="attachment://icon.png")
    await interaction.edit_original_message(embed=embed, file=disnake.File("images/icon.png") if image else None)
    add_cooldown(interaction.author.id, "fetch", 5)

@fetch_command.sub_command(name="weather", description="Fetch the weather in a region")
async def fetch_weather_command(
        interaction,
        region: str = Param(description="The region you want to check the weather for"),
    ):
    await interaction.response.defer()
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={region}&appid={os.environ['WEATHER_KEY']}&units=metric").json()
    except:
        await interaction.edit_original_message(content=f'I was unable to fetch the weather for **"{region}"**')
        return
    try:
        if response['cod'] == '404':
            await interaction.edit_original_message(content="The specified region wasn't found!")
            return
    except:
        pass
    time_offset = datetime.timedelta(0, response['timezone'])
    current_time = str(datetime.datetime.now() + time_offset).split(" ")[1].split(".")[0]
    sunrise_time = str(datetime.datetime.fromtimestamp(response['sys']['sunrise']) + time_offset).split(" ")[1].split(".")[0]
    sunset_time = str(datetime.datetime.fromtimestamp(response['sys']['sunset']) + time_offset).split(" ")[1].split(".")[0]
    precipitation = "None"
    if "rain" in response.keys():
        precipitation = f"Rain: {response['rain']['1h']} mm"
    elif "snow" in response.keys():
        precipitation = f"Snow: {response['snow']['1h']} mm"
    try:
        country = f" ({response['sys']['country']})"
    except:
        country = ""

    embed = disnake.Embed(color=variables.embed_color())
    embed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{response['weather'][0]['icon']}@2x.png")
    embed.add_field(name=f"Location{country}", value=response['name'])
    embed.add_field(name="Current Weather", value=response['weather'][0]['main'])
    embed.add_field(name="Description", value=response['weather'][0]['description'].title())
    embed.add_field(name="Temperature", value=str(response['main']['temp'])+"°C")
    embed.add_field(name="Coldest", value=str(response['main']['temp_min'])+"°C")
    embed.add_field(name="Hottest", value=str(response['main']['temp_max'])+"°C")
    embed.add_field(name="Feels Like", value=str(response['main']['feels_like'])+"°C")
    embed.add_field(name="Pressure", value=str(response['main']['pressure'])+" hPa")
    embed.add_field(name="Humidity", value=str(response['main']['humidity'])+"%")
    embed.add_field(name="Precipitation (1h)", value=precipitation)
    embed.add_field(name="Cloudiness", value=str(response['clouds']['all'])+"%")
    embed.add_field(name="Wind Speed", value=str(response['wind']['speed'])+" m/s")
    embed.add_field(name="Current Time", value=current_time)
    embed.add_field(name="Sunrise Time", value=sunrise_time)
    embed.add_field(name="Sunset Time", value=sunset_time)
    await interaction.edit_original_message(embed=embed)
    add_cooldown(interaction.author.id, "fetch", 3)

@fetch_command.sub_command(name="astronauts", description="Fetch the people that are currently in space")
async def fetch_astronauts_command(interaction):
    await interaction.response.defer()
    try:
        response = requests.get("http://api.open-notify.org/astros.json").json()
    except:
        await interaction.edit_original_message(content="I was unable to fetch the people in space")
        return
    embed = disnake.Embed(color=variables.embed_color())
    stations = []
    for person in response["people"]:
        if person["craft"] not in stations:
            stations.append(person["craft"])
    for station in stations:
        value = ""
        for person in response["people"]:
            if person["craft"] == station:
                value += f"\n{person['name']}"
        embed.add_field(name=station, value=value)
    number = response['number']
    embed.set_footer(text=f"There {'is' if number == 1 else 'are'} currently {number} {'person' if number == 1 else 'people'} in space")
    await interaction.edit_original_message(embed=embed)
    add_cooldown(interaction.author.id, "fetch", 3)

@fetch_command.sub_command(name="meme", description="Fetch a random meme from Reddit")
async def meme_command(interaction):
    await interaction.response.defer()
    try:
        response = requests.get("https://meme-api.herokuapp.com/gimme").json()
    except:
        await interaction.edit_original_message(content="I was unable to fetch a meme from Reddit")
        return
    description = f"Posted by **{response['author']}** in **{response['subreddit']}** (**{response['ups']}** upvotes)"
    embed = disnake.Embed(title=response["title"], url=response["postLink"], description=description, color=variables.embed_color())
    embed.set_image(url=response["url"])
    await interaction.edit_original_message(embed=embed)
    add_cooldown(interaction.author.id, "fetch", 3)

@fetch_command.sub_command(name="joke", description="Fetch a random joke")
async def joke_command(interaction):
    await interaction.response.defer()
    response = requests.get("http://yet-another-api.herokuapp.com/api/jokes/random").json()
    embed = disnake.Embed(description=f"Here's a `{response['type']}` joke:\n{response['setup']} **{response['punchline']}**", color=variables.embed_color())
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
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    if member.top_role.position >= interaction.author.top_role.position and "mute" not in member.top_role.name.lower():
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission_unmute").format(member), ephemeral=True)
        return

    mute_role = None; exists = False
    for role in interaction.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if exists:
        try:
            await member.remove_roles(mute_role)
        except:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "unable_to_unmute").format(member))
            return
    await interaction.response.send_message(functions.get_text(interaction.author.id, "user_unmuted").format(member))

@client.slash_command(name="mute", description="Mute a specified member on your server")
async def mute_command(
        interaction,
        member: disnake.Member = Param(description="The member you want to mute"),
        duration: str = Param(0, description="The target duration"),
    ):
    if interaction.author.guild_permissions.manage_roles or interaction.author.guild_permissions.administrator or interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    if member.top_role.position >= interaction.author.top_role.position and "mute" not in member.top_role.name.lower():
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission_mute").format(member), ephemeral=True)
        return

    original_duration = duration
    try:
        duration = functions.parse_time(duration) / 60
    except:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "invalid_duration"), ephemeral=True)
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
            await interaction.response.send_message(functions.get_text(interaction.author.id, "unable_to_mute").format(member), ephemeral=True)
            return
        await interaction.response.send_message(functions.get_text(interaction.author.id, "user_muted_permanently").format(member))
    else:
        if duration > 43200:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "duration_too_long"), ephemeral=True)
            return
        if duration < 0:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "no_negative_numbers"), ephemeral=True)
            return
        try:
            moderation_data = json.loads(database["mute." + str(interaction.guild.id)])
        except:
            database["mute." + str(interaction.guild.id)] = json.dumps([])
            moderation_data = json.loads(database["mute." + str(interaction.guild.id)])
        try:
            await member.add_roles(mute_role)
            moderation_data.append([member.id, round(time.time()), duration])
            database["mute." + str(interaction.guild.id)] = json.dumps(moderation_data)
        except:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "unable_to_mute").format(member), ephemeral=True)
            return
        await interaction.response.send_message(functions.get_text(interaction.author.id, "user_muted_temporarily").format(member, functions.display_time(interaction.author.id, functions.parse_time(original_duration))))

@client.user_command(name="Mute Member")
async def user_mute_command(interaction):
    if not interaction.author.guild_permissions.manage_roles and interaction.author.id not in variables.permission_override and not interaction.author.guild_permissions.administrator:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    if interaction.target.top_role.position >= interaction.author.top_role.position and "mute" not in interaction.target.top_role.name.lower():
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission_mute").format(interaction.target), ephemeral=True)
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
    try:
        await interaction.target.add_roles(mute_role)
        await interaction.response.send_message(functions.get_text(interaction.author.id, "user_muted_permanently").format(interaction.target))
    except:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "unable_to_mute").format(interaction.target), ephemeral=True)

@client.user_command(name="Unmute Member")
async def user_unmute_command(interaction):
    if not interaction.author.guild_permissions.manage_roles and interaction.author.id not in variables.permission_override and not interaction.author.guild_permissions.administrator:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    if interaction.target.top_role.position >= interaction.author.top_role.position and "mute" not in interaction.target.top_role.name.lower():
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission_unmute").format(interaction.target), ephemeral=True)
        return
    mute_role = None; exists = False
    for role in interaction.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if exists:
        try:
            await interaction.target.remove_roles(mute_role)
            await interaction.response.send_message(functions.get_text(interaction.author.id, "user_unmuted").format(interaction.target))
        except:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "unable_to_unmute").format(interaction.target))
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "unable_to_unmute").format(interaction.target))

@client.slash_command(name="filter", description="Manage the auto-moderation filters")
async def filter_command(_):
    pass

@filter_command.sub_command_group(name="ignore", description="Make a specific filter ignore messages from a specific channel")
async def filter_ignore_command(_):
    pass

@filter_ignore_command.sub_command(name="add", description="Add a channel to the filter ignore list")
async def filter_ignore_add_command(
        interaction,
        filter: FilterOption = Param(description="The filter you want to add"),
        channel: disnake.TextChannel = Param(description="The channel you want to add"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    filter_name = functions.get_filter_name(filter)
    try:
        current_values = json.loads(database[f"filter-ignore.{interaction.guild.id}"])
    except:
        current_values = {}
    if filter_name not in current_values:
        current_values[filter_name] = []
    if len(current_values[filter_name]) >= 10:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "item_limit").format("10"), ephemeral=True)
        return
    current_values[filter_name].append(channel.id)
    database[f"filter-ignore.{interaction.guild.id}"] = json.dumps(current_values)
    await interaction.response.send_message(f"<#{channel.id}> has been added to the **{filter}** filter's ignore list")

@filter_ignore_command.sub_command(name="remove", description="Remove a channel from the filter ignore list")
async def filter_ignore_remove_command(
        interaction,
        filter: FilterOption = Param(description="The filter you want to add"),
        channel: disnake.TextChannel = Param(description="The channel you want to add"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    filter_name = functions.get_filter_name(filter)
    try:
        current_values = json.loads(database[f"filter-ignore.{interaction.guild.id}"])
    except:
        current_values = {}
    if filter_name not in current_values:
        current_values[filter_name] = []
    if channel.id in current_values[filter_name]:
        current_values[filter_name].remove(channel.id)
        database[f"filter-ignore.{interaction.guild.id}"] = json.dumps(current_values)
        await interaction.response.send_message(f"<#{channel.id}> has been removed from the **{filter}** filter's ignore list")
    else:
        await interaction.response.send_message(f"<#{channel.id}> is not in the **{filter}** filter's ignore list")

@filter_ignore_command.sub_command(name="list", description="List the ignored channels")
async def filter_ignore_list_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    try:
        current_values = json.loads(database[f"filter-ignore.{interaction.guild.id}"])
    except:
        current_values = {}
    description = ""
    for value in current_values:
        channels = []
        deleted = []
        for channel in current_values[value]:
            exists = False
            for server_channel in interaction.guild.channels:
                if server_channel.id == channel:
                    exists = True
            if exists:
                channels.append(f"<#{channel}>")
            else:
                deleted.append(channel)
        for channel in deleted:
            values = current_values[value]
            values.remove(channel)
            current_values[value] = values
        if channels != []:
            description += f"{functions.get_filter_name(value).title()}: {' '.join(channels)}\n"
    database[f"filter-ignore.{interaction.guild.id}"] = json.dumps(current_values)
    embed = disnake.Embed(
        title="Ignored Channels",
        description=description if description != "" else "There are no ignored channels",
        color=variables.embed_color(),
    )
    await interaction.response.send_message(embed=embed)

@filter_command.sub_command_group(name="insults", description="Manage the insults filter")
async def insults_command(_):
    pass

@insults_command.sub_command(name="list", description="List all the words in the insults filter")
async def insults_list_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    try:
        insults_data = json.loads(database[f"insults.list.{interaction.guild.id}"])
    except:
        insults_data = []
    insults = []
    counter = 0
    for insult in insults_data:
        counter += 1
        insults.append(f"**{counter}.** {insult}")
    embed = disnake.Embed(title="Insults List", description="There are no insults configured for this server" if insults == [] else '\n'.join(insults), color=variables.embed_color())
    await interaction.response.send_message(embed=embed)

@insults_command.sub_command(name="status", description="See the current status of the insults filter")
async def insults_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    try:
        current_status = json.loads(database[f"insults.toggle.{interaction.guild.id}"])
    except:
        current_status = False
    await interaction.response.send_message(f"The insults filter is currently **{'enabled' if current_status else 'disabled'}**")

@insults_command.sub_command(name="enable", description="Enable the insults filter")
async def insults_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"insults.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("The insults filter has been successfully **enabled**")

@insults_command.sub_command(name="disable", description="Disable the insults filter")
async def insults_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"insults.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("The insults filter has been successfully **disabled**")

@insults_command.sub_command(name="add", description="Add a word to the insults filter")
async def insults_add_command(
        interaction,
        word: str = Param(description="The word you want to add"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    try:
        insults_data = json.loads(database[f"insults.list.{interaction.guild.id}"])
    except:
        insults_data = []
        database[f"insults.list.{interaction.guild.id}"] = json.dumps([])
    if len(insults_data) >= 20:
        await interaction.response.send_message("You can only add up to **20 words**!", ephemeral=True)
        return
    if len(word) <= 50:
        insults_data.append(word)
    else:
        await interaction.response.send_message("The specified word is too long!", ephemeral=True)
        return
    database[f"insults.list.{interaction.guild.id}"] = json.dumps(insults_data)
    await interaction.response.send_message(f'Successfully added **"{word}"** to your insults list')

async def insults_remove_autocomplete(interaction, string):
    try:
        words = json.loads(database[f"insults.list.{interaction.guild.id}"])
    except:
        words = []
    return list(filter(lambda word: string.lower() in word.lower(), words))[:20]

@insults_command.sub_command(name="remove", description="Remove a word from the insults filter")
async def insults_remove_command(
        interaction,
        word: str = Param(description="The word you want to remove", autocomplete=insults_remove_autocomplete),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    try:
        insults_data = json.loads(database[f"insults.list.{interaction.guild.id}"])
    except:
        insults_data = []
        database[f"insults.list.{interaction.guild.id}"] = json.dumps([])
    try:
        insults_data.remove(word)
    except:
        await interaction.response.send_message("That word does not exist in the insults filter!", ephemeral=True)
        return
    database[f"insults.list.{interaction.guild.id}"] = json.dumps(insults_data)
    await interaction.response.send_message(f'Successfully removed **"{word}"** from the insults list')

@filter_command.sub_command_group(name="links", description="Manage the links filter")
async def links_filter_command(_):
    pass

@links_filter_command.sub_command(name="enable", description="Enable the links filter")
async def links_filter_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"links.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("The links filter has been successfully **enabled**")

@links_filter_command.sub_command(name="disable", description="Disable the links filter")
async def links_filter_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"links.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("The links filter has been successfully **disabled**")

@links_filter_command.sub_command(name="status", description="See the current status of the links filter")
async def links_filter_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    value = False
    try:
        value = json.loads(database[f"links.toggle.{interaction.guild.id}"])
    except:
        pass
    await interaction.response.send_message(f"The links filter is currently **{'enabled' if value else 'disabled'}**")

@filter_command.sub_command_group(name="newline", description="Manage the newline filter")
async def newline_command(_):
    pass

@newline_command.sub_command(name="enable", description="Enable the newline filter")
async def newline_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"newline.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("The newline filter has been successfully **enabled**")

@newline_command.sub_command(name="disable", description="Disable the newline filter")
async def newline_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"newline.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("The newline filter has been successfully **disabled**")

@newline_command.sub_command(name="set", description="Set the limit for the newline filter")
async def newline_set_command(
        interaction,
        limit: int = Param(description="The limit you want to set"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    if limit < 1:
        limit = 1
    if limit > 800:
        limit = 800
    database[f"newline.limit.{interaction.guild.id}"] = limit
    await interaction.response.send_message(f"The newline filter limit has been set to **{limit} {'newline' if limit == 1 else 'newlines'}** per message")

@newline_command.sub_command(name="status", description="See the current status for the newline filter")
async def newline_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    value = 0
    try:
        value = json.loads(database[f"newline.toggle.{interaction.guild.id}"])
    except:
        pass
    limit = 10
    try:
        limit = json.loads(database[f"newline.limit.{interaction.guild.id}"])
    except:
        pass
    await interaction.response.send_message(f"The newline filter is currently **{'enabled' if value else 'disabled'}** (limit is **{limit}**)")

@filter_command.sub_command_group(name="mention", description="Manage the mention spam filter")
async def mention_command(_):
    pass

@mention_command.sub_command(name="enable", description="Enable the mention spam filter")
async def mention_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"mention.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("The mention filter has been successfully **enabled**")

@mention_command.sub_command(name="disable", description="Disable the mention spam filter")
async def mention_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"mention.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("The mention filter has been successfully **disabled**")

@mention_command.sub_command(name="set", description="Set the limit for the mention spam filter")
async def mention_set_command(
        interaction,
        limit: int = Param(description="The limit you want to set"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200
    database[f"mention.limit.{interaction.guild.id}"] = limit
    await interaction.response.send_message(f"The mention filter limit has been set to **{limit} {'mention' if limit == 1 else 'mentions'}** per message")

@mention_command.sub_command(name="status", description="See the current status for the mention spam filter")
async def mention_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    value = 0
    try:
        value = json.loads(database[f"mention.toggle.{interaction.guild.id}"])
    except:
        pass
    limit = 10
    try:
        limit = json.loads(database[f"mention.limit.{interaction.guild.id}"])
    except:
        pass
    await interaction.response.send_message(f"The mention spam filter is currently **{'enabled' if value else 'disabled'}** (limit is **{limit}**)")

@filter_command.sub_command_group(name="spam", description="Manage the spam filter")
async def spam_command(_):
    pass

@spam_command.sub_command(name="enable", description="Enable the spam filter")
async def spam_enable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"spamming.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("The spam filter has been successfully **enabled**")

@spam_command.sub_command(name="disable", description="Disable the spam filter")
async def spam_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"spamming.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("The spam filter has been successfully **disabled**")

@spam_command.sub_command(name="set", description="Set the limit for the spam filter")
async def spam_set_command(
        interaction,
        limit: int = Param(description="The limit you want to set"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    if limit < 1:
        limit = 1
    if limit > 25:
        limit = 25
    database[f"spamming.limit.{interaction.guild.id}"] = limit
    await interaction.response.send_message(f"The spam filter limit has been set to **{limit} {'message' if limit == 1 else 'messages'}** per **15 seconds**")

@spam_command.sub_command(name="status", description="See the current status for the spam filter")
async def spam_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
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
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    try:
        database[f"leave.text.{interaction.guild.id}"]
    except:
        await interaction.response.send_message(f"Please set a leave channel and message first", ephemeral=True)
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
        await interaction.response.send_message(f"Please set a leave channel and message first", ephemeral=True)
        return

    database[f"leave.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("Leave messages have been successfully **enabled**")

@leave_command.sub_command(name="disable", description="Disable leave messages")
async def leave_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"leave.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("Leave messages have been successfully **disabled**")

@leave_command.sub_command(name="text", description="Change the leave message text")
async def leave_text_command(
        interaction,
        text: str = Param(description="The leave message text"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
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
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
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
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
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
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    try:
        database[f"welcome.text.{interaction.guild.id}"]
    except:
        await interaction.response.send_message(f"Please set a welcome channel and message first", ephemeral=True)
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
        await interaction.response.send_message(f"Please set a welcome channel and message first", ephemeral=True)
        return

    database[f"welcome.toggle.{interaction.guild.id}"] = 1
    await interaction.response.send_message("Welcome messages have been successfully **enabled**")

@welcome_command.sub_command(name="disable", description="Disable welcome messages")
async def welcome_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"welcome.toggle.{interaction.guild.id}"] = 0
    await interaction.response.send_message("Welcome messages have been successfully **disabled**")

@welcome_command.sub_command(name="text", description="Change the welcome message text")
async def welcome_text_command(
        interaction,
        text: str = Param(description="The welcome message text"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
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
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
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
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
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

@client.slash_command(name="server", description="View information about this server")
async def server_command(_):
    pass

@server_command.sub_command(name="status", description="View statistics for this server")
async def server_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    await interaction.response.defer()
    embed = disnake.Embed(color=variables.embed_color())
    raid_protection = 0
    try:
        raid_protection = json.loads(database[f"{interaction.guild.id}.raid-protection"])
    except:
        pass
    insults_filter = 0
    try:
        insults_filter = json.loads(database[f"insults.toggle.{interaction.guild.id}"])
    except:
        pass
    spam_filter = 0
    try:
        spam_filter = json.loads(database[f"spamming.toggle.{interaction.guild.id}"])
    except:
        pass
    links_filter = 0
    try:
        links_filter = json.loads(database[f"links.toggle.{interaction.guild.id}"])
    except:
        pass
    mention_filter = 0
    try:
        mention_filter = json.loads(database[f"mention.toggle.{interaction.guild.id}"])
    except:
        pass
    newline_filter = 0
    try:
        newline_filter = json.loads(database[f"newline.toggle.{interaction.guild.id}"])
    except:
        pass
    try:
        doge_role_position = interaction.guild.me.top_role.position
    except:
        doge_role_position = 0
    mute_role = None; exists = False
    for role in interaction.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    mute_role_position = 0
    if exists:
        mute_role_position = mute_role.position
    ban_role = None; exists = False
    for role in interaction.guild.roles:
        if "ban" in role.name.lower():
            ban_role = role; exists = True
    ban_role_position = 0
    if exists:
        ban_role_position = ban_role.position
    differences = []
    members = []
    channels = []
    counter = 0
    current_second = math.floor(time.time())
    for cached_message in client.cached_messages:
        if cached_message.guild:
            if cached_message.guild.id != interaction.guild.id:
                continue
        if cached_message.author.id not in members:
            members.append(cached_message.author.id)
        if cached_message.channel.id not in channels:
            channels.append(cached_message.channel.id)
        sent_time = math.floor(cached_message.created_at.timestamp())
        if current_second != sent_time:
            differences.append(counter)
            current_second = sent_time
            counter = 0
        else:
            counter += 1
    if len(differences) > 0:
        average = round(sum(differences)/len(differences), 2)
        if average == 1.0:
            average = 1
    else:
        average = 0.0
    embed.add_field(name="Raid Protection", value=":white_check_mark: Enabled" if raid_protection else ":x: Disabled")
    embed.add_field(name="Newline Filter", value=":white_check_mark: Enabled" if newline_filter else ":x: Disabled")
    embed.add_field(name="Insults Filter", value=":white_check_mark: Enabled" if insults_filter else ":x: Disabled")
    embed.add_field(name="Spam Filter", value=":white_check_mark: Enabled" if spam_filter else ":x: Disabled")
    embed.add_field(name="Links Filter", value=":white_check_mark: Enabled" if links_filter else ":x: Disabled")
    embed.add_field(name="Mention Filter", value=":white_check_mark: Enabled" if mention_filter else ":x: Disabled")
    embed.add_field(name="Bot Role", value=f"{':white_check_mark:' if doge_role_position != 0 else ':x:'} #{doge_role_position}")
    embed.add_field(name="Muted Role", value=f"{':white_check_mark:' if doge_role_position > mute_role_position and mute_role_position != 0 else ':x:'} #{mute_role_position}")
    embed.add_field(name="Banned Role", value=f"{':white_check_mark:' if doge_role_position > ban_role_position and ban_role_position != 0 else ':x:'} #{ban_role_position}")
    embed.add_field(name="Message Rate", value=f"{average}/s")
    embed.add_field(name="Active Members", value=f"{len(members)}")
    embed.add_field(name="Active Channels", value=f"{len(channels)}")
    await interaction.edit_original_message(embed=embed)
    add_cooldown(interaction.author.id, "server", 5)

@server_command.sub_command_group(name="logging", description="Manage the log channel for your server")
async def logging_command(_):
    pass

@logging_command.sub_command(name="status", description="See the current log channel")
async def logging_status_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    channel = None
    try:
        channel = json.loads(database[f"logging.{interaction.guild.id}"])
    except:
        pass
    if channel == None:
        await interaction.response.send_message("This server does not have logging configured")
    else:
        await interaction.response.send_message(f"This server's log channel is set to <#{channel}>")

@logging_command.sub_command(name="set", description="Set the logging channel for your server")
async def logging_set_command(
        interaction,
        channel: disnake.channel.TextChannel = Param(description="The channel you want the bot to log messages to"),
    ):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    database[f"logging.{interaction.guild.id}"] = channel.id
    await interaction.response.send_message(f"This server's log channel has been set to <#{channel.id}>")

@logging_command.sub_command(name="disable", description="Disable logging for your server")
async def logging_disable_command(interaction):
    if not interaction.author.guild_permissions.administrator and interaction.author.id not in variables.permission_override:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    try:
        del database[f"logging.{interaction.guild.id}"]
    except:
        pass
    await interaction.response.send_message("Logging has been successfully disabled for this server")

@server_command.sub_command(name="suggest", description="Send a suggestion to the server owner")
async def server_suggest_command(
        interaction,
        suggestion: str = Param(description="The suggestion you want to send"),
    ):
    suggestion = functions.shrink(suggestion, 1500)
    await interaction.response.send_message(functions.get_text(interaction.author.id, "sending_suggestion"), ephemeral=True)
    try:
        await interaction.guild.owner.send(f"**{interaction.author.name}#{interaction.author.discriminator}** has sent a suggestion for **{interaction.guild.name}**\n{suggestion}")
        await interaction.edit_original_message(content=functions.get_text(interaction.author.id, "suggestion_sent"))
    except:
        await interaction.edit_original_message(content="Unable to send your suggestion")
    add_cooldown(interaction.author.id, "server", 300)

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
        title=functions.get_text(interaction.author.id, "guild_members"),
        description=f"{functions.get_text(interaction.author.id, 'user_accounts')}: **{users}**\n{functions.get_text(interaction.author.id, 'bot_accounts')}: **{bots}**\n{functions.get_text(interaction.author.id, 'total_members')}: **{users + bots}**",
        color=variables.embed_color(),
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

    embed = disnake.Embed(color=variables.embed_color())
    if interaction.guild.icon != None:
        embed.set_thumbnail(url=interaction.guild.icon)
    if interaction.guild.banner != None:
        embed.set_image(url=interaction.guild.banner)
    embed.add_field(name="Server ID", value=f"`{interaction.guild.id}`")
    embed.add_field(name="Server Region", value=f"{interaction.guild.region}")
    embed.add_field(name="Creation Time", value=f"<t:{functions.parse_snowflake(interaction.guild.id)}:R>")
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
    await interaction.response.defer()
    response = requests.get(f"https://api.github.com/repos/{repository.strip()}").json()
    try:
        if response["message"] == "Not Found":
            await interaction.edit_original_message(content="That GitHub repository was not found")
            return
    except:
        pass
    embed = disnake.Embed(color=variables.embed_color())
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
    await interaction.edit_original_message(embed=embed)
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
    await interaction.response.send_message(f'{functions.get_text(interaction.author.id, "i_choose")} **"{random_item}"**')

@client.slash_command(name="pypi", description="Fetch a project on PyPi")
async def pypi_command(
        interaction,
        project: str = Param(description="The PyPi project that you want to search"),
    ):
    await interaction.response.defer()
    response = requests.get(f"https://pypi.org/pypi/{project.strip()}/json")
    if response.status_code == 404:
        await interaction.edit_original_message(content="That PyPi package was not found")
        return
    response = response.json()
    size_unit = "bytes"; size = response["urls"][len(response["urls"])-1]["size"]
    if size > 1000:
        size_unit = "KB"
        size = size / 1000
        if size > 1000:
            size_unit = "MB"
            size = size / 1000
    embed = disnake.Embed(color=variables.embed_color())
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
    await interaction.edit_original_message(embed=embed)
    add_cooldown(interaction.author.id, "pypi", 5)

@client.slash_command(name="discriminator", description="Find users with the same discriminator")
async def discriminator_command(
        interaction,
        discriminator: str = Param(default=lambda interaction: interaction.author.discriminator, description="The discriminator to look for"),
    ):
    await interaction.response.defer()
    members = []
    discriminator = discriminator.replace("#", "")
    try:
        int(discriminator)
        if len(discriminator) != 4:
            raise Exception("invalid discriminator")
    except:
        await interaction.edit_original_message(content="That is not a valid discriminator!")
        return

    for member in client.get_all_members():
        if member.discriminator == discriminator:
            if str(member) not in members:
                members.append(str(member))
    if members == []:
        await interaction.edit_original_message(content="There are no other users with the same discriminator")
        return

    output = "\n".join(members)
    segments = disnake_paginator.split(output, 1000)
    pager = disnake_paginator.ButtonPaginator(
        prefix=f"```\n", suffix="```", color=variables.embed_color(), title="Discriminator", segments=segments,
        invalid_user_function=functions.invalid_user_function,
    )
    await pager.start(interaction, deferred=True)
    add_cooldown(interaction.author.id, "discriminator", 5)

@client.slash_command(name="warn", description="Warn a member in your server")
async def warn_command(
        interaction,
        member: disnake.Member = Param(description="The member you want to warn"),
        warning: str = Param(0, description="The warning you want to give the member (use 'reset' to reset the warnings)"),
    ):
    if interaction.author.guild_permissions.kick_members and interaction.author.guild_permissions.ban_members:
        pass
    elif interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return
    if warning == 0:
        warning = functions.get_text(member.id, "not_specified")
    
    try:
        warnings = json.loads(database[f"warnings.{member.id}"])
    except:
        warnings = {}
    try:
        guild_warnings = warnings[str(interaction.guild.id)]
    except:
        guild_warnings = 0
    guild_warnings += 1
    if warning.lower() == "reset":
        guild_warnings = 0
    else:
        if member.id == interaction.author.id:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "cannot_warn_self"), ephemeral=True)
            return
        if member.bot:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "cannot_warn_bot"), ephemeral=True)
            return
        if member.guild_permissions.administrator:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "cannot_warn_administrator"), ephemeral=True)
            return
        if member.top_role.position >= interaction.author.top_role.position:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission_warn").format(member), ephemeral=True)
            return
    warnings[str(interaction.guild.id)] = guild_warnings
    database[f"warnings.{member.id}"] = json.dumps(warnings)
    if warning.lower() == "reset":
        await interaction.response.send_message(functions.get_text(interaction.author.id, "warnings_reset").format(member), ephemeral=True)
        await log_message(interaction.guild, f"**{member}**'s warnings have been reset by **{interaction.author}**")
        return
    try:
        warning_embed = disnake.Embed(title=functions.get_text(member.id, "warning"), description=warning, color=disnake.Color.yellow())
        warning_embed.set_footer(text=functions.get_text(member.id, "warning_count").format(guild_warnings, f"{functions.get_text(member.id, 'warning_lower') if guild_warnings == 1 else functions.get_text(member.id, 'warnings_lower')}", interaction.guild.name))
        await member.send(embed=warning_embed)
        await interaction.response.send_message(embed=disnake.Embed(description=functions.get_text(interaction.author.id, "user_warned").format(member, guild_warnings), color=disnake.Color.green()))
        await log_message(interaction.guild, f"**{member}** has been warned by **{interaction.author}** (**{guild_warnings}**): {warning}")
    except:
        await interaction.response.send_message(embed=disnake.Embed(description=functions.get_text(interaction.author.id, "unable_to_warn").format(member), color=disnake.Color.red()))
    add_cooldown(interaction.author.id, "warn", 5)

@client.slash_command(name="kick", description="Kick a member from your server")
async def kick_command(
        interaction,
        member: disnake.Member = Param(description="The member you want to kick"),
        reason: str = Param(0, description="The reason for kicking the member"),
    ):
    if reason == 0:
        reason = functions.get_text(member.id, "not_specified")

    if interaction.author.guild_permissions.kick_members or interaction.author.id in variables.permission_override:
        if member.top_role.position >= interaction.author.top_role.position:
            await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission_kick").format(member), ephemeral=True)
            return
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(
                embed=disnake.Embed(
                    color=disnake.Color.green(),
                    description=functions.get_text(interaction.author.id, "user_kicked").format(member),
                )
            )
            await log_message(interaction.guild, f"**{member}** has been kicked by **{interaction.author}**: {reason}")
        except:
            await interaction.response.send_message(
                embed=disnake.Embed(
                    color=disnake.Color.red(),
                    description=functions.get_text(interaction.author.id, "unable_to_kick").format(member),
                ),
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)

@client.slash_command(name="ban", description="Ban a specified member from your server")
async def ban_command(
        interaction,
        user: disnake.User = Param(description="The ID of the member you want to ban"),
        reason: str = Param(0, description="The reason for banning the member"),
    ):
    if interaction.author.guild_permissions.ban_members or interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    if reason == 0:
        reason = functions.get_text(user.id, "not_specified")
    for member in interaction.guild.members:
        if member.id == user.id:
            if member.top_role.position >= interaction.author.top_role.position:
                await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission_ban").format(member), ephemeral=True)
                return
    try:
        await interaction.guild.ban(user, reason=reason, delete_message_days=0)
        await interaction.response.send_message(
            embed=disnake.Embed(
                color=disnake.Color.green(),
                description=functions.get_text(interaction.author.id, "user_banned").format(user),
            ),
        )
        await log_message(interaction.guild, f"**{user}** has been banned by **{interaction.author}**: {reason}")
    except:
        await interaction.response.send_message(
            embed=disnake.Embed(
                color=disnake.Color.red(),
                description=functions.get_text(interaction.author.id, "unable_to_ban").format(user),
            ),
            ephemeral=True,
        )

@client.slash_command(name="unban", description="Unban a specified member from your server")
async def unban_command(
        interaction,
        member: str = Param(description="The member you want to unban"),
    ):
    if interaction.author.guild_permissions.ban_members or interaction.author.id in variables.permission_override:
        pass
    else:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_permission"), ephemeral=True)
        return

    try:
        user_id = int(functions.remove_mentions(member))
        user = await client.fetch_user(user_id)
    except:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "mention_valid_user"), ephemeral=True)
        return
    try:
        await interaction.guild.unban(user)
        await interaction.response.send_message(
            embed=disnake.Embed(
                color=disnake.Color.green(),
                description=functions.get_text(interaction.author.id, "user_unbanned").format(user),
            ),
        )
        await log_message(interaction.guild, f"**{user}** has been unbanned by **{interaction.author}**")
    except:
        await interaction.response.send_message(
            embed=disnake.Embed(
                color=disnake.Color.red(),
                description=functions.get_text(interaction.author.id, "unable_to_unban").format(user),
            ),
            ephemeral=True,
        )

def autocomplete_units(_, string):
    results = []
    for conversion in converter.conversions:
        if conversion.input not in results:
            results.append(conversion.input)
    return list(filter(lambda unit: string.lower() in unit.lower(), results))[:20]

@client.slash_command(name="convert", description="Convert amounts to different units")
async def convert_command(
        interaction,
        amount: float = Param(description="The amount (for the input unit)"),
        input_unit: str = Param(name="input-unit", description="The input unit", autocomplete=autocomplete_units),
        output_unit: str = Param(name="output-unit", description="The output unit", autocomplete=autocomplete_units),
    ):
    input_unit = input_unit.strip()
    output_unit = output_unit.strip()
    data = converter.convert(amount, input_unit, output_unit)
    if data["error"] == 404:
        await interaction.response.send_message("That input/output pair is not supported!", ephemeral=True)
        return
    elif data["error"] == 403:
        await interaction.response.send_message("The input and output unit is the same!", ephemeral=True)
        return
    description = f"**{round(amount, 6):,} {data['input_abbreviation']}** = **{round(data['result'], 6):,} {data['output_abbreviation']}**\n\n**Unit abbreviations:**\n`{data['input_abbreviation']}` = `{data['input_unit']}`, `{data['output_abbreviation']}` = `{data['output_unit']}`"
    embed = disnake.Embed(
        title="Conversion",
        color=variables.embed_color(),
        description=description,
    )
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "convert", 3)

@client.slash_command(name="translate", description="Translate text to different languages")
async def translate_command(
        interaction,
        language: str = Param(description="The language you want to translate to", autocomplete=autocomplete_languages),
        text: str = Param(description="The text you want to translate"),
    ):
    await interaction.response.defer()
    try:
        translator = googletrans.Translator()
        result = translator.translate(text, dest=language.strip())
        embed = disnake.Embed(color=variables.embed_color())
        source_language = googletrans.LANGUAGES[result.src.lower()].title().replace("(", "").replace(")", "")
        destination_language = googletrans.LANGUAGES[result.dest.lower()].title().replace("(", "").replace(")", "")
        embed.add_field(name=f"Original Text ({source_language})", value=text, inline=False)
        embed.add_field(name=f"Translated Text ({destination_language})", value=result.text)
        await interaction.edit_original_message(embed=embed)
        add_cooldown(interaction.author.id, "translate", 5)
    except Exception as error:
        if "or fewer in length" in str(error):
            await interaction.edit_original_message(content="The output translation is too long!")
        else:
            await interaction.edit_original_message(content=f"There was an error while trying to translate the specified text: `{error}`")

@client.message_command(name="Translate")
async def message_translate_command(interaction):
    await interaction.response.defer(ephemeral=True) 
    try:
        text = interaction.target.content
        if text == "":
            if len(interaction.target.embeds) > 0:
                text = interaction.target.embeds[0].description
                if type(text) == disnake.embeds._EmptyEmbed:
                    await interaction.edit_original_message(content="That message does not have any text!")
                    return
            else:
                await interaction.edit_original_message(content="That message does not have any text!")
                return
        translator = googletrans.Translator()
        result = translator.translate(text, dest=functions.get_settings(interaction.author.id)["language"])
        embed = disnake.Embed(color=variables.embed_color())
        source_language = googletrans.LANGUAGES[result.src.lower()].title().replace("(", "").replace(")", "")
        destination_language = googletrans.LANGUAGES[result.dest.lower()].title().replace("(", "").replace(")", "")
        embed.add_field(name=f"Original Text ({source_language})", value=text, inline=False)
        embed.add_field(name=f"Translated Text ({destination_language})", value=result.text)
        await interaction.edit_original_message(embed=embed)
        add_cooldown(interaction.author.id, "translate", 5)
    except Exception as error:
        if "or fewer in length" in str(error):
            await interaction.edit_original_message(content="The output translation is too long!")
        else:
            await interaction.edit_original_message(content=f"There was an error while trying to translate the specified text: `{error}`")

@client.slash_command(name="definition", description="Find the definition of a word")
async def definition_command(
        interaction,
        word: str = Param(description="The word you want to find the definition of"),
        language: str = Param(None, description="The word's language"),
    ):
    await interaction.response.defer()

    if language == None:
        settings = functions.get_settings(interaction.author.id)
        language = settings["language"]
    else:
        language = language.strip().lower()
    reversed_languages = {value: key for key, value in googletrans.LANGUAGES.items()}
    if language in reversed_languages.keys():
        language = reversed_languages[language]
    response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/{language}/{word.strip()}").json()
    try:
        if response["title"] == "No Definitions Found":
            try:
                language_name = googletrans.LANGUAGES[language].title()
            except:
                language_name = language
            await interaction.edit_original_message(content=f"That word was not found in the **{language_name}** dictionary")
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
    embed = disnake.Embed(title="Definition", description=description, color=variables.embed_color())
    await interaction.edit_original_message(embed=embed)
    add_cooldown(interaction.author.id, "definition", 5)

@client.slash_command(name="todo", description="Manage your to-do list")
async def todo_command(_):
    pass

@todo_command.sub_command(name="list", description="Show your to-do list")
async def todo_list_command(interaction):
    try:
        todo_list = json.loads(database[f"todo.{interaction.author.id}"])
    except:
        todo_list = []
    text = ""
    counter = 0
    for todo in todo_list:
        counter += 1
        text += f"**{counter}.** {todo}\n"
    if text == "":
        text = functions.get_text(interaction.author.id, "todo_empty")
    embed = disnake.Embed(title=functions.get_text(interaction.author.id, "todo_list"), description=text, color=variables.embed_color())
    await interaction.response.send_message(embed=embed)

@todo_command.sub_command(name="add", description="Add an item to your to-do list")
async def todo_add_command(
        interaction,
        item: str = Param(description="The item you want to add to your to-do list"),
    ):
    item = item.strip()
    try:
        todo_list = json.loads(database[f"todo.{interaction.author.id}"])
    except:
        todo_list = []
    if len(todo_list) >= 20:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "item_limit").format("20"), ephemeral=True)
        return
    if len(item) > 50:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "text_too_long"), ephemeral=True)
        return
    if item not in todo_list: 
        todo_list.append(item)
    else:
        await interaction.response.send_message("That item is already in your to-do list!", ephemeral=True)
        return
    database[f"todo.{interaction.author.id}"] = json.dumps(todo_list)
    await interaction.response.send_message(functions.get_text(interaction.author.id, "todo_added").format(item))

async def todo_remove_autocomplete(interaction, string):
    try:
        items = json.loads(database[f"todo.{interaction.author.id}"])
    except:
        items = []
    return list(filter(lambda item: string.lower() in item.lower(), items))[:20]

@todo_command.sub_command(name="remove", description="Remove an item from your to-do list")
async def todo_remove_command(
        interaction,
        item: str = Param(description="The item you want to add to your to-do list", autocomplete=todo_remove_autocomplete),
    ):
    item = item.strip()
    try:
        todo_list = json.loads(database[f"todo.{interaction.author.id}"])
    except:
        todo_list = []
    if item in todo_list:
        todo_list.remove(item)
    else:
        await interaction.response.send_message("That item is not in your to-do list!", ephemeral=True)
        return
    database[f"todo.{interaction.author.id}"] = json.dumps(todo_list)
    await interaction.response.send_message(functions.get_text(interaction.author.id, "todo_removed").format(item))

@client.slash_command(name="reminders", description="Remind yourself about something")
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
        text += f"**{functions.get_text(interaction.author.id, 'time')}:** <t:{round(end_time)}:R>\n**{functions.get_text(interaction.author.id, 'text')}:** {reminder[2]}\n\n"
    if text == "":
        text = functions.get_text(interaction.author.id, "no_reminders")
    embed = disnake.Embed(
        title=functions.get_text(interaction.author.id, "reminders"),
        description=text, 
        color=variables.embed_color(),
    )
    await interaction.response.send_message(embed=embed)
    add_cooldown(interaction.author.id, "reminders", 3)

async def remind_remove_autocomplete(interaction, string):
    try:
        reminders = json.loads(database[f"reminders.{interaction.author.id}"])
    except:
        reminders = []
    text = []
    for reminder in reminders:
        text.append(reminder[2])
    return list(filter(lambda reminder: string.lower() in reminder.lower(), text))[:20]

@remind_command.sub_command(name="remove", description="Remove a reminder")
async def remind_remove_command(
        interaction,
        text: str = Param(description="The name of the reminder", autocomplete=remind_remove_autocomplete),
    ):
    try:
        current_reminders = json.loads(database[f"reminders.{interaction.author.id}"])
    except:
        current_reminders = []
    key = None
    for reminder in current_reminders:
        if reminder[2] == text:
            key = reminder
    if key == None:
        await interaction.response.send_message("That reminder does not exist!", ephemeral=True)
        return
    current_reminders.remove(key)
    database[f"reminders.{interaction.author.id}"] = json.dumps(current_reminders)
    await interaction.response.send_message(functions.get_text(interaction.author.id, "reminder_removed"))

@remind_command.sub_command(name="add", description="Add a new reminder")
async def remind_add_command(
        interaction,
        duration: str = Param(description="The duration of the reminder"),
        text: str = Param(description="The name of the reminder"),
    ):
    original_duration = duration
    try:
        duration = functions.parse_time(duration) / 60
    except:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "invalid_duration"), ephemeral=True)
        return

    if len(text) > 100:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "text_too_long"), ephemeral=True)
        return
    if duration > 10080:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "duration_too_long"), ephemeral=True)
        return
    if duration < 0:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "no_negative_numbers"), ephemeral=True)
        return
    try:
        current_reminders = json.loads(database[f"reminders.{interaction.author.id}"])
    except:
        current_reminders = []
    if len(current_reminders) >= 5:
        await interaction.response.send_message(functions.get_text(interaction.author.id, "item_limit").format("5"), ephemeral=True)
        return
    current_reminders.append([round(time.time()), duration*60, text])
    database[f"reminders.{interaction.author.id}"] = json.dumps(current_reminders)
    await interaction.response.send_message(functions.get_text(interaction.author.id, 'reminder_added').format(functions.display_time(interaction.author.id, functions.parse_time(original_duration))))

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

def hash_text(hash_type, input_text, length=None):
    hasher = hashlib.new(hash_type)
    hasher.update(input_text.encode("utf-8"))
    output_hash = None
    try:
        output_hash = hasher.hexdigest()
    except:
        if length != None:
            output_hash = hasher.hexdigest(length)
    if output_hash != None:
        return output_hash
    else:
        raise Exception("unable to hash text")

def get_variable(name):
    try:
        return math_variables[name]
    except:
        return None

def set_variable(name, value):
    math_variables[name] = value
    return value

def parse_application_command(command):
    command_data = "/" + command.data.name + " "
    for option in command.data.options:
        command_data += option.name
        command_data += " "
        for sub_option_group in option.options:
            command_data += f"[{sub_option_group.name}]"
            command_data += " "
            if sub_option_group.options != []:
                for sub_option in sub_option_group.options:
                    command_data += f"[{sub_option.name}]"
                    command_data += " "
    return command_data.strip()

def parse_interaction(interaction):
    interaction_data = "/" + interaction.data.name + " "
    for option in interaction.data.options:
        interaction_data += option.name
        if option.value != "" and option.value != None:
            interaction_data += f":{option.value}"
        interaction_data += " "
        for sub_option_group in option.options:
            if sub_option_group.value != "" and sub_option_group.value != None:
                interaction_data += f"{sub_option_group.name}:{sub_option_group.value}"
            else:
                interaction_data += f"{sub_option_group.name}"
            interaction_data += " "
            if sub_option_group.options != []:
                for sub_option in sub_option_group.options:
                    if sub_option.value != "" and sub_option.value != None:
                        interaction_data += f"{sub_option.name}:{sub_option.value}"
                    else:
                        interaction_data += f"{sub_option.name}"
                    interaction_data += " "
    return interaction_data.strip()

def build_member_permissions(member):
    permission_list = ""
    for permission in member.guild_permissions:
        if permission[1] == True:
            permission_list += f":white_check_mark: `{permission[0]}`\n"
        else:
            permission_list += f":x: `{permission[0]}`\n"
    return permission_list

def build_role_permissions(role):
    permission_list = ""
    for permission in role.permissions:
        if permission[1] == True:
            permission_list += f":white_check_mark: `{permission[0]}`\n"
        else:
            permission_list += f":x: `{permission[0]}`\n"
    return permission_list

def evaluate_expression(expression):
    expression = expression.replace("^", "**")
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")

    math_functions = {
        "boo": "Boo!",
        "pi": math.pi,
        "π": math.pi,
        "time": time.time(),
        "round": lambda x: round(x),
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
        "log": lambda value: math.log(value),
        "sin": lambda value: math.sin(value),
        "cos": lambda value: math.cos(value),
        "tan": lambda value: math.tan(value),
    }

    try:
        answer = str(simpleeval.simple_eval(expression, functions=math_functions))
    except:
        answer = None
    return answer

async def log_message(guild, message):
    try:
        log_channel = json.loads(database[f"logging.{guild.id}"])
        for channel in guild.channels:
            if channel.id == log_channel:
                await channel.send(message, allowed_mentions=disnake.AllowedMentions.none())
    except:
        pass

def rgb_to_hex(rgb_color):
    for value in rgb_color:
        if value >= 0 and value <= 255:
            pass
        else:
            raise Exception("invalid RGB color code")
    return '#%02x%02x%02x' % rgb_color

def generate_color(color_code, generate_image=True):
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
            if generate_image:
                image = Image.new("RGB", (image_width, image_height), color_code)
                image.save("images/color.png")

            value = color_code.lstrip('#'); length = len(value)
            rgb_color = tuple(int(value[i:i+length//3], 16) for i in range(0, length, length//3))
            return (color_code, rgb_color)
        except:
            return 1
    elif color_code.count(",") == 2 and "(" in color_code and ")" in color_code:
        try:
            color_code = color_code.replace("(", ""); color_code = color_code.replace(")", "")
            color_code = color_code.replace(", ", ","); rgb_color = tuple(map(int, color_code.split(',')))
            color_code = rgb_to_hex(rgb_color)
            if generate_image:
                image = Image.new("RGB", (image_width, image_height), color_code)
                image.save("images/color.png")

            return (color_code, rgb_color)
        except:
            return 1
    else:
        return 1

async def mute_member(member, duration):
    mute_role = None; exists = False
    for role in member.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if not exists:
        return

    if duration == 0:
        try:
            await member.add_roles(mute_role)
        except:
            pass
    else:
        try:
            moderation_data = json.loads(database["mute." + str(member.guild.id)])
        except:
            database["mute." + str(member.guild.id)] = json.dumps([])
            moderation_data = json.loads(database["mute." + str(member.guild.id)])
        try:
            await member.add_roles(mute_role)
            moderation_data.append([member.id, round(time.time()), duration])
            database["mute." + str(member.guild.id)] = json.dumps(moderation_data)
        except:
            pass

async def send_user_message(user_id, message):
    for guild in client.guilds:
        for member in guild.members:
            if str(member.id) == str(user_id):
                await member.send(message)
                return

async def send_vote_message(user_id):
    if functions.get_settings(user_id)["vote_messages"]:
        for guild in client.guilds:
            for member in guild.members:
                if str(member.id) == str(user_id):
                    interaction = disnake_paginator.wrappers.UserInteractionWrapper(member)
                    await interaction.response.send_message(
                        language.get(
                            functions.get_settings(user_id)["language"], "vote_message"),
                            view=get_vote_view(functions.get_text(user_id, "vote_add_reminder")),
                        )
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
                    welcome_message = welcome_message.replace("{discriminator}", member.discriminator)
                    welcome_message = welcome_message.replace("{members}", str(member.guild.member_count))
                    welcome_message = welcome_message.replace("{server}", member.guild.name)
                    await channel.send(welcome_message)
    except:
        pass
    mute_key = f"muted.{member.id}.{member.guild.id}".encode("utf-8")
    if mute_key in database.keys():
        del database[mute_key]
        mute_role = None; exists = False
        for role in member.guild.roles:
            if "mute" in role.name.lower():
                mute_role = role; exists = True
        if exists:
            try:
                await member.add_roles(mute_role)
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
                    leave_message = leave_message.replace("{discriminator}", member.discriminator)
                    leave_message = leave_message.replace("{members}", str(member.guild.member_count))
                    leave_message = leave_message.replace("{server}", member.guild.name)
                    await channel.send(leave_message)
    except:
        pass
    muted = False
    for role in member.roles:
        if "mute" in role.name.lower():
            muted = True
    if muted:
        database[f"muted.{member.id}.{member.guild.id}"] = 1

async def on_guild_remove(guild):
    for key in database.keys():
        if str(guild.id) in key.decode("utf-8"):
            del database[key]

async def on_guild_join(guild):
    try:
        async for entry in guild.audit_logs(limit=10):
            if entry.action == disnake.AuditLogAction.bot_add:
                if entry.target.id == client.user.id:
                    await help_paginator.start(disnake_paginator.wrappers.UserInteractionWrapper(entry.user))
                    break
    except:
        pass

async def on_reaction_add(payload):
    if payload.user_id == client.user.id or payload.user_id in blacklisted_users or payload.guild_id == None:
        return
    try:
        reaction_roles = json.loads(database[f"reaction-roles.{payload.guild_id}"])
    except:
        return

    for reaction_role in reaction_roles:
        if int(reaction_role["message"]) == payload.message_id:
            if reaction_role["channel"] == payload.channel_id:
                if reaction_role["emoji"] == str(payload.emoji):
                    target_guild = None
                    role = None
                    for guild in client.guilds:
                        for guild_role in guild.roles:
                            if guild_role.id == reaction_role["role"]:
                                target_guild = guild
                                role = guild_role
                    if role:
                        if payload.member:
                            try:
                                await payload.member.add_roles(role)
                                try:
                                    await payload.member.send(f"You have been given the **{role.name}** role in **{target_guild.name}**")
                                except:
                                    pass
                            except:
                                try:
                                    await payload.member.send(f"I was unable to give you the **{role.name}** role in **{target_guild.name}**")
                                except:
                                    pass
                                await log_message(target_guild, f"Unable to give **{payload.member}** the **{role.name}** role (reaction roles)")
                    else:
                        reaction_roles.remove(reaction_role)
                        database[f"reaction-roles.{payload.guild_id}"] = json.dumps(reaction_roles)
                    return

async def on_reaction_remove(payload):
    if payload.user_id == client.user.id or payload.user_id in blacklisted_users or payload.guild_id == None:
        return
    try:
        reaction_roles = json.loads(database[f"reaction-roles.{payload.guild_id}"])
    except:
        return

    for reaction_role in reaction_roles:
        if int(reaction_role["message"]) == payload.message_id:
            if reaction_role["channel"] == payload.channel_id:
                if reaction_role["emoji"] == str(payload.emoji):
                    target_guild = None
                    role = None
                    for guild in client.guilds:
                        for guild_role in guild.roles:
                            if guild_role.id == reaction_role["role"]:
                                target_guild = guild
                                role = guild_role
                    if role:
                        member = None
                        for guild in client.guilds:
                            if guild.id == payload.guild_id:
                                for user in guild.members:
                                    if user.id == payload.user_id:
                                        member = user
                        if member:
                            try:
                                await member.remove_roles(role)
                                try:
                                    await member.send(f"Your **{role.name}** role has been removed in **{target_guild.name}**")
                                except:
                                    pass
                            except:
                                try:
                                    await member.send(f"I was unable to remove your **{role.name}** role in **{target_guild.name}**")
                                except:
                                    pass
                                await log_message(target_guild, f"Unable to remove **{member}**'s **{role.name}** role (reaction roles)")
                    else:
                        reaction_roles.remove(reaction_role)
                        database[f"reaction-roles.{payload.guild_id}"] = json.dumps(reaction_roles)
                    return

async def on_message(message):
    if message.author.bot or not message.guild:
        return

    prefix = variables.prefix
    if message.content == f"<@{client.user.id}>" or message.content == f"<@!{client.user.id}>":
        await message.channel.send(embed=disnake.Embed(title="New Prefix", description=f"My prefix here is `/` (slash commands)\nIf you do not see any slash commands, make sure the bot is invited with [this link]({variables.bot_invite_link})", color=variables.embed_color()))
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
                ignored_channels = json.loads(database[f"filter-ignore.{message.guild.id}"])
            except:
                ignored_channels = {}
            for filter in variables.filters.values():
                if filter not in ignored_channels:
                    ignored_channels[filter] = []
            try:
                if message.channel.id not in ignored_channels["insults"]:
                    if json.loads(database[f"insults.toggle.{message.guild.id}"]):
                        insults = json.loads(database[f"insults.list.{message.guild.id}"])
                        for word in insults:
                            if word.lower() in message.content.lower().replace(" ", ""):
                                try:
                                    await message.delete()
                                except:
                                    pass
                                try:
                                    await message.author.send(f'Please do not use the word **"{word.lower()}"** in this server!')
                                except:
                                    pass
                                await mute_member(message.author, 0.16)
                                await log_message(message.guild, f'{message.author.mention} used the word **"{word.lower()}"** in <#{message.channel.id}>\n\n{functions.shrink(message.content, 1500)}')
                                return
            except:
                pass
            try:
                if message.channel.id not in ignored_channels["links"]:
                    if json.loads(database[f"links.toggle.{message.guild.id}"]):
                        link_regexes = ["http://", "https://", "www.", "discord.gg/"]
                        for regex in link_regexes:
                            if regex in message.content.lower().replace(" ", ""):
                                try:
                                    await message.delete()
                                except:
                                    pass
                                try:
                                    await message.author.send("Please do not put links in your message!")
                                except:
                                    pass
                                await mute_member(message.author, 0.16)
                                await log_message(message.guild, f'{message.author.mention} sent a link in <#{message.channel.id}>\n\n{functions.shrink(message.content, 1500)}')
                                return
            except:
                pass
            try:
                if message.channel.id not in ignored_channels["spamming"]:
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
                            if strikes >= strike_limit:
                                try:
                                    await message.delete()
                                except:
                                    pass
                                try:
                                    await message.author.send(f"Stop spamming! You are sending more than **{strikes} {'message' if strikes == 1 else 'messages'}** in **15 seconds**!")
                                except:
                                    pass
                                await mute_member(message.author, 0.16)
                                await log_message(message.guild, f'{message.author.mention} is spamming (**{strikes}**) in <#{message.channel.id}>\n\n{functions.shrink(message.content, 1500)}')
                                return
            except:
                pass
            try:
                if message.channel.id not in ignored_channels["mention"]:
                    if json.loads(database[f"mention.toggle.{message.guild.id}"]):
                        limit = 10
                        try:
                            limit = json.loads(database[f"mention.limit.{message.guild.id}"])
                        except:
                            pass
                        mentions = len(message.raw_mentions)
                        if mentions > limit:
                            try:
                                await message.delete()
                            except:
                                pass
                            try:
                                await message.author.send(f"Please do not spam mentions in your message! You just mentioned **{mentions} {'user' if mentions == 1 else 'users'}**!")
                            except:
                                pass
                            await mute_member(message.author, 0.16)
                            await log_message(message.guild, f'{message.author.mention} is spamming mentions (**{mentions}**) in <#{message.channel.id}>\n\n{functions.shrink(message.content, 1500)}')
                            return
            except:
                pass
            try:
                if message.channel.id not in ignored_channels["newline"]:
                    if json.loads(database[f"newline.toggle.{message.guild.id}"]):
                        limit = 10
                        try:
                            limit = json.loads(database[f"newline.limit.{message.guild.id}"])
                        except:
                            pass
                        newlines = message.content.count("\n")
                        if "\n"*limit in message.content:
                            try:
                                await message.delete()
                            except:
                                pass
                            try:
                                await message.author.send(f"Please do not spam newlines in your message! You just sent **{newlines} {'newline' if newlines == 1 else 'newlines'}** in **1 message**!")
                            except:
                                pass
                            await mute_member(message.author, 0.16)
                            newline = "\n"
                            await log_message(message.guild, f'{message.author.mention} is spamming newlines (**{newlines}**) in <#{message.channel.id}>\n\n{functions.shrink(message.content, 1500).replace(newline*8, newline+"..."+newline)}')
                            return
            except:
                pass
    last_messages[message.author.id] = time.time()
  
    afk_key = f"afk.{message.author.id}".encode("utf-8")
    if afk_key in database.keys():
        del database[afk_key]
        try:
            await message.author.send(functions.get_text(message.author.id, "afk_removed"))
        except:
            pass
    for mention in message.mentions:
        try:
            afk_status = json.loads(database[f"afk.{mention.id}"])
            user_name = None
            for user in client.users:
                if user.id == mention.id:
                    user_name = user.name
            if not user_name:
                user_name = functions.get_text(message.author.id, "mentioned_user")
            await message.reply(
                functions.get_text(
                    message.author.id, "currently_afk",
                ).format(
                    user_name,
                    f"<t:{afk_status[0]}:R>",
                    functions.remove_mentions(afk_status[1]),
                ),
            )
        except:
            pass
    
    if message.content.startswith(prefix) and len(message.content) > 1 and message.author.id not in variables.bot_owners:
        await message.channel.send("We have migrated to slash commands!", embed=disnake.Embed(title="New Prefix", description=f"My prefix here is `/` (slash commands)\nIf you do not see any slash commands, make sure the bot is invited with [this link]({variables.bot_invite_link})", color=variables.embed_color()))
        return

    if message.content.startswith(prefix+"execute"):
        length = len(prefix+"execute ")
        if len(message.content) >= length:
            code = message.content[length:]
        else:
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
        if code.startswith("`") and code.endswith("`"):
            code = code[1:-1]

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
        
        output = output.replace(os.getenv("TOKEN"), "<TOKEN>")
        segments = disnake_paginator.split(output)
        if len(output) > 2000:
            output = output.replace("`", "\`")
            pager = disnake_paginator.ButtonPaginator(
                prefix=f"{codeblock}{output_language}\n", 
                suffix=codeblock, 
                color=variables.embed_color(), 
                title=f"Code Output", 
                segments=segments,
                invalid_user_function=functions.invalid_user_function,
            )
            await pager.start(disnake_paginator.wrappers.MessageInteractionWrapper(message))
        elif len(output.strip()) == 0:
            await message.add_reaction("✅")
        else:
            await message.channel.send(output)

async def on_slash_command_error(interaction, error):
    error_text = str(error)
    if error_text.startswith("InteractionResponded:") or error_text.startswith("Command raised an exception: InteractionResponded:"):
        return

    if type(error) == disnake.errors.Forbidden:
        try:
            await interaction.author.send("I do not have the required permissions!")
        except:
            return
    else:
        if "or fewer in length" in error_text:
            try:
                await interaction.response.send_message("Message too long to be sent!", ephemeral=True)
            except:
                try:
                    await interaction.edit_original_message(content="Message too long to be sent!")
                except:
                    await interaction.channel.send("Message too long to be sent!")
            return

        error_id = random.randint(0, 32768)
        escaped_character = '\`'
        interaction_data = parse_interaction(interaction)
        formatted_error = str(''.join(traceback.format_exception(error, error, error.__traceback__)))
        file = open(f"error-{error_id}.txt", "w+")
        file.write(formatted_error)
        file.close()
        output = f"**{interaction.author.name}#{interaction.author.discriminator}** (`{interaction.author.id}`) has ran into an error in **{interaction.author.guild.name}** (`{interaction.author.guild.id}`)\n\n**Command:**\n```\n{interaction_data.replace('`', escaped_character)}```**Error**:\n```\n{error}```**Time:**\n```\n{datetime.datetime.now()}```"
        report_embed = disnake.Embed(
            title="Error Report",
            description=output,
            color=disnake.Color.red(),
        )

        for user_id in variables.message_managers:
            sent = False
            for guild in client.guilds:
                for member in guild.members:
                    if member.id == user_id:
                        try:
                            if not sent:
                                await member.send(embed=report_embed, file=disnake.File(f"error-{error_id}.txt"))
                                sent = True
                        except Exception as new_error:
                            print(f"Unable to send error to {member}: {new_error}")

        embed = disnake.Embed(title=functions.get_text(interaction.author.id, "bot_error"), description=f"{functions.get_text(interaction.author.id, 'error_message')}\n```\n{error}\n```", color=disnake.Color.red(), timestamp=datetime.datetime.now())
        embed.set_footer(text=functions.get_text(interaction.author.id, "bot_error_report"))
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            try:
                await interaction.edit_original_message(embed=embed)
            except:
                await interaction.channel.send(embed=embed)

        await asyncio.sleep(30)
        os.remove(f"error-{error_id}.txt")
