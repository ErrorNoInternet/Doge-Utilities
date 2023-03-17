import math
import string
import time

import disnake
import disnake_paginator

import core
import language
import variables


async def auto_count(channel_id):
    digits = str(string.digits)
    for guild in core.client.guilds:
        for channel in guild.channels:
            if channel.id == channel_id:
                last_message = await channel.history(limit=1).flatten()
                last_message = last_message[0]
                number = ""
                for letter in last_message.content:
                    for digit in digits:
                        if digit == letter:
                            number += letter
                try:
                    number = int(number) + 1
                except:
                    number = 0
                await channel.send(number)


async def post_update(message, items):
    for guild in core.client.guilds:
        if guild.id == 879662689708806154:
            for channel in guild.channels:
                if channel.id == 897679369835774002:
                    description = ""
                    for item in items:
                        description += f"**-** {item}\n"
                    embed = disnake.Embed(
                        description=description, color=variables.embed_color())

                    class CommandView(disnake.ui.View):
                        def __init__(self, channel):
                            super().__init__()
                            self.channel = channel

                        @disnake.ui.button(label="Post Update", style=disnake.ButtonStyle.green)
                        async def post_update(self, _, interaction):
                            if interaction.author != message.author:
                                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                                return

                            await old_message.edit(view=None)
                            announcement = await self.channel.send(embed=embed)
                            await announcement.publish()
                            self.stop()

                        @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.red)
                        async def cancel(self, _, interaction):
                            if interaction.author != message.author:
                                await interaction.response.send_message(variables.not_command_owner_text, ephemeral=True)
                                return

                            await old_message.edit(view=None)
                            await interaction.response.send_message("Successfully cancelled update", ephemeral=True)
                            self.stop()
                    old_message = await message.channel.send(view=CommandView(channel), embed=embed)


async def post_announcement(message, title, text, mention=False):
    for guild in core.client.guilds:
        if guild.id == 879662689708806154:
            for channel in guild.channels:
                if channel.id == 879665441545519134:
                    embed = disnake.Embed(
                        title=title, description=text, color=variables.embed_color())

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
    if not counter:
        text += f"Unable to find `{user_id}`"
    else:
        text += f"\nFound `{user_id}` in `{counter}/{len(core.client.guilds)}` servers"
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

    if target_language not in language.data:
        language.data[target_language] = {}
    questions = []
    results = []
    for key in language.data["en"].keys():
        if key not in language.data[target_language].keys():
            questions.append(key)
    if len(questions) == 0:
        print(
            f"There is nothing missing for **{get_language(target_language).title()}**")
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
        language.data[target_language][question] = msg.content
    if not stopped:
        await target_user.send("Looks like we are done! Thank you for all your translations!")
        await target_user.send("Do you have anything extra to say? If you do, please send them. If you don't, please send \"no\".")
        msg = await core.client.wait_for("message", check=check)
        results.append("\n**Additional text:** " + msg.content)
        await msg.reply("Got it! Thanks!", mention_author=False)
    output = f"Translations for **{get_language(target_language).title()}** from **{target_user}**\n\n" + \
        "\n".join(results)
    pager = disnake_paginator.ButtonPaginator(
        title="Translations", segments=disnake_paginator.split(output), color=variables.embed_color())
    await pager.start(disnake_paginator.wrappers.UserInteractionWrapper(message.author))


def messages_per_second():
    differences = []
    guilds = []
    members = []
    counter = 0
    current_second = math.floor(time.time())
    for cached_message in core.client.cached_messages:
        if str(cached_message.channel.type) != "private":
            if cached_message.guild.id not in guilds:
                guilds.append(cached_message.guild.id)
        if cached_message.author.id not in members:
            members.append(cached_message.author.id)
        sent_time = math.floor(cached_message.created_at.timestamp())
        if current_second != sent_time:
            differences.append(counter)
            current_second = sent_time
            counter = 0
        else:
            counter += 1
    average = round(sum(differences)/len(differences), 2)
    if average == 1.0:
        average = 1
    print(f"I am receiving **{average} {'message' if average == 1 else 'messages'}/s** from **{len(members)} {'member' if len(members) == 1 else 'members'}** across **{len(guilds)} {'guild' if len(guilds) == 1 else 'guilds'}**")
