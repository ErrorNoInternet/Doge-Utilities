import discord
import variables
import functions

async def autoCount(channelID):
	import string; digits = str(string.digits)
	for guild in functions.client.guilds:
		for channel in guild.channels:
			if channel.id == channelID:
				lastMessage = await channel.history(limit=1).flatten()
				lastMessage = lastMessage[0]; number = ""
				for letter in lastMessage.content:
					for digit in digits:
						if digit == letter:
							number += letter
				try:
					number = int(number) + 1
				except:
					number = 0
				await channel.send(number)

async def postAnnouncement(title, text, mention=False):
  for guild in functions.client.guilds:
    if guild.id == 879662689708806154:
      for channel in guild.channels:
        if channel.id == 879665441545519134:
          embed = discord.Embed(title=title, description=text, color=variables.embedColor)
          message = await channel.send("<@&879665075642835006>" if mention else "", embed=embed)
          await message.publish()

