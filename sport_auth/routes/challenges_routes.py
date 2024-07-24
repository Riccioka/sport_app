from flask import Flask, jsonify, session
# from database import execute_query
from routes.auth_routes import session

app = Flask(__name__)

def init_challenges_routes(app):
    @app.route('/current-challenges', methods=['GET'])
    def current_challenges():
        if 'loggedin' in session:
            current_challenges = [{
                    'id': 1,
                    'name': "Пробежать 1км",
                    'progress': 30,
                    'points': 50
                }]
            return jsonify({'status': 200, 'message': 'successfully', 'current_challenges': current_challenges})
        return jsonify({'status': 401, 'message': 'Unauthorized'})

    @app.route('/completed-challenges', methods=['GET'])
    def completed_challenges():
        if 'loggedin' in session:
            completed_challenges = [{
                    'id': 2,
                    'name': "Проплыть 500м",
                    'progress': 100,
                    'points': 40
                }]
            return jsonify({'status': 200, 'message': 'successfully', 'completed_challenges': completed_challenges})
        return jsonify({'status': 401, 'message': 'Unauthorized'})

    # def challenges_points(challenge_id):
    #     if 'loggedin' in session:
    #         user_id = session['id']
    #         challenges_points = execute_query('SELECT points FROM challenges WHERE id = %s', (challenge_id,))
    #         execute_query('UPDATE users SET points = points + %s WHERE id = %s', (challenges_points[0], user_id,), update=True)