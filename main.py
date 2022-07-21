from mydef import *
from bd import bd_create
from collections import Counter

if __name__ == '__main__':

    bd_create()

    while True:
        msg_text, user_id = listen()
        info = user_get(user_id)

        user_id = info[0].get("id")
        user_name = info[0].get("first_name")

        if msg_text == 'начать':
            menu(user_id, user_name)

        if msg_text == 'регистрация' and user_in_bd(user_id) is None:

            bdate = info[0].get("bdate")
            sex = info[0].get("sex")  # 1- ж, 2 - м
            city = info[0].get("city").get("id")
            city_name = info[0].get("city").get("title")
            relation = info[0].get("relation")

            if len(bdate) < 5 or bdate is None:
                age = question(user_id, "Сколько Вам лет?")
                while condition(age, 18, 100):
                    age = question(user_id, "Введите число от 18 до 100")

            else:
                age = calculate_age(bdate)

            if city is None:
                city = question(user_id, "Укажите город")
                search_city_status, city_id = database_getcities(city)
                while search_city_status:
                    city = question(user_id, f"Укажите город {city_id}")
                    search_city_status, city_id = database_getcities(city)

            if relation is None:
                relation = question(user_id, "Укажите статус \n"
                                           "1- не женат (не замужем),\n"
                                           " 2 — встречается,\n"
                                           " 3 — помолвлен(-а),\n"
                                           "4 — женат (замужем),\n"
                                           "5 — всё сложно,\n"
                                           "6 - в активном поиске,\n"
                                           "7 — влюблен(-а),\n"
                                           "8 — в гражданском браке.\n")

                while condition(relation, 1, 8):
                    relation = question(user_id, "Укажите Ваш статус \n"
                                               "1- не женат (не замужем),\n"
                                               "2 — встречается,\n"
                                               "3 — помолвлен(-а),\n"
                                               "4 — женат (замужем),\n"
                                               "5 — всё сложно,\n"
                                               "6 - в активном поиске\n"
                                               "7 — влюблен(-а),\n"
                                               "8 — в гражданском браке.\n")

            insert_db(where="users", col_name=("user_id", "user_name", "age", "sex", "city", "relation"),
                      value=(user_id, user_name, int(age), int(sex), int(city), int(relation)))

            menu(user_id, user_name)

        if msg_text == 'поиск' and user_in_bd(user_id):

            keybord_auto = VkKeyboard(one_time=True)
            keybord_auto.add_button('ручной', VkKeyboardColor.POSITIVE)
            keybord_auto.add_button('автопоиск', VkKeyboardColor.POSITIVE)

            auto = question(user_id, "ручной или автопоиск?", keybord_auto)
            menu(user_id, user_name)

            try:
                if auto == "ручной":
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
                    same_search = select_db(what="COUNT(id)", froom="search",
                                            wherer=tuple(('age_from', 'age_to', 'sex', 'city', 'status')),
                                            val=(int(age_from), int(age_to), int(city_id), int(sex), int(status)), fet=False)

                    req = users_search(int(age_from), int(age_to), int(city_id), int(sex), int(status), int(same_search[0])*20)

                    insert_db(where="search", col_name=("user_id", "age_from", "age_to", "city", "sex", "status"),
                              value=(user_id, int(age_from), int(age_to), int(city_id), int(sex), int(status)))
                    write_msg(user_id, f"Ищем: c {age_from} по {age_to} в городе {city}. Найдено {req['count']}")
                    search_id = select_db(what="MAX(id)", froom="search", wherer="user_id", val=user_id, fet=False)

                else:
                    select_user = select_db("*", "users", "user_id", user_id, fet=False)
                    age = select_user[2]
                    sex = select_user[3]
                    city = select_user[4]
                    relation = select_user[5]

                    if sex == 2:
                        sex = 1
                    else:
                        sex = 2

                    same_search = select_db(what="COUNT(id)", froom="search",
                              wherer=tuple(('age_from', 'age_to', 'sex', 'city', 'status')), val=(int(age), int(age), int(city), int(sex), int(relation)), fet=False)

                    req = users_search(int(age), int(age), int(city), int(sex), int(relation), int(same_search[0])*20)

                    insert_db(where="search", col_name=("user_id", "age_from", "age_to", "city", "sex", "status"),
                              value=(user_id, int(age), int(age), int(city), int(sex), int(relation)))
                    write_msg(user_id, f"Автопоиск, возможно Вам понравится. Найдено {req['count']}")
                    search_id = select_db(what="MAX(id)", froom="search", wherer="user_id", val=user_id, fet=False)

                for el in req['items']:
                    if el['is_closed'] is False:
                        insert_db(where="result_search",
                                  col_name=("user_id", "search_id", "search_user_name", "search_user_id"),
                                  value=(user_id, int(search_id[0]), el['first_name'], el['id']))

                user_all = select_db(what="id,search_user_id", froom="result_search",
                                     wherer=tuple(('search_id', 'user_id')), val=(search_id[0], user_id), fet=True)

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
                            att = False

                        kes = VkKeyboard(inline=True)
                        kes.add_button("Да", VkKeyboardColor.POSITIVE)
                        kes.add_button("Нет", VkKeyboardColor.NEGATIVE)

                        like = question(user_id,
                                        f"Нравится? https://vk.com/id{us_id} ",
                                        kes, att)
                        if like == "да":
                            insert_db(where="people_like", col_name=("user_id", "like_user_id"), value=(user_id, us_id))

                        elif like == "стоп" or like == "поиск":
                            break

                        elif like == 'my like':
                            my_like(user_id, True)
                            break

                        elif like == 'my dislike':
                            dizlike(user_id, True)
                            break
                        else:
                            insert_db(where="people_dislike", col_name=("user_id", "like_user_id"),
                                      value=(user_id, us_id))
                    else:
                        continue
            except Exception as exc:
                write_msg(user_id, "Что-то пошло не так, попробуйте снова ")
                print(exc)

        if msg_text == 'my like' and user_in_bd(user_id):
            my_like(user_id, True)

        if msg_text == 'my dislike' and user_in_bd(user_id):
            dizlike(user_id, True)
