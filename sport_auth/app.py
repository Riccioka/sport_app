from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS

import re
import psycopg2

from flask_cors import cross_origin


app = Flask(__name__)
CORS(app)
app.secret_key = 'qwerty'

def get_db_connection():
    return psycopg2.connect(database="sport_auth", user="postgres", password="pilot", host="localhost", port="5432")

def execute_query(query, args=None, fetchall=False):
    conn = get_db_connection()
    cur = conn.cursor()
    if args:
        cur.execute(query, args)
    else:
        cur.execute(query)
    result = cur.fetchall() if fetchall else cur.fetchone()
    conn.commit()
    conn.close()
    return result

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
# @cross_origin(origin='http://127.0.0.1:3000', headers=['Content-Type', 'Authorization']) # why
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        print(email, password)

        user = execute_query('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        if user:
            session['loggedin'] = True
            session['id'] = user[0]
            session['surname'] = user[1]
            session['name'] = user[2]
            session['email'] = user[4]
            return jsonify({'status': 200})
        else:
            return jsonify({'status':0})
    if request.method == 'GET':
        username = session['name']
        return jsonify({'message': 'Received data successfully', 'name': 'name'}) #username

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        execute_query('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email,))
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)

@app.route('/index')
def index():
    if 'loggedin' in session:
        user_id = session.get('id')
        user_data = execute_query('SELECT age, height, weight FROM users WHERE id = %s', (user_id,))
        if user_data:
            age, height, weight = user_data
        else:
            age, height, weight = None, None, None
        return render_template('index.html', age=age, height=height, weight=weight)
    return redirect(url_for('login'))


@app.route('/edit_person_data', methods=['GET', 'POST'])
def edit_person_data():
    msg = ''
    if 'loggedin' in session:
        user_id = session.get('id')
        user_data = execute_query('SELECT age, height, weight FROM users WHERE id = %s', (user_id,))
        if not user_data:
            return 'User data not found', 404
        age, height, weight = user_data
        if request.method == 'POST':
            age_form = request.form.get('age')
            height_form = request.form.get('height')
            weight_form = request.form.get('weight')

            age = int(age_form)
            height = int(height_form)
            weight = int(weight_form)

            execute_query('UPDATE users SET age = %s, height = %s, weight = %s WHERE id = %s', (age, height, weight, user_id,))

    return jsonify({'age':9, 'height':height, 'weight':weight})

if __name__ == '__main__':
    app.run(debug=True)
