from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import psycopg2
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


@app.route('/index')
def index():
    if 'loggedin' in session:
        user_id = session.get('id')
        user_data = execute_query('SELECT name, age, height, weight FROM users WHERE id = %s', (user_id,))
        if user_data:
            name, age, height, weight = user_data
            print(name)
            return jsonify({'status': 200, 'name': name, 'age': age, 'height': height, 'weight': weight})
        else:
            return jsonify({'status': 404, 'message': 'User data not found'})
    return jsonify({'status': 401, 'message': 'Unauthorized'})


@app.route('/edit_person_data', methods=['POST'])
def edit_person_data():
    # if 'loggedin' in session:
    #     user_id = session.get('id')
    #     user_data = execute_query('SELECT age, height, weight FROM users WHERE id = %s', (user_id,))
    #     if not user_data:
    #         return jsonify({'status': 404, 'message': 'User data not found'})
    #     age, height, weight = user_data
    #     if request.method == 'POST':
    #         age_form = request.form.get('age')
    #         height_form = request.form.get('height')
    #         weight_form = request.form.get('weight')
    #
    #         age = int(age_form)
    #         height = int(height_form)
    #         weight = int(weight_form)
    #
    #         execute_query('UPDATE users SET age = %s, height = %s, weight = %s WHERE id = %s', (age, height, weight, user_id,))
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


@app.route('/create_post', methods=['POST']) # не готово
def create_post():
    if 'loggedin' in session:
        author_id = session.get('id')
        data = request.json
        time_of_publication = datetime.datetime.now()
        status = data.get('status') #false пока не изменен пост
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

# def вывод ИМТ при известных рост вес (вес/рост/рост * 10000)

if __name__ == '__main__':
    app.run(debug=True)
