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

def find_user(user_id):
    text = ""
    counter = 0
    for guild in core.client.guilds:
      for member in guild.members:
        if member.id == user_id:
          counter += 1
          text += f"Found `{member}` in `{guild}`\n"
    if not counter: text += f"Unable to find `{user_id}`"
    else: text += f"\nFound `{user_id}` in `{counter}/{len(core.client.guilds)}` servers"
    print(text)

def get_translations(languages=["en", "zh-cn", "de", "ru", "sk"]):
    for language_name in languages:
        print(f"`{language_name}`: {len(language.data[language_name])}")

async def ask_translations(message, user_id, target_language):
    target_user = None
    for user in core.client.users:
        if user.id == user_id:
            target_user = user
    if target_user == None:
        print(f"`{user_id}` was not found")
        return
    def check(result):
        return result.author.id == target_user.id and str(result.channel.type) == "private"
    def get_language(code):
        return core.googletrans.LANGUAGES[code]

    questions = []
    results = []
    for key in language.data["en"].keys():
        if key not in language.data[target_language].keys():
            questions.append(key)
    if len(questions) == 0:
        print(f"There is nothing missing for **{get_language(target_language).title()}**")
        return
    await target_user.send('Hello! I am here to ask you for some translations... If you want to stop, simply reply with "cancel" or "stop".')
    counter = 0
    stopped = False
    for question in questions:
        counter += 1
        await target_user.send(f'({counter}/{len(questions)}) What is **{get_language(target_language).title()}** for "{language.data["en"][question]}"?')
        msg = await core.client.wait_for("message", check=check)
        if msg.content.lower() == "cancel" or msg.content.lower() == "stop":
            await target_user.send("Okay! Thanks for participating!")
            stopped = True
            break
        results.append(f'`{question}`: "{msg.content}"')
    if not stopped:
        await target_user.send("Looks like we are done! Thank you for all your translations!")
        await target_user.send("Do you have anything extra to say? If you do, please send them. If you don't, please send \"no\".")
        msg = await core.client.wait_for("message", check=check)
        results.append("\n**Additional text:** " + msg.content)
        await target_user.send("We are finished! Thanks!")
    output = f"Translations for **{get_language(target_language).title()}** from **{target_user}**\n\n" + "\n".join(results)
    pager = core.Paginator(title="Translations", segments=[output[i: i + 2000] for i in range(0, len(output), 2000)], color=variables.embed_color)
    await pager.start(core.FakeUserInteraction(message.author))

