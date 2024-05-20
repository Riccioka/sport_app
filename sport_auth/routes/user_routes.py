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

# ФИ, рост, вес, почта, аватарка

    @app.route('/profile', methods=['GET'])
    def profile():
        if 'loggedin' in session:
            user_id = session.get('id')
            try:
                user_profile = execute_query('SELECT * FROM users WHERE id = %s', (user_id,))
                if user_profile:
                    profile_data = {
                        'id': user_profile[0],
                        'lastName': user_profile[1],
                        'firstName': user_profile[2],
                        'email': user_profile[4],
                        'height': user_profile[8],
                        'weight': user_profile[9],
                        # 'activity': [{'type': 'pool', 'color': 'blue', 'time': 16, 'calories': 8500}],  # заглушка для активности
                        # 'team': 1,  # заглушка для команды
                        # 'league': "gold",  # заглушка для лиги
                        # 'avatar': session.get('avatar', 'default_avatar_url')  # заглушка для аватара
                    }
                    print(profile_data)
                    return jsonify({'status': 200, 'profile': profile_data})
                else:
                    return jsonify({'status': 404, 'message': 'User not found'})
            except Exception as e:
                print("Error fetching user profile:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})
        else:
            return jsonify({'status': 401, 'message': 'Unauthorized'})


    # отдельно изменить рост, вес. отдельно аватарка ФИ почта. отдельно прогресс? цель
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

    @app.route('/logout', methods=['POST'])
    def logout():
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('name', None)
        return jsonify({'status': 200, 'message': 'Logged out successfully'})

    @app.route('/delete_account', methods=['DELETE'])
    def delete_account():
        user_id = session.get('id')
        print("id = ", user_id)
        if user_id:
            try:
                print("id 1= ", user_id)
                execute_query('DELETE FROM users WHERE id = %s', (user_id,), delete=True)
                print("id 2= ", user_id)
                session.pop('loggedin', None)
                session.pop('id', None)
                session.pop('name', None)
                return jsonify({'status': 200, 'message': 'Account deleted successfully'})
            except Exception as e:
                return jsonify({'status': 500, 'error': str(e)})
        else:
            return jsonify({'status': 401, 'message': 'User not logged in'})
