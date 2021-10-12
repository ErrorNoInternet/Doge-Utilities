import os
import core
import json
import time
import topgg
import disnake
import asyncio
import variables
import threading

initialize_time = time.time()
first_run = False
server_roles = {}
server_channels = {}
if not os.path.exists("images"):
    os.mkdir("images")

def update_objects():
    time.sleep(2)
    while True:
        for guild in core.client.guilds:
            server_channels[guild.id] = guild.channels
            server_roles[guild.id] = guild.roles
        time.sleep(8)

async def random_status():
    idle = False; cycles = 120
    while True:
        cycles += 1
        try:
            if time.time() - variables.last_command > 180:
                if not idle:
                    await core.client.change_presence(status=disnake.Status.idle); idle = True
            else:
                if idle or cycles > 120:
                    await core.select_status()
                    cycles = 0; idle = False
        except Exception as error:
            print("Error: " + str(error))
        await asyncio.sleep(1)

@core.client.event
async def on_guild_channel_delete(channel):
    try:
        current_setting = json.loads(core.database[f"{channel.guild.id}.raid-protection"])
        if not current_setting:
            return
    except:
        return

    global server_channels
    for cached_channel in server_channels[channel.guild.id]:
        if channel.id == cached_channel.id:
            if type(channel) == disnake.TextChannel:
                new_channel = await channel.guild.create_text_channel(name=cached_channel.name, position=cached_channel.position, category=cached_channel.category, slowmode_delay=cached_channel.slowmode_delay, topic=cached_channel.topic)
                await new_channel.edit(is_nsfw=cached_channel.is_nsfw())
                server_channels[channel.guild.id].append(new_channel)
            elif type(channel) == disnake.CategoryChannel:
                server_channels[channel.guild.id].append(await channel.guild.create_category(name=cached_channel.name, position=cached_channel.position))
            else:
                server_channels[channel.guild.id].append(await channel.guild.create_voice_channel(name=cached_channel.name, position=cached_channel.position, category=cached_channel.category, user_limit=cached_channel.user_limit, bitrate=cached_channel.bitrate))

@core.client.event
async def on_guild_role_delete(role):
    try:
        current_setting = json.loads(core.database[f"{role.guild.id}.raid-protection"])
        if not current_setting:
            return
    except:
        return

    if role.managed:
        return

    global server_roles
    for cached_role in server_roles[role.guild.id]:
        if role.id == cached_role.id:
            new_role = await role.guild.create_role(name=cached_role.name, color=cached_role.color, permissions=cached_role.permissions)
            await new_role.edit(position=cached_role.position)
            server_roles[role.guild.id].append(new_role)

@core.client.event
async def on_ready():
    print(f"Successfully logged in as {core.client.user} in {round(time.time() - initialize_time, 1)} seconds")
    
    global first_run
    if not first_run:
        first_run = True
        threading.Thread(name="raid-protection", target=update_objects).start()
        await random_status()

@core.client.event
async def on_member_join(member):
    await core.on_member_join(member)

@core.client.event
async def on_member_remove(member):
    await core.on_member_remove(member)

@core.client.event
async def on_message(message):
    try:
        await core.on_message(message)
    except Exception as error:
        print("Uncaught exception: " + str(error))

@core.client.event
async def on_message_delete(message):
    await core.on_message_delete(message)

@core.client.event
async def on_message_edit(message, new_message):
    await core.on_message_delete(message, new_message)

@core.client.event
async def on_guild_join(guild):
    await core.on_guild_join(guild)

@core.client.event
async def on_error(event, _):
    if event == "on_application_command":
        return
    else:
        print(f"Uncaught exception in {event}")

@core.client.event
async def on_slash_command_error(interaction, error):
    await core.on_slash_command_error(interaction, error)

core.client.topggpy = topgg.DBLClient(
    core.client,
    os.environ["TOPGG_TOKEN"],
    autopost=True,
    post_shard_count=True
)
core.client.run(os.environ["TOKEN"])
