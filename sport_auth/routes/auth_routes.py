from flask import jsonify, request, session
from database import execute_query

session = {}
def init_auth_routes(app):
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
            session['midname'] = user[3]
            session['email'] = user[4]
            session['password'] = user[5]
            session['age'] = user[6]
            session['gender'] = user[7]
            session['height'] = user[8]
            session['weight'] = user[9]
            session['points'] = user[10]
            session['team_id'] = user[11]

            return jsonify({'status': 200, 'message': 'Login successful'})
        else:
            return jsonify({'status': 401, 'message': 'Invalid credentials'})

    # @app.route('/logout', methods=['GET'])
    # def logout():
    #     session.pop('loggedin', None)
    #     session.pop('id', None)
    #     session.pop('name', None)
    #     return jsonify({'status': 200, 'message': 'Logged out successfully'})

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


    @app.route('/get_hello_status', methods=['GET'])
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
                return jsonify({'status': 500, 'message': str(e)})
        else:
            return jsonify({'status': 401, 'message': 'User not logged in'})

    @app.route('/update_f_hello', methods=['POST'])
    def update_f_hello():
        if 'loggedin' in session:
            user_id = session['id']
            try:
                execute_query('UPDATE users SET f_hello = %s WHERE id = %s', (True, user_id), insert=True)
                return jsonify({'status': 200, 'message': 'f_hello updated successfully'})
            except Exception as e:
                print("Error updating data:", e)
                return jsonify({'status': 500, 'message': str(e)})
        else:
            return jsonify({'status': 401, 'message': 'User not logged in'})