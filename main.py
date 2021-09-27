import os
if os.getenv("TOKEN") == None:
    print("Unable to load TOKEN variable"); exit()
if os.getenv("TOPGG_TOKEN") == None:
    print("Unable to load TOPGG_TOKEN variable"); exit()
if os.getenv("REDIS_URL") == None:
    print("Unable to load REDIS_URL variable"); exit()

import json
import time
import topgg
import disnake
import asyncio
import functions
import threading

initialize_time = time.time()
first_run = False
server_roles = {}
server_channels = {}
if not os.path.exists("last-command"):
    file = open("last-command", "w+")
    file.write("0"); file.close()
if not os.path.exists("images"):
    os.mkdir("images")

def update_objects():
    time.sleep(2)
    while True:
        for guild in functions.client.guilds:
            server_channels[guild.id] = guild.channels
            server_roles[guild.id] = guild.roles
        time.sleep(8)

async def random_status():
    idle = False; cycles = 120
    while True:
        cycles += 1
        try:
            last_command_file = open("last-command", "r")
            last_command = int(last_command_file.read()); last_command_file.close()
            if time.time() - last_command > 180:
                if not idle:
                    await functions.client.change_presence(status=disnake.Status.idle); idle = True
            else:
                if idle or cycles > 120:
                    await functions.select_status()
                    cycles = 0; idle = False
        except Exception as error:
            print("Error: " + str(error))
        await asyncio.sleep(1)

@functions.client.event
async def on_guild_channel_delete(channel):
    try:
        current_setting = json.loads(functions.database[f"{channel.guild.id}.raid-protection"])
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
            elif type(channel) == disnake.CategoryChannel:
                await channel.guild.create_category(name=cached_channel.name, position=cached_channel.position)
            else:
                await channel.guild.create_voice_channel(name=cached_channel.name, position=cached_channel.position, category=cached_channel.category, user_limit=cached_channel.user_limit, bitrate=cached_channel.bitrate)

@functions.client.event
async def on_guild_role_delete(role):
    try:
        current_setting = json.loads(functions.database[f"{role.guild.id}.raid-protection"])
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

@functions.client.event
async def on_ready():
    print(f"Successfully logged in as {functions.client.user} in {round(time.time() - initialize_time, 1)} seconds")
    
    global first_run
    if not first_run:
        first_run = True
        threading.Thread(name="raid-protection", target=update_objects).start()
        await random_status()

@functions.client.event
async def on_member_join(member):
    await functions.on_member_join(member)

@functions.client.event
async def on_member_remove(member):
    await functions.on_member_remove(member)

@functions.client.event
async def on_message(message):
    try:
        await functions.on_message(message)
    except Exception as error:
        print("Uncaught exception: " + str(error))

@functions.client.event
async def on_message_delete(message):
    await functions.on_message_delete(message)

@functions.client.event
async def on_message_edit(message, new_message):
    await functions.on_message_delete(message, new_message)

@functions.client.event
async def on_guild_join(guild):
    await functions.on_guild_join(guild)

functions.client.topggpy = topgg.DBLClient(
    functions.client,
    os.getenv("TOPGG_TOKEN"),
    autopost=True,
    post_shard_count=True
)
functions.client.run(os.getenv("TOKEN"))
