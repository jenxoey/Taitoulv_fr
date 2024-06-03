import sqlite3
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
def create_tables():
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'taitoulv_fr.db'))
    c = conn.cursor()

    # 创建用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL)''')

    # 创建教室表
    c.execute('''CREATE TABLE IF NOT EXISTS classrooms (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE NOT NULL)''')

    # 创建课程时间表，添加size列表示课堂人数
    c.execute('''CREATE TABLE IF NOT EXISTS class_times (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 class_room_id INTEGER NOT NULL,
                 time TEXT NOT NULL,
                 photo TEXT,
                 capacity INTEGER NOT NULL DEFAULT 4,
                 FOREIGN KEY (class_room_id) REFERENCES classrooms (id))''')

    conn.commit()

    # 插入初始用户数据
    initial_user = ('111', 'abc123456')
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', initial_user)

    # 插入教室数据
    classrooms = [
        'N101', 'N102', 'N103', 'N104', 'N105', 'N106', 'N107', 'N108',
        'N109', 'N110', 'N111', 'N112', 'N113', 'N114', 'N115', 'N116',
        'N201', 'N202', 'N203', 'N204'
    ]

    for classroom in classrooms:
        c.execute('INSERT INTO classrooms (name) VALUES (?)', (classroom,))

    # 插入课程时间数据，默认课堂人数为4，N204为5
    class_times = [
        ('N101', 'Monday_1_2', 4), ('N102', 'Monday_3_4', 4), ('N103', 'Monday_5_6', 4),
        ('N104', 'Monday_7_8', 4), ('N105', 'Tuesday_1_2', 4), ('N106', 'Tuesday_3_4', 4),
        ('N107', 'Tuesday_5_6', 4), ('N108', 'Tuesday_7_8', 4), ('N109', 'Wednesday_1_2', 4),
        ('N110', 'Wednesday_3_4', 4), ('N111', 'Wednesday_5_6', 4), ('N112', 'Wednesday_7_8', 4),
        ('N113', 'Thursday_1_2', 4), ('N114', 'Thursday_3_4', 4), ('N115', 'Thursday_5_6', 4),
        ('N116', 'Thursday_7_8', 4), ('N201', 'Friday_1_2', 4), ('N202', 'Friday_3_4', 4),
        ('N203', 'Friday_5_6', 4), ('N204', 'Friday_7_8', 10)
    ]

    for room, time, size in class_times:
        photo = f'{room}{time}.jpg'
        c.execute(
            'INSERT INTO class_times (class_room_id, time, photo, size) VALUES ((SELECT id FROM classrooms WHERE name = ?), ?, ?, ?)',
            (room, time, photo, size))

    conn.commit()
    conn.close()

create_tables()
