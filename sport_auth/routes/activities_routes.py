from flask import jsonify, request
from database import execute_query
from routes.auth_routes import token_required

def init_activities_routes(app):
    @app.route('/user/activities/week', methods=['GET'])
    @token_required
    def activities_week():
        user_id = request.user_id
        try:
            results = execute_query("""
                SELECT
                    activities.tag, activities.name, activities.color,
                    SUM(
                        CASE
                            WHEN feeds.time_beginning <= feeds.time_ending THEN
                                EXTRACT(EPOCH FROM (feeds.time_ending - feeds.time_beginning)) / 60
                            ELSE
                                EXTRACT(EPOCH FROM (feeds.time_ending - feeds.time_beginning + INTERVAL '1 day')) / 60
                        END
                    ) AS total_minutes
                FROM activities
                JOIN feeds ON activities.id = feeds.activity_id
                WHERE feeds.author_id = %s AND feeds.time_of_publication >= NOW() - INTERVAL '1 WEEK'
                GROUP BY activities.tag, activities.name, activities.color
            """, (user_id,), fetchall=True)

            activities = []
            for row in results:
                total_minutes = row[3]
                print("total_minutes ", total_minutes)

                hours = int(total_minutes // 60)
                minutes = int(total_minutes % 60)

                time_str = f"{hours:02}:{minutes:02}"

                average_time = round(total_minutes / 7)

                activity = {
                    'tag': row[0],
                    'type': row[1],
                    'color': row[2],
                    'time': time_str,
                    'average': average_time}
                activities.append(activity)
                print('act', activity)

            return jsonify({'status': 200, 'activities': activities})
        except Exception as e:
            return jsonify({'status': 500, 'message': f'Error fetching data: {str(e)}'}), 500

    @app.route('/user/activities/month', methods=['GET'])
    @token_required
    def activities_month():
        user_id = request.user_id
        try:
            results = execute_query("""
                SELECT
                    activities.tag, activities.name, activities.color,
                    SUM(
                        CASE
                            WHEN feeds.time_beginning <= feeds.time_ending THEN
                                EXTRACT(EPOCH FROM (feeds.time_ending - feeds.time_beginning)) / 60
                            ELSE
                                EXTRACT(EPOCH FROM (feeds.time_ending - feeds.time_beginning + INTERVAL '1 day')) / 60
                        END
                    ) AS total_minutes
                FROM activities
                JOIN feeds ON activities.id = feeds.activity_id
                WHERE feeds.author_id = %s AND feeds.time_of_publication >= NOW() - INTERVAL '1 MONTH'
                GROUP BY activities.tag, activities.name, activities.color
            """, (user_id,), fetchall=True)

            activities = []
            for row in results:
                total_minutes = row[3]
                print("total_minutes ", total_minutes)

                hours = int(total_minutes // 60)
                minutes = int(total_minutes % 60)

                time_str = f"{hours:02}:{minutes:02}"
                average_time = round(total_minutes / 30)  # важно ли какой месяц и сколько точно дней?

                activity = {
                    'tag': row[0],
                    'type': row[1],
                    'color': row[2],
                    'time': time_str,
                    'average': average_time}

                activities.append(activity)

            return jsonify({'status': 200, 'activities': activities})
        except Exception as e:
            return jsonify({'status': 500, 'message': f'Error fetching data: {str(e)}'}), 500

    @app.route('/user/activities/all', methods=['GET'])
    @token_required
    def activities_all():
        user_id = request.user_id
        try:
            results = execute_query("""
                SELECT
                    activities.tag, activities.name, activities.color,
                    SUM(
                        CASE
                            WHEN feeds.time_beginning <= feeds.time_ending THEN
                                EXTRACT(EPOCH FROM (feeds.time_ending - feeds.time_beginning)) / 60
                            ELSE
                                EXTRACT(EPOCH FROM (feeds.time_ending - feeds.time_beginning + INTERVAL '1 day')) / 60
                        END
                    ) AS total_minutes
                FROM activities
                JOIN feeds ON activities.id = feeds.activity_id
                WHERE feeds.author_id = %s
                GROUP BY activities.tag, activities.name, activities.color
            """, (user_id,), fetchall=True)

            activities = []
            for row in results:
                total_minutes = row[3]
                print("total_minutes ", total_minutes)

                hours = int(total_minutes // 60)
                minutes = int(total_minutes % 60)

                time_str = f"{hours:02}:{minutes:02}"

                activity = {
                    'tag': row[0],
                    'type': row[1],
                    'color': row[2],
                    'time': time_str,
                }
                activities.append(activity)

            return jsonify({'status': 200, 'activities': activities})
        except Exception as e:
            return jsonify({'status': 500, 'message': f'Error fetching data: {str(e)}'}), 500

