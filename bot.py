import telebot
import psycopg2
import functions as func
from datetime import datetime
import pytz
from telebot import types


bot = telebot.TeleBot('')


@bot.message_handler(commands=['start'])
def start_message(message):
    answer = 'Привет!\n Я бот помогающий управлять задачами в группе. Я работаю только в групповых чатах. Чтобы' \
             ' зарегистрировать текущий чат напишите /reg.\nЧтобы присоединиться напишите /join.\n' \
             'Чтобы поставить задачу определенному человеку напишите "/set_task @person_username Task День:Месяц:Год", ' \
             'где @person_username - username пользователя, которму вы хотите назначить задачу, Task - задача, ' \
             'День:Месяц:Год - Дедлайн для задачи.\n Для того, чтобы просмотреть свои задачи напишите /show и я пришлю их ' \
             'вам в личные сообщения'
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['help'])
def help_message(message):
    answer = 'Чтобы' \
             ' зарегистрировать текущий чат напишите /reg.\n Чтобы присоединиться напишите /join.\n' \
             'Чтобы поставить задачу определенному человеку напишите "/set_task @person_username Task День:Месяц:Год", ' \
             'где @person_username - username пользователя, которму вы хотите назначить задачу, Task - задача, ' \
             'День:Месяц:Год - Дедлайн для задачи.\n Для того, чтобы просмотреть свои задачи напишите /show и я пришлю их ' \
             'вам в личные сообщения. И помните, что я работаю только в групповых чатах =)))'
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['drop'])
def drop_message(message):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    cursor.execute('SELECT group_id FROM groups')
    res = cursor.fetchall()
    for elem in res:
        string = 'DROP TABLE ' + str(func.idtoname(elem[0]))
        cursor.execute(string)
    cursor.execute('DROP TABLE groups')
    conn.commit()
    cursor.close()
    conn.close()


@bot.message_handler(commands=['reg'])
def reg_message(message):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS groups (group_name VARCHAR(255) NOT NULL, group_id VARCHAR(255))')
    cursor.execute('SELECT group_id FROM groups')
    res = cursor.fetchall()
    for elem in res:
        if str(message.chat.id) in elem:
            bot.send_message(message.chat.id, "Похоже данная группа уже зарегистрированна")
            cursor.close()
            conn.close()
            return
    cursor.execute("INSERT INTO groups VALUES (%s, %s)",
                   (str(message.chat.title), str(message.chat.id)))
    string = "CREATE TABLE IF NOT EXISTS " + str(func.idtoname(message.chat.id)) + " (person VARCHAR(255), username VARCHAR(255), id VARCHAR(255))"
    cursor.execute(string)
    bot.send_message(message.chat.id, "Регистрация группы " + str(message.chat.title) + " успешна")
    conn.commit()
    cursor.close()
    conn.close()


@bot.message_handler(commands=['join'])
def join_message(message):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS groups (group_name VARCHAR(255) NOT NULL, group_id VARCHAR(255))')
    cursor.execute('SELECT group_id FROM groups')
    res = cursor.fetchall()
    for elem in res:
        if str(message.chat.id) in elem:
            cursor.execute('SELECT id FROM ' + str(func.idtoname(message.chat.id)))
            tmp = cursor.fetchall()
            for sup in tmp:
                if str(message.from_user.id) in sup:
                    bot.send_message(message.chat.id,
                                     "Похоже вы уже присоединились к данной группе")
                    return
            string = "INSERT INTO " + str(func.idtoname(message.chat.id)) + " VALUES (%s, %s, %s)"
            cursor.execute(string, (str(message.from_user.first_name), str(message.from_user.username), str(message.from_user.id)))
            string = 'CREATE TABLE IF NOT EXISTS ' + str(message.from_user.username) +\
                     ' (task VARCHAR(255) NOT NULL, group_name VARCHAR(255)' + \
                     ', group_id VARCHAR(255), deadline VARCHAR(255))'
            cursor.execute(string)
            conn.commit()
            cursor.close()
            conn.close()
            bot.send_message(message.chat.id, "Вы успешно присоединились к группе")
            return
    bot.send_message(message.chat.id, "Похоже данная группа еще не зарегистрированна, для регистрации введите /reg")
    conn.commit()
    cursor.close()
    conn.close()


@bot.message_handler(commands=['set_task'])
def set_task_message(message):
    if func.check_set_message(message.text) != 0:
        data = func.check_set_message(message.text)
        string = data[1].split(':')
        if len(string) == 5:
            if 0 <= int(string[0]) <= 23:
                tz = pytz.timezone('Europe/Moscow')
                deadline = func.fetch_deadline(data[1])
                if deadline > datetime.now(tz):
                    if func.check_group(message):
                        if func.check_person(message, data[0]):
                            conn = psycopg2.connect(dbname='', user='',
                                                    password='',
                                                    host='')
                            cursor = conn.cursor()
                            string = 'INSERT INTO ' + (data[0])[1:] + ' VALUES (%s, %s, %s, %s)'
                            cursor.execute(string, (
                            str(data[2]), str(message.chat.title), str(func.idtoname(message.chat.id)), str(data[1])))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            bot.send_message(message.chat.id,
                                             'Задание для ' + "@" + (data[0])[1:] + ' успешно созданно')
                            answer = '@' + str(message.from_user.username) + ' установил вам задачу: "' + str(
                                data[2]) + '" до ' + str(data[1])
                            bot.send_message(func.get_id(message, data[0]), answer)
                        else:
                            bot.send_message(message.chat.id,
                                             "Похоже " + data[0] + ' еще не присоединилась к данной группе')
                    else:
                        bot.send_message(message.chat.id,
                                         "Похоже данная группа еще не зарегистрированна, для регистрации введите /reg")
                else:
                    bot.send_message(message.chat.id, "К сожалению, у меня нет машины времени =(")
            else:
                bot.send_message(message.chat.id, "Ошибка, неверный формат")
        else:
            bot.send_message(message.chat.id, "Ошибка, неверный формат")
    else:
        bot.send_message(message.chat.id, "Похоже вы ввели команду в неправильном формате, для подробной информации введите /help")


@bot.message_handler(commands=['show'])
def show_message(message):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    string = 'CREATE TABLE IF NOT EXISTS ' + str(message.from_user.username) + \
             ' (task VARCHAR(255) NOT NULL, group_name VARCHAR(255)' + \
             ', group_id VARCHAR(255), deadline VARCHAR(255))'
    cursor.execute(string)
    cursor.execute('SELECT task, deadline FROM ' + str(message.from_user.username))
    tmp = cursor.fetchall()
    answer = ''
    if not tmp:
        bot.send_message(message.from_user.id, 'У вас нет дедлайнов =)')
        return
    for elem in tmp:
        answer += 'Задание: "' + elem[0] + '" нужно выполнить к ' + elem[1] + '\n'
    bot.send_message(message.from_user.id, answer)
    conn.commit()
    cursor.close()
    conn.close()


@bot.message_handler(commands=['del'])
def del_message(message):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    string = 'CREATE TABLE IF NOT EXISTS ' + str(message.from_user.username) + \
             ' (task VARCHAR(255) NOT NULL, group_name VARCHAR(255)' + \
             ', group_id VARCHAR(255), deadline VARCHAR(255))'
    cursor.execute(string)
    cursor.execute('SELECT task, deadline FROM ' + str(message.from_user.username))
    tmp = cursor.fetchall()
    keyboard1 = telebot.types.ReplyKeyboardMarkup()
    for elem in tmp:
        keyboard1.row(str(elem[0]) + '-' + str(elem[1]))
    if not tmp:
        bot.send_message(message.from_user.id, 'У вас нет дедлайнов =)')
    else:
        keyboard1.one_time_keyboard = True
        bot.send_message(message.from_user.id, 'Выбери какой дедлайн нужно удалить:', reply_markup=keyboard1)
        bot.register_next_step_handler(message, delet)
    conn.commit()
    cursor.close()
    conn.close()


def delet(message):
    sup = message.text.split('-')
    func.delete(sup[0], sup[1], message.from_user.username)
    bot.send_message(message.from_user.id, 'Дедлайн успешно удален')


@bot.message_handler(commands=['add_personal'])
def add_message(message):
    bot.send_message(message.from_user.id, "Какой дедлайн назначить? (Пример: 'Сделать контест по акос')")
    bot.register_next_step_handler(message, remember)


@bot.message_handler(commands=['update'])
def update_message(message):
    func.update(str(message.from_user.username))
    bot.send_message(message.from_user.id, "Ваши дедлайны успешно обновлены")

def remember(message):
    bot.send_message(message.from_user.id, "Когда у вас дедлайн? (формат: часы:минуты:день:месяц:год)")
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    string = 'CREATE TABLE IF NOT EXISTS ' + str(message.from_user.username) + \
             ' (task VARCHAR(255) NOT NULL, group_name VARCHAR(255)' + \
             ', group_id VARCHAR(255), deadline VARCHAR(255))'
    cursor.execute(string)
    string = 'INSERT INTO ' + str(message.from_user.username) + ' VALUES (%s, %s, %s, %s)'
    cursor.execute(string, (message.text, str(message.chat.title), str(func.idtoname(message.chat.id)), 'inserting'))
    conn.commit()
    cursor.close()
    conn.close()
    bot.register_next_step_handler(message, date)


def date(message):
    string = (str(message.text)).split(":")
    if len(string) == 5:
        if 0 <= int(string[0]) <= 23:
            deadline = func.fetch_deadline(message.text)
            tz = pytz.timezone('Europe/Moscow')
            if deadline > datetime.now(tz):
                conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
                cursor = conn.cursor()
                request = 'DELETE FROM ' + str(message.from_user.username) + " WHERE deadline = '" + 'inserting' + "'"
                cursor.execute(request)
                conn.commit()
                cursor.close()
                conn.close()
                bot.send_message(message.from_user.id, "К сожалению, у меня нет машины времени =(")
            else:
                conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
                cursor = conn.cursor()
                string = 'UPDATE ' + str(message.from_user.username) + ' SET deadline = ' + "'" + str(message.text) + "'" + " WHERE deadline = '" + 'inserting' + "'"
                cursor.execute(string)
                conn.commit()
                cursor.close()
                conn.close()
                bot.send_message(message.from_user.id, "Отлично, запомню")
    else:
        bot.send_message(message.from_user.id, "Ошибка, попробуем снова")
        bot.send_message(message.from_user.id, "Когда у тебя дедлайн? (формат: часы:минуты:день:месяц:год(4 числа))")
        bot.register_next_step_handler(message, date)


bot.polling(none_stop=True)
