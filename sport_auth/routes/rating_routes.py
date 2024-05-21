from flask import jsonify
from database import execute_query
from routes.auth_routes import session

def init_rating_routes(app):
    @app.route('/users_leaderboard', methods=['GET'])
    def get_users_leaderboard():
        results = execute_query("""
            SELECT 
                users.surname, users.name, users.points, 
                teams.name
            FROM users
            JOIN teams ON users.team_id = teams.id
            GROUP BY users.id
            ORDER BY points DESC;
        """, fetchall=True)

        leaderboard = []
        for row in results:
            leaderboard.append({
                'surname': row[0],
                'name': row[1],
                'points': row[2],
                'team': row[3]
            })
        return jsonify({'status': 200, 'message': 'Users rating created successfully', 'leaderboard': leaderboard})

    @app.route('/teams_leaderboard', methods=['GET'])
    def get_teams_leaderboard():
        results = execute_query("""
            SELECT
                teams.name, teams.points, 
                COUNT(users.team_id)
            FROM teams JOIN users ON teams.id = users.team_id
            GROUP BY teams.id
            ORDER BY teams.points DESC ;
        """, fetchall=True)
        # count_users = execute_query("SELECT COUNT(*) FROM users WHERE team_id", fetchall=True)

        leaderboard = []
        for row in results:
            leaderboard.append({
                'name': row[0],
                'points': row[1],
                'count_users': row[2]
            })
        return jsonify({'status': 200, 'message': 'Teams rating created successfully', 'leaderboard': leaderboard})
