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
	"0": "None",
	"1": "Discord Employee",
	"2": "Discord Partner",
	"4": "HypeSquad Events",
	"8": "Bug Hunter Level 1",
	"16": "2FA Enabled",
	"32": "Dismissed Nitro promotion",
	"64": "HypeSquad Bravery",
	"128": "HypeSquad Brilliance",
	"256": "HypeSquad Balance",
	"512": "Early Supporter",
	"1024": "Team User",
	"2048": "Discord Partner",
	"4096": "System User",
	"8192": "Has an unread system message",
	"16384": "Bug Hunter Level 2",
	"32768": "Pending deletion for being underage",
	"65536": "Verified Bot",
	"131072": "Verified Bot Developer",
	"262144": "Discord Certified Moderator",
}

