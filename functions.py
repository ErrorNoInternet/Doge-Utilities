import core
import json

def get_settings(user_id):
    try:
        settings = json.loads(core.database[f"settings.{user_id}"])
    except:
        settings = {}
    if "language" not in settings:
        settings["language"] = "en"
    return settings

def set_settings(settings, user_id):
    core.database[f"settings.{user_id}"] = json.dumps(settings)

def remove_mentions(user):
    user = user.replace("<", "")
    user = user.replace("@", "")
    user = user.replace("!", "")
    user = user.replace(">", "")
    return user

def parse_snowflake(id):
    return round(((id >> 22) + 1420070400000) / 1000)

