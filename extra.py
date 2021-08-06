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

