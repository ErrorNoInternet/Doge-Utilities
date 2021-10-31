import os
import sys
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
    time.sleep(10)

    global server_channels
    global server_roles
    while True:
        for guild in core.client.guilds:
            server_channels[guild.id] = guild.channels
            server_roles[guild.id] = guild.roles
        time.sleep(5)

async def random_status():
    idle = False
    cycles = 120
    while True:
        cycles += 1
        try:
            if time.time() - variables.last_command > 180:
                if not idle:
                    await core.client.change_presence(status=disnake.Status.idle)
                    idle = True
            else:
                if idle or cycles > 120:
                    await core.select_status()
                    cycles = 0
                    idle = False
        except Exception as error:
            print("Error: " + str(error))
        await asyncio.sleep(1)

def update_counter(guild_id):
    if guild_id not in variables.protected_guilds:
        variables.protected_guilds[guild_id] = 1
    else:
        variables.protected_guilds[guild_id] += 1

@core.client.event
async def on_guild_channel_create(channel):
    try:
        current_setting = json.loads(core.database[f"{role.guild.id}.raid-protection"])
        if not current_setting:
            return
        variables.updated_channels.append(channel.id)
        await channel.delete()
    except:
        pass

    mute_role = None; exists = False
    for role in channel.guild.roles:
        if "mute" in role.name.lower():
            mute_role = role; exists = True
    if exists:
        try:
            try:
                await channel.set_permissions(mute_role, send_messages=False)
            except:
                await channel.set_permissions(mute_role, connect=False)
        except:
            pass
    ban_role = None; exists = False
    for role in channel.guild.roles:
        if "ban" in role.name.lower():
            ban_role = role; exists = True
    if exists:
        try:
            await channel.set_permissions(ban_role, view_channel=False)
        except:
            pass

@core.client.event
async def on_guild_channel_update(before, after):
    try:
        current_setting = json.loads(core.database[f"{before.guild.id}.raid-protection"])
        if not current_setting:
            return
    except:
        return

    if after.id in variables.updated_channels:
        variables.updated_channels.remove(after.id)
        return
    variables.updated_channels.append(after.id)
    if type(after) == disnake.TextChannel:
        await after.edit(name=before.name, topic=before.topic, category=before.category, slowmode_delay=before.slowmode_delay)
    elif type(after) == disnake.VoiceChannel:
        await after.edit(name=before.name, category=before.category)
    elif type(after) == disnake.CategoryChannel:
        await after.edit(name=before.name)
    update_counter(before.guild.id)

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
    update_counter(channel.guild.id)

@core.client.event
async def on_guild_role_create(role):
    try:
        current_setting = json.loads(core.database[f"{role.guild.id}.raid-protection"])
        if not current_setting:
            return
        variables.updated_roles.append(role.id)
        await role.delete()
    except:
        pass

@core.client.event
async def on_guild_role_update(before, after):
    try:
        current_setting = json.loads(core.database[f"{before.guild.id}.raid-protection"])
        if not current_setting:
            return
    except:
        return

    if before.managed:
        return

    if after.id in variables.updated_roles:
        variables.updated_roles.remove(after.id)
        return
    variables.updated_roles.append(after.id)
    await after.edit(name=before.name, color=before.color, permissions=before.permissions)
    update_counter(before.guild.id)

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
    update_counter(role.guild.id)

@core.client.event
async def on_ready():
    print(f"Successfully logged in as {core.client.user} in {round(time.time() - initialize_time, 1)} seconds")
    
    global first_run
    if not first_run:
        first_run = True
        threading.Thread(
            name="random_status",
            target=asyncio.run_coroutine_threadsafe,
            args=(random_status(), core.client.loop, ),
        ).start()
        core.client.add_view(core.get_vote_view())

@core.client.event
async def on_raw_reaction_add(payload):
    await core.on_reaction_add(payload)

@core.client.event
async def on_raw_reaction_remove(payload):
    await core.on_reaction_remove(payload)

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
async def on_guild_join(guild):
    await core.on_guild_join(guild)

@core.client.event
async def on_error(event, *_):
    if event == "on_application_command":
        return
    else:
        print(f"Uncaught exception in {event}: {sys.exc_info()[1]}")

@core.client.event
async def on_slash_command_error(interaction, error):
    await core.on_slash_command_error(interaction, error)

threading.Thread(name="raid-protection", target=update_objects).start()
core.client.topggpy = topgg.DBLClient(
    core.client,
    os.environ["TOPGG_TOKEN"],
    autopost=True,
    post_shard_count=True
)
core.client.run(os.environ["TOKEN"])
