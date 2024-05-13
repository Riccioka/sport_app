from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import re
import psycopg2
import random
import string
import datetime


app = Flask(__name__)
CORS(app)
app.secret_key = 'qwerty'


def get_db_connection():
    return psycopg2.connect(database="sport_auth", user="postgres", password="pilot", host="localhost", port="5432")

def execute_query(query, args=None, fetchall=False, insert=False):
    conn = get_db_connection()
    cur = conn.cursor()
    if args:
        cur.execute(query, args)
    else:
        cur.execute(query)

    if insert:
        conn.commit()
        conn.close()
        return None
    else:
        result = cur.fetchall() if fetchall else cur.fetchone()
        conn.close()
        return result

def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


session = {}

@app.route('/')
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = execute_query('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
    if user:
        session['loggedin'] = True
        session['id'] = user[0]
        session['surname'] = user[1]
        session['name'] = user[2]
        session['email'] = user[4]
        return jsonify({'status': 200, 'message': 'Login successful'})
    else:
        return jsonify({'status': 401, 'message': 'Invalid credentials'})


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return jsonify({'status': 200, 'message': 'Logged out successfully'})


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        surname = data.get('surname')
        name = data.get('name')
        midname = data.get('patronymic')
        email = data.get('email')
        password = data.get('password')

        try:
            existing_user = execute_query('SELECT * FROM users WHERE email = %s', (email,), fetchall=True)
            if existing_user:
                return jsonify({'status': 400, 'message': 'Email already exists'})

            execute_query('INSERT INTO users (surname, name, midname, email, password) VALUES (%s, %s, %s, %s, %s)',
                          (surname, name, midname, email, password), insert=True)

            return jsonify({'status': 200, 'message': 'User registered successfully'})
        except Exception as e:
            print("Error inserting data:", e)
            return jsonify({'status': 500, 'message': str(e)})


@app.route('/main', methods=['GET'])
def main():
    if 'loggedin' in session:
        name = session['name']
        return jsonify({'status': 200, 'name': name})
    return jsonify({'status': 401, 'message': 'Unauthorized', 'name': 'test'})


@app.route('/profile')
def profile():
    if 'loggedin' in session:
        surname = session['surname']
        name = session['name']
        age = session['age']
        height = session['height']
        weight = session['weight']
        return render_template({'status': 200, 'surname': surname, 'name': name, 'age': age, 'height': height, 'weight': weight})
    return jsonify({'status': 401, 'message': 'Unauthorized'})


@app.route('/edit_person_data', methods=['POST'])  # не готово
def edit_person_data():
    if 'loggedin' in session:
        user_id = session.get('id')
        data = request.json
        age = data.get('age')
        height = data.get('height')
        weight = data.get('weight')

        try:
            execute_query('UPDATE users SET age = %s, height = %s, weight = %s WHERE id = %s',
                          (age, height, weight, user_id,))
            return jsonify({'status': 200, 'message': 'User data updated successfully'})
        except Exception as e:
            print("Error updating user data:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})
    return jsonify({'status': 401, 'message': 'Unauthorized'})


#создать пост тест на бэк
# def create_post():
#     conn = psycopg2.connect(database="sport_auth", user="postgres", password="pilot", host="localhost", port="5432")
#     cur = conn.cursor()
#
#     try:
#         author_id = 5
#         status = False
#         progress = 100
#         activity_id = 1
#
#         time_of_publication = datetime.datetime.now()
#         databeginning = datetime.datetime.now()
#         dataending = datetime.datetime.now()
#         commentactivity = "Hello"
#
#         cur.execute('INSERT INTO feeds (author_id, time_of_publication, status, progress, databeginning, dataending, activity_id, commentactivity) '
#                     'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
#                     (author_id, time_of_publication, status, progress, databeginning, dataending, activity_id, commentactivity))
#
#         conn.commit()
#         conn.close()
#
#         return {'status': 200, 'message': 'Post created successfully'}
#     except Exception as e:
#         print("Error creating post:", e)
#         return {'status': 500, 'message': 'Internal server error'}


@app.route('/create_post', methods=['POST']) # не готово
def create_post():
    if 'loggedin' in session:
        author_id = session['id']

        data = request.json
        time_of_publication = datetime.datetime.now()
        status = False #false пока не изменен пост
        progress = data.get('progress') #км/ч/шаги
        databeginning = data.get('databeginning')
        dataending = data.get('dataending')
        activity_id = data.get('activity_id')
        commentactivity = data.get('commentactivity')
        proof = data.get('proof')

        try:
            execute_query('INSERT INTO posts (author_id, time_of_publication, status, progress, databeginning, dataending, activity_id, commentactivity, proof) '
                          'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                          (author_id, time_of_publication, status, progress, databeginning, dataending, activity_id, commentactivity, proof), insert=True)
            return jsonify({'status': 200, 'message': 'Post created successfully'})
        except Exception as e:
            print("Error creating post:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})
    return jsonify({'status': 401, 'message': 'Unauthorized'})


if __name__ == '__main__':
    app.run(debug=True)
