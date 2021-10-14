import os

prefix = "="
shard_count = 2
last_command = 0
owner_commands = ["blacklist"]
bot_owners = [531392146767347712, 599186408925560833, 890264136477462618]
permission_override = bot_owners
message_managers = bot_owners.remove(890264136477462618)
test_guilds = None
#embed_color = 0x20c2f6
embed_color = 0xfc4c02
large_number = 1e1000
version_number = 0
build_number = 0
for file in os.listdir():
    try:
        code_file = open(file, "r"); code = code_file.read(); code_file.close()
        version_number += int(str(len(code) / 1000).split(".")[0])
        build_number += int(str(len(code) / 1000).split(".")[1])
    except:
        pass
version_number = round((version_number / 10) / 14, 2)

bot_invite_link = "https://discord.com/oauth2/authorize?client_id=854965721805226005&permissions=8&scope=applications.commands%20bot"
support_server_invite = "https://discord.gg/3Tp7R8FUsC"
no_permission_text = "You do not have permission to use this command!"
not_command_owner_text = "You are not the sender of that command!"
vote_message = "Thank you for voting for Doge Utilities!"
previous_button_text = "<"
next_button_text = ">"
first_button_text = "<<"
last_button_text = ">>"
help_text = "**Hello!** My name is Doge Utilities, and I am a Discord bot made to help you with all sorts of tasks. I use **slash commands**, which is Discord's new command system made for Discord bots. If you would like to see my commands, simply type `/` into the chat box and click on the <:DogeUtilities:879683075393613824> icon.\n\nOne of the first things to do is to enable raid protection for your server. This feature allows you to protect your server from hackers and raid bots. If someone deletes a channel or a role while this feature is on, Doge Utilities will automatically re-create whatever was deleted. To enable this, run the `/raid-protection enable` command.\n\nAnother thing to do is the run the `/setup muted` and `/setup banned` command. These commands will help you create a role that can mute members (so they can no longer send messages) in your server. The bot will automatically configure the role for **all your channels**.\n\nThe third thing you want to do is to enable filters. Filters are moderation tools that can help you automatically manage your server. There are currently **4 filters**. Namely `links`, `spam`, `mention`, and `insults`. Type `/filter` to see the commands for all the filters. There is also a log feature, which lets you know when a member triggers a filter on your server. To set this up, run `/logging set <#channel>`.\n\nYou might also want to setup welcome and leave messages. These are messages that get sent whenever someone joins or leaves your server. You can choose a welcome channel with `/greetings welcome channel <#channel>` and set a **custom welcome message** with `/greetings welcome text <message>`. Most people would want to put a helpful message introducing the user to the server.\n\nThe last thing to do is to configure autorole. Roles basically tell people what you are in a specific server. If you have the 'Administrator' role, then everyone would know that you have all the permissions on this server and can do anything. If you have the 'Developer' role, then people might ask you questions about programming. Autorole is a feature that can automatically assign roles to users when they join your server. To get started with this, simply run `/autorole set <role>`. The limit for the amount of roles you can set is **5**.\n\nIf you have any questions, please join the [official support server](https://discord.gg/3Tp7R8FUsC) and ask for help. If you have a suggestion, please send them with the `/suggest` command. Thank you for using Doge Utilities!"
status_types = ["Playing", "Watching", "Listening", "Competing"]
status1 = ["with Discord", "with [users] users", "on some servers", "Halloween games"]
status2 = ["over Discord", "[servers] servers", "Dogecoin stocks", "over the world", "for candy"]
status3 = ["lofi music", "requests", "suggestions", "the radio", "[servers] servers"]
status4 = ["the Olympics", "[servers] servers", "a contest", "a competition"]
weekdays = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
public_flags = {
    "1": "Discord Employee",
    "2": "Discord Partner",
    "4": "HypeSquad Events",
    "8": "Bug Hunter Level 1",
    "64": "HypeSquad Bravery",
    "128": "HypeSquad Brilliance",
    "256": "HypeSquad Balance",
    "512": "Early Supporter",
    "1024": "Team User",
    "16384": "Bug Hunter Level 2",
    "65536": "Verified Bot",
    "131072": "Verified Bot Developer",
    "262144": "Discord Certified Moderator",
}
badge_list = {
    "Discord Employee": "<:DiscordStaff:879666899980546068>",
    "Discord Partner": "<:DiscordPartner:879668340434534400>",
    "Bug Hunter Level 1": "<:BugHunter1:879666851448234014>",
    "Bug Hunter Level 2": "<:BugHunter2:879666866971357224>",
    "HypeSquad Bravery": "<:HypeSquadBravery:879666945153175612>",
    "HypeSquad Brilliance": "<:HypeSquadBrilliance:879666956884643861>",
    "HypeSquad Balance": "<:HypeSquadBalance:879666934717771786>",
    "HypeSquad Events": "<:HypeSquadEvents:879666970310606848>",
    "Early Supporter": "<:EarlySupporter:879666916493496400>",
    "Verified Bot Developer": "<:VerifiedBotDeveloper:879669786550890507>",
    "Discord Certified Moderator": "<:DiscordModerator:879666882976837654>",
    "Verified Bot": "<:VerifiedBot:879670687554498591>",
    "Team User": "<:TeamUser:890866907996127305>",
}
