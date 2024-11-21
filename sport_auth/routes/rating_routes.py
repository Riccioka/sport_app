from flask import jsonify
from database import execute_query

def init_rating_routes(app):
    @app.route('/participants-rating', methods=['GET'])
    def participants():
        try:
            results = execute_query("""
                SELECT 
                    users.id, users.surname, users.name, users.points, users.league,
                    teams.name
                FROM users
                JOIN teams ON users.team_id = teams.id
                GROUP BY users.id, users.surname, users.name, users.points, teams.name
                ORDER BY users.points DESC;
            """, fetchall=True)
            #results = [
            #    (1, "Ivanov", "Vanya", 230, "gold", "team1"),
            #    (2, "Petrov", "Petr", 54, "silver", "team2"),
            #    (3, "Alexandrov", "Sasha", 12, "bronze", "team3"),
            #]
            leaderboard = []
            for row in results:
                leaderboard.append({
                    'id': row[0],
                    'lastName': row[1],
                    'firstName': row[2],
                    'progress': row[3],
                    'league': row[4],
                    'team': row[5]
                })
            return jsonify({'status': 200, 'message': 'Users rating created successfully', 'leaderboard': leaderboard})
        except Exception as e:
            print("Error fetching participants rating:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/teams-rating', methods=['GET'])
    def teams():
        try:
            results = execute_query("""
                SELECT
                    teams.id, teams.name, SUM(users.points) as points, 
                    COUNT(users.id) as members
                FROM teams
                JOIN users ON teams.id = users.team_id
                GROUP BY teams.id, teams.name
                ORDER BY points DESC;
            """, fetchall=True)

            leaderboard = []
            for row in results:
                leaderboard.append({
                    'id': row[0],
                    'name': row[1],
                    'totalProgress': row[2],
                    'members': row[3]
                })
            return jsonify({'status': 200, 'message': 'Teams rating created successfully', 'leaderboard': leaderboard})
        except Exception as e:
            print("Error fetching teams rating:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

