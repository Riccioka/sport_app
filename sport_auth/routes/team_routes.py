import random
from database import execute_query

def create_teams():
    users = execute_query('SELECT id FROM users', fetchall=True)
    user_ids = [user[0] for user in users]

    random.shuffle(user_ids )

    # num_teams = (len(user_ids ) + 2) // 3

    user_groups = [user_ids [i:i + 3] for i in range(0, len(user_ids ), 3)]

    # print("group ->", user_groups)

    for i, group in enumerate(user_groups, start=1):
        for user_id in group:
            execute_query("UPDATE users SET team_id = %s WHERE id = %s", (i, user_id), update=True)
    calculate_team_points()


def calculate_team_points():
    team_ids = execute_query("SELECT DISTINCT team_id FROM users", fetchall=True)

    for team_id in team_ids:
        total_points = execute_query("SELECT SUM(points) FROM users WHERE team_id = %s", (team_id,), fetchall=True)
        total_points = total_points[0][0] if total_points[0][0] else 0

        execute_query("UPDATE teams SET points = %s WHERE id = %s", (total_points, team_id), update=True)
