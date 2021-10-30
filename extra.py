import core
import string
import disnake
import language
import variables

async def auto_count(channel_id):
	digits = str(string.digits)
	for guild in core.client.guilds:
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

async def post_announcement(message, title, text, mention=False):
    for guild in core.client.guilds:
        if guild.id == 879662689708806154:
            for channel in guild.channels:
                if channel.id == 879665441545519134:
                    embed = disnake.Embed(title=title, description=text, color=variables.embed_color)
                    class CommandView(disnake.ui.View):
                        def __init__(self, channel):
                            super().__init__()
                            self.channel = channel

                        @disnake.ui.button(label="Post Announcement", style=disnake.ButtonStyle.green)
                        async def post_announcement(self, _, interaction):
                            if interaction.author != message.author:
                                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                                return

                            await old_message.edit(view=None)
                            announcement = await self.channel.send("<@&879665075642835006>" if mention else "", embed=embed)
                            await announcement.publish()
                            self.stop()

                        @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.red)
                        async def cancel(self, _, interaction):
                            if interaction.author != message.author:
                                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                                return

                            await old_message.edit(view=None)
                            await interaction.response.send_message("Successfully cancelled announcement", ephemeral=True)
                            self.stop()
                    old_message = await message.channel.send(view=CommandView(channel), embed=embed)

def find_user(client, user_id):
    text = ""
    counter = 0
    for guild in client.guilds:
      for member in guild.members:
        if member.id == user_id:
          counter += 1
          text += f"Found `{member}` in `{guild}`\n"
    if not counter: text += f"Unable to find `{user_id}`"
    else: text += f"\nFound `{user_id}` in `{counter}/{len(client.guilds)}` servers"
    print(text)

def get_translations(languages=["en", "zh-cn", "de", "ru", "sk"]):
    for language_name in languages:
        print(f"`{language_name}`: {len(language.data[language_name])}")

