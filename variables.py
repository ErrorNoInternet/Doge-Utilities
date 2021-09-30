import os
import functions

shard_count = 2
bot_owner = 531392146767347712
message_managers = [531392146767347712]
permission_override = [531392146767347712]
test_guilds = [518893687627841574]
embed_color = 0x20c2f6
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
version_number = round((version_number / 10) / 4, 2)

bot_invite_link = "https://discord.com/oauth2/authorize?client_id=854965721805226005&permissions=8&scope=applications.commands%20bot"
support_server_invite = "https://discord.gg/3Tp7R8FUsC"
no_permission_text = "You do not have permission to use this command!"
not_command_owner_text = "You are not the sender of that command!"
vote_message = "Thank you for voting for Doge Utilities!"
previous_button_text = "<"
next_button_text = ">"
first_button_text = "<<"
last_button_text = ">>"

status_types = ["Playing", "Watching", "Listening", "Competing"]
status1 = ["with Discord", "with [users] users", "on some servers", "capture the flag"]
status2 = ["over Discord", "[servers] servers", "Dogecoin stocks", "over the world"]
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
