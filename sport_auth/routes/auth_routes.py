from flask import jsonify, request, session
# from database import execute_query

session = {}
def init_auth_routes(app):
    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        email = data.get('email')
        password = data.get('password')

        print(email, password)
        if (email == "k@k.k") and (password == "kkk"):
            session['loggedin'] = True
            session['id'] = 1
            session['surname'] = "Кузин"
            session['name'] = "Олег"
            session['midname'] = "Владимирович"
            session['email'] = "k@k.k"
            session['password'] = "kkk"
            session['age'] = 23
            session['gender'] = "М"
            session['height'] = 180
            session['weight'] = 70
            session['points'] = 94
            session['team_id'] = 1

            return jsonify({'status': 200, 'message': 'Login successful'})
        else:
            return jsonify({'status': 401, 'message': 'Invalid credentials'})


    @app.route('/get_hello_status', methods=['GET'])
    def get_hello_status():
        if 'loggedin' in session:
            f_hello = "t"
            return jsonify({'status': 200, 'f_hello': f_hello[0]})
        else:
            return jsonify({'status': 401, 'message': 'User not logged in'})

    @app.route('/update_f_hello', methods=['POST'])
    def update_f_hello():
        return jsonify({'status': 200, 'message': 'f_hello updated successfully'})