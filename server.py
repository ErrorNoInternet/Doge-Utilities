import os
import core
import json
import time
import flask
import random
import asyncio
import logging
import variables
import threading
from requests_oauthlib import OAuth2Session

app = flask.Flask("doge-server")
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

OAUTH_CLIENT_ID = os.environ['OAUTH_ID']
OAUTH_CLIENT_SECRET = os.environ['OAUTH_SECRET']
app.config['SECRET_KEY'] = OAUTH_CLIENT_SECRET

WEBSITE_URL = os.environ['WEBSITE_URL']
OAUTH_REDIRECT_URI = WEBSITE_URL + "/web/callback"
URL_SCHEME = "https"
if "http://" in WEBSITE_URL:
    URL_SCHEME = "http"

BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = BASE_URL + '/oauth2/authorize'
TOKEN_URL = BASE_URL + '/oauth2/token'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

colors = ["#e74c3c", "#2ecc71"]
user_ids = {}
user_tokens = {}
user_cache = {}
ratelimits = {}
website_views = 0
vote_counter = 0

def manage_cache():
    global user_cache
    while True:
        time.sleep(3600)
        user_cache = {}

def manage_ratelimits():
    global ratelimits
    while True:
        time.sleep(60)
        ratelimits = {}

def load_file(file_name, mimetype="text/html", binary=False, replace={}):
    html = "<p>Unable to load HTML</p>"
    try:
        file = open(f"static/{file_name}", "r" if not binary else "rb")
        html = file.read()
        file.close()
    except:
        pass

    for key in replace:
        html = html.replace(key, replace[key])
    if mimetype == "text/html":
        side_bar_file = open("static/side_bar.html", "r")
        side_bar = side_bar_file.read()
        side_bar_file.close()
        html = html.replace("(side_bar)", side_bar)

    response = flask.make_response(html, 200)
    response.mimetype = mimetype
    return response

def get_ip(request):
    try:
        ip = request.headers['X-Forwarded-For']
    except:
        ip = request.remote_addr
    return ip

def token_updater(token):
    flask.session['oauth2_token'] = token

def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH_CLIENT_ID,
            'client_secret': OAUTH_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater
    )

@app.before_request
def request_handler():
    ip_address = get_ip(flask.request)
    counter = 0
    if ip_address in ratelimits:
        counter = ratelimits[ip_address]
    if counter > 30:
        flask.abort(429, "You are being ratelimited!")
    ratelimits[ip_address] = counter + 1

    if not core.client.is_ready():
        flask.abort(503, "Doge Utilities is getting ready. Please try again later.")

@app.route("/web/authenticate")
def web_authenticate():
    ip_address = get_ip(flask.request)
    if ip_address in user_cache.keys():
        return flask.redirect(flask.url_for("web_dashboard", _scheme=URL_SCHEME, _external=True))

    scope = flask.request.args.get('scope', "identify guilds")
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    flask.session['oauth2_state'] = state
    return flask.redirect(authorization_url)

@app.route("/web/callback")
def web_callback():
    if flask.request.values.get('error'):
        return flask.request.values['error']
    discord = make_session(state=flask.session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH_CLIENT_SECRET,
        authorization_response=flask.request.url)
    flask.session['oauth2_token'] = token
    return flask.redirect(flask.url_for("web_dashboard", _scheme=URL_SCHEME, _external=True))

@app.route('/web')
def web_dashboard():
    ip_address = get_ip(flask.request)
    if ip_address in user_cache.keys():
        cache = user_cache[ip_address]
        user_data = cache[0]
        user_guilds = cache[1]
    else:
        discord = make_session(token=flask.session.get('oauth2_token'))
        user_data = discord.get(BASE_URL + '/users/@me').json()
        user_guilds = discord.get(BASE_URL + '/users/@me/guilds').json()
        user_cache[ip_address] = [user_data, user_guilds]

    try:
        if user_data["message"] == "401: Unauthorized":
            del user_cache[ip_address]
            del user_tokens[user_ids[ip_address]]
            return flask.redirect(flask.url_for("web_authenticate", _scheme=URL_SCHEME, _external=True))
    except:
        pass

    if ip_address not in user_ids.keys():
        new_token = str(random.randint(0, random.randint(2**63, 2**511)))
        user_ids[ip_address] = user_data["id"]
        user_tokens[user_data["id"]] = new_token
        token = new_token
    else:
        user_id = user_ids[ip_address]
        token = user_tokens[user_id]

    target_user = None
    for user in core.client.users:
        if user.id == int(user_data['id']):
            target_user = user
    if target_user == None:
        return load_file("no_servers.html", replace={"(invite)": variables.bot_invite_link})

    mutual_guilds = []
    for user_guild in user_guilds:
        for guild in core.client.guilds:
            if int(user_guild['id']) == guild.id:
                for member in guild.members:
                    if member.id == int(user_data["id"]):
                        if member.guild_permissions.administrator:
                            mutual_guilds.append(guild)
    if mutual_guilds == []:
        return load_file("no_servers.html", replace={"(invite)": variables.bot_invite_link})

    profile = f"<img class='userIcon' src='{target_user.avatar}'><p>{target_user}</p>"

    servers = ""
    for guild in mutual_guilds:
        default_icon = "/doge"
        servers += f"<a href='#{guild.id}'><img class='guildIcon' src='{guild.icon if guild.icon != None else default_icon}' alt='{guild.name}'></a>"

    server_dashboard = ""
    for guild in mutual_guilds:
        toggle_raid_protection_function = f"raidProtection('{token}', '{guild.id}')"
        toggle_insults_filter_function = f"toggleFilter('{token}', 'insults', '{guild.id}')"
        toggle_spam_filter_function = f"toggleFilter('{token}', 'spam', '{guild.id}')"
        toggle_links_filter_function = f"toggleFilter('{token}', 'links', '{guild.id}')"
        toggle_mention_filter_function = f"toggleFilter('{token}', 'mention', '{guild.id}')"
        bots = 0
        users = 0
        for member in guild.members:
            if member.bot:
                bots += 1
            else:
                users += 1
        raid_protection = 0
        try:
            raid_protection = json.loads(core.database[f"{guild.id}.raid-protection"])
        except:
            pass
        insults_filter = 0
        try:
            insults_filter = json.loads(core.database[f"insults.toggle.{guild.id}"])
        except:
            pass
        spam_filter = 0
        try:
            spam_filter = json.loads(core.database[f"spamming.toggle.{guild.id}"])
        except:
            pass
        links_filter = 0
        try:
            links_filter = json.loads(core.database[f"links.toggle.{guild.id}"])
        except:
            pass
        mention_filter = 0
        try:
            mention_filter = json.loads(core.database[f"mention.toggle.{guild.id}"])
        except:
            pass
        server_dashboard += f"<h2 class='serverTitle' id='{guild.id}'>{guild.name}</h2>"
        server_dashboard += f"<p style='margin-top: 0;'><b>{users}</b> {'user' if users == 1 else 'users'} and <b>{bots}</b> {'bot' if bots == 1 else 'bots'} (<b>{bots + users}</b> total)</p>"
        server_dashboard += f'<button style="margin-top: 20; background-color: {colors[raid_protection]};" id="raid-protection-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_raid_protection_function}">Raid Protection: {"Enabled" if raid_protection == 1 else "Disabled"}</button>'

        server_dashboard += f"<h4 class='subTitle' id='{guild.id}'>Filters</h4>"
        server_dashboard += f'<button style="margin-top: 5;" id="insults-filter-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_insults_filter_function}">Insults: {"Enabled" if insults_filter == 1 else "Disabled"}</button>'
        server_dashboard += f'<button style="margin-top: 0;" id="spam-filter-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_spam_filter_function}">Spam: {"Enabled" if spam_filter == 1 else "Disabled"}</button>'
        server_dashboard += f'<button style="margin-top: 0;" id="links-filter-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_links_filter_function}">Links: {"Enabled" if links_filter == 1 else "Disabled"}</button>'
        server_dashboard += f'<button style="margin-top: 0;" id="mention-filter-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_mention_filter_function}">Mention: {"Enabled" if mention_filter == 1 else "Disabled"}</button>'
        server_dashboard += "<hr class='separator'>"

    return load_file("web_dashboard.html", replace={"(profile)": profile, "(servers)": servers, "(server_dashboard)": server_dashboard})

@app.route("/css")
def fetch_css():
    return load_file("index.css", mimetype="text/css")

@app.route("/web/javascript")
def fetch_javascript():
    return load_file("dashboard.js", mimetype="text/javascript", replace={"(website)": WEBSITE_URL})

@app.route("/favicon.ico")
def fetch_favicon():
    return load_file("favicon.ico", mimetype="image/vnd.microsoft.icon", binary=True)

@app.route("/doge")
def fetch_doge_image():
    return load_file("doge.png", mimetype="image/png", binary=True)

@app.route("/vote", methods=["POST"])
def handle_vote():
    global vote_counter
    vote_counter += 1
    if flask.request.headers["Authorization"] == os.getenv("WEB_SECRET"):
        vote_user_id = flask.request.json["user"]
        asyncio.run_coroutine_threadsafe(
            core.send_vote_message(vote_user_id), core.client.loop,
        )

        response = flask.make_response("OK", 200)
        response.mimetype = "text/plain"; return response
    else:
        response = flask.make_response("Forbidden", 403)
        response.mimetype = "text/plain"; return response

@app.route("/")
def index():
    global website_views
    website_views += 1
    return load_file("index.html")

@app.route("/invite")
def fetch_invite():
    return "<meta http-equiv=\"refresh\" content=\"0; url=" + variables.bot_invite_link + "\">"

@app.route("/support")
def fetch_server_invite():
    return "<meta http-equiv=\"refresh\" content=\"0; url=" + variables.support_server_invite + "\">"

@app.route("/donate")
def fetch_donations():
    return load_file("donate.html")

@app.route("/commands")
def fetch_commands():
    text = "<div class='wrapper'>"
    for command in core.client.slash_commands:
        if command.name in variables.owner_commands:
            continue
        usages = []
        text += f"<p style='color: #ffffff; margin: 25;'>"
        text += f"<b>{command.name}</b><br>{command.description}<br><br>"
        for option in command.options:
            if str(option.type) == "OptionType.sub_command_group":
                for sub_option in option.options:
                    for argument in sub_option.options:
                        text += f"<code>/{command.name} {option.name} {sub_option.name} [{argument.name}]</code><br>"
            elif str(option.type) == "OptionType.sub_command":
                arguments = ""
                for argument in option.options:
                    arguments += "[" + argument.name + "] "
                arguments = arguments.strip()
                if arguments != "":
                    text += f"<code>/{command.name} {option.name} {arguments}</code><br>"
                else:
                    text += f"<code>/{command.name} {option.name}</code><br>"
            else:
                usages.append(f"[{option.name}]")
        if usages != []:
            text += f"<code>/{command.name} {' '.join(usages)}</code>"
        if command.options == []:
            text += f"<code>/{command.name}</code>"
        text += "</p>"
    text += "</div>"
   
    return load_file("commands.html", replace={"(text)": text, "(count)": str(len(core.client.slash_commands) - len(variables.owner_commands))})

@app.route("/web/api/raid-protection/<token>/<server>")
def toggle_raid_protection(token, server):
    try:
        user_id = user_ids[get_ip(flask.request)]
        if user_tokens[user_id] != token:
            flask.abort(403)
        found = False
        for guild in core.client.guilds:
            if str(guild.id) == server:
                for member in guild.members:
                    if str(member.id) == user_id:
                        if member.guild_permissions.administrator:
                            found = True
        if not found:
            flask.abort(403)
    except:
        flask.abort(403)

    value = 0
    try:
        value = json.loads(core.database[f"{server}.raid-protection"])
    except:
        pass
    new_value = 0
    if value == 0:
        new_value = 1
    core.database[f"{server}.raid-protection"] = new_value
    return str(new_value)

@app.route("/web/api/filter/<token>/<name>/<server>")
def toggle_filter_settings(token, name, server):
    try:
        user_id = user_ids[get_ip(flask.request)]
        if user_tokens[user_id] != token:
            flask.abort(403)
        found = False
        for guild in core.client.guilds:
            if str(guild.id) == server:
                for member in guild.members:
                    if str(member.id) == user_id:
                        if member.guild_permissions.administrator:
                            found = True
        if not found:
            flask.abort(403)
    except:
        flask.abort(403)

    filter_name = ""
    if name == "insults":
        filter_name = "insults"
    elif name == "spam":
        filter_name = "spamming"
    elif name == "links":
        filter_name = "links"
    elif name == "mention":
        filter_name = "mention"
    if filter_name == "":
        flask.abort(404)

    value = 0
    try:
        value = json.loads(core.database[f"{filter_name}.toggle.{server}"])
    except:
        pass
    new_value = 0
    if value == 0:
        new_value = 1
    core.database[f"{filter_name}.toggle.{server}"] = new_value
    return str(new_value)

def run():
    threading.Thread(target=manage_cache).start()
    threading.Thread(target=manage_ratelimits).start()
    app.run("0.0.0.0", port=8080 if not os.getenv("PORT") else os.getenv("PORT"))

