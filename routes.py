import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import subprocess
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_db_connection():
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'taitoulv_fr.db'))
    conn.row_factory = sqlite3.Row
    return conn

def is_valid_password(password):
    import re
    return re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful')
            return redirect(url_for('class_selection'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not is_valid_password(password):
            flash('密码至少为8位且包含数字和字母')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Registration successful')
        except sqlite3.IntegrityError:
            flash('Username already exists')
        finally:
            conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']

        if not is_valid_password(new_password):
            flash('密码至少为8位且包含数字和字母')
            return redirect(url_for('reset_password'))

        hashed_password = generate_password_hash(new_password)

        conn = get_db_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

            if user:
                conn.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, username))
                conn.commit()
                flash('Password reset successful')
            else:
                flash('Username not found')
        finally:
            conn.close()

        return redirect(url_for('login'))
    return render_template('reset_password.html')

def count_objects(image_path):
    import matlab.engine
    eng = matlab.engine.start_matlab()
    num_objects = eng.face_collection(image_path)
    eng.quit()
    return num_objects

def rate_cal(class_room, course_time):
    face = 0
    real_person = 0

    img_path = os.path.join(BASE_DIR, 'faces', f"{class_room}{course_time}.jpg")
    print(f"Image path: {img_path}")
    img = cv2.imread(img_path)
    if img is None:
        return None, None, "Error: Image not found."

    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    classfier = cv2.CascadeClassifier(os.path.join(BASE_DIR, 'haarcascade_frontalface_alt2.xml'))
    faceRects = classfier.detectMultiScale(grey, scaleFactor=1.2, minNeighbors=3, minSize=(32, 32))
    face = len(faceRects)
    real_person = count_objects(img_path)
    print(f"Real person count: {real_person}")
    right = max(real_person, face)

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT c.capacity
    FROM class_times ct
    JOIN classrooms c ON ct.class_room_id = c.id
    WHERE c.name = ? AND ct.time = ?
    """
    cursor.execute(query, (class_room, course_time))
    result = cursor.fetchone()

    if result:
        capacity = result[0]
        print(f"Classroom capacity: {capacity}")
    else:
        capacity = 0

    conn.close()

    if real_person > 0:
        rate = face / real_person
    else:
        rate = 0

    if capacity > 0:
        attendance_rate = right / capacity
    else:
        attendance_rate = 0

    print(f"Head-up rate: {rate}, Attendance rate: {attendance_rate}")
    return rate, attendance_rate, None

@app.route('/class_selection', methods=['GET', 'POST'])
def class_selection():
    class_room = None
    course_time = None
    image = None
    head_up_rate = None
    attendance_rate = None
    suggestion = None

    if request.method == 'POST':
        class_room = request.form['class_room']
        course_time = request.form['course_time']
        action = request.form['action']

        if action == 'confirm':
            image = f"{class_room}{course_time}.jpg"

        if action == 'show_result':
            image = f"{class_room}{course_time}.jpg"
            head_up_rate, attendance_rate, error = rate_cal(class_room, course_time)
            if error:
                flash(error)
                return redirect(url_for('class_selection'))

            if head_up_rate < 0.4:
                suggestion = "抬头率低，需要督促"
            elif head_up_rate > 0.9:
                suggestion = "抬头率较高，值得表扬"
            else:
                suggestion = "抬头率处于正常范围，学习状态良好"

            if attendance_rate < 0.6:
                suggestion += " 到课率低，需要督促学生到课"
            elif attendance_rate > 0.9:
                suggestion += " 到课率较高，值得表扬"
            else:
                suggestion += " 到课率处于正常范围，出勤情况良好"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM classrooms")
    classrooms = cursor.fetchall()
    cursor.execute("SELECT time FROM class_times")
    class_times = cursor.fetchall()
    conn.close()

    return render_template('classroom_selection.html', classrooms=classrooms, class_times=class_times,
                           class_room=class_room, course_time=course_time, image=image,
                           head_up_rate=head_up_rate, attendance_rate=attendance_rate, suggestion=suggestion)

@app.route('/faces/<filename>')
def faces(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'faces'), filename)


if __name__ == '__main__':
    app.run(debug=True)