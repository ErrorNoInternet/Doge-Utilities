import os
import flask
import asyncio
import variables
import functions

app = flask.Flask("doge-server")
invite_link = "https://discord.com/oauth2/authorize?client_id=854965721805226005&permissions=8&scope=applications.commands%20bot"
support_server_link = "https://discord.gg/3Tp7R8FUsC"
website_views = 0
vote_counter = 0

def load_file(file_name, mimetype="text/html", binary=False):
    html = "<p>Unable to load HTML</p>"
    try:
        file = open(f"static/{file_name}", "r" if not binary else "rb")
        html = file.read()
        file.close()
    except:
        pass

    response = flask.make_response(html, 200)
    response.mimetype = mimetype
    return response

@app.route("/css")
def fetch_css():
    return load_file("index.css", mimetype="text/css")

@app.route("/favicon.ico")
def fetch_favicon():
    return load_file("favicon.ico", mimetype="image/vnd.microsoft.icon", binary=True)

@app.route("/doge")
def fetch_doge_image():
    return load_file("doge.png", mimetype="image/png", binary=True)

@app.route("/vote")
def handle_vote():
    vote_counter += 1
    if flask.request.headers["Authorization"] == os.getenv("WEB_SECRET"):
        vote_user_id = flask.request.json["user"]
        asyncio.run_coroutine_threadsafe(
            functions.send_user_message(vote_user_id, variables.vote_message), functions.client.loop,
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
    return "<meta http-equiv=\"refresh\" content=\"0; url=" + invite_link + "\">"

@app.route("/support")
def fetch_server_invite():
    return "<meta http-equiv=\"refresh\" content=\"0; url=" + support_server_link + "\">"

def run():
    app.run("0.0.0.0", port=8080 if not os.getenv("PORT") else os.getenv("PORT"))

