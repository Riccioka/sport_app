from flask import Flask, jsonify, session
from database import execute_query
from routes.auth_routes import session

app = Flask(__name__)

def init_challenges_routes(app):
    @app.route('/current-challenges', methods=['GET'])
    def current_challenges():
        if 'loggedin' in session:
            user_id = session['id']
            challenges = execute_query("""
                SELECT c.id, c.name, uc.progress, c.points
                FROM challenges c
                JOIN user_challenges uc ON c.id = uc.challenge_id
                WHERE uc.user_id = %s AND uc.status = 'current'
            """, (user_id,), fetchall=True)
            current_challenges = []
            for challenge in challenges:
                current_challenges.append({
                    'id': challenge[0],
                    'name': challenge[1],
                    'progress': challenge[2],
                    'points': challenge[3]
                })
            return jsonify({'status': 200, 'message': 'successfully', 'current_challenges': current_challenges})
        return jsonify({'status': 401, 'message': 'Unauthorized'})

    @app.route('/completed-challenges', methods=['GET'])
    def completed_challenges():
        if 'loggedin' in session:
            user_id = session['id']
            challenges = execute_query("""
                SELECT c.id, c.name, uc.progress, c.points
                FROM challenges c
                JOIN user_challenges uc ON c.id = uc.challenge_id
                WHERE uc.user_id = %s AND uc.status = 'completed'
            """, (user_id,), fetchall=True)
            completed_challenges = []
            for challenge in challenges:
                completed_challenges.append({
                    'id': challenge[0],
                    'name': challenge[1],
                    'progress': challenge[2],
                    'points': challenge[3]
                })
            return jsonify({'status': 200, 'message': 'successfully', 'completed_challenges': completed_challenges})
        return jsonify({'status': 401, 'message': 'Unauthorized'})

    def challenges_points(challenge_id):
        if 'loggedin' in session:
            user_id = session['id']
            challenges_points = execute_query('SELECT points FROM challenges WHERE id = %s', (challenge_id,))
            execute_query('UPDATE users SET points = points + %s WHERE id = %s', (challenges_points[0], user_id,), update=True)