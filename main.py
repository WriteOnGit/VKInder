import vk_api
import key
import urllib3
import sqlite3 as sl
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# token = key.group_token
# vk = vk_api.VkApi(token=token)
# longpoll = VkLongPoll(vk)
#
# connect = sl.connect('vkinder.db')
# cursor = connect.cursor()
#
#
# def user_get(user_id):
#     status = vk.method('users.get', {'user_id': user_id, 'fields':'bdate,city,photo_max_orig'})
#     print(status)
#     return status
# # i = user_get(52445897)
# # print(i[0]["bdate"])
# # print(i[0]["city"]["title"])
#
# def write_msg(user_id, message,keyboard=None):
#     post = {
#         'user_id': user_id,
#         'message': message,
#         'random_id': randrange(10 ** 7)
#     }
#     if keyboard != None:
#         post["keyboard"] = keyboard.get_keyboard()
#     else:
#         post =post
#     vk.method('messages.send', post)
#
# for event in longpoll.listen():
#     if event.type == VkEventType.MESSAGE_NEW:
#
#         if event.to_me:
#             request = event.text
#
#             if request == "Начать":
#                 info = user_get(event.user_id)
#                 name = info[0]['first_name']
#
#                 reg = VkKeyboard()
#                 reg.add_openlink_button("Зарегистрироваться","https://oauth.vk.com/authorize?client_id=8215675&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.131")
#
#                 write_msg(event.user_id, "Добро пожаловать в VK Tinder! \n"
#                                          "Первый раз? Зарегистрируйтесь \n"
#                                          "Или войдите в систему \n", reg)
#
#                 already_exist = """SELECT user_id FROM users WHERE user_id= ?"""
#                 cursor.execute(already_exist, (event.user_id,))
#                 result = cursor.fetchone()
#
#                 if result is None:
#                     sql = """INSERT INTO users (user_id,user_name,age) VALUES (?,?,?);"""
#                     cursor.execute(sql, (event.user_id, name, 1,))
#                     connect.commit()
#                     write_msg(event.user_id, "УСПЕШНО ЗАРЕГИСТИРОВАЛИСЬ")
#                 else:
#                     write_msg(event.user_id,"УЖЕ ЕСТЬ В СИСТЕМЕ")
#
#
#
#             elif request == "пока":
#                 write_msg(event.user_id, "Пока((")
#             else:
#                 write_msg(event.user_id, "Не поняла вашего ответа...")
#
# def status_get(group_id):
#     status = vk.method('groups.getOnlineStatus', {'group_id': group_id})
#     return status
#
#
# def getTokenPermissions():
#     status = vk.method('groups.getTokenPermissions')
#     return status
#
#
#
# def wall_createComment(message):
#     status = vk.method('wall.createComment', {'owner_id':'-214443877','post_id':1,'from_group':214443877,'message':message})
#     return status

# def users_search(q,count,fields,age_from,age_to):
#     status = vk_user.method('users.search', {'q':q,'count':count,'fields':fields,'age_from':age_from,'age_to':age_to})
#     return status
# print(users_search("Vladislav Suprun", 2,["bdate","country","status"],34,45))


def users_search(age_from,age_to, city, sex, status):
    #sex 1-Ж, 2 -М, 0 - любой
    #status 1- не женат (не замужем), 6 - в активном поиске,
    resp = vk_user.method('users.search', {'age_from':age_from,'age_to':age_to,'city':city,'sex':sex,'status':status})
    return resp

def photos_get(owner_id,photo_ids = None,album_id='profile',extended = 1):

    resp = vk_user.method('photos.get', {'owner_id':owner_id,'photo_ids':photo_ids,'album_id':album_id,'extended':extended})
    return resp


user_token = key.user_token
vk_user = vk_api.VkApi(token=user_token)
vlad = photos_get(1)

popular = { }
for i in vlad['items']:
    #print(i['likes']['count'])
    popular[i['id']] = i['likes']['count']

print(popular)

from collections import Counter
x = Counter(popular)
sorted_popular = x.most_common()
print(sorted_popular)
print(sorted_popular[0][0])
print(photos_get(1,[sorted_popular[0][0]]))

#print(photos_get(1))

