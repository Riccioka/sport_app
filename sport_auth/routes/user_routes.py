from flask import jsonify, request
from database import execute_query

def init_user_routes(app):
    @app.route('/main/<int:user_id>', methods=['GET'])
    def main(user_id):
        user_data = execute_query('SELECT name, avatar, points FROM users WHERE id = %s', (user_id,))
        if user_data:
            return jsonify({'status': 200, 'name': user_data[0], 'avatar': user_data[1], 'points': user_data[2]})
        return jsonify({'status': 404, 'message': 'User not found'})

    @app.route('/profile/<int:user_id>', methods=['GET'])
    def profile(user_id):
        try:
            user_profile = execute_query('SELECT * FROM users WHERE id = %s', (user_id,))
            if user_profile:
                if user_profile[14]:
                    place_league = execute_query("""
                        WITH ranked_users AS(
                            SELECT id, points, league, RANK() OVER(PARTITION BY league
                            ORDER BY points DESC) AS league_rank
                            FROM users
                        )
                        SELECT league_rank
                        FROM ranked_users
                        WHERE id = %s;
                    """, (user_id,))
                else:
                    place_league = 100

                profile_data = {
                    'id': user_profile[0],
                    'lastName': user_profile[1],
                    'firstName': user_profile[2],
                    'email': user_profile[4],
                    'height': user_profile[8],
                    'weight': user_profile[9],
                    'points': user_profile[10],
                    'avatar': f"http://localhost:5000/avatars/{user_profile[12]}" if user_profile[12] else "https://i.pinimg.com/736x/19/dd/ac/19ddacef8e14946b73248fe5b20338b0.jpg",
                    'team': user_profile[11],
                    'league': user_profile[14],
                    'place_league': place_league
                }

                return jsonify({'status': 200, 'profile': profile_data})
            else:
                return jsonify({'status': 404, 'message': 'User not found'})
        except Exception as e:
            print("Error fetching user profile:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/edit_person_data/<int:user_id>', methods=['POST'])
    def edit_person_data(user_id):
        data = request.json
        age = data.get('age')
        height = data.get('height')
        weight = data.get('weight')

        query_args = []
        update_fields = []
        if age is not None:
            query_args.append(age)
            update_fields.append('age = %s')
        if height is not None:
            query_args.append(height)
            update_fields.append('height = %s')
        if weight is not None:
            query_args.append(weight)
            update_fields.append('weight = %s')

        if update_fields:
            query_args.append(user_id)
            update_fields = ', '.join(update_fields)
            query = f"UPDATE users SET {update_fields} WHERE id = %s"
            try:
                execute_query(query, tuple(query_args), update=True)
                return jsonify({'status': 200, 'message': 'User data updated successfully'})
            except Exception as e:
                print("Error updating user data:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})
        else:
            return jsonify({'status': 400, 'message': 'No data provided for update'})

    @app.route('/logout', methods=['POST'])
    def logout():
        return jsonify({'status': 200, 'message': 'Logged out successfully'})

    @app.route('/delete_account/<int:user_id>', methods=['DELETE'])
    def delete_account(user_id):
        if user_id:
            try:
                execute_query('DELETE FROM users WHERE id = %s', (user_id,), delete=True)
                return jsonify({'status': 200, 'message': 'Account deleted successfully'})
            except Exception as e:
                return jsonify({'status': 500, 'error': str(e)})
        else:
            return jsonify({'status': 401, 'message': 'User not logged in'})
