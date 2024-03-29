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
        DB.insert('Users', ['id', 'name', 'surname', 'num_class', 'let_class', 'id_team', 'status'], [[message.chat.id, message.chat.first_name, "NaN", 5, 'А', -1, 'reg_menu']])
        return {"id": message.chat.id, "name": message.chat.first_name, "num_class": 5, "let_class": 'А', "id_team": -1, "status": 'reg_menu'}

def log(message, user):
    query = "INSERT INTO log (text) VALUES (%s)"

def user_update(user, status=None):
    DB.update('Users', {'status': status}, [['id', '=', user['id']]])

def markups(buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b = []
    for i in buttons:
        b.append(types.KeyboardButton(i))
    markup.add(*b)
    return markup

def menu_markups(user):
    answer = markups(["Задачи🖥️", "Инфоℹ", "Топ🔝","Настройки⚙️"])
    return answer

@bot.message_handler(commands=['start'])
def start_message(message):
    user = get_user(message)
    if(user["status"] != "reg_menu"):
        bot.send_message(message.chat.id,"Привет! Я бот, в котором можно тренеровать навыки в CTF(Capture the flag)", reply_markup=menu_markups(user))
        log(message, user)
        user_update(user, "menu")
    else:
        bot.send_message(user["id"], "Инициализирован процесс регистрации, пожалуйста следуйте инструкциям:\n <b>1. Если вы учитель</b>, введите своё имя и фамилию, после ввода всех данных нажмите кнопку 'Учитель'. \n <b>2. Если вы капитан команды</b>, введите своё имя, фамилию, номер класса, букву класса, в меню ID команды введите 0, для создания команды, после ввода всех данных нажмите кнопку 'Готово'. \n <b>3. Если вы участник команды(не капитан)</b>, введите своё имя, фамилию, номер класса, букву класса, в меню ID команды введите, ID которое вывело капитану после регистрации команды, после ввода всех данных нажмите кнопку 'Готово'", parse_mode="HTML", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))

@bot.message_handler(commands=['restart'])
def start_message(message):
    user = get_user(message)
    bot.send_message(message.chat.id,"Перезаряжаю!!!!!!!!!!", reply_markup=menu_markups(user))
    log(message, user)
    user_update(user, "menu")

class MessageHandler:
    class Main:
        def to_menu(bot, message, user):
            bot.send_message(user["id"], "Хорошего дня!", reply_markup=menu_markups(user))
            user_update(user, status="menu")
            return True

        def menu(bot, message, user):
            if ("ИНФО" in message.text.upper()):
                bot.send_message(message.chat.id, "Привет, я бот для тренировки в CTF. Здесь ты можешь по практиковаться в задачах CTF\n<b>Если вы хотите решать задачи,</b> нажмите кнопку 'Задачи', но учтите ответы на задания может загружать только капитан.\n<b>Если при регистрации ввели, что-то не так</b> в настройках вы можете поменять любую информацию о себе\n<b>Если нашли недочёт,</b> пишите об этом мне, @Gladfn", parse_mode="HTML", reply_markup=menu_markups(user))
                return True
            elif ("ЗАДАЧИ" in message.text.upper()):
                tasks = DB.select('Tasks')

                but = []

                answer = ''
                for i in range(len(tasks)):
                    data = json.loads(tasks[i][4])
                    print(data)
                    if(user['id_team'] not in json.loads(tasks[i][4])):
                        answer += "Задача №" + str(i + 1) + ")"
                        answer += " " + tasks[i][1]
                        answer += "\n"
                        but.append(tasks[i][1])
                
                bot.send_message(message.chat.id, "На данный момент у вашей команды не решены следующие задачи:")
                bot.send_message(user['id'], answer)
                but.append('Загрузить решение')
                but.append('Назад')
                bot.send_message(message.chat.id, "Выберите задачу которую хотите решить:", reply_markup=markups(but))
                user_update(user, status="tasks")
                return MessageHandler.Main.tasks(bot, message, user)                
            elif ("НАСТРОЙКИ" in message.text.upper()):
                bot.send_message(user['id'], "Выберите, что хотите изменить:", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'Готово']))
                return MessageHandler.Settings.set_to_menu(bot, message, user)
            elif ("ТОП" in message.text.upper()):
                teams = DB.select('Teams', ['team_name', 'points'])
                answer = ""
                teams.sort(key = lambda x: x[1], reverse=True)
                user_team = DB.select('Teams', ['team_name', 'points'], where=[['id', '=', user['id_team']]])
                h = teams.index(user_team[0])
                if(len(teams) > 10):
                    if (h <= 9):
                        for i in range(10):
                            if(h == i):
                                answer += f"<b>{i + 1}) {teams[i][0]} {teams[i][1]}</b>\n"
                            else:
                                answer += f"{i + 1}) {teams[i][0]} {teams[i][1]}\n"

                    else:
                        for i in range(10):
                            answer += f"{i + 1}) {teams[i][0]} {teams[i][1]}\n"
                        answer += f"<b>{h + 1} + {user_team[0][1]}</b>"
                else:
                    for i in range(len(teams)):
                        if(h == i):
                            answer += f"<b>{i + 1}) {teams[i][0]} {teams[i][1]}</b>\n"
                        else:
                            answer += f"{i + 1}) {teams[i][0]} {teams[i][1]}\n"
                bot.send_message(user['id'], f"<b>Топ 10</b>\n{answer}", parse_mode="HTML")

            else:
                return False
            
            return True
        
        def tasks(bot, message, user):
            if("НАЗАД" in message.text.upper()):
                return MessageHandler.Main.to_menu(bot, message, user)
            if("ЗАГРУЗИТЬ РЕШЕНИЕ" in message.text.upper()):
                if(user['id'] == user['id_team']):
                    user_update(user, status='tasks_comp')
                    tasks = DB.select('Tasks')

                    but = []

                    for i in range(len(tasks)):
                        data = json.loads(tasks[i][4])
                        if(user['id_team'] not in json.loads(tasks[i][4])):
                            but.append(tasks[i][1])

                    but.append('Назад')
                    bot.send_message(user['id'], 'Выберите решение на какую задачу хотите сдать:', reply_markup=markups(but))
                    
                    return MessageHandler.Main.tasks_comp(bot, message, user)
                else:
                    bot.send_message(user["id"], "Вы не являетессь капитаном")
            if("ЗАДАЧИ" not in message.text.upper() and "НАЗАД" not in message.text.upper()):
                data = DB.select('Tasks', where=[['name', '=', message.text]], limit=1)
                data = data[0]
                if(data[-1] != None):
                    bot.send_message(user['id'], f"Задача: {data[1]}\n{data[-1]}\nФайлы к задаче:")
                else:
                    bot.send_message(user['id'], f"Задача: {data[1]}\nФайлы к задаче:")
                files = json.loads(data[2])
                for i in range(len(files)):
                    
                    doc = open(f'tasks/{int(data[0])}/{files[i]}', 'rb')
                    bot.send_document(user['id'], doc)
            
            return True
        
        def tasks_comp(bot, message, user):
            if("НАЗАД" in message.text.upper()):
                user_update(user, status='tasks')
                return MessageHandler.Main.tasks(bot, message, user)
            elif("ЗАГРУЗИТЬ РЕШЕНИЕ" not in message.text.upper()):
                tasks = DB.select('Tasks', where=[['name', '=', message.text]])
                bot.send_message(user['id'], "Введите ключ, следующим образом(без кавычек): 'id задания,ключ':")
                user_update(user, status='tasks_comp_end')
                return MessageHandler.Main.tasks_comp_end(bot, message, user)
            return True
        
        def tasks_comp_end(bot, message, user):
            if("НАЗАД" in message.text.upper()):
                user_update(user, status='tasks')
                return MessageHandler.Main.tasks(bot, message, user)
            elif("ЗАГРУЗИТЬ РЕШЕНИЕ" not in message.text.upper()):
                if(',' in message.text):
                    for i in range(len(message.text)):
                        if(message.text[i] == ","):
                            data = DB.select('Tasks', [['id', '=', int(message.text[:i])]])
                            if(len(data) == 1 and message.text[i+1:]):
                                data = data[0]
                                people = len(json.loads(data[4])) + 1
                                points = DB.select('Teams', ['points'], [['id', '=', user["id_team"]]])
                                DB.update('Teams', {'points' : points + data[3]}, [['id', '=', user['id_team']]])
                                DB.update('Tasks', {'values' : ((((100 - 1000)/(people ** 2)) * (data[5] ** 2)) + 1000) // 1}, [['id', '=' ,data['id']]])
            return True
        
    class Settings:
        def set_to_menu(bot, message, user):
            user_update(user, status="set_menu")
            return True

        def set_menu(bot, message, user):
            if(message.text.upper() == "ИМЯ"):
                user_update(user, status="set_name")
                bot.send_message(user["id"], "Введите ваше имя", reply_markup=markups(['Назад']))
                return MessageHandler.Settings.set_name(bot, message, user)
            if(message.text.upper() == "ФАМИЛИЯ"):
                bot.send_message(user["id"], "Введите вашу фамилию", reply_markup=markups(['Назад']))
                user_update(user, status="set_surname")
                return MessageHandler.Settings.set_surname(bot, message, user)
            if(message.text.upper() == "НОМЕР КЛАССА"):
                bot.send_message(user["id"], "Выберите номер вашего класса", reply_markup=markups(['7', '8', '9', 'Назад']))
                user_update(user, status="set_num_class")
                return MessageHandler.Settings.set_num_class(bot, message, user)
            if(message.text.upper() == "БУКВА КЛАССА"):
                bot.send_message(user["id"], "Введите букву вашего класса, русской заглавной буквой", reply_markup=markups(['Назад']))
                user_update(user, status="set_let_class")
                return MessageHandler.Settings.set_let_class(bot, message, user)
            if(message.text.upper() == "ГОТОВО"):
                bot.send_message(user['id'], "Успешно", reply_markup=menu_markups(user))
                return MessageHandler.Main.to_menu(bot, message, user)

            return True

        def set_name(bot, message, user):
            
            if(message.text.upper() == "НАЗАД"):
                bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'Готово']))
                return MessageHandler.Settings.set_to_menu(bot, message, user)
            elif(message.text.upper() != "ИМЯ" and message.text.upper() != "НАЗАД"):
                DB.update('Users', {'name': message.text}, [['id', '=', user['id']]])
                bot.send_message(user['id'], "Данные успешно изменены", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'Готово']))
                return MessageHandler.Settings.set_to_menu(bot, message, user)    
            return True
        
        def set_surname(bot, message, user):
            
            if(message.text.upper() == "НАЗАД"):
                bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'Готово']))
                return MessageHandler.Settings.set_to_menu(bot, message, user)    
            elif(message.text.upper() != "ФАМИЛИЯ" and message.text.upper() != "НАЗАД"):
                DB.update('Users', {'surname': message.text}, [['id', '=', user['id']]])
                bot.send_message(user['id'], "Данные успешно изменены", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'Готово']))
                return MessageHandler.Settings.set_to_menu(bot, message, user)    
            return True
        
        def set_num_class(bot, message, user):
            
            if(message.text.upper() == "НАЗАД"):
                bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'Готово']))
                return MessageHandler.Settings.set_to_menu(bot, message, user)    
            elif(message.text.upper() != "НОМЕР КЛАССА" and message.text.upper() != "НАЗАД"):
                if('7' in message.text or '8' in message.text or '9' in message.text):
                    DB.update('Users', {'num_class': int(message.text)}, [['id', '=', user['id']]])
                    bot.send_message(user['id'], "Данные успешно изменены", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'Готово']))
                    return MessageHandler.Settings.set_to_menu(bot, message, user)    
            return True
        
        def set_let_class(bot, message, user):
            
            if(message.text.upper() == "НАЗАД"):
                bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'Готово']))
                return MessageHandler.Settings.set_to_menu(bot, message, user)    
            
            elif(message.text.upper() != "БУКВА КЛАССА" and message.text.upper() != "НАЗАД"):
                DB.update('Users', {'let_class': message.text}, [['id', '=', user['id']]])
                bot.send_message(user['id'], "Данные успешно добавлены", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'Готово']))
                return MessageHandler.Settings.set_to_menu(bot, message, user)    
            
            return True
        pass

    class Reg:
        def reg_to_menu(bot, message, user):
            user_update(user, status="reg_menu")
            return True

        def reg_menu(bot, message, user):
            if(message.text.upper() == "ИМЯ"):
                user_update(user, status="reg_name")
                bot.send_message(user["id"], "Введите ваше имя", reply_markup=markups(['Назад']))
                return MessageHandler.Reg.reg_name(bot, message, user)
            if(message.text.upper() == "ФАМИЛИЯ"):
                bot.send_message(user["id"], "Введите вашу фамилию", reply_markup=markups(['Назад']))
                user_update(user, status="reg_surname")
                return MessageHandler.Reg.reg_surname(bot, message, user)
            if(message.text.upper() == "НОМЕР КЛАССА"):
                bot.send_message(user["id"], "Выберите номер вашего класса", reply_markup=markups(['7', '8', '9', 'Назад']))
                user_update(user, status="reg_num_class")
                return MessageHandler.Reg.reg_num_class(bot, message, user)
            if(message.text.upper() == "БУКВА КЛАССА"):
                bot.send_message(user["id"], "Введите букву вашего класса, русской заглавной буквой", reply_markup=markups(['Назад']))
                user_update(user, status="reg_let_class")
                return MessageHandler.Reg.reg_let_class(bot, message, user)
            if(message.text.upper() == "ID КОМАНДЫ"):
                bot.send_message(user["id"], "Введите номер вашей команды, если у вас нет команды, введите 0", reply_markup=markups(['Назад']))
                user_update(user, status="reg_id_team")
            if(message.text.upper() == "УЧИТЕЛЬ"):
                data = DB.select('Users', ['surname'], [['id', '=', user['id']]])
                if(data[0][0] == 'NaN'):
                    bot.send_message(user['id'], 'Вы не ввелии фамилию')
                else:
                    DB.update(user, {'id_team': 0}, [['id', '=', user['id']]])
                    bot.send_message(user['id'], "Регистрация прошла успешна", reply_markup=menu_markups(user))
                    return MessageHandler.Main.to_menu(bot, message, user)
            if(message.text.upper() == "ГОТОВО"):
                data = DB.select('Users', ['surname', 'id_team'], [['id', '=', user['id']]])
                if(data[0][0] == 'NaN' or data[0][1] == -1):
                    bot.send_message(user['id'], "Вы не ввели некоторые данные")
                else:
                    bot.send_message(user['id'], "Регистрация прошла успешна", reply_markup=menu_markups(user))
                    return MessageHandler.Main.to_menu(bot, message, user)

            return True

        def reg_name(bot, message, user):
            
            if(message.text.upper() == "НАЗАД"):
                bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                return MessageHandler.Reg.reg_to_menu(bot, message, user)
            elif(message.text.upper() != "ИМЯ" and message.text.upper() != "НАЗАД"):
                DB.update('Users', {'name': message.text}, [['id', '=', user['id']]])
                bot.send_message(user['id'], "Данные успешно добавлены", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                return MessageHandler.Reg.reg_to_menu(bot, message, user)    
            return True
        
        def reg_surname(bot, message, user):
            
            if(message.text.upper() == "НАЗАД"):
                bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                return MessageHandler.Reg.reg_to_menu(bot, message, user)
            elif(message.text.upper() != "ФАМИЛИЯ" and message.text.upper() != "НАЗАД"):
                DB.update('Users', {'surname': message.text}, [['id', '=', user['id']]])
                bot.send_message(user['id'], "Данные успешно добавлены", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                return MessageHandler.Reg.reg_to_menu(bot, message, user)
            return True
        
        def reg_num_class(bot, message, user):
            
            if(message.text.upper() == "НАЗАД"):
                bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                return MessageHandler.Reg.reg_to_menu(bot, message, user)
            elif(message.text.upper() != "НОМЕР КЛАССА" and message.text.upper() != "НАЗАД"):
                if('7' in message.text or '8' in message.text or '9' in message.text):
                    DB.update('Users', {'num_class': int(message.text)}, [['id', '=', user['id']]])
                    bot.send_message(user['id'], "Данные успешно добавлены", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                    return MessageHandler.Reg.reg_to_menu(bot, message, user)
            return True
        
        def reg_let_class(bot, message, user):
            
            if(message.text.upper() == "НАЗАД"):
                bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                return MessageHandler.Reg.reg_to_menu(bot, message, user)
            
            elif(message.text.upper() != "БУКВА КЛАССА" and message.text.upper() != "НАЗАД"):
                DB.update('Users', {'let_class': message.text}, [['id', '=', user['id']]])
                bot.send_message(user['id'], "Данные успешно добавлены", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                return MessageHandler.Reg.reg_to_menu(bot, message, user)
            
            return True
        
        def reg_team_id(bot, message, user):

            if(message.text.upper() == "НАЗАД"):
                bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                return MessageHandler.Reg.reg_to_menu(bot, message, user)
            elif(message.text.upper() == "0"):
                user_update(user, status="reg_team")
                bot.send_message(user["id"], "Введите данные команды", reply_markup=markups(['Название', 'Назад']))
                return MessageHandler.Reg.Team.reg_team_to_menu(bot, message, user)
            elif(message.text.upper() != "БУКВА КЛАССА" and message.text.upper() != "НАЗАД"):
                data = DB.select('Teams', where= [['id', '=', int(message.text)]], limit=1)
                if(len(data) == 1):
                    data = data[0]
                    DB.update('Users', {'id_team': int(message.text)}, [['id', '=', user['id']]])
                    people = json.loads(data[2])
                    people.append(user['id'])
                    DB.update('Teams', {'people': json.dumps(people)}, [['id', '=', user['id_team']]])
                    bot.send_message(user["id"], "Вы успешно присоединились к команде", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                    return MessageHandler.Reg.reg_to_menu(bot, message, user)
                else:
                    bot.send_message(user["id"], "Такой команды не найдено")
            return True

        
        class Team:
            def reg_team_to_menu(bot, message, user):
                user_update(user, 'reg_team_menu')
                return True

            def reg_team_menu(bot, message, user):
                if("НАЗВАНИЕ" in message.text.upper()):
                    bot.send_message(user["id"], "Введите название команды:", reply_markup=markups(['Назад']))
                    return MessageHandler.Reg.Team.reg_team_name(bot, message, user)
                if("НАЗАД" in message.text.upper()):
                    bot.send_message(user["id"], "Возвращаю", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                    return MessageHandler.Reg.reg_to_menu(bot, message, user)
                return True
            
            def reg_team_name(bot, message, user):
                user_update(user, 'reg_team_name')
                if("НАЗВАНИЕ" not in message.text.upper() and "НАЗАД" not in message.text.upper()):
                    data = []
                    data.append(user['id'])
                    DB.insert('Teams', ['id', 'team_name', 'people', 'points'], [[message.chat.id, message.text,json.dumps(data, indent=2), 0]])
                    print('b1')
                    bot.send_message(user["id"], f"Команда успешно зарегистрирована, ID вашей команды: <b>{user['id']}</b>", parse_mode="HTML", reply_markup=markups(['Имя', 'Фамилия', 'Номер класса', 'Буква класса', 'ID Команды', 'Готово', 'Учитель']))
                    DB.update("Users", {'id_team' : user['id']}, [['id', '=', user['id']]])
                    return MessageHandler.Reg.reg_to_menu(bot, message, user)
                if("НАЗАД" in message.text.upper()):
                    bot.send_message(user["id"], "Возвращаю",reply_markup=markups(["Название", "Готово"]))
                    return MessageHandler.Reg.Team.reg_team_to_menu(bot, message, user)
                return True
        


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
        "tasks": MessageHandler.Main.tasks,
        "tasks_comp": MessageHandler.Main.tasks_comp,
        "tasks_comp_end": MessageHandler.Main.tasks_comp_end,
        "set_menu": MessageHandler.Settings.set_menu,
        "set_name": MessageHandler.Settings.set_name,
        "set_surname": MessageHandler.Settings.set_surname,
        "set_let_class": MessageHandler.Settings.set_let_class,
        "set_num_class": MessageHandler.Settings.set_num_class,
        "reg_menu": MessageHandler.Reg.reg_menu,
        "reg_name": MessageHandler.Reg.reg_name,
        "reg_surname": MessageHandler.Reg.reg_surname,
        "reg_let_class": MessageHandler.Reg.reg_let_class,
        "reg_num_class": MessageHandler.Reg.reg_num_class,
        "reg_id_team": MessageHandler.Reg.reg_team_id,
        "reg_team_menu": MessageHandler.Reg.Team.reg_team_menu,
        "reg_team_name": MessageHandler.Reg.Team.reg_team_name
    }
    if action.get(user["status"]):
        if not action[user["status"]](bot, message, user):
            bot.send_message(user["id"], "Не понял!")
    else:
        bot.send_message(user["id"], f"Статус {user['status']} не найден!")
    return

bot.polling()