from flask import jsonify, request, send_from_directory
# from database import execute_query
from routes.auth_routes import session
from admin.recalc_points import recalculate_user_points
from admin.create_teams import calculate_team_points
import datetime
from datetime import datetime, time
import os
import pytz

def init_post_routes(app):
    @app.route('/list_of_activities', methods=['GET'])
    def list_of_activities():
        if 'loggedin' in session:

            activities_data = [{
                    'type': "Бег",
                    'scorecard': "км",
                    'color': "green",
                    'tag': "run"
                }]

            return jsonify({'status': 200, 'activities': activities_data})
        return jsonify({'status': 401, 'message': 'Unauthorized'})

    @app.route('/uploads/<filename>', methods=['GET'])
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/uploads', methods=['POST'])
    def upload_image():
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image = request.files['image']
        if image.filename == '':
            return jsonify({'error': 'No selected image'}), 400

        if image:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filename)

            print("Image saved successfully:", filename)

            return jsonify({'imageUrl': filename}), 200

        return jsonify({'error': 'Upload failed'}), 500

    @app.route('/activities', methods=['POST'])  # изменить на create_post
    def activities():
                return jsonify({'status': 200, 'message': 'Post created successfully'})

    @app.route('/posts', methods=['GET'])
    def posts():
        if 'loggedin' in session:
            time_beginning_obj = datetime.strptime(str("12:00:00"), '%H:%M:%S').time()
            time_ending_obj = datetime.strptime(str("13:30:00"), '%H:%M:%S').time()

            time_delta = datetime.combine(datetime.min, time_ending_obj) - datetime.combine(datetime.min,
                                                                                            time_beginning_obj)
            hours = time_delta.seconds // 3600
            minutes = (time_delta.seconds % 3600) // 60
            # timestamp_obj = post[5].replace(tzinfo=pytz.UTC)
            timestamp_str = str("2024-06-20 15:07:42.452234")


            formatted_posts = [{
                    'id': 1,
                    'username': "Алина",
                    # 'name': post[2],
                    'fireCount': 35,
                    # 'miniAvatar': "uploads\photo_2024-05-15_12-39-41.jpg",
                    'timestamp': timestamp_str,
                    # 'image': "uploads\photo_2024-05-15_12-39-41.jpg",
                    'type': "Бег",
                    'scorecard': "км",
                    'color': "green",
                    'tag': "run",
                    'time': f"{hours:02}:{minutes:02}",
                    'progress': 323,
                    'calories': 454,
                    'text': "runrunrun",
                    'feed_id': 1,
                    'likeCount': 5,
                    'isLiked': -1 > 0
                    # 'isLiked': False,
                }]

            # formatted_posts = sorted(formatted_posts, key=lambda x: x['timestamp'], reverse=True)
            return jsonify({'status': 200, 'posts': formatted_posts})
        else:
            return jsonify({'status': 401, 'message': 'Unauthorized'})

    # проверка доступа на редактирование есть у фронта?
    @app.route('/edit_post/<int:post_id>', methods=['PUT'])
    def edit_post(post_id):
            return jsonify({'status': 200, 'message': 'Post updated successfully'})

    # проверка доступа на удаление есть у фронта?
    @app.route('/delete_post/<int:post_id>', methods=['DELETE'])  # <int:post_id>
    def delete_post(post_id):
            return jsonify({'status': 200, 'message': 'Post deleted successfully'})