import os
import time
import flask
import asyncio
import functions
import threading

app = flask.Flask(__name__)
botName = "a Discord bot"

@app.route("/")
def index():
	response = flask.make_response(f"Hello World! I am {botName}!", 200)
	response.mimetype = "text/plain"; return response

@app.route("/vote", methods=["GET", "POST"])
def handleVote():
	if flask.request.method == "POST":
		try:
			if flask.request.headers["Authorization"] == os.getenv("SECRET"):
				voteUserID = flask.request.json["user"]
				message = "Thank you for voting for Doge Utilities on Top.GG!"
				asyncio.run_coroutine_threadsafe(functions.sendUserMessage(voteUserID, message), functions.client.loop)

				response = flask.make_response("200", 200)
				response.mimetype = "text/plain"; return response
			else:
				response = flask.make_response("Forbidden", 403)
				response.mimetype = "text/plain"; return response
		except:
			response = flask.make_response("Error", 200)
			response.mimetype = "text/plain"; return response
	else:
		response = flask.make_response("Invalid method", 200)
		response.mimetype = "text/plain"; return response

def run():
	app.run(host='0.0.0.0', port=8080)

def start(name):
	global botName; botName = name
	threading.Thread(target=run).start()
	
