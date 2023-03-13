import os
import string
import random
import subprocess

bot_owners = [531392146767347712, 469870741165441034]
permission_override = bot_owners
message_managers = bot_owners


def embed_color(): return 0x20c2f6


secrets = [
    "OAUTH_ID",
    "OAUTH_SECRET",
    "REDIS_HOST",
    "REDIS_PASSWORD",
    "REDIS_PORT",
    "TOKEN",
    "TOPGG_TOKEN",
    "WEATHER_KEY",
    "WEB_SECRET",
    "WEBSITE_URL",
]
prefix = "="
shard_count = 2
last_command = 0
protected_guilds = {}
test_guilds = None
large_number = 1e1000
updated_channels = []
updated_roles = []
updated_members = []
settings_cache = {}
ascii_characters = string.ascii_lowercase + \
    string.ascii_uppercase + string.digits
bold_characters = "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
italic_characters = "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡0123456789"
extension_characters = string.punctuation + " "
ascii_characters += extension_characters
bold_characters += extension_characters
italic_characters += extension_characters

owner_commands = [
    "execute",
    "blacklist",
]
filters = {
    "insults": "insults",
    "spam": "spamming",
    "links": "links",
    "mention": "mention",
    "newline": "newline",
}
units = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}
unit_abbreviations = {
    "s": ["sec", "second"],
    "m": ["min", "minute"],
    "h": ["hr", "hour"],
    "d": ["day"],
    "w": ["week"],
}
default_settings = {
    "language": "en",
    "vote_messages": True,
    "afk_messages": True,
}
supporters = {
    "translators": {
        "en": [531392146767347712],
        "zh-cn": [531392146767347712],
        "de": [469870741165441034, 851344098597797948],
        "ru": [652953834360143876],
        "sk": [394208818419990528],
    },
    "developers": [
        531392146767347712,
    ],
    "ideas": [
        531392146767347712,
        469870741165441034,
        652953834360143876,
        507511172061200395,
    ],
}
bot_version = "unknown"
try:
    bot_version = subprocess.check_output(
        ['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
except:
    print("[WARNING] Unable to get Git commit hash")
bot_last_updated = "unknown"
try:
    bot_last_updated = subprocess.check_output(
        ["git", "log", "-1", "--date=short", "--format=%cd"]).decode("ascii").strip()
except:
    print("[WARNING] Unable to get Git commit date")

bot_invite_link = "https://discord.com/oauth2/authorize?client_id=854965721805226005&permissions=8&scope=applications.commands%20bot"
support_server_invite = "https://discord.gg/3Tp7R8FUsC"
help_text = "**Hello there!** My name is **Doge Utilities**, and I am a Discord bot made to help you with all sorts of tasks. I use **slash commands**, which is Discord's new command system made for Discord bots. If you would like to see all my commands, simply press the `/` key on your keyboard into the chat box and click on the <:DogeUtilities:879683075393613824> icon.\n\nOne of the first things to do is to enable raid protection for your server. This feature allows you to protect your server from hackers and raid bots. If someone deletes a channel or a role while this feature is on, Doge Utilities will automatically re-create whatever was deleted. To enable this, run the `/raid-protection enable` command.\n\nThe third thing you want to do is to enable filters. Filters are moderation tools that can help you automatically manage your server. There are currently **5 filters**. Namely `links`, `spam`, `mention`, `insults`, and `newline`. Type `/filter` to see the commands for all the filters. There is also a log feature, which lets you know when a member triggers a filter on your server. To set this up, run `/server logging set <#channel>`.\n\nYou might also want to setup welcome and leave messages. These are messages that get sent whenever someone joins or leaves your server. You can choose a welcome channel with `/greetings welcome channel <#channel>` and set a **custom welcome message** with `/greetings welcome text <message>`. Most people would want to put a helpful message introducing the user to the server. You can also include things like \"{user}\" or \"{server}\" as variables in your greeting message. {user} will get replaced by the user's username, {server} will get replaced by the server's name, and so on. The full list is: `{user}`, `{user_id}`, `{discriminator}`, `{members}`, and `{server}`.\n\nThe last thing to do is to configure autorole. Roles basically tell people what you are in a specific server. If you have the 'Administrator' role, then everyone would know that you have all the permissions on this server and can do anything. If you have the 'Developer' role, then people might ask you questions about programming. Autorole is a feature that can automatically assign roles to users when they join your server. To get started with this, simply run `/autorole set <role>`. The limit for the amount of roles you can set is **5**.\n\nIf you have any questions, please join the [official support server](https://discord.gg/3Tp7R8FUsC) and ask for help. If you have a suggestion, please send them with the `/suggest` command. Thank you for using Doge Utilities!\n\nDoge Utilities privacy policy: <WEBSITE_URL>/privacy\nDoge Utilities terms of use: <WEBSITE_URL>/terms\nDoge Utilities source code: https://github.com/ErrorNoInternet/Doge-Utilities".replace(
    "<WEBSITE_URL>", os.getenv("WEBSITE_URL"))
status_types = ["Playing", "Watching", "Listening", "Competing"]
status1 = ["with Discord", "with [users] users", "on [servers] servers"]
status2 = ["over Discord", "[servers] servers",
           "Dogecoin stocks", "over the world"]
status3 = ["lofi music", "requests", "suggestions",
           "the radio", "[servers] servers"]
status4 = ["the Olympics", "[servers] servers", "a contest", "a competition"]
weekdays = {1: "Monday", 2: "Tuesday", 3: "Wednesday",
            4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
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
    "524288": "HTTP Interactions Only",
    "4194304": "Active Developer",
}
badge_list = {
    "Discord Employee": "<:DiscordStaff:879666899980546068>",
    "Discord Partner": "<:DiscordPartner:879668340434534400>",
    "HypeSquad Events": "<:HypeSquadEvents:879666970310606848>",
    "Bug Hunter Level 1": "<:BugHunter1:879666851448234014>",
    "HypeSquad Bravery": "<:HypeSquadBravery:879666945153175612>",
    "HypeSquad Brilliance": "<:HypeSquadBrilliance:879666956884643861>",
    "HypeSquad Balance": "<:HypeSquadBalance:879666934717771786>",
    "Early Supporter": "<:EarlySupporter:879666916493496400>",
    "Team User": "<:TeamUser:890866907996127305>",
    "Bug Hunter Level 2": "<:BugHunter2:879666866971357224>",
    "Verified Bot": "<:VerifiedBot:879670687554498591>",
    "Verified Bot Developer": "<:VerifiedBotDeveloper:879669786550890507>",
    "Discord Certified Moderator": "<:DiscordModerator:879666882976837654>",
    "HTTP Interactions Only": "<:HTTPInteractionsOnly:1047141867806015559>",
    "Active Developer": "<:ActiveDeveloper:1047141451244523592>",
}
application_flags = {
    1 << 12: "Presence Intent",
    1 << 13: "Presence Intent (unverified)",
    1 << 14: "Guild Members Intent",
    1 << 15: "Guild Members Intent (unverified)",
    1 << 16: "Unusual Growth (verification suspended)",
    1 << 18: "Message Content Intent",
    1 << 19: "Message Content Intent (unverified)",
    1 << 23: "Suports Application Commands",
}
