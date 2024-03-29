import asyncio
import json
import logging
import os
import random
import threading
import time

import flask
from requests_oauthlib import OAuth2Session

import core
import functions
import variables

app = flask.Flask("doge-utilities")
logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)

OAUTH_CLIENT_ID = os.environ["OAUTH_ID"]
OAUTH_CLIENT_SECRET = os.environ["OAUTH_SECRET"]
app.config["SECRET_KEY"] = OAUTH_CLIENT_SECRET
WEBSITE_URL = os.environ["WEBSITE_URL"]
OAUTH_REDIRECT_URI = WEBSITE_URL + "/web/callback"
URL_SCHEME = "https"
if "http://" in WEBSITE_URL:
    URL_SCHEME = "http"
BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = BASE_URL + "/oauth2/authorize"
TOKEN_URL = BASE_URL + "/oauth2/token"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

allowed_endpoints = [
    "status-page",
    "commands-page",
    "invite-page",
    "support-page",
    "donate-page",
    "css-page",
    "index-page",
    "version-endpoint",
    "doge-image-endpoint",
    "icon-endpoint",
    "privacy-page",
    "terms-page",
    "execute-endpoint",
]
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
        time.sleep(1800)
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
        html = html.replace("(website)", os.environ["WEBSITE_URL"])

    response = flask.make_response(html, 200)
    response.mimetype = mimetype
    return response


def get_ip(request):
    try:
        ip = request.headers["X-Forwarded-For"]
    except:
        ip = request.remote_addr
    return ip


def token_updater(token):
    flask.session["oauth2_token"] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH_REDIRECT_URI,
        auto_refresh_kwargs={
            "client_id": OAUTH_CLIENT_ID,
            "client_secret": OAUTH_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater,
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

    global website_views
    website_views += 1
    if flask.request.endpoint not in allowed_endpoints:
        if not core.client.is_ready():
            flask.abort(503, "Doge Utilities is getting ready. Please try again later.")


@app.route("/backend/execute", endpoint="execute-endpoint")
def execute_code():
    try:
        if flask.request.headers["Authorization"] == os.getenv("WEB_SECRET"):
            try:
                code = flask.request.json["code"]
            except:
                response = flask.make_response("no code specified", 500)
                response.mimetype = "text/plain"
                return response

            stdout = core.io.StringIO()
            try:
                with core.contextlib.redirect_stdout(stdout):
                    if "#globals" in code:
                        exec(
                            f"def run_code():\n{core.textwrap.indent(code, '   ')}",
                            globals(),
                        )
                        globals()["run_code"]()
                    else:
                        dictionary = dict(locals(), **globals())
                        exec(
                            f"def run_code():\n{core.textwrap.indent(code, '   ')}",
                            dictionary,
                            dictionary,
                        )
                        dictionary["run_code"]()
                    output = stdout.getvalue()
            except Exception as error:
                output = "`" + str(error) + "`"
            output = output.replace(os.getenv("TOKEN"), "<TOKEN>")

            response = flask.make_response(output, 200)
            response.mimetype = "text/plain"
            return response
        else:
            response = flask.make_response("invalid web secret", 403)
            response.mimetype = "text/plain"
            return response
    except:
        response = flask.make_response("Forbidden", 403)
        response.mimetype = "text/plain"
        return response


@app.route("/web/authenticate")
def web_authenticate():
    ip_address = get_ip(flask.request)
    if ip_address in user_cache.keys():
        return flask.redirect(
            flask.url_for("web_dashboard", _scheme=URL_SCHEME, _external=True)
        )

    scope = flask.request.args.get("scope", "identify guilds")
    discord = make_session(scope=scope.split(" "))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    flask.session["oauth2_state"] = state
    return flask.redirect(authorization_url)


@app.route("/web/callback")
def web_callback():
    if flask.request.values.get("error"):
        return flask.request.values["error"]
    discord = make_session(state=flask.session.get("oauth2_state"))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH_CLIENT_SECRET,
        authorization_response=flask.request.url,
    )
    flask.session["oauth2_token"] = token
    return flask.redirect(
        flask.url_for("web_dashboard", _scheme=URL_SCHEME, _external=True)
    )


@app.route("/web")
def web_dashboard():
    ip_address = get_ip(flask.request)
    if ip_address in user_cache.keys():
        cache = user_cache[ip_address]
        user_data = cache[0]
        user_guilds = cache[1]
    else:
        discord = make_session(token=flask.session.get("oauth2_token"))
        user_data = discord.get(BASE_URL + "/users/@me").json()
        user_guilds = discord.get(BASE_URL + "/users/@me/guilds").json()
        user_cache[ip_address] = [user_data, user_guilds]

    try:
        if user_data["message"] == "401: Unauthorized":
            try:
                del user_ids[ip_address]
            except:
                pass
            try:
                del user_cache[ip_address]
            except:
                pass
            try:
                del user_tokens[user_ids[ip_address]]
            except:
                pass
            return flask.redirect(
                flask.url_for("web_authenticate", _scheme=URL_SCHEME, _external=True)
            )
    except:
        pass

    if ip_address not in user_ids.keys():
        new_token = str(random.randint(0, random.randint(2**63, 2**511)))
        user_ids[ip_address] = user_data["id"]
        user_tokens[user_data["id"]] = new_token
        token = new_token
    else:
        user_id = user_ids[ip_address]
        try:
            token = user_tokens[user_id]
        except:
            del user_ids[ip_address]
            return flask.redirect(
                flask.url_for("web_authenticate", _scheme=URL_SCHEME, _external=True)
            )

    target_user = None
    for user in core.client.users:
        if user.id == int(user_data["id"]):
            target_user = user
    if target_user == None:
        return load_file(
            "no_servers.html", replace={"(invite)": variables.bot_invite_link}
        )

    mutual_guilds = []
    for user_guild in user_guilds:
        for guild in core.client.guilds:
            if int(user_guild["id"]) == guild.id:
                for member in guild.members:
                    if member.id == int(user_data["id"]):
                        if member.guild_permissions.administrator:
                            mutual_guilds.append(guild)
    if mutual_guilds == []:
        return load_file(
            "no_servers.html", replace={"(invite)": variables.bot_invite_link}
        )

    avatar_url = target_user.avatar
    if avatar_url == None:
        avatar_url = f"https://cdn.discordapp.com/embed/avatars/{int(target_user.discriminator) % 5}.png"
    profile = f"<a href='#user-settings'><img class='userIcon' src='{avatar_url}'><p>{target_user}</p></a>"

    servers = ""
    for guild in mutual_guilds:
        default_icon = "/doge"
        servers += f"<a href='#{guild.id}'><img class='guildIcon' src='{guild.icon if guild.icon != None else default_icon}'></a>"

    server_dashboard = ""
    for guild in mutual_guilds:
        toggle_raid_protection_function = f"raidProtection('{token}', '{guild.id}')"
        toggle_insults_filter_function = (
            f"toggleFilter('{token}', 'insults', '{guild.id}')"
        )
        toggle_spam_filter_function = f"toggleFilter('{token}', 'spam', '{guild.id}')"
        toggle_links_filter_function = f"toggleFilter('{token}', 'links', '{guild.id}')"
        toggle_mention_filter_function = (
            f"toggleFilter('{token}', 'mention', '{guild.id}')"
        )
        toggle_newline_filter_function = (
            f"toggleFilter('{token}', 'newline', '{guild.id}')"
        )
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
        newline_filter = 0
        try:
            newline_filter = json.loads(core.database[f"newline.toggle.{guild.id}"])
        except:
            pass
        server_dashboard += (
            f"<h2 class='sectionTitle' id='{guild.id}'>{guild.name}</h2>"
        )
        server_dashboard += f"<p style='margin-top: 0;'><b>{users}</b> {'user' if users == 1 else 'users'} and <b>{bots}</b> {'bot' if bots == 1 else 'bots'} (<b>{bots + users}</b> total)</p>"
        server_dashboard += f'<button style="margin-top: 20; background-color: {colors[raid_protection]};" id="raid-protection-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_raid_protection_function}">Raid Protection: {"Enabled" if raid_protection == 1 else "Disabled"}</button>'

        server_dashboard += f"<h4 class='sectionTitle' id='{guild.id}'>Filters</h4>"
        server_dashboard += f'<button style="margin-top: 5;" id="insults-filter-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_insults_filter_function}">Insults: {"Enabled" if insults_filter == 1 else "Disabled"}</button>'
        server_dashboard += f'<button style="margin-top: 0;" id="spam-filter-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_spam_filter_function}">Spam: {"Enabled" if spam_filter == 1 else "Disabled"}</button>'
        server_dashboard += f'<button style="margin-top: 0;" id="links-filter-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_links_filter_function}">Links: {"Enabled" if links_filter == 1 else "Disabled"}</button>'
        server_dashboard += f'<button style="margin-top: 0;" id="mention-filter-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_mention_filter_function}">Mention: {"Enabled" if mention_filter == 1 else "Disabled"}</button>'
        server_dashboard += f'<button style="margin-top: 0;" id="newline-filter-button.{guild.id}" style="font-size: 100%;" onclick="{toggle_newline_filter_function}">Newline: {"Enabled" if newline_filter == 1 else "Disabled"}</button>'
        server_dashboard += "<hr class='separator'>"

    save_language_function = f"saveLanguage('{token}', '{target_user.id}')"
    toggle_vote_messages_function = f"toggleVoteMessages('{token}', '{target_user.id}')"
    vote_messages = 0
    try:
        vote_messages = functions.get_settings(target_user.id)["vote_messages"]
    except:
        pass
    user_dashboard = f"<h1 class='sectionTitle' id='user-settings'>User Settings</h1>"
    user_dashboard += "<div id='languageSelection'><select name='languages' id='language-select' style='margin-top: 20; width: 150; height: 34;'>"
    user_language = functions.get_settings(target_user.id)["language"]
    language_codes = core.googletrans.LANGUAGES
    user_dashboard += f"<option value='{user_language}'>{language_codes[user_language].title()}</option>"
    added = [user_language]
    for language in language_codes:
        if language not in added:
            user_dashboard += f"<option value='{language}'>{language_codes[language].title()}</option>"
    user_dashboard += f'</select></div><div id="languageSelection"><button style="margin-top: 5;" id="save-language-button" style="font-size: 100%;" onclick="{save_language_function}">Save</button></div>'
    user_dashboard += f'<button style="margin-top: 2; background-color: {colors[vote_messages]};" id="vote-messages-button" style="font-size: 100%;" onclick="{toggle_vote_messages_function}">Vote Messages: {"Enabled" if vote_messages == 1 else "Disabled"}</button>'
    user_dashboard += "<hr class='separator'>"

    return load_file(
        "web_dashboard.html",
        replace={
            "(profile)": profile,
            "(servers)": servers,
            "(server_dashboard)": server_dashboard,
            "(user_dashboard)": user_dashboard,
        },
    )


@app.route("/css", endpoint="css-page")
def fetch_css():
    return load_file("index.css", mimetype="text/css")


@app.route("/web/javascript")
def fetch_javascript():
    return load_file(
        "dashboard.js", mimetype="text/javascript", replace={"(website)": WEBSITE_URL}
    )


@app.route("/favicon.ico", endpoint="icon-endpoint")
def fetch_favicon():
    return load_file("favicon.ico", mimetype="image/vnd.microsoft.icon", binary=True)


@app.route("/doge", endpoint="doge-image-endpoint")
def fetch_doge_image():
    return load_file("doge.png", mimetype="image/png", binary=True)


@app.route("/vote", methods=["POST"])
def handle_vote():
    global vote_counter
    vote_counter += 1
    try:
        if flask.request.headers["Authorization"] == os.getenv("WEB_SECRET"):
            vote_user_id = flask.request.json["user"]
            asyncio.run_coroutine_threadsafe(
                core.send_vote_message(vote_user_id),
                core.client.loop,
            )

            response = flask.make_response("OK", 200)
            response.mimetype = "text/plain"
            return response
        else:
            response = flask.make_response("Forbidden", 403)
            response.mimetype = "text/plain"
            return response
    except:
        response = flask.make_response("Forbidden", 403)
        response.mimetype = "text/plain"
        return response


@app.route("/", endpoint="index-page")
def index():
    if not core.client.is_ready():
        warning_message = "<center><div id='banner'><div style='margin-left: 170;' id='bannerContent'>Doge Utilities is currently getting ready. You might encounter some issues when using certain features.</div></div></center>"
        banner_margin = " margin-top: 50;"
    else:
        warning_message = ""
        banner_margin = ""
    return load_file(
        "index.html",
        replace={
            "(warning_message)": warning_message,
            "(banner_margin)": banner_margin,
        },
    )


@app.route("/invite", endpoint="invite-page")
def fetch_invite():
    return (
        '<meta http-equiv="refresh" content="0; url=' + variables.bot_invite_link + '">'
    )


@app.route("/support", endpoint="support-page")
def fetch_server_invite():
    return (
        '<meta http-equiv="refresh" content="0; url='
        + variables.support_server_invite
        + '">'
    )


@app.route("/donate", endpoint="donate-page")
def fetch_donations():
    return load_file("donate.html")


@app.route("/privacy", endpoint="privacy-page")
def fetch_privacy_page():
    return load_file("privacy.html")


@app.route("/terms", endpoint="terms-page")
def fetch_terms_page():
    return load_file("terms.html")


@app.route("/status", endpoint="status-page")
def fetch_status():
    member_count = 0
    channel_count = 0
    uptime = ""
    for guild in core.client.guilds:
        member_count += len(guild.members)
        channel_count += len(guild.channels)
    process = core.psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1000000
    seconds_time = time.time() - core.start_time
    minutes_time = seconds_time / 60
    hours_time = minutes_time / 60
    days_time = hours_time / 24
    seconds_time = seconds_time % 60
    minutes_time = minutes_time % 60
    hours_time = hours_time % 24
    if days_time >= 1:
        uptime += str(core.math.floor(days_time)) + "d "
    if hours_time >= 1:
        uptime += str(core.math.floor(hours_time)) + "hr "
    if minutes_time >= 1:
        uptime += str(core.math.floor(minutes_time)) + "m "
    if seconds_time >= 1:
        uptime += str(core.math.floor(seconds_time)) + "s "
    if uptime == "":
        uptime = "Unknown"
    else:
        uptime = uptime.split(" ")
        uptime = " ".join(uptime[:3])
    user_ip = get_ip(flask.request)
    user_id = 0
    if user_ip in user_ids:
        user_id = user_ids[user_ip]
    bot_status_text = functions.get_text(user_id, "bot_status")
    text = "<div class='statusWrapper'>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'latency')}</b><br><code>{round(core.client.latency*1000, 2)} ms</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'cpu_usage')}</b><br><code>{core.psutil.cpu_percent()}%</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'ram_usage')}</b><br><code>{round(memory_usage, 2)} MB</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'thread_count')}</b><br><code>{threading.active_count()}</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'joined_guilds')}</b><br><code>{len(core.client.guilds)}</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'active_shards')}</b><br><code>{len(core.client.shards)}</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'member_count')}</b><br><code>{member_count}</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'channel_count')}</b><br><code>{channel_count}</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'command_count')}</b><br><code>{len(core.client.slash_commands)}</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'disnake_version')}</b><br><code>{core.disnake.__version__}</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'bot_version')}</b><br><code>{variables.bot_version}</code></p>"
    text += f"<p class='statusText'><b>{functions.get_text(user_id, 'bot_uptime')}</b><br><code>{uptime.strip()}</code></p>"
    text += "</div>"
    return load_file(
        "status.html", replace={"(text)": text, "(bot_status)": bot_status_text}
    )


@app.route("/commands", endpoint="commands-page")
def fetch_commands():
    text = "<div class='commandsWrapper'>"
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
                    text += (
                        f"<code>/{command.name} {option.name} {arguments}</code><br>"
                    )
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
    return load_file(
        "commands.html",
        replace={"(text)": text, "(count)": str(len(core.client.slash_commands))},
    )


@app.route("/api/version", endpoint="version-endpoint")
def fetch_version():
    response = flask.make_response(
        f"{variables.bot_version}",
        200,
    )
    response.mimetype = "text/plain"
    return response


@app.route("/web/api/save-language/<token>/<user>/<language>")
def save_language(token, user, language):
    try:
        user_id = user_ids[get_ip(flask.request)]
        if user_tokens[user_id] != token:
            flask.abort(403)
    except:
        flask.abort(403)

    if language not in core.googletrans.LANGUAGES.keys():
        flask.abort(404)
    settings = functions.get_settings(user)
    settings["language"] = language
    functions.set_settings(settings, user)
    return "OK"


@app.route("/web/api/vote-messages/<token>/<user>")
def toggle_vote_messages(token, user):
    try:
        user_id = user_ids[get_ip(flask.request)]
        if user_tokens[user_id] != token:
            flask.abort(403)
    except:
        flask.abort(403)

    settings = functions.get_settings(user)
    value = False
    try:
        value = settings["vote_messages"]
    except:
        pass
    new_value = False
    if value == False:
        new_value = True
    settings["vote_messages"] = new_value
    functions.set_settings(settings, user)
    return str(int(new_value))


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

    filter_name = functions.get_filter_name(name)
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
