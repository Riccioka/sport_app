from flask import Flask, jsonify, request, session
from database import execute_query

session = {}
def init_auth_routes(app):
    @app.route('/user', methods=['POST'])
    #@app.route('/<int:user_id>', methods=['GET'])
    def get_user_data():
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')
            user = execute_query('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))

            #user = execute_query('SELECT * FROM users WHERE id = %s', (user_id,))

            if user:
                session['loggedin'] = True
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
            else:
                return jsonify({'status': 404, 'message': 'User not found'})
        except Exception as e:
            print("Error fetching user data:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    #@app.route('/user/register', methods=['POST'])
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

            execute_query('INSERT INTO users (surname, name, midname, email, password) VALUES (%s, %s, %s, %s, %s)',
                          (surname, name, midname, email, password), insert=True)

            return jsonify({'status': 200, 'message': 'User registered successfully'})
        except Exception as e:
            print("Error inserting data:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/user/get_hello_status', methods=['GET'])
    def get_hello_status():
        if 'loggedin' in session:
            user_id = session['id']
        try:
            f_hello = execute_query('SELECT f_hello FROM users WHERE id = %s', (user_id,))

            if f_hello:
                return jsonify({'status': 200, 'f_hello': f_hello[0]})
            else:
                return jsonify({'status': 404, 'message': 'User not found'})
        except Exception as e:
            print("Error fetching data:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/user/update_f_hello', methods=['POST'])
    def update_f_hello():
        if 'loggedin' in session:
            user_id = session['id']
        try:
            execute_query('UPDATE users SET f_hello = %s WHERE id = %s', (True, user_id), update=True)
            return jsonify({'status': 200, 'message': 'f_hello updated successfully'})
        except Exception as e:
            print("Error updating data:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})
