from flask import jsonify
from database import execute_query
from routes.auth_routes import session
import datetime
from datetime import datetime, time, timedelta

def init_activities_routes(app):
    @app.route('/activities/week', methods=['GET'])
    def activities_week():
        user_id = session['id']
        print("user_id", user_id)
        results = execute_query("""
            SELECT 
                activities.tag, activities.name, activities.color, 
                feeds.time_beginning, feeds.time_ending
            FROM activities
            JOIN feeds ON activities.id = feeds.activity_id
            WHERE feeds.author_id = %s AND feeds.time_of_publication >= NOW() - INTERVAL '1 WEEK'
            GROUP BY activities.tag, activities.name, activities.color, feeds.time_beginning, feeds.time_ending
        """, (user_id,), fetchall=True)


        activities = []
        for row in results:
            time_beginning_obj = datetime.strptime(str(row[3]), '%H:%M:%S').time()
            time_ending_obj = datetime.strptime(str(row[4]), '%H:%M:%S').time()

            time_delta = datetime.combine(datetime.min, time_ending_obj) - datetime.combine(datetime.min,
                                                                                            time_beginning_obj)

            average_time = round((time_delta.total_seconds() / 7) / 60)
            hours = time_delta.seconds // 3600
            minutes = (time_delta.seconds % 3600) // 60

            activity = {
                'tag': row[0],
                'type': row[1],
                'color': row[2],
                'time': f"{hours:02}:{minutes:02}",
                'average': average_time}
            activities.append(activity)

        return jsonify({'status': 200, 'activities': activities})

    @app.route('/activities/month', methods=['GET'])
    def activities_month():
        user_id = session['id']
        results = execute_query("""
            SELECT
                activities.tag, activities.name, activities.color,
                feeds.time_beginning, feeds.time_ending
            FROM activities
            JOIN feeds ON activities.id = feeds.activity_id
            WHERE feeds.author_id = %s AND feeds.time_of_publication >= NOW() - INTERVAL '1 MONTH'
            GROUP BY activities.tag, activities.name, activities.color, feeds.time_beginning, feeds.time_ending
        """, (user_id,), fetchall=True)

        activities = []
        for row in results:
            time_beginning_obj = datetime.strptime(str(row[3]), '%H:%M:%S').time()
            time_ending_obj = datetime.strptime(str(row[4]), '%H:%M:%S').time()

            time_delta = datetime.combine(datetime.min, time_ending_obj) - datetime.combine(datetime.min,
                                                                                            time_beginning_obj)
            average_time = round((time_delta.total_seconds() / 30) / 60)  # важно ли какой месяц и сколько точно дней?
            hours = time_delta.seconds // 3600
            minutes = (time_delta.seconds % 3600) // 60

            activity = {
                'tag': row[0],
                'type': row[1],
                'color': row[2],
                'time': f"{hours:02}:{minutes:02}",
                'average': average_time}
            activities.append(activity)
        return jsonify({'status': 200, 'activities': activities})

    # @app.route('/activities/month', methods=['GET'])
    # def activities_month():
    #     user_id = session['id']
    #     results = execute_query("""
    #         SELECT
    #             activities.tag, activities.name, activities.color,
    #             SUM(EXTRACT(EPOCH FROM (feeds.time_ending - feeds.time_beginning)) / 60) AS total_minutes
    #         FROM activities
    #         JOIN feeds ON activities.id = feeds.activity_id
    #         WHERE feeds.author_id = %s AND feeds.time_of_publication >= NOW() - INTERVAL '1 MONTH'
    #         GROUP BY activities.tag, activities.name, activities.color
    #     """, (user_id,), fetchall=True)
    #
    #     activities = []
    #     for row in results:
    #         total_minutes = row[3]
    #
    #         # Вычисляем часы и минуты из общего времени в минутах
    #         hours = int(total_minutes // 60)
    #         minutes = int(total_minutes % 60)
    #
    #         # Форматируем время для отображения
    #         time_str = f"{hours:02}:{minutes:02}"
    #
    #         activity = {
    #             'tag': row[0],
    #             'type': row[1],
    #             'color': row[2],
    #             'time': time_str,
    #         }
    #         activities.append(activity)
    #
    #     return jsonify({'status': 200, 'activities': activities})

    @app.route('/activities/all', methods=['GET'])
    def activities_all():
        user_id = session['id']
        results = execute_query("""
            SELECT 
                activities.tag, activities.name, activities.color, 
                feeds.time_beginning, feeds.time_ending
            FROM activities
            JOIN feeds ON activities.id = feeds.activity_id
            WHERE feeds.author_id = %s
            GROUP BY activities.tag, activities.name, activities.color, feeds.time_beginning, feeds.time_ending
        """, (user_id,), fetchall=True)


        activities = []
        for row in results:
            time_beginning_obj = datetime.strptime(str(row[3]), '%H:%M:%S').time()
            time_ending_obj = datetime.strptime(str(row[4]), '%H:%M:%S').time()

            time_delta = datetime.combine(datetime.min, time_ending_obj) - datetime.combine(datetime.min,
                                                                                            time_beginning_obj)
            average_time = round((time_delta.total_seconds() / 7) / 60)
            hours = time_delta.seconds // 3600
            minutes = (time_delta.seconds % 3600) // 60

            activity = {
                'tag': row[0],
                'type': row[1],
                'color': row[2],
                'time': f"{hours:02}:{minutes:02}"}
            activities.append(activity)
        return jsonify({'status': 200, 'activities': activities})