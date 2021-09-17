import os
import functions

shard_count = 2
bot_owner = 531392146767347712
message_managers = [531392146767347712]
permission_override = [531392146767347712]
embed_color = 0xf1c40f
large_number = 1e1000

version_number = 0; build_number = 0
for file in os.listdir():
	try:
		code_file = open(file, "r"); code = code_file.read(); code_file.close()
		version_number += int(str(len(code) / 1000).split(".")[0])
		build_number += int(str(len(code) / 1000).split(".")[1])
	except:
		pass
version_number = round((version_number / 10) / 4, 2)

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
	"Discord Employee": "<:discord_staff:879666899980546068>",
	"Discord Partner": "<:discord_partner:879668340434534400>",
	"Bug Hunter Level 1": "<:bug_hunter1:879666851448234014>",
	"Bug Hunter Level 2": "<:bug_hunter2:879666866971357224>",
	"HypeSquad Bravery": "<:HypeSquad_bravery:879666945153175612>",
	"HypeSquad Brilliance": "<:HypeSquad_brilliance:879666956884643861>",
	"HypeSquad Balance": "<:HypeSquad_balance:879666934717771786>",
	"HypeSquad Events": "<:HypeSquad_events:879666970310606848>",
	"Early Supporter": "<:early_supporter:879666916493496400>",
	"Verified Bot Developer": "<:verified_bot_developer:879669786550890507>",
	"Discord Certified Moderator": "<:discord_moderator:879666882976837654>",
	"Verified Bot": "<:verified_bot:879670687554498591>",
}
