import telebot
import config
import json
import time
import mysql.connector

from DB import DB as D
from threading import Thread
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
DB = D(config.mysql)

bot.send_message(1294113685, "Start Bot")

def json_loads(data):
    try:
        return json.loads(data)
    except:
        return None

def get_user(message):
    data = DB.select('Users', ['id', 'name', 'surname', 'num_class', 'let_class', 'id_team', 'status'], [['id', '=', message.chat.id]], 1)
    if (data):
        return {"id": data[0][0], "name": data[0][1], "surname": data[0][2], "num_class": data[0][3], "let_class": data[0][4], "id_team":data[0][5], "status": data[0][6],}
    else:
        DB.insert('Users', ['id', 'name', 'surname', 'num_class', 'let_class', 'id_team', 'status'], [[message.chat.id, message.chat.first_name, "NaN", 5, 'А', 0, 'reg_menu']])
        return {"id": message.chat.id, "name": message.chat.first_name, "num_class": 5, "let_class": 'А', "id_team": 0, "status": 'reg_menu'}

def log(message, user):
    query = "INSERT INTO log (text) VALUES (%s)"

def user_update(user, status=None, settings=None):
    DB.update('Users', {'status': status}, [['id', '=', user['id']]])

def markups(buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b = []
    for i in buttons:
        b.append(types.KeyboardButton(i))
    markup.add(*b)
    return markup

def menu_markups(user):
    answer = markups(["Тренировкаю🖥️", "Инфоℹ", "Настройки⚙️"])

@bot.message_handler(commands=['start'])
def start_message(message):
    user = get_user(message)
    if(user["status"] != "reg"):
        bot.send_message(message.chat.id,"Привет! Я бот, в котором можно тренеровать навыки в CTF(Capture the flag)", reply_markup=menu_markups(user))
        log(message, user)
        user_update(user, "menu")
    else:
        bot.send_message(user["id"], "Инициализирован процесс регистрации, пожалуйста следуйте инструкциям:\n <b>1. Если вы учитель</b>, введите своё имя и фамилию, после ввода всех данных нажмите кнопку 'Учитель'. \n <b>2. Если вы капитан команды</b>, введите своё имя, фамилию, номер класса, букву класса, в меню ID команды введите 0, для создания команды, после ввода всех данных нажмите кнопку 'Готово'. \n <b>2. Если вы участник команды(не капитан)</b>, введите своё имя, фамилию, номер класса, букву класса, в меню ID команды введите, ID которое вывело капитану после регистрации команды, после ввода всех данных нажмите кнопку 'Готово'", parse_mode="HTML", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды'  'Готово']))

@bot.message_handler(commands=['restart'])
def start_message(message):
    user = get_user(message)
    bot.send_message(message.chat.id,"Перезаряжаю!!!!!!!!!!", reply_markup=menu_markups(user))
    log(message, user)
    user_update(user, "menu")

class MessageHandler:
    class Main:
        def menu(bot, message, user):
            if "ИНФО" in message.text.upper():
                bot.send_message(message.chat.id, "Привет, я бот для тренировки в CTF, Здесь есть различные задания разной сложности") #Добавить лидер борд
                return True

        
        def to_menu(bot, message, user):
            bot.send_message(user["id"], "Хорошего дня!", reply_markup=menu_markups(user))
            user_update(user, status="menu")
            return True
        
    class Reg:
        def reg_to_menu(bot, message, user):
            user_update(user, status="reg_menu")
            return True

        def reg_menu(bot, message, user):
            if(message.text.upper() == "ИМЯ"):
                user_update(user, status="reg_name")
                return MessageHandler.Reg.reg_name(bot, message, user)
            if(message.text.upper() == "ФАМИЛИЯ"):
                user_update(user, status="reg_surname")
                return MessageHandler.Reg.reg_surname(bot, message, user)
            if(message.text.upper() == "НОМЕР КЛАССА"):
                user_update(user, status="reg_num_class")
                return MessageHandler.Reg.reg_num_class(bot, message, user)
            if(message.text.upper() == "БУКВА КЛАССА"):
                user_update(user, status="reg_let_class")
                return MessageHandler.Reg.reg_let_class(bot, message, user)
            if(message.text.upper() == "ID КОМАНДЫ"):
                user_update(user, status="reg_id_team")
            
            return True

        def reg_name(bot, message, user):
            bot.send_message(user["id"], "Введите ваше имя", reply_markup=markups(['Назад']))
            if(message.text.upper() == "НАЗАД"):
                return MessageHandler.Reg.reg_to_menu
            elif(message.text.upper() != "ИМЯ" and message.text.upper() != "НАЗАД"):
                DB.update(user, {'name': message.text}, [['id', '=', user['id']]])
            
            return True
        def reg_surname(bot, message, user):
            bot.send_message(user["id"], "Введите вашу фамилию", reply_markup=markups(['Назад']))
            if(message.text.upper() == "НАЗАД"):
                return MessageHandler.Reg.reg_to_menu
            elif(message.text.upper() != "ФАМИЛИЯ" and message.text.upper() != "НАЗАД"):
                DB.update(user, {'surname': message.text}, [['id', '=', user['id']]])
            
            return True
        
        def reg_num_class(bot, message, user):
            bot.send_message(user["id"], "Введите номер вашего класса", reply_markup=markups(['Назад']))
            if(message.text.upper() == "НАЗАД"):
                return MessageHandler.Reg.reg_to_menu
            elif(message.text.upper() != "НОМЕР КЛАССА" and message.text.upper() != "НАЗАД"):
                DB.update(user, {'num_class': message.text}, [['id', '=', user['id']]])
            return True
        
        def reg_let_class(bot, message, user):
            bot.send_message(user["id"], "Введите букву вашего класса", reply_markup=markups(['Назад']))
            if(message.text.upper() == "НАЗАД"):
                return MessageHandler.Reg.reg_to_menu
            elif(message.text.upper() != "БУКВА КЛАССА" and message.text.upper() != "НАЗАД"):
                DB.update(user, {'let_class': message.text}, [['id', '=', user['id']]])
            
            return True
        
        def reg_team_id(bot, message, user):
            bot.send_message(user["id"], "Введите номер вашей команды, если у вас нет команды введите 0", reply_markup=markups(['Назад']))
            if(message.text.upper() == "НАЗАД"):
                return MessageHandler.Reg.reg_to_menu(bot, message, user)
            elif(message.text.upper() == "0"):
                user_update(user, status="reg_team")
                return MessageHandler.Reg.reg_team(bot, message, user)
            elif(message.text.upper() != "БУКВА КЛАССА" and message.text.upper() != "НАЗАД"):
                data = DB.select('Teams', where= [['id', '=', int(message.text)]], limit=1)
                print(data)
                if(len(data) == 1):
                    DB.update(user, {'team_id': message.text}, [['id', '=', user['id']]])
                    bot.send_message(user["id"], "Вы успешно присоединились к команде", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды'  'Готово']))
                else:
                    bot.send_message(user["id"], "Такой команды не найдено")
            return True

        
        class Team:
            def reg_team(bot, message, user):
                bot.send_message(user["id"], "")
        


def update_connection():
    while True:
        try:
            del DB
            DB = DB(mysql)
            time.sleep(5)
        except:
            pass

thread1 = Thread(target=update_connection)
thread1.start()

@bot.message_handler(content_types=["text"])
def handle_text(message):
    print(f"{message.chat.id} {message.chat.first_name} |{message.text}|")
    message.text = message.text.strip().replace("  ", " ").replace("\t\t", "\t")
    user = get_user(message)
    log(message, user)
    action = {
        "menu": MessageHandler.Main.menu,
        "reg_menu": MessageHandler.Reg.reg_menu,
        "reg_name": MessageHandler.Reg.reg_name,
        "reg_surname": MessageHandler.Reg.reg_surname,
        "reg_let_class": MessageHandler.Reg.reg_let_class,
        "reg_num_class": MessageHandler.Reg.reg_num_class,
        "reg_id_team": MessageHandler.Reg.reg_team_id,
    }
    if action.get(user["status"]):
        if not action[user["status"]](bot, message, user):
            bot.send_message(user["id"], "Не понял!")
    else:
        bot.send_message(user["id"], f"Статус {user['status']} не найден!")
    return

bot.polling()