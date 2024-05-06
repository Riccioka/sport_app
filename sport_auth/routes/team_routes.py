# командные действия

import random
from database import execute_query

def create_teams():
    # execute_query("DELETE FROM teams")

    users_data = execute_query('SELECT * FROM users')
    # print(users_data)
    # print(users_data[0])

    for user_row in users_data:
        print(user_row)
    users = users_data

    num_users = len(users)
    num_teams = -(-num_users // 3)  # Эквивалентно ceil(num_users / 3)

    # Создаем команды
    print(num_teams)
    # for team_id in range(1, num_teams + 1):
    #     # team_users = random.sample(users, min(3, len(users)))
    #     team_users = users[(team_id - 1) * 3:team_id * 3]
    #     # for user in team_users:
    #         # users.remove(user)
    #
    #     # execute_query("INSERT INTO teams (team_id) VALUES (%s)", (team_id,), insert=True)
    #     for user in team_users:
    #         execute_query("UPDATE users SET team_id = %s WHERE id = %s", (team_id, user[0]))

    for team_id in range(1, num_teams + 1):

        team_users = users[(team_id - 1) * 3:team_id * 3]
        print(team_users)
        # team_users = random.sample(users, min(3, len(users)))
        for i in range(1, 4):
            print("user = ", team_users[i][0])
            execute_query("UPDATE users SET team_id = %s WHERE id = %s", (team_id, team_users[i][0]))
        # for i in range(1, 4):
        #     print(i)
        #     print(team_users)
        #     user_id = team_users[i][0] # Получаем id пользователя из кортежа
            # execute_query("UPDATE users SET team_id = %s WHERE id = %s", (team_id, user_id), insert=True)


    # users = execute_query("SELECT * FROM users")
    # # users = [list(user) for user in users]
    # # random.shuffle(users)
    # num_users = len(users)
    # # количество команд, округленное вверх
    # num_teams = -(-num_users // 3)
    #
    # for team_id in range(1, num_teams + 1):
    #     # team_users = random.sample(users, min(3, len(users)))
    #     team_users = users[(team_id - 1) * 3:team_id * 3]
    #     # for user in team_users:
    #         # users.remove(user)
    #
    #     # execute_query("INSERT INTO teams (team_id) VALUES (%s)", (team_id,), insert=True)
    #     for user in team_users:
    #         execute_query("UPDATE users SET team_id = %s WHERE id = %s", (team_id, user[0]))

# create_teams()