import core

def get_settings(user_id):
    try:
        settings = core.database[f"settings.{user_id}"]
    except:
        settings = {}
    if "language" not in settings:
        settings["language"] = "en"
    return settings

def remove_mentions(user):
    user = user.replace("<", "")
    user = user.replace("@", "")
    user = user.replace("!", "")
    user = user.replace(">", "")
    return user

