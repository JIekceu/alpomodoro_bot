import telebot
import time
from bot_settings import bot_token
from telebot import types

bot = telebot.TeleBot(bot_token)

worktime_min = int()
worktime_sec = int()
pausetime_min = int()
pausetime_sec = int()
repeats = int()
UserId = int()
numb_profile = int()


savings = {}  # {123456789: [[1, 1, 1], [2, 2, 2], [3, 3, 3]], 987654321: [[2, 1, 2], [5, 4, 3]]}
#               {User_ID: [[worktime_min, pausetime_min, repeats]]}


@bot.message_handler(commands=['start'])
def start(message):
    global UserId
    UserId = message.from_user.id
    if UserId not in savings:
        savings[UserId] = []
    if message.text == '/start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        menu = types.KeyboardButton("/Menu")
        markup.add(menu)
        bot.send_message(message.from_user.id,
                         text="Hi, {0.first_name}! I'm Pomodoro and I'll try to save your time. Press /Menu to begin.\n\n(Bot run in test mode, speed x60)"
                         .format(message.from_user), reply_markup=markup)
    get_continue(message)


@bot.message_handler(content_types=['text'])
def get_continue(message):
    if message.text == '/Menu':
        begin(message)


def begin(message):
    global UserId, worktime_min, pausetime_min, repeats, numb_profile
    if len(savings[UserId]) == 0:
        bot.send_message(message.from_user.id, "Input Task working time, minutes:")
        bot.register_next_step_handler(message, get_worktime)
    elif len(savings[UserId]) == 3:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        profile1 = types.KeyboardButton("Profile1")
        profile2 = types.KeyboardButton("Profile2")
        profile3 = types.KeyboardButton("Profile3")
        markup.add(profile1, profile2, profile3)
        bot.send_message(message.from_user.id,
                         "Input Task working time, minutes, or chose saved profile:", reply_markup=markup)
        bot.register_next_step_handler(message, profile_check)
    elif len(savings[UserId]) == 2:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        profile1 = types.KeyboardButton("Profile1")
        profile2 = types.KeyboardButton("Profile2")
        markup.add(profile1, profile2)
        bot.send_message(message.from_user.id,
                         "Input Task working time, minutes, or chose saved profile:", reply_markup=markup)
        bot.register_next_step_handler(message, profile_check)
    elif len(savings[UserId]) == 1:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        profile1 = types.KeyboardButton("Profile1")
        markup.add(profile1)
        bot.send_message(message.from_user.id,
                         "Input Task working time, minutes, or chose saved profile:", reply_markup=markup)
        bot.register_next_step_handler(message, profile_check)


def profile_check(message):
    global UserId, worktime_min, pausetime_min, repeats, numb_profile
    if message.text == "Profile1" or message.text == "Profile2" or message.text == "Profile3":
        if message.text == "Profile1" and len(savings[UserId]) > 0:
            numb_profile = 0
            worktime_min = savings[UserId][0][0]
            pausetime_min = savings[UserId][0][1]
            repeats = savings[UserId][0][2]
        elif message.text == "Profile2" and len(savings[UserId]) > 1:
            numb_profile = 1
            worktime_min = savings[UserId][1][0]
            pausetime_min = savings[UserId][1][1]
            repeats = savings[UserId][1][2]
        elif message.text == "Profile3" and len(savings[UserId]) > 2:
            numb_profile = 2
            worktime_min = savings[UserId][2][0]
            pausetime_min = savings[UserId][2][1]
            repeats = savings[UserId][2][2]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        run = types.KeyboardButton("Run")
        delete = types.KeyboardButton("Delete")
        menu = types.KeyboardButton("/Menu")
        markup.add(run, delete, menu)
        bot.send_message(message.from_user.id,
                         "{0} has been loaded: Work time {1} min, Pause {2} min with {3} repeats".format(
                             message.text, worktime_min, pausetime_min, repeats), reply_markup=markup)
        bot.register_next_step_handler(message, in_profile)
    else:
        get_worktime(message)


def in_profile(message):
    global numb_profile
    if message.text == "Run":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        menu = types.KeyboardButton("/Menu")
        markup.add(menu)
        bot.send_message(message.chat.id, "This Profile has been run", reply_markup=markup)
        cycle_pomodoro()
    elif message.text == "Delete":
        del savings[UserId][numb_profile]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        menu = types.KeyboardButton("/Menu")
        markup.add(menu)
        bot.send_message(message.from_user.id, "This Profile has been deleted", reply_markup=markup)
    elif message.text == "/Menu":
        get_continue(message)


def get_worktime(message):
    global worktime_min
    try:
        worktime_min = int(message.text)
        bot.send_message(message.from_user.id, 'Input pause time of pomodoro, minutes:')
        bot.register_next_step_handler(message, get_pausetime)
    except Exception:
        bot.send_message(message.from_user.id, 'Digits, please! Press /Menu and try again')


def get_pausetime(message):
    global pausetime_min
    try:
        pausetime_min = int(message.text)
        bot.send_message(message.from_user.id, 'Input quantity of repeats:')
        bot.register_next_step_handler(message, get_repeats)
    except Exception:
        bot.send_message(message.from_user.id, 'Digits, please! Press /Menu and try again')


def get_repeats(message):
    global repeats
    global UserId
    try:
        repeats = int(message.text)
    except Exception:
        bot.send_message(message.from_user.id, 'Digits, please! Press /Menu and try again')
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Yes', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='No', callback_data='no')
    keyboard.add(key_no)
    question = 'Would you like to save this pomodoro before begin?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        if len(savings[UserId]) == 3:
            bot.send_message(UserId, "Sorry, there is no any empty profile")
        else:
            savings[UserId].append([worktime_min, pausetime_min, repeats])
            bot.send_message(call.message.chat.id, 'Profile saved')
    cycle_pomodoro()


def cycle_pomodoro():
    global UserId
    global repeats
    global worktime_min
    global worktime_sec
    global pausetime_min
    global pausetime_sec

    bot.send_message(UserId, "Pomodoro has been started. Let's work!")
    while repeats > 0:
        worktime_sec = int(time.time()) + worktime_min  # * 60
        while worktime_sec > int(time.time()):
            pass
        else:
            repeats -= 1
            if repeats > 0:
                bot.send_message(UserId, 'Task has been finished, have a rest')
                pausetime_sec = int(time.time()) + pausetime_min  # * 60
                while pausetime_sec > int(time.time()):
                    pass
                else:
                    bot.send_message(UserId, "Time for rest is over, let's work!")
            else:
                bot.send_message(UserId, 'All tasks has been finished, press /Menu to begin again.')


bot.polling(none_stop=True, interval=0)
