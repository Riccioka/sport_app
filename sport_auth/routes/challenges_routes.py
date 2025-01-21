from flask import Flask, jsonify, request
from database import execute_query
from routes.auth_routes import token_required

app = Flask(__name__)

def init_challenges_routes(app):
    @app.route('/user/available-challenges', methods=['GET'])
    @token_required
    def available_challenges():
        # user_id = request.user_id
        # try:
        #     challenges = execute_query(
        #         SELECT c.id, c.name, uc.progress, c.points
        #         FROM challenges c
        #         JOIN user_challenges uc ON c.id = uc.challenge_id
        #         WHERE uc.user_id = %s AND uc.status = 'current'
        #     , (user_id,), fetchall=True)
        #
        #     current_challenges = []
        #     for challenge in challenges:
        #         current_challenges.append({
        #             'id': challenge[0],
        #             'name': challenge[1],
        #             'progress': challenge[2],
        #             'points': challenge[3]
        #         })
        #     return jsonify({'status': 200, 'message': 'successfully', 'current_challenges': current_challenges})
        # except Exception as e:
        #     return jsonify({'status': 500, 'message': f'Error fetching data: {str(e)}'}), 500

        user_id = request.user_id
        try:
            challenges = execute_query("""
                SELECT c.id, c.name, c.points
                FROM challenges c
                WHERE c.id NOT IN (
                    SELECT challenge_id
                    FROM user_challenges
                    WHERE user_id = %s
                )
            """, (user_id,), fetchall=True)

            available_challenges = []
            for challenge in challenges:
                available_challenges.append({
                    'id': challenge[0],
                    'name': challenge[1],
                    'points': challenge[2]
                })

            return jsonify({
                'status': 200,
                'message': 'Available challenges fetched successfully',
                'available_challenges': available_challenges
            })
        except Exception as e:
            return jsonify({'status': 500, 'message': f'Error fetching data: {str(e)}'}), 500

    @app.route('/user/current-challenges', methods=['GET'])
    @token_required
    def current_challenges():
        user_id = request.user_id
        try:
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
        except Exception as e:
            return jsonify({'status': 500, 'message': f'Error fetching data: {str(e)}'}), 500

    @app.route('/user/completed-challenges', methods=['GET'])
    @token_required
    def completed_challenges():
        user_id = request.user_id
        try:
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
        except Exception as e:
            return jsonify({'status': 500, 'message': f'Error fetching data: {str(e)}'}), 500

    @token_required
    def challenges_points(challenge_id):
        user_id = request.user_id
        try:
            challenges_points = execute_query('SELECT points FROM challenges WHERE id = %s', (challenge_id,))
            execute_query('UPDATE users SET points = points + %s WHERE id = %s', (challenges_points[0], user_id),
                          update=True)
        except Exception as e:
            return jsonify({'status': 500, 'message': f'Error fetching data: {str(e)}'}), 500


