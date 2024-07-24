from flask import jsonify
def init_activities_routes(app):
    @app.route('/activities/week', methods=['GET'])
    def activities_week():
        hours = 2
        minutes = 10

        time_str = f"{hours:02}:{minutes:02}"

        average_time = round(100 / 7)

        activities = [{
            'tag': "run",
            'type': "Бег",
            'color': "green",
            'time': time_str,
            'average': average_time}]

        return jsonify({'status': 200, 'activities': activities})



    @app.route('/activities/month', methods=['GET'])
    def activities_month():
        hours = 2
        minutes = 10

        time_str = f"{hours:02}:{minutes:02}"

        average_time = round(100 / 30)

        activities = [{
            'tag': "run",
            'type': "Бег",
            'color': "green",
            'time': time_str,
            'average': average_time}]

        return jsonify({'status': 200, 'activities': activities})


    @app.route('/activities/all', methods=['GET'])
    def activities_all():
        hours = 2
        minutes = 10

        time_str = f"{hours:02}:{minutes:02}"

        activities = [{
            'tag': "run",
            'type': "Бег",
            'color': "green",
            'time': time_str}]

        return jsonify({'status': 200, 'activities': activities})