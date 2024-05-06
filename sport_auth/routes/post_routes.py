from flask import jsonify, request
from routes.auth_routes import session
from database import execute_query
import datetime
import base64

def init_post_routes(app):
    @app.route('/list_of_activities', methods=['GET'])
    def get_activities():
        if 'loggedin' in session:
            activities = execute_query('SELECT name, scorecard, color FROM activities')

            activities_data = []
            for activity in activities:
                activity_data = {
                    'name': activity.name,
                    'scorecard': activity.scorecard,
                    'color': activity.color
                }
                activities_data.append(activity_data)

            return jsonify({'status': 200, 'activities': activities_data})
        return jsonify({'status': 401, 'message': 'Unauthorized'})


    @app.route('/activities', methods=['POST'])
    def activities():
        if request.method == 'POST':
            if 'id' in session:
                author_id = session['id']
            else:
                return jsonify({'status': 401, 'message': 'Unauthorized'})
            data = request.get_json()
            time_of_publication = datetime.datetime.now()
            status = False  # false пока не изменен пост
            progress = data.get('distance')
            calories = data.get('calories')  # км/ч/шаги
            time_beginning = data.get('startTime')
            time_ending = data.get('endTime')
            activity_id = 2
            # activity_id = data.get('type')
            commentactivity = data.get('description')

            proof = None
            # if proof_image is not None:
            #     proof = proof_image.read()

            # verification_file = request.files['verification']
            # proof = verification_file.read()


            # proof_image = data.get('verification')
            #
            # proof = None
            # if proof_image is not None:
            #     binary_data = proof_image.read()
            #     proof = base64.b64encode(binary_data)

            try:
                execute_query(
                    'INSERT INTO feeds (author_id, time_of_publication, status, progress, activity_id, commentactivity, calories, time_beginning, time_ending, proof) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (author_id, time_of_publication, status, progress, activity_id, commentactivity, calories,
                     time_beginning, time_ending, proof), insert=True)

                activity_points = execute_query('SELECT proportion_steps FROM activities WHERE id = %s', (activity_id,))
                if activity_points:

                    execute_query('UPDATE users SET points = points + %s WHERE id = %s', (activity_points[0], author_id),
                                  update=True)

                return jsonify({'status': 200, 'message': 'Post created successfully'})
            except Exception as e:
                print("Error creating post:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})
        return jsonify({'status': 401, 'message': 'Unauthorized'})


    # @app.route('/edit_post/<int:post_id>', methods=['PUT'])
    # def edit_post(post_id):
    #     pass
    #
    # @app.route('/delete_post/<int:post_id>', methods=['DELETE'])
    # def delete_post(post_id):
    #     pass