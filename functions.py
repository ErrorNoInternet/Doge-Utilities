import time
import json
import core
import language
import variables

default_settings = {"language": "en", "vote_messages": True}
settings_cache = {}

def get_filter_name(name):
    if name in variables.filters.keys():
        return variables.filters[name]
    elif name in variables.filters.values():
        return {value: key for key, value in variables.filters.items()}[name]
    else:
        return ""

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
    user_id = str(user_id)
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

