import psycopg2
from datetime import datetime
import pytz


def check_group(message):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS groups (group_name VARCHAR(255) NOT NULL, group_id VARCHAR(255))')
    cursor.execute('SELECT group_id FROM groups')
    res = cursor.fetchall()
    for elem in res:
        if str(message.chat.id) in elem:
            cursor.close()
            conn.close()
            return True
    cursor.close()
    conn.close()
    return False


def check_person(message, name):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM ' + str(idtoname(message.chat.id)))
    tmp = cursor.fetchall()
    for sup in tmp:
        if str(name[1:]) in sup:
            cursor.close()
            conn.close()
            return True
    cursor.close()
    conn.close()
    return False


def idtoname(x):
    id_x = int(x)
    result = ''
    if id_x < 0:
        result += 'z'
        id_x = -1 * id_x
    while id_x > 0:
        result += chr(id_x % 10 + 97)
        id_x = id_x // 10
    return result


def check_set_message(message):
    lst = message.split()
    if len(lst) >= 4:
        name = lst[1]
        date = lst[-1]
        sep = ' '
        string = sep.join(lst[2:-1])
        return [name, date, string]
    else:
        return 0


def get_id(message, name):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    cursor.execute('SELECT username, id FROM ' + str(idtoname(message.chat.id)))
    tmp = cursor.fetchall()
    for sup in tmp:
        if str(name[1:]) in sup:
            cursor.close()
            conn.close()
            return int(sup[1])


def delete(inlet, deadline, table):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    request = 'DELETE FROM ' + table + " WHERE task = '" + inlet  + "' AND deadline = '" + deadline + "'"
    cursor.execute(request)
    conn.commit()
    cursor.close()
    conn.close()


def fetch_deadline(string):
    hours, minutes, day, month, year = string.split(':')
    tz = pytz.timezone('Europe/Moscow')
    deadline = datetime(int(year), int(month), int(day), int(hours), int(minutes), tzinfo=tz)
    return deadline


def update(table):
    conn = psycopg2.connect(dbname='', user='',
                            password='',
                            host='')
    cursor = conn.cursor()
    cursor.execute('SELECT task, deadline FROM ' + str(table))
    tmp = cursor.fetchall()
    for elem in tmp:
        deadline = fetch_deadline(elem[1])
        if deadline < datetime.now(tz):
            request = 'DELETE FROM ' + table + " WHERE deadline = '" + elem[1] + "'"
            cursor.execute(request)
    conn.commit()
    cursor.close()
    conn.close()