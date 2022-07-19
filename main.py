"""
Импортируем нужные библиотеки
vk_api https://vk-api.readthedocs.io/ документация (импорт для работы с событиями и чатбот кнопками)
key - в файле 2 параметра group_token и user_token
urllib3 - чтобы обойти ошибку сертификатов
sqlite3 - используем простую БД - файл для записи результатов
random - для генерации случайного значения

"""
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import key
import urllib3
import sqlite3 as sl
from random import randrange
from collections import Counter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

""" Подключаемся к БД, если файла нет будет создана"""
connect = sl.connect('vkinder.db')
cursor = connect.cursor()
create = """
CREATE TABLE IF NOT EXISTS users (
user_id not null primary key unique,
user_name varchar(40) not null);

CREATE TABLE IF NOT EXISTS search (
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
user_id INTEGER not null REFERENCES users(user_id), 
age_from INTEGER not null,
age_to INTEGER not null,
sex INTEGER not null,
city INTEGER not null, 
status INTEGER not null
);

CREATE TABLE IF NOT EXISTS result_search (
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
user_id INTEGER not null REFERENCES users(user_id),
search_id INTEGER not null REFERENCES id(search),
search_user_name varchar(40) not null,
search_user_id INTEGER not null
);

CREATE TABLE IF NOT EXISTS people_like (
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
user_id INTEGER not null REFERENCES users(user_id),
like_user_id INTEGER not null
);

CREATE TABLE IF NOT EXISTS people_dislike (
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
user_id INTEGER not null REFERENCES users(user_id),
like_user_id INTEGER not null
);
"""
cursor.executescript(create)
connect.commit()

""" 
 присваиваем переменной токен группы
 создаем 2 экземляра класса vk.api и передаем в него токен (группы и user) 

"""

vk_group = vk_api.VkApi(token=key.group_token)
longpoll = VkLongPoll(vk_group)

vk_user = vk_api.VkApi(token=key.user_token)


def select_db(what, froom, wherer, val, fet=False):
    try:
        if isinstance(wherer, tuple):
            sql_z = f"SELECT {what} FROM {froom}  WHERE {wherer[0]} = {val[0]} AND {wherer[1]} = {val[1]}"
            print(sql_z)
        else:
            sql_z = f"SELECT {what} FROM {froom}  WHERE {wherer} = {val}"
            print(sql_z)
        cursor.execute(sql_z)
        if fet is False:
            req_sql = cursor.fetchone()
        else:
            req_sql = cursor.fetchall()

        return req_sql
    except Exception as exce:
        print("Ошибка базы данных при SELECT данных")
        print(exce)


def insert_db(where, col_name, value):
    try:
        sql_id = f"INSERT INTO {where} {col_name} VALUES {value};"
        print(sql_id)
        cursor.execute(sql_id)
        connect.commit()
    except Exception as exce:
        print("Ошибка базы данных при INSERT данных")
        print(exce)


def user_get(user_id):
    status = vk_group.method('users.get', {'user_id': user_id, 'fields': 'bdate,city,photo_max_orig'})
    return status


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


def listen():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                text = event.text
                return text.lower(), event.user_id


def user_in_bd(user_id):
    already_exist = """SELECT user_id FROM users WHERE user_id= ?"""
    cursor.execute(already_exist, (user_id,))
    result = cursor.fetchone()
    return result


def menu(user_id, user_name):
    if user_in_bd(user_id) is None:
        reg = VkKeyboard(one_time=True)
        reg.add_button('Регистрация', VkKeyboardColor.POSITIVE)
        reg.add_line()
        reg.add_openlink_button("Получить токен",
                                f"https://oauth.vk.com/authorize?client_id={key.IDApps}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=&response_type=token&v=5.131")
        write_msg(user_id,
                  f"{user_name}, добро пожаловать в VK Tinder! \n Первый раз? Нажмите на кнопку Регистрация \n", reg)

    else:
        keyboard = VkKeyboard(one_time=False)
        buttons = ['Поиск', ' MY LIKE', 'MY DISLIKE', 'Стоп']
        buttons_color = [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE,
                         VkKeyboardColor.PRIMARY]
        for btn, btn_color in zip(buttons, buttons_color):
            keyboard.add_button(btn, btn_color)
        write_msg(user_id, f"{user_name}, приступим к поиску", keyboard)


def users_search(iage_from, iage_to, icity, isex, istatus):
    resp = vk_user.method('users.search',
                          {'age_from': iage_from, 'age_to': iage_to, 'city': icity, 'sex': isex, 'status': istatus})
    return resp


def question(iuser_id, text, keyboard=None, attachment=None):
    write_msg(iuser_id, f"{text}", keyboard, attachment)
    imsg_text, iuser_id = listen()
    result = imsg_text.lower()
    return result


def photos_get(owner_id, photo_ids=None, album_id='profile', extended=1):
    resp = vk_user.method('photos.get',
                          {'owner_id': owner_id, 'photo_ids': photo_ids, 'album_id': album_id, 'extended': extended})
    return resp


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


if __name__ == '__main__':
    while True:
        msg_text, user_id = listen()
        info = user_get(user_id)
        user_name = info[0]["first_name"]

        if msg_text == 'начать':
            menu(user_id, user_name)

        if msg_text == 'регистрация' and user_in_bd(user_id) is None:
            sql = """INSERT INTO users (user_id,user_name) VALUES (?,?);"""
            cursor.execute(sql, (user_id, user_name,))
            connect.commit()
            menu(user_id, user_name)

        if msg_text == 'поиск' and user_in_bd(user_id):
            try:
                age_from = question(user_id, "Укажите возраст с: ")
                while condition(age_from, 18, 100):
                    age_from = question(user_id, "Укажите возраст с: ")

                age_to = question(user_id, "Укажите возраст до:")
                while condition(age_to, int(age_from), 100):
                    age_to = question(user_id, "Укажите возраст до:")

                city = question(user_id, "Укажите город")
                search_city_status, city_id = database_getcities(city)
                while search_city_status:
                    city = question(user_id, f"Укажите город {city_id}")
                    search_city_status, city_id = database_getcities(city)

                sex = question(user_id, "Укажите пол 1-Ж, 2 - М, 0 - неважно")
                while condition(sex, 0, 2):
                    sex = question(user_id, "Укажите пол 1-Ж, 2 - М, 0 - неважно")

                status = question(user_id, "Укажите статус \n"
                                           "1- не женат (не замужем),\n"
                                           " 2 — встречается,\n"
                                           " 3 — помолвлен(-а),\n"
                                           "4 — женат (замужем),\n"
                                           "5 — всё сложно,\n"
                                           "6 - в активном поиске,\n"
                                           "7 — влюблен(-а),\n"
                                           "8 — в гражданском браке.\n")

                while condition(status, 1, 8):
                    status = question(user_id, "Укажите статус \n"
                                               "1- не женат (не замужем),\n"
                                               "2 — встречается,\n"
                                               "3 — помолвлен(-а),\n"
                                               "4 — женат (замужем),\n"
                                               "5 — всё сложно,\n"
                                               "6 - в активном поиске\n"
                                               "7 — влюблен(-а),\n"
                                               "8 — в гражданском браке.\n"

                                      )

                req = users_search(int(age_from), int(age_to), int(city_id), int(sex), int(status))

                insert_db(where="search", col_name=("user_id", "age_from", "age_to", "city", "sex", "status"),
                          value=(user_id, int(age_from), int(age_to), int(city_id), int(sex), int(status)))
                write_msg(user_id, f"Ищем: c {age_from} по {age_to} в городе {city}. Найдено {req['count']}")
                search_id = select_db(what="MAX(id)", froom="search", wherer="user_id", val=user_id, fet=False)

                for el in req['items']:
                    if el['is_closed'] is False:
                        insert_db(where="result_search",
                                  col_name=("user_id", "search_id", "search_user_name", "search_user_id"),
                                  value=(user_id, int(search_id[0]), el['first_name'], el['id']))

                user_all = select_db(what="id,search_user_id", froom="result_search",
                                     wherer=tuple(('search_id', 'user_id')), val=(search_id[0], user_id), fet=True)

                print(user_all)

                select_user_like = my_like(user_id)
                select_user_dizlike = dizlike(user_id)

                for num_id, us_id in user_all:
                    if us_id not in select_user_like and us_id not in select_user_dizlike:
                        user_photo = photos_get(us_id)
                        popular = {}
                        for i in user_photo['items']:
                            popular[i['id']] = i['likes']['count'] + i['comments']['count']

                        x = Counter(popular)
                        sorted_popular = x.most_common()

                        if len(sorted_popular) != 0:

                            if len(sorted_popular) < 3:
                                att = ''
                                for id, likes in sorted_popular:
                                    att += f'photo{us_id}_{id},'
                            else:
                                att = f'photo{us_id}_{sorted_popular[0][0]},photo{us_id}_{sorted_popular[1][0]},photo{us_id}_{sorted_popular[2][0]},'

                        else:
                            print("Нет фото")

                        kes = VkKeyboard(inline=True)
                        kes.add_button("Да", VkKeyboardColor.POSITIVE)
                        kes.add_button("Нет", VkKeyboardColor.NEGATIVE)

                        like = question(user_id,
                                        f"Пользователь по поиску {search_id} номер анкеты {num_id} \n Нравится? https://vk.com/id{us_id} ",
                                        kes, att)
                        if like == "да":
                            insert_db(where="people_like", col_name=("user_id", "like_user_id"), value=(user_id, us_id))


                        elif like == "нет":
                            insert_db(where="people_dislike", col_name=("user_id", "like_user_id"),
                                      value=(user_id, us_id))

                        elif like == "стоп":
                            break

                        elif like == 'my like':
                            my_like(user_id, True)
                            break


                        elif like == 'my dislike':
                            dizlike(user_id, True)
                            break

                    else:
                        continue
            except Exception as exc:
                write_msg(user_id, "Что-то пошло не так, попробуйте снова ")
                print(exc)

        if msg_text == 'my like' and user_in_bd(user_id):
            my_like(user_id, True)

        if msg_text == 'my dislike' and user_in_bd(user_id):
            dizlike(user_id, True)
