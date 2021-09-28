[1mdiff --git a/Procfile b/Procfile[m
[1mindex a41f29c..9fadd60 100644[m
[1m--- a/Procfile[m
[1m+++ b/Procfile[m
[36m@@ -1 +1 @@[m
[31m-worker: python3 -OO main.py[m
[32m+[m[32mweb: python3 -OO main.py[m
[1mdiff --git a/README.md b/README.md[m
[1mindex 3e0eda4..ba33e21 100644[m
[1m--- a/README.md[m
[1m+++ b/README.md[m
[36m@@ -19,6 +19,7 @@[m [mFeel free to donate some Dogecoin at `D5Gy8ADPTbzGLD3qvpv4ZkNNrPMNkYX49j`![m
   - `REDIS_HOST` - Redis database host[m
   - `REDIS_PORT` - Redis database port[m
   - `REDIS_PASSWORD` - Redis database password[m
[32m+[m[32m  - `WEB_SECRET` - Bot website secret[m
 [m
 ```sh[m
 git clone https://github.com/ErrorNoInternet/Doge-Utilities[m
[1mdiff --git a/functions.py b/functions.py[m
[1mindex b44c086..63959e0 100644[m
[1m--- a/functions.py[m
[1m+++ b/functions.py[m
[36m@@ -8,6 +8,7 @@[m [mimport time[m
 import math[m
 import redis[m
 import extra[m
[32m+[m[32mimport server[m
 import urllib[m
 import base64[m
 import string[m
[36m@@ -260,6 +261,7 @@[m [mexcept:[m
     ).start()[m
     threading.Thread(name="reset_strikes", target=reset_strikes).start()[m
     threading.Thread(name="blacklist_manager", target=manage_blacklist).start()[m
[32m+[m[32m    threading.Thread(name="web_server", target=server.run).start()[m
 [m
 async def select_status():[m
     client_status = disnake.Status.online; status_type = random.choice(variables.status_types)[m
[36m@@ -322,6 +324,7 @@[m [mdef reload_data():[m
         math,[m
         redis,[m
         extra,[m
[32m+[m[32m        server,[m
         urllib,[m
         base64,[m
         string,[m
[1mdiff --git a/requirements.txt b/requirements.txt[m
[1mindex 90dd829..7f514ad 100644[m
[1m--- a/requirements.txt[m
[1m+++ b/requirements.txt[m
[36m@@ -1,5 +1,6 @@[m
 pytz[m
 redis[m
[32m+[m[32mflask[m
 psutil[m
 pillow[m
 topggpy[m
[1mdiff --git a/variables.py b/variables.py[m
[1mindex 925a28e..3d84617 100644[m
[1m--- a/variables.py[m
[1m+++ b/variables.py[m
[36m@@ -21,6 +21,7 @@[m [mversion_number = round((version_number / 10) / 4, 2)[m
 support_server_invite = "https://discord.gg/3Tp7R8FUsC"[m
 no_permission_text = "You do not have permission to use this command!"[m
 not_command_owner_text = "You are not the sender of that command!"[m
[32m+[m[32mvote_message = "Thank you for voting for Doge Utilities!"[m
 previous_button_text = "<"[m
 next_button_text = ">"[m
 first_button_text = "<<"[m
