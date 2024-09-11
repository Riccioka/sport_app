from flask import jsonify, request, send_from_directory
from database import execute_query
from admin.recalc_points import recalculate_user_points
from admin.create_teams import calculate_team_points
import datetime
from datetime import datetime, time
import os
import pytz

def init_post_routes(app):
    @app.route('/user/<int:user_id>/list_of_activities', methods=['GET'])
    def list_of_activities(user_id):
        activities = execute_query('SELECT name, scorecard, color, tag FROM activities', fetchall=True)

        activities_data = []
        for activity in activities:
            activity_data = {
                'type': activity[0],
                'scorecard': activity[1],
                'color': activity[2],
                'tag': activity[3]
            }
            activities_data.append(activity_data)

        return jsonify({'status': 200, 'activities': activities_data})

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

    @app.route('/user/<int:user_id>/activities', methods=['POST'])  # изменить на create_post
    def activities(user_id):
            data = request.get_json()
            time_of_publication = datetime.now()
            status = False  # false пока не изменен пост
            progress = data.get('distance')
            calories = data.get('calories')  # км/ч/шаги
            time_beginning = data.get('startTime')
            time_ending = data.get('endTime')
            activity_name = data.get('type')
            commentactivity = data.get('description')
            proof = data.get('verification')
            image = data.get('image')

            activity_id = execute_query('SELECT id FROM activities WHERE tag = %s', (activity_name,))
            try:
                execute_query(
                    'INSERT INTO feeds (author_id, time_of_publication, status, progress, activity_id, commentactivity, calories, time_beginning, time_ending, proof, image) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (user_id, time_of_publication, status, progress, activity_id, commentactivity, calories,
                     time_beginning, time_ending, proof, image), insert=True)

                activity_points = execute_query('SELECT proportion_steps FROM activities WHERE id = %s', (activity_id,))
                if activity_points:
                    execute_query('UPDATE users SET points = points + %s WHERE id = %s', (activity_points[0], user_id),
                                  update=True)
                author_team = execute_query('SELECT team_id FROM users WHERE id = %s', (user_id,))
                print('author_team', author_team)
                calculate_team_points(author_team)
                return jsonify({'status': 200, 'message': 'Post created successfully'})
            except Exception as e:
                print("Error creating post:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/user/<int:user_id>/posts', methods=['GET'])
    def posts(user_id):
            posts = execute_query("""
                SELECT
                    users.id, users.surname, users.name, users.points, users.avatar,
                    feeds.time_of_publication, feeds.image,
                    activities.name AS type, activities.scorecard,  activities.color, activities.tag,
                    feeds.time_beginning, feeds.time_ending, feeds.progress, feeds.calories,
                    feeds.commentactivity, feeds.id AS feed_id,
                    (SELECT COUNT(*) FROM likes WHERE likes.feed_id = feeds.id) AS like_count,
                    (SELECT COUNT(*) FROM likes WHERE likes.feed_id = feeds.id AND likes.user_id = %s) AS is_liked
                FROM feeds
                JOIN users ON feeds.author_id = users.id
                JOIN activities ON feeds.activity_id = activities.id
            """, (user_id,), fetchall=True)

            # if isinstance(posts, list):
            #     print("Posts:", posts)

            formatted_posts = []
            for post in posts:
                time_beginning_obj = datetime.strptime(str(post[11]), '%H:%M:%S').time()
                time_ending_obj = datetime.strptime(str(post[12]), '%H:%M:%S').time()

                time_delta = datetime.combine(datetime.min, time_ending_obj) - datetime.combine(datetime.min,
                                                                                                time_beginning_obj)
                hours = time_delta.seconds // 3600
                minutes = (time_delta.seconds % 3600) // 60
                timestamp_obj = post[5].replace(tzinfo=pytz.UTC)
                timestamp_str = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')

                print("post id", post[16])
                print("likeCount", post[17])
                print("like?", post[18])

                formatted_post = {
                    'id': post[0],
                    'username': post[1],
                    # 'name': post[2],
                    'fireCount': post[3],
                    'miniAvatar': post[4],
                    'timestamp': timestamp_str,
                    'image': post[6],
                    'type': post[7],
                    'scorecard': post[8],
                    'color': post[9],
                    'tag': post[10],
                    'time': f"{hours:02}:{minutes:02}",
                    'progress': post[13],
                    'calories': post[14],
                    'text': post[15],
                    'feed_id': post[16],
                    'likeCount': post[17],
                    'isLiked': post[18] > 0
                    # 'isLiked': False,
                }
                formatted_posts.append(formatted_post)

            formatted_posts = sorted(formatted_posts, key=lambda x: x['timestamp'], reverse=True)
            return jsonify({'status': 200, 'posts': formatted_posts})

    # проверка доступа на редактирование есть у фронта?
    @app.route('/user/<int:user_id>/edit_post/<int:post_id>', methods=['PUT'])
    def edit_post(user_id, post_id):
            post = execute_query("SELECT * FROM feeds WHERE id = %s", args=(post_id,))
            if not post:
                return jsonify({'status': 404, 'message': 'Post not found'})

            post_author_id = post[1]

            if post_author_id != user_id:
                return jsonify({'status': 403, 'message': 'Forbidden: You can only edit your own posts'})

            data = request.get_json()

            # что еще можно изменить?
            execute_query("""
                    UPDATE feeds
                    SET status = True, progress = %s, activity_id = %s, commentactivity = %s, proof = %s, calories = %s,
                        time_beginning = %s, time_ending = %s, image = %s
                    WHERE id = %s
                """, args=(data['distance'], data['type'], data['description'], data['verification'], data['calories'],
                           data['startTime'], data['endTime'], data['image']), update=True)

            # пересчет баллов пользователя + команды?
            recalculate_user_points(user_id)

            #запрос на выборку нужной команды
            team_id = execute_query("SELECT team_id FROM users WHERE id = %s", args=(user_id,))
            calculate_team_points(team_id)

            return jsonify({'status': 200, 'message': 'Post updated successfully'})

    # проверка доступа на удаление есть у фронта?
    @app.route('/user/<int:user_id>/delete_post/<int:post_id>', methods=['DELETE'])  # <int:post_id>
    def delete_post(user_id, post_id):
            post = execute_query("SELECT * FROM feeds WHERE id = %s", args=(post_id,))
            if not post:
                return jsonify({'status': 404, 'message': 'Post not found'})

            # post_author_id = post['author_id']
            post_author_id = post[1]

            if post_author_id != user_id:
                return jsonify({'status': 403, 'message': 'Forbidden: You can only delete your own posts'})

            execute_query("DELETE FROM feeds WHERE id = %s", args=(post_id,), delete=True)  #каскадное удаление на бд

            return jsonify({'status': 200, 'message': 'Post deleted successfully'})