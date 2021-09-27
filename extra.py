import string
import disnake
import variables
import functions

async def auto_count(channel_id):
	digits = str(string.digits)
	for guild in functions.client.guilds:
		for channel in guild.channels:
			if channel.id == channel_id:
				last_message = await channel.history(limit=1).flatten()
				last_message = last_message[0]; number = ""
				for letter in last_message.content:
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

async def find_user(client, message, user_id):
    text = ""
    counter = 0
    for guild in client.guilds:
      for member in guild.members:
        if member.id == user_id:
          counter += 1
          text += f"Found `{member}` in `{guild}`\n"
    if not counter: text += f"Unable to find `{user_id}`"
    else: text += f"\nFound `{user_id}` in `{counter}/{len(client.guilds)}` servers"
    await message.channel.send(text)

