import time
import json
import core
import struct
import socket
import language
import variables

def parse_color(color):
  string = str(hex(color))[2:]
  while len(string) < 6:
    string = "0" + string
  return "#" + string

def minepinger(ip):
    port = 25565
    if ":" in ip:
        port = int(ip.split(":")[1])
        ip = ip.split(":")[0]

    def read_var_int():
        i = 0
        j = 0
        while True:
            k = sock.recv(1)
            if not k:
                return 0
            k = k[0]
            i |= (k & 0x7f) << (j * 7)
            j += 1
            if j > 5:
                raise ValueError('var_int too big')
            if not (k & 0x80):
                return i

    sock = socket.socket()
    sock.settimeout(10)
    sock.connect((ip, port))
    try:
        host = ip.encode('utf-8')
        data = b''
        data += b'\x00'
        data += b'\x04'
        data += struct.pack('>b', len(host)) + host
        data += struct.pack('>H', port)
        data += b'\x01'
        data = struct.pack('>b', len(data)) + data
        sock.sendall(data + b'\x01\x00')
        length = read_var_int()
        if length < 10:
            if length < 0:
                raise ValueError('negative length read')
            else:
                raise ValueError('invalid response %s' % sock.read(length))

        sock.recv(1)
        length = read_var_int()
        data = b''
        while len(data) != length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                raise ValueError('connection abborted')
            data += chunk
        return json.loads(data)
    finally:
        sock.close()

async def invalid_user_function(interaction):
    await interaction.response.send_message(get_text(interaction.author.id, "not_command_sender"), ephemeral=True)

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
    timestamp = timestamp.replace(" ", "").lower()
    numbers = ""
    unit = ""
    for letter in timestamp:
        number = False
        try:
            int(letter)
            number = True
        except:
            pass
        if number or letter == ".":
            numbers += letter
        else:
            unit += letter
    for key, value in variables.unit_abbreviations.items():
        if unit in value or unit[:-1] in value:
            unit = key
            break
    if unit == "":
        unit = "m"
    return float(numbers) * variables.units[unit.lower()]

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
        if time.time() - data[0] < 20:
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

