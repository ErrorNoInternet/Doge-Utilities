import time
import json
import core
import language

default_settings = {"language": "en", "vote_messages": True}
settings_cache = {}

def get_settings(user_id):
    try:
        settings = json.loads(core.database[f"settings.{user_id}"])
    except:
        settings = {}
    for key in default_settings.keys():
        if key not in settings:
            settings[key] = default_settings[key]
    return settings

def set_settings(settings, user_id):
    core.database[f"settings.{user_id}"] = json.dumps(settings)

def get_text(user_id, key):
    settings = None
    if user_id in settings_cache:
        data = settings_cache[user_id]
        if time.time() - data[0] < 10:
            settings = data[1]
        else:
            settings = get_settings(user_id)
            settings_cache[user_id] = [time.time(), settings]
    else:
        settings = get_settings(user_id)
        settings_cache[user_id] = [time.time(), settings]
    return language.get(settings['language'], key)

def remove_mentions(user):
    user = user.replace("<", "")
    user = user.replace("@", "")
    user = user.replace("!", "")
    user = user.replace(">", "")
    return user

def parse_snowflake(id):
    return round(((id >> 22) + 1420070400000) / 1000)

