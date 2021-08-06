import os
import time
import random
import discord
import asyncio
import webServer
import functions
import variables
import threading

initializeTime = time.time()
serverChannels = {}; serverRoles = {}
if not os.path.exists("last-command"):
	file = open("last-command", "w+")
	file.write("0"); file.close()

def updateObjects():
	time.sleep(2)
	while True:
		for guild in functions.client.guilds:
			serverChannels[guild.id] = guild.channels
			serverRoles[guild.id] = guild.roles
		time.sleep(8)

async def randomStatus():
	idle = False; cycles = 120
	while True:
		cycles += 1
		try:
			lastCommandFile = open("last-command", "r")
			lastCommand = int(lastCommandFile.read()); lastCommandFile.close()
			if time.time() - lastCommand > 180:
				if not idle:
					await functions.client.change_presence(status=discord.Status.idle); idle = True
			else:
				if idle or cycles > 120:
					await functions.selectStatus()
					cycles = 0; idle = False
		except Exception as error:
			print("Error: " + str(error))
		await asyncio.sleep(1)

@functions.client.event
async def on_guild_channel_delete(channel):
	try:
		currentSetting = functions.settingsDatabase[f"{channel.guild.id}|raid-protection"]
		if not currentSetting:
			return
	except:
		return

	global serverChannels
	for cachedChannel in serverChannels[channel.guild.id]:
		if channel.id == cachedChannel.id:
			if type(channel) == discord.TextChannel:
				newChannel = await channel.guild.create_text_channel(name=cachedChannel.name, position=cachedChannel.position, category=cachedChannel.category, slowmode_delay=cachedChannel.slowmode_delay, topic=cachedChannel.topic)
				await newChannel.edit(is_nsfw=cachedChannel.is_nsfw())
			elif type(channel) == discord.CategoryChannel:
				await channel.guild.create_category(name=cachedChannel.name, position=cachedChannel.position)
			else:
				await channel.guild.create_voice_channel(name=cachedChannel.name, position=cachedChannel.position, category=cachedChannel.category, user_limit=cachedChannel.user_limit, bitrate=cachedChannel.bitrate)

@functions.client.event
async def on_guild_role_delete(role):
	try:
		currentSetting = functions.settingsDatabase[f"{role.guild.id}|raid-protection"]
		if not currentSetting:
			return
	except:
		return

	global serverRoles
	for cachedRole in serverRoles[role.guild.id]:
		if role.id == cachedRole.id:
			newRole = await role.guild.create_role(name=cachedRole.name, color=cachedRole.color, permissions=cachedRole.permissions)
			await newRole.edit(position=cachedRole.position)

@functions.client.event
async def on_ready():
	print("Initializing plugins...", end=''); functions.discord_components.DiscordComponents(functions.client)
	print(f"\rSuccessfully logged in as {functions.client.user} in {round(time.time() - initializeTime, 1)} seconds")

	threading.Thread(target=updateObjects).start()
	await randomStatus()

@functions.client.event
async def on_member_join(member):
	try:
		autoroles = functions.autoroleDatabase[member.guild.id]
		for role in member.guild.roles:
			for roleID in autoroles:
				if int(roleID) == role.id:
					await member.add_roles(role)
	except:
		pass

@functions.client.event
async def on_message(message):
	await functions.on_message(message)

webServer.start("Doge Utilities")
functions.client.run(os.getenv("TOKEN"))

