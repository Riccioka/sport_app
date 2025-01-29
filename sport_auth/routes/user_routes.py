from flask import jsonify, request
from database import execute_query
import math
from routes.auth_routes import token_required

def init_user_routes(app):
    # user id !!!
    @app.route('/participants/progress', methods=['GET'])
    def get_total_participants_progress():
        # 1 000 км
        goal_calories = 10000

        total_calories_data = execute_query('SELECT SUM(calories) as total_calories FROM feeds', fetchall=False)

        total_calories = total_calories_data[0] if total_calories_data and total_calories_data[0] is not None else 0

        total_calories = 10000
        all_progress = min((total_calories / goal_calories) * 100, 100)

        return jsonify({'status': 200, 'all_progress': round(all_progress, 2)})


    @app.route('/main', methods=['GET'])
    @token_required
    def main():
        user_id = request.user_id

        try:
            user_data = execute_query('SELECT name, avatar, points FROM users WHERE id = %s', (user_id,))
            team_count = execute_query('SELECT COUNT(*) FROM teams')[0] if execute_query('SELECT COUNT(*) FROM teams') else 0
            participant_count = execute_query('SELECT COUNT(*) FROM users')[0] if execute_query('SELECT COUNT(*) FROM users') else 0
#        progress = get_total_participants_progress()
#             goal_progress_data = execute_query('SELECT SUM(calories) as total_calories FROM feeds', fetchall=False)
            # total_calories = goal_progress_data[0] if goal_progress_data and goal_progress_data[0] is not None else 0
            # progress = min((total_calories / (402 * 53)) * 100, 100)
            # distance = math.ceil(total_calories / 60)
            goal_progress_data = execute_query('SELECT SUM(points) as total_points FROM users', fetchall=False)
            total_points = goal_progress_data[0] if goal_progress_data and goal_progress_data[0] is not None else 0
            progress = min((total_points / (402 * 10)) * 100, 100)

            distance = math.ceil(total_points / 10)

            if user_data:
                return jsonify({
                    'status': 200,
                    'name': user_data[0],
                    'avatar': user_data[1],
                    'points': user_data[2],
                    'teams': team_count,
                    'participants': participant_count,
                    'count': distance,
                    'goal': progress
            })
            return jsonify({'status': 404, 'message': 'User not found'})
        except Exception as e:
            return jsonify({'status': 500, 'message': f'Error fetching data: {str(e)}'}), 500


    @app.route('/profile', methods=['GET'])
    @token_required
    def profile():
        user_id = request.user_id

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
                    'avatar': user_profile[12],
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

    @app.route('/user/team_members', methods=['GET'])
    @token_required
    def get_team_members():
        user_id = request.user_id

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

    @app.route('/user/progress', methods=['GET'])
    @token_required
    def get_weight_progress():
        user_id = request.user_id

        progress = execute_query("""
            SELECT target_weight, start_weight
            FROM user_progress
            WHERE user_id = %s
        """, (user_id,))

        if not progress:
            progress = 0
        #    return jsonify({'status': 404, 'message': 'Progress data not found'}), 404
        else:
            target_weight = progress[0]
            start_weight = progress[1]

            current_weight = execute_query("SELECT weight FROM users WHERE id = %s", (user_id,), fetchall=False)
            current_weight = current_weight[0]

            if target_weight is None or start_weight is None or current_weight is None:
                return jsonify({'status': 500, 'message': 'Invalid weight data'}), 500

            if target_weight > start_weight:
                if current_weight >= start_weight:
                    progress = min(100, (current_weight - start_weight) / (target_weight - start_weight) * 100)
                else:
                    progress = 0
            else:
                if current_weight <= start_weight:
                    progress = min(100, (start_weight - current_weight) / (start_weight - target_weight) * 100)
                else:
                    progress = 0

       # cur_weight_difference = abs(target_weight - current_weight)
       # start_weight_difference = abs(target_weight - start_weight)
       # progress = 100 - (cur_weight_difference / start_weight_difference) * 100

        return jsonify({'status': 200, 'progress': progress})


    @app.route('/user/set_goal', methods=['POST'])
    @token_required
    def set_weight_goal():
        user_id = request.user_id

        data = request.get_json()
        target_weight = data.get('target_weight')
        current_weight = data.get('weight')

        if target_weight is None or current_weight is None:
            return jsonify({'status': 400, 'message': 'Target weight or current weight not provided'}), 400

        try:
            existing_row = execute_query("SELECT 1 FROM user_progress WHERE user_id = %s", (user_id,), fetchall=False)

            if existing_row:
                query = """
                UPDATE user_progress
                SET target_weight = %s, start_weight = %s
                WHERE user_id = %s
                """
                execute_query(query, (target_weight, current_weight, user_id), update=True)
            else:
                query = """
                INSERT INTO user_progress (user_id, target_weight, start_weight)
                VALUES (%s, %s, %s)
                """
                execute_query(query, (user_id, target_weight, current_weight), update=True)

            return jsonify({'status': 200, 'message': 'Goal saved successfully'})
        except Exception as e:
            print("Error setting weight goal:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})



    @app.route('/edit_person_data', methods=['POST'])
    @token_required
    def edit_person_data():
        user_id = request.user_id

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

    @app.route('/edit_fio_data', methods=['POST'])
    @token_required
    def edit_fio_data():
        user_id = request.user_id

        data = request.json
        name = data.get('firstName')
        surname = data.get('lastName')
        email = data.get('email')
        password = data.get('password')
        avatar = data.get('avatar')

        query_args = []
        update_fields = []

        if name is not None:
            query_args.append(name)
            update_fields.append('name = %s')
        if surname is not None:
            query_args.append(surname)
            update_fields.append('surname = %s')
        if email is not None:
            query_args.append(email)
            update_fields.append('email = %s')
        if password is not None:
            query_args.append(password)
            update_fields.append('password = %s')
        if avatar is not None:
            query_args.append(avatar)
            update_fields.append('avatar = %s')


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
    # @token_required
    def logout():
        # user_id = request.user_id
        token = request.headers.get('Authorization').split("Bearer ")[1]
        try:
            execute_query('INSERT INTO token_blacklist (token) VALUES (%s)', (token,))
            return jsonify({'status': 200, 'message': 'Logged out successfully'})
        except Exception as e:
            return jsonify({'status': 500, 'error': str(e)})

    @app.route('/delete_account', methods=['DELETE'])
    @token_required
    def delete_account():
        user_id = request.user_id
        token = request.headers.get('Authorization').split("Bearer ")[1]
        try:
            execute_query('DELETE FROM users WHERE id = %s', (user_id,), delete=True)
            execute_query('INSERT INTO token_blacklist (token) VALUES (%s)', (token,))
            return jsonify({'status': 200, 'message': 'Account deleted successfully'})
        except Exception as e:
            return jsonify({'status': 500, 'error': str(e)})


