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
        "reminder": "Reminder",
        "time": "Time",
        "text": "Text",
        "vote_again": "Don't forget to vote for me!",
        "todo_list": "To-do List",
        "todo_empty": "Your to-do list is empty",
        "generate_number": "Generate Number",
        "number_prompt": "Your random number is",
        "bot_latency": "Bot Latency",
        "cpu_usage": "CPU Usage",
        "ram_usage": "RAM Usage",
        "thread_count": "Thread Count",
        "joined_guilds": "Joined Guilds",
        "active_shards": "Active Shards",
        "member_count": "Member Count",
        "channel_count": "Channel Count",
        "command_count": "Command Count",
        "disnake_version": "Disnake Version",
        "bot_version": "Bot Version",
        "bot_uptime": "Bot Uptime",
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
        "reminder": "提醒",
        "time": "时间",
        "text": "文字",
        "vote_again": "不要忘记给我投票!",
        "todo_list": "待办事项列表",
        "todo_empty": "你的待办事列表是空的",
        "generate_number": "生成数字",
        "number_prompt": "你的随机数字是",
        "bot_latency": "机器人延迟",
        "cpu_usage": "CPU使用率",
        "ram_usage": "RAM使用率",
        "thread_count": "机器人程序数",
        "joined_guilds": "机器人服务器",
        "active_shards": "机器人碎片",
        "member_count": "人数",
        "channel_count": "频道数",
        "command_count": "指令数",
        "disnake_version": "Disnake版本",
        "bot_version": "机器人版本",
        "bot_uptime": "机器人运行时间",
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
        "todo_list": "Список дел",
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

