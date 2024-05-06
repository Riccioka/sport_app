from flask import jsonify, request, render_template
from routes.auth_routes import session
from database import execute_query

def init_user_routes(app):
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
