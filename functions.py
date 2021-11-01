import time
import json
import core
import language
import variables

def display_time(user_id, duration):
    unit = "seconds"
    if duration >= 60:
        unit = "minutes"
        duration = duration / 60
        if duration >= 60:
            unit = "hours"
            duration = duration / 60
            if duration >= 24:
                unit = "days"
                duration = duration / 24
                if duration >= 30.4:
                    unit = "months"
                    duration = duration / 30.4
                    if duration >= 12:
                        unit = "years"
                        duration = duration / 12
    duration = round(duration, 1)
    if str(duration).endswith(".0"):
        duration = round(duration)
    if duration == 1:
        unit = get_text(user_id, unit[:-1])
    else:
        unit = get_text(user_id, unit)
    if str(duration) == "inf":
        duration = get_text(user_id, "infinity")
    return f"{duration} {unit}"

def shrink(text, length):
    original_length = len(text)
    text = text[:length]
    if len(text) == original_length:
        return text.strip()
    else:
        return text[:-3].strip() + "..."

def parse_time(timestamp):
    timestamp = timestamp.replace(" ", "")
    numbers = ""
    unit = ""
    for letter in timestamp:
        try:
            number = False
            try:
                int(letter)
                number = True
            except:
                pass
            if number or letter == ".":
                numbers += letter
        except:
            unit += letter
    for key, value in variables.unit_abbreviations.items():
        if unit in value or unit[:-1] in value:
            unit = key
            break
    return int(numbers) * variables.units[unit.lower()]

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
    for key in variables.default_settings.keys():
        if key not in settings:
            settings[key] = variables.default_settings[key]
    return settings

def set_settings(settings, user_id):
    core.database[f"settings.{user_id}"] = json.dumps(settings)

def get_text(user_id, key):
    user_id = str(user_id)
    settings = None
    if user_id in variables.settings_cache:
        data = variables.settings_cache[user_id]
        if time.time() - data[0] < 10:
            settings = data[1]
        else:
            settings = get_settings(user_id)
            variables.settings_cache[user_id] = [time.time(), settings]
    else:
        settings = get_settings(user_id)
        variables.settings_cache[user_id] = [time.time(), settings]
    return language.get(settings['language'], key)

def remove_mentions(user):
    user = user.replace("<", "")
    user = user.replace("@", "")
    user = user.replace("!", "")
    user = user.replace(">", "")
    return user

def parse_snowflake(id):
    return round(((id >> 22) + 1420070400000) / 1000)

