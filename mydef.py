import vk_api
import sqlite3 as sl
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import key
import urllib3
from random import randrange

from datetime import date, datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

connect = sl.connect('vkinder.db')
cursor = connect.cursor()

vk_group = vk_api.VkApi(token=key.group_token)
longpoll = VkLongPoll(vk_group)
vk_user = vk_api.VkApi(token=key.user_token)

# функция для выборки данных из БД


def select_db(what, froom, wherer, val, fet=False):
    try:
        if isinstance(wherer, tuple):
            sql_z = f"SELECT {what} FROM {froom}  WHERE {wherer[0]} = {val[0]} AND {wherer[1]} = {val[1]}"

        else:
            sql_z = f"SELECT {what} FROM {froom}  WHERE {wherer} = {val}"

        cursor.execute(sql_z)
        if fet is False:
            req_sql = cursor.fetchone()
        else:
            req_sql = cursor.fetchall()

        return req_sql
    except Exception as exce:
        print("Ошибка базы данных при SELECT данных")
        print(exce)

# функция для вставки данных в БД


def insert_db(where, col_name, value):
    try:
        sql_id = f"INSERT INTO {where} {col_name} VALUES {value};"

        cursor.execute(sql_id)
        connect.commit()
    except Exception as exce:
        print("Ошибка базы данных при INSERT данных")
        print(exce)

# функция для получения данных от пользователя который пишет боту


def user_get(user_id):
    status = vk_group.method('users.get', {'user_id': user_id, 'fields': 'bdate,sex,city,relation'})
    print(status)
    return status

# функция которая пишет пользователю


def write_msg(user_id, message, keyboard=None, attachment=None):
    post = {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7)
    }
    if keyboard is not None:
        post["keyboard"] = keyboard.get_keyboard()
    if attachment is not None:
        post["attachment"] = attachment

    vk_group.method('messages.send', post)

# функция которая прослушивает новые сообщения


def listen():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                text = event.text
                return text.lower(), event.user_id

# функция проверяет есть ли пользователь в БД


def user_in_bd(user_id):
    already_exist = """SELECT user_id FROM users WHERE user_id= ?"""
    cursor.execute(already_exist, (user_id,))
    result = cursor.fetchone()
    return result

# функция отправляет интерактивные кнопки пользователю


def menu(user_id, user_name):
    if user_in_bd(user_id) is None:
        reg = VkKeyboard(one_time=True)
        reg.add_button('Регистрация', VkKeyboardColor.POSITIVE)
        reg.add_line()
        reg.add_openlink_button("Получить токен",
                                f"https://oauth.vk.com/authorize?client_id={key1.IDApps}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=&response_type=token&v=5.131")
        write_msg(user_id,
                  f"{user_name}, добро пожаловать в VK Tinder! \n Первый раз? Нажмите на кнопку Регистрация \n", reg)

    else:
        keyboard = VkKeyboard(one_time=False)
        buttons = ['Поиск', ' MY LIKE', 'MY DISLIKE', 'Стоп']
        buttons_color = [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE,
                         VkKeyboardColor.PRIMARY]
        for btn, btn_color in zip(buttons, buttons_color):
            keyboard.add_button(btn, btn_color)
        write_msg(user_id, f"{user_name}, нажмите на кнопку поиск", keyboard)

# функция которая ищет пользователей по критериям


def users_search(iage_from, iage_to, icity, isex, istatus, offset=False):
    resp = vk_user.method('users.search',
                          {'age_from': iage_from, 'age_to': iage_to, 'city': icity, 'sex': isex, 'status': istatus, 'offset': offset})
    return resp

# функция которая ждет ответ от пользователя


def question(iuser_id, text, keyboard=None, attachment=None):
    write_msg(iuser_id, f"{text}", keyboard, attachment)
    imsg_text, iuser_id = listen()
    result = imsg_text.lower()
    return result

# функция которая получает список фото


def photos_get(owner_id, photo_ids=None, album_id='profile', extended=1):
    resp = vk_user.method('photos.get',
                          {'owner_id': owner_id, 'photo_ids': photo_ids, 'album_id': album_id, 'extended': extended})
    return resp

# функция которая задает условия для остановки цикла


def condition(num, f=None, t=None):
    try:
        a = int(num)
        if f is not None and t is not None:
            if a >= f and a <= t:
                return False
            else:
                return True
        else:
            return False
    except ValueError:
        return True

# функция которая отдает город по текстовому названию


def database_getcities(city):
    resp = vk_user.method('database.getCities', {'country_id': 1, 'q': city})
    list_city = []
    for o in resp['items']:
        title = o["title"]

        if title.lower() == city.lower():
            return False, int(o["id"])
        else:
            list_city.append(title)
    if len(list_city) < 15:
        return True, f"уточните поиск, возможные значения:  {list_city}"
    else:
        return True, f"Найдено {resp['count']} городов, уточните поиск"

# функция которая добавляет пользователя в БД like


def my_like(user_id, link=False):
    user_all = select_db(what="like_user_id", froom="people_like", wherer="user_id", val=user_id, fet=True)
    list_like = []

    if link:
        for user in user_all:
            list_like.append(user[0])

        lis = ""
        for u in list_like:
            lis += f"http://vk.com/id{u} \n"
        write_msg(user_id, f"Ваши избранные анкеты \n{lis}")

    for user in user_all:
        list_like.append(user[0])
    return list_like

# функция которая добавляет пользователя в БД dizlike


def dizlike(user_id, link=False):
    user_all = select_db(what="like_user_id", froom="people_dislike", wherer="user_id", val=user_id, fet=True)
    list_dislike = []

    if link:
        for user in user_all:
            list_dislike.append(user[0])

        lis = ""
        for u in list_dislike:
            lis += f"http://vk.com/id{u} \n"
        write_msg(user_id, f"Ваши просмотренные анкеты \n{lis}")

    for user in user_all:
        list_dislike.append(user[0])
    return list_dislike

# функция которая вычисляет количество лет


def calculate_age(born):
    date_formatter = "%d.%m.%Y"
    born = datetime.strptime(born, date_formatter)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
