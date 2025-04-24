from database import execute_query

def validate_activity_data(data):
    required_fields = ['type', 'distance', 'duration', 'calories', 'steps']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing field: {field}")
    return data

def get_activity_by_name(activity_name):
    return execute_query("SELECT * FROM activities WHERE name = %s", (activity_name,), fetchone=True)

def get_user_data(user_id):
    return execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)

def calculate_calories_per_km(activity):
    return activity["calories_per_km"]

def calculate_activity_metrics(activity, activity_data, user_data, user_id):
    distance = activity_data['distance']
    duration_hours = activity_data['duration'] / 60
    calories_burned = calculate_calories_per_km(activity) * distance
    activity_points = round(calories_burned / 10)
    return distance, duration_hours, calories_burned, activity_points

def calculate_calories_and_points(activity, distance):
    calories_burned = calculate_calories_per_km(activity) * distance
    points = round(calories_burned / 10)
    return calories_burned, points

def recalculate_user_points(user_id):
    points = execute_query("SELECT SUM(points) FROM feeds WHERE author_id = %s", (user_id,), fetchone=True)[0]
    execute_query("UPDATE users SET points = %s WHERE id = %s", (points, user_id))

def calculate_team_points(team_id):
    return execute_query("SELECT SUM(points) FROM users WHERE team_id = %s", (team_id,), fetchone=True)[0]

