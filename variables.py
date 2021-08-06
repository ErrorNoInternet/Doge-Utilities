import os

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
	"262144": "Discord Certified Moderator"
}
commands = {
	"ping": "Display the bot's current latency",
	"status": "Show the bot's current statistics",
	"tests": "Run a series of tests to diagnose Doge",
	"vote": "Display a link to upvote Doge Utilities",
	"version": "Display the bot's current version",
	"prefix": "Change the bot's prefix on this server",
	"invite": "Invite this bot to another server",
	"shards <page>": "View information about Doge Utilities' shards", 
	"setup-muted": "Generate a role that mutes members", 
	"setup-banned": "Generate a role that disables access to channels", 
	"random <low> <high>": "Generate a random number within the range", 
	"disconnect-members": "Disconnect all the members in voice channels", 
	"suggest <suggestion>": "Send a suggestion to the bot creators", 
	"autorole <role>": "Change the role that is automatically given to users", 
	"lookup <user>": "Display profile information for the specified user",
	"clear <messages>": "Delete the specified amount of messages",
	"raid-protection <on/off>": "Toggle server's raid protection",
	"wide <text>": "Add spaces to every character in the text",
	"cringe <text>": "Randomly change the cases of the text",
	"spoiler <text>": "Add spoilers to every character in the text",
	"reverse <text>": "Reverse the specified text (last character first)",
	"corrupt <text>": "Make the specified text appear to be corrupted",
	"epoch-date <epoch>": "Convert an epoch timestamp into a date",
	"base64 <encode/decode> <text>": "Convert the text to/from base64",
	"date-epoch <date>": "Covert a date into an epoch timestamp",
	"hash <type> <text>": "Hash the text object with the specified type",
	"calculate <expression>": "Calculate the specified math expression",
	"color <color code>": "Display information about the color code",
	"permissions <user>": "Display the permissions for the specified user",
	"time <timezone>": "Display the current time for the specified timezone",
	"binary <encode/decode> <text>": "Convert the text to/from binary"
}

