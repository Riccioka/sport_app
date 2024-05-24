import random
from database import execute_query


def create_leagues():
    users = execute_query('SELECT id, points FROM users ORDER BY points DESC', fetchall=True)
    total_users = len(users)

    num_gold = total_users // 3
    num_silver = total_users // 3
    # num_bronze = total_users - num_gold - num_silver

    for idx, (user_id, points) in enumerate(users):
        if idx < num_gold:
            league = 'Золотая лига'
        elif idx < num_gold + num_silver:
            league = 'Серебряная лига'
        else:
            league = 'Бронзовая лига'

        execute_query("UPDATE users SET league = %s WHERE id = %s", (league, user_id), update=True)



#
# def calculate_team_points(team_id):
#     total_points = execute_query("SELECT SUM(points) FROM users WHERE team_id = %s", (team_id,), fetchall=True)
#     total_points = total_points[0][0] if total_points[0][0] else 0
#
#     execute_query("UPDATE teams SET points = %s WHERE id = %s", (total_points, team_id), update=True)
#
# def calculate_teams_points():
#     team_ids = execute_query("SELECT DISTINCT team_id FROM users", fetchall=True)
#
#     for team_id_tuple in team_ids:
#         team_id = team_id_tuple[0]
#         # team_id = team_id_tuple
#         calculate_team_points(team_id)
