from flask import jsonify, request
from routes.auth_routes import session
from database import execute_query
import datetime
from datetime import datetime, time
import os
import base64
from flask_cors import CORS

def init_post_routes(app):
    @app.route('/list_of_activities', methods=['GET'])
    def list_of_activities():
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


    @app.route('/activities', methods=['POST']) # изменить на create_post
    def activities():
        if request.method == 'POST':
            if 'id' in session:
                author_id = session['id']
            else:
                return jsonify({'status': 401, 'message': 'Unauthorized'})

            data = request.get_json()
            time_of_publication = datetime.now()
            status = False  # false пока не изменен пост
            progress = data.get('distance')
            calories = data.get('calories')  # км/ч/шаги
            time_beginning = data.get('startTime')
            time_ending = data.get('endTime')
            activity_id = 3
            # activity_id = data.get('type')
            commentactivity = data.get('description')
            proof = data.get('verification')
            image = data.get('image')

            try:
                execute_query(
                    'INSERT INTO feeds (author_id, time_of_publication, status, progress, activity_id, commentactivity, calories, time_beginning, time_ending, proof, image) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (author_id, time_of_publication, status, progress, activity_id, commentactivity, calories,
                     time_beginning, time_ending, proof, image), insert=True)

                activity_points = execute_query('SELECT proportion_steps FROM activities WHERE id = %s', (activity_id,))
                if activity_points:
                    execute_query('UPDATE users SET points = points + %s WHERE id = %s', (activity_points[0], author_id),
                                  update=True)

                return jsonify({'status': 200, 'message': 'Post created successfully'})
            except Exception as e:
                print("Error creating post:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})
        return jsonify({'status': 401, 'message': 'Unauthorized'})


    @app.route('/posts', methods=['GET'])
    def posts():
        if 'loggedin' in session:
            posts = execute_query("""
                SELECT
                    users.id, users.surname, users.name, users.points, users.avatar,
                    feeds.time_of_publication, feeds.proof,
                    activities.name AS type, activities.scorecard,  activities.color,
                    feeds.time_beginning, feeds.time_ending, feeds.progress, feeds.calories,
                    feeds.commentactivity
                FROM feeds
                JOIN users ON feeds.author_id = users.id
                JOIN activities ON feeds.activity_id = activities.id
            """, fetchall=True)

            # if isinstance(posts, list):
            #     print("Posts:", posts)

            formatted_posts = []
            for post in posts:
                # print("time of publication = ", post[5])

                time_beginning_str = str(post[10])
                time_ending_str = str(post[11])

                time_beginning_obj = datetime.strptime(time_beginning_str, '%H:%M:%S').time()
                time_ending_obj = datetime.strptime(time_ending_str, '%H:%M:%S').time()

                time_delta = datetime.combine(datetime.min, time_ending_obj) - datetime.combine(datetime.min,
                                                                                                time_beginning_obj)

                hours = time_delta.seconds // 3600
                minutes = (time_delta.seconds % 3600) // 60

                time = {'hours': hours, 'minutes': minutes}

                # print(time)

                formatted_post = {
                    'id': post[0],
                    'username': post[1],
                    # 'name': post[2],
                    'fireCount': post[3],
                    'miniAvatar': post[4],
                    'timestamp': post[5],
                    'image': post[6],
                    'title': post[7],
                    'scorecard': post[8],
                    'color': post[9],
                    # 'time': time,
                    'time': f"{hours:02}:{minutes:02}",
                    'progress': post[12],
                    'calories': post[13],
                    'text': post[14],
                    # 'isLiked': post['isLiked'],
                    # 'likeCount': post['likeCount'],
                }
                formatted_posts.append(formatted_post)

            return jsonify({'status': 200, 'posts': formatted_posts})
        else:
            return jsonify({'status': 401, 'message': 'Unauthorized'})


    @app.route('/edit_post/<int:post_id>', methods=['PUT'])
    def edit_post(post_id):
        if 'loggedin' in session:
            data = request.get_json()

            # что еще можно изменить?
            execute_query("""
                    UPDATE feeds
                    SET title = %s, text = %s
                    WHERE id = %s
                """, args=(data['title'], data['text'], post_id))

            return jsonify({'status': 200, 'message': 'Post updated successfully'})
        else:
            return jsonify({'status': 401, 'message': 'Unauthorized'})

    @app.route('/delete_post/<int:post_id>', methods=['DELETE'])
    def delete_post(post_id):
        if 'loggedin' in session:
            post = execute_query("SELECT * FROM feeds WHERE id = %s", args=(post_id,), fetchone=True)
            if not post:
                return jsonify({'status': 404, 'message': 'Post not found'})

            execute_query("DELETE FROM feeds WHERE id = %s", args=(post_id,))

            return jsonify({'status': 200, 'message': 'Post deleted successfully'})
        else:
            return jsonify({'status': 401, 'message': 'Unauthorized'})