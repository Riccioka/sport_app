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

                goal_data = execute_query("""
                  SELECT target_weight
                  FROM user_progress
                  WHERE user_id = %s
                  LIMIT 1
                """, (user_id,), fetchall=False)

                target_weight = goal_data if goal_data else (None, None)

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
                    'place_league': place_league,
                    'target_weight': target_weight
                }

                return jsonify({'status': 200, 'profile': profile_data})
            else:
                return jsonify({'status': 404, 'message': 'User not found'})
        except Exception as e:
            print("Error fetching user profile:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/user/<int:user_id>/team_members', methods=['GET'])
    def get_team_members(user_id):
        team_id = execute_query("SELECT team_id FROM users WHERE id = %s", (user_id,))

        if not team_id:
            return jsonify({'status': 400, 'message': 'team_id is required'}), 400

        try:
            members = execute_query("""
                SELECT users.id, users.name, users.surname
                FROM users
                WHERE users.team_id = %s
            """, (team_id,), fetchall=True)

            if not members:
                return jsonify({'status': 404, 'message': 'No members found for the team'}), 404

            team_members = [{'id': member[0], 'name': member[1], 'surname': member[2]} for member in members]

            return jsonify({'status': 200, 'teamMembers': team_members}), 200

        except Exception as e:
            print(f"Error fetching team members: {e}")
            return jsonify({'status': 500, 'message': 'Internal server error'}), 500

    @app.route('/user/<int:user_id>/progress', methods=['GET'])
    def get_weight_progress(user_id):
        progress = execute_query("""
            SELECT target_weight, start_weight
            FROM user_progress
            WHERE user_id = %s
        """, (user_id,))

        if not progress:
            return jsonify({'status': 404, 'message': 'Progress data not found'}), 404

        target_weight = progress[0]
        start_weight = progress[1]

        current_weight = execute_query("SELECT weight FROM users WHERE id = %s", (user_id,), fetchall=False)
        current_weight = current_weight[0]

        if target_weight is None or start_weight is None or current_weight is None:
            return jsonify({'status': 500, 'message': 'Invalid weight data'}), 500

        cur_weight_difference = abs(target_weight - current_weight)
        start_weight_difference = abs(target_weight - start_weight)
        progress = 100 - (cur_weight_difference / start_weight_difference) * 100

        return jsonify({'status': 200, 'progress': progress})


    @app.route('/user/<int:user_id>/set_goal', methods=['POST'])
    def set_weight_goal(user_id):
        data = request.get_json()
        target_weight = data.get('target_weight')
        current_weight = data.get('weight')

        if target_weight is None or current_weight is None:
            return jsonify({'status': 400, 'message': 'Target weight or current weight not provided'}), 400

        try:
        # Проверка существования строки
            existing_row = execute_query("SELECT 1 FROM user_progress WHERE user_id = %s", (user_id,), fetchall=False)

            if existing_row:
            # Обновление существующей записи
                query = """
                UPDATE user_progress
                SET target_weight = %s, start_weight = %s
                WHERE user_id = %s
                """
                execute_query(query, (target_weight, current_weight, user_id), update=True)
            else:
            # Вставка новой записи
                query = """
                INSERT INTO user_progress (user_id, target_weight, start_weight)
                VALUES (%s, %s, %s)
                """
                execute_query(query, (user_id, target_weight, current_weight), update=True)

            return jsonify({'status': 200, 'message': 'Goal saved successfully'})
        except Exception as e:
            print("Error setting weight goal:", e)
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

    @app.route('/edit_fio_data/<int:user_id>', methods=['POST'])
    def edit_fio_data(user_id):
        data = request.json
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        query_args = []
        update_fields = []

        if first_name is not None:
            query_args.append(first_name)
            update_fields.append('first_name = %s')
        if last_name is not None:
            query_args.append(last_name)
            update_fields.append('last_name = %s')
        if email is not None:
            query_args.append(email)
            update_fields.append('email = %s')
        if password is not None:
            query_args.append(password)
            update_fields.append('password = %s')

        if update_fields:
            query_args.append(user_id)
            update_fields = ', '.join(update_fields)
            query = f"UPDATE users SET {update_fields} WHERE id = %s"
            try:
                execute_query(query, tuple(query_args), update=True)
                return jsonify({'status': 200, 'message': 'User info updated successfully'})
            except Exception as e:
                print("Error updating user info:", e)
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
