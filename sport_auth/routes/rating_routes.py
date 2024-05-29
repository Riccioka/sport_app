from flask import jsonify
from database import execute_query
from routes.auth_routes import session

def init_rating_routes(app):
    @app.route('/participants-rating', methods=['GET'])
    def participants():
        results = execute_query("""
            SELECT 
                users.id, users.surname, users.name, users.points, 
                teams.name
            FROM users
            JOIN teams ON users.team_id = teams.id
            GROUP BY users.id, users.surname, users.name, users.points, teams.name
            ORDER BY users.points DESC;
        """, fetchall=True)

        leaderboard = []
        for row in results:
            leaderboard.append({
                'id': row[0],
                'lastName': row[1],
                'firstName': row[2],
                'progress': row[3],
                'team': row[4]
            })
        return jsonify({'status': 200, 'message': 'Users rating created successfully', 'leaderboard': leaderboard})

    @app.route('/teams-rating', methods=['GET'])
    def teams():
        results = execute_query("""
                   SELECT
                       teams.id, teams.name, teams.points as points, 
                       COUNT(users.id) as members
                   FROM teams
                   JOIN users ON teams.id = users.team_id
                   GROUP BY teams.id
                   ORDER BY points DESC;
               """, fetchall=True)
        # SUM(users.points) as points,

        # count_users = execute_query("SELECT COUNT(*) FROM users WHERE team_id", fetchall=True)

        leaderboard = []
        for row in results:
            leaderboard.append({
                'id': row[0],
                'name': row[1],
                'totalProgress': row[2],
                'members': row[3]
            })
        return jsonify({'status': 200, 'message': 'Teams rating created successfully', 'leaderboard': leaderboard})
