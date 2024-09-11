from flask import Flask, jsonify
from database import execute_query

app = Flask(__name__)


def init_challenges_routes(app):
    @app.route('/user/<int:user_id>/current-challenges', methods=['GET'])
    def current_challenges(user_id):
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

    @app.route('/user/<int:user_id>/completed-challenges', methods=['GET'])
    def completed_challenges(user_id):
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

    def challenges_points(user_id, challenge_id):
        challenges_points = execute_query('SELECT points FROM challenges WHERE id = %s', (challenge_id,))
        execute_query('UPDATE users SET points = points + %s WHERE id = %s', (challenges_points[0], user_id),
                      update=True)
