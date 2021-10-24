data = {
    "en": {
        "no_permission": "You do not have permission to use this command!",
        "not_command_sender": "You are not the sender of that command!",
        "vote_message": "Thank you for voting for Doge Utilities!",
        "banned_message": "You are banned from using Doge Utilities!",
        "error_message": "Oops! Doge Utilities has ran into an error...",
        "use_in_server": "Please use Doge Utilities in a server for the best experience!",
        "no_reminders": "You have no active reminders",
        "reminders": "Reminders",
        "time": "Time",
        "text": "Text",
    },
    "zh-cn": {
        "no_permission": "你没有权限用这个指令!",
        "not_command_sender": "这个指令不是你发的!",
        "vote_message": "谢谢你给我投票!",
        "banned_message": "你已被禁止使用Doge Utilities!",
        "error_message": "很抱歉，Doge Utilities出错了。。。",
        "use_in_server": "请你在服务器里用Doge Utilities!",
        "no_reminders": "你没有提醒",
        "reminders": "提醒",
        "time": "时间",
        "text": "文字",
    },
    "ru": {
        "no_permission": "У вас нет разрешений на использование этой команды!",
        "not_command_sender": "Вы не являетесь отправителем данной команды!",
        "vote_message": "Спасибо за то, что вы проголосовали за меня!",
        "banned_message": "Вам запретили использовать Doge Utilities!",
        "error_message": "Упс... Doge Utilities столкнулся с ошибкой...",
        "use_in_server": "Пожалуйста, используйте Doge Utilities на сервере для лучшего опыта!",
        "no_reminders": "У вас нет активных напоминаний",
        "reminders": "Напоминания",
        "time": "Время",
        "text": "Текст",
    },
}
data["zh-tw"] = data["zh-cn"]

def get(language, key):
    language = language.lower()
    key = key.lower()
    if language not in data.keys():
        language = "en"
    language_data = data[language]
    if key not in language_data:
        language_data = data["en"]
        return language_data[key]
    else:
        return language_data[key]

