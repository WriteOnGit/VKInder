import sqlite3 as sl


def bd_create():
    """ Подключаемся к БД, если файла нет будет создана"""
    connect = sl.connect('vkinder.db')
    cursor = connect.cursor()
    create = """
    CREATE TABLE IF NOT EXISTS users (
    user_id not null primary key unique,
    user_name varchar(40) not null,
    age INTEGER not null,
    sex INTEGER not null,
    city INTEGER not null,
    relation INTEGER not null);
    
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
