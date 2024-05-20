from database import execute_query
from admin.create_teams import calculate_teams_points

def recalculate_user_points(user_id):
    try:
        user_posts = execute_query('SELECT * FROM feeds WHERE author_id = %s', (user_id,), fetchall=True)
        total_points = 0

        for post in user_posts:
            activity_id = post[5]

            activity = execute_query('SELECT proportion_steps FROM activities WHERE id = %s', (activity_id,))
            proportion_steps = activity[0]

            total_points += proportion_steps

        execute_query('UPDATE users SET points = %s WHERE id = %s', (total_points, user_id,), update=True)

        calculate_teams_points()
        return total_points
    except Exception as e:
        print("Error recalculating user points:", e)
        raise

def recalculate_all_users_points():
    try:
        users = execute_query('SELECT id FROM users', fetchall=True)
        for user in users:
            user_id = user[0]
            recalculate_user_points(user_id)

    except Exception as e:
        print("Error recalculating all users points:", e)
        raise
