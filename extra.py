import string
import disnake
import variables
import functions

async def auto_count(channel_id):
	digits = str(string.digits)
	for guild in functions.client.guilds:
		for channel in guild.channels:
			if channel.id == channel_id:
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

async def post_announcement(title, text, mention=False):
    for guild in functions.client.guilds:
        if guild.id == 879662689708806154:
            for channel in guild.channels:
                if channel.id == 879665441545519134:
                    embed = disnake.Embed(title=title, description=text, color=variables.embed_color)
                    announcement = await channel.send("<@&879665075642835006>" if mention else "", embed=embed)
                    await announcement.publish()

