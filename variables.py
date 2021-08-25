import os
import functions

shardCount = 2
botOwner = 531392146767347712
messageManagers = [531392146767347712]
permissionOverride = [531392146767347712]
embedColor = 0x20c2f6
largeNumber = 10000e1000+1000.1000

versionNumber = 0; buildNumber = 0
for file in os.listdir():
	try:
		codeFile = open(file, "r"); code = codeFile.read(); codeFile.close()
		versionNumber += int(str(len(code) / 1000).split(".")[0])
		buildNumber += int(str(len(code) / 1000).split(".")[1])
	except:
		pass
versionNumber = round((versionNumber / 10) / 4, 2)

statusTypes = ["Playing", "Watching", "Listening", "Competing"]
status1 = ["with Discord", "with users", "on some servers", "with Dogecoin", "capture the flag", "with bots"]
status2 = ["over Discord", "YouTube videos", "over servers", "Dogecoin stocks", "over the world", "people talk"]
status3 = ["music", "jokes", "requests", "port 80", "announcements", "suggestions", "port 443"]
status4 = ["the Olympics", "NBA", "some servers", "Discord", "a competition"]
publicFlags = {
	"1": "Discord Employee"
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
badgeList = {
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
}
