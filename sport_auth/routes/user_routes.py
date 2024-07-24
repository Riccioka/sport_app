from flask import jsonify, request, render_template
from routes.auth_routes import session
# from database import execute_query

def init_user_routes(app):
    @app.route('/main', methods=['GET'])
    def main():
        if 'loggedin' in session:

            return jsonify({'status': 200, 'name': "Мария", 'points': 54})
        return jsonify({'status': 401, 'message': 'Unauthorized', 'name': 'test'})

# ФИ, рост, вес, почта, аватарка

    @app.route('/profile', methods=['GET'])
    def profile():

        profile_data = {
            'id': 1,
            'lastName': "Иванов",
            'firstName': "Арсений",
            'email': "k@k.k",
            'height': 165,
            'weight': 56,
            'points': 65,
            'avatar': "https://i.pinimg.com/736x/19/dd/ac/19ddacef8e14946b73248fe5b20338b0.jpg",
            'team': "1",
            'league': "gold",
            'place_league': 1
        }
        return jsonify({'status': 200, 'profile': profile_data})


    # отдельно изменить рост, вес. отдельно аватарка ФИ почта. отдельно прогресс? цель
    @app.route('/edit_person_data', methods=['POST'])  # не готово
    def edit_person_data():
        return jsonify({'status': 200, 'message': 'User data updated successfully'})

    @app.route('/logout', methods=['POST'])
    def logout():
        return jsonify({'status': 200, 'message': 'Logged out successfully'})

    @app.route('/delete_account', methods=['DELETE'])
    def delete_account():
        return jsonify({'status': 200, 'message': 'Account deleted successfully'})
