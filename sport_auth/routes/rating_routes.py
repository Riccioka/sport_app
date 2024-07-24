from flask import jsonify
# from database import execute_query
from routes.auth_routes import session

def init_rating_routes(app):
    @app.route('/participants-rating', methods=['GET'])
    def participants():

        leaderboard = [{
                'id': 1,
                'lastName': "Конев",
                'firstName': "Георгий",
                'progress': 40,
                'league': "gold",
                'team': "1"
            }]
        return jsonify({'status': 200, 'message': 'Users rating created successfully', 'leaderboard': leaderboard})

    @app.route('/teams-rating', methods=['GET'])
    def teams():
        leaderboard = [{
                'id': 1,
                'lastName': "Конев",
                'firstName': "Георгий",
                'progress': 40,
                'league': "gold",
                'team': "1"
            }]
        return jsonify({'status': 200, 'message': 'Teams rating created successfully', 'leaderboard': leaderboard})
