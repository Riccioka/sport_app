import jwt
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash
from database import execute_query
from config import SECRET_KEY
#
from flask import session
#

def generate_token(user_id):
    expiration = datetime.utcnow() + timedelta(days=1)
    payload = {'user_id': user_id, 'exp': expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded['user_id']
    except jwt.ExpiredSignatureError:
        return "expired"
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        if not token:
            return jsonify({'status': 401, 'message': 'Token is required'}), 401

        user_id = decode_token(token)
        if user_id == "expired":
            return jsonify({'status': 401, 'message': 'Token expired'}), 401
        if user_id is None:
            return jsonify({'status': 401, 'message': 'Invalid token'}), 401

        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated

def init_auth_routes(app):
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = execute_query('SELECT id, password FROM users WHERE email = %s', (email,))
        if user and check_password_hash(user[1], password):
            token = generate_token(user[0])
            return jsonify({'status': 200, 'message': 'Login successful', 'token': token})
        return jsonify({'status': 401, 'message': 'Invalid credentials'})

    @app.route('/user', methods=['GET'])
    @token_required
    def get_user_data():
        user_id = request.user_id
        user = execute_query('SELECT * FROM users WHERE id = %s', (user_id,))

        if user:
            user_data = {
                'id': user[0],
                'surname': user[1],
                'name': user[2],
                'midname': user[3],
                'email': user[4],
                'age': user[6],
                'gender': user[7],
                'height': user[8],
                'weight': user[9],
                'points': user[10],
                'team_id': user[11]
            }

            return jsonify({'status': 200, 'user_data': user_data})
        return jsonify({'status': 404, 'message': 'User not found'})

    @app.route('/register', methods=['POST'])
    def register():
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

            password_hash = generate_password_hash(password)
            execute_query('INSERT INTO users (surname, name, midname, email, password) VALUES (%s, %s, %s, %s, %s)',
                          (surname, name, midname, email, password), insert=True)

            return jsonify({'status': 200, 'message': 'User registered successfully'})
        except Exception as e:
            print("Error inserting data:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/user/get_hello_status', methods=['GET'])
    @token_required
    def get_hello_status():
        user_id = request.user_id
        try:
            f_hello = execute_query('SELECT f_hello FROM users WHERE id = %s', (user_id,))

            if f_hello:
                return jsonify({'status': 200, 'f_hello': f_hello[0]})
            return jsonify({'status': 404, 'message': 'User not found'})
        except Exception as e:
            print("Error fetching data:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/user/update_f_hello', methods=['POST'])
    @token_required
    def update_f_hello():
        user_id = request.user_id
        try:
            execute_query('UPDATE users SET f_hello = %s WHERE id = %s', (True, user_id), update=True)
            return jsonify({'status': 200, 'message': 'f_hello updated successfully'})
        except Exception as e:
            print("Error updating data:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})
