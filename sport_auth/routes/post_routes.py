from flask import jsonify, request, send_from_directory
from flasgger import Swagger, swag_from
from database import execute_query
from admin.recalc_points import recalculate_user_points
from admin.create_teams import calculate_team_points
import datetime
from datetime import datetime, time, timedelta
import os
import pytz
from routes.auth_routes import token_required

def init_post_routes(app):
    @app.route('/user/list_of_activities', methods=['GET'])
    @token_required
    @swag_from({
        'responses': {
            200: {
                'description': 'List of activities available for the user',
                'examples': {
                    'application/json': {
                        'status': 200,
                        'activities': [
                            {'type': 'Running', 'scorecard': 'High', 'color': '#FF0000', 'tag': 'run'}
                        ]
                    }
                }
            }
        }
    })
    def list_of_activities():
        """Get a list of activities
        This endpoint returns a list of available activities.
        ---
        parameters:
          - name: user_id
            in: path
            type: integer
            required: true
            description: ID of the user
        responses:
          200:
            description: List of activities
        """


        user_id = request.user_id
        activities = execute_query('SELECT name, scorecard, color, tag FROM activities ORDER BY id ASC', fetchall=True)

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
    @swag_from({
        'responses': {
            200: {
                'description': 'Image successfully uploaded',
                'examples': {
                    'application/json': {
                        'imageUrl': '/path/to/uploaded/image'
                    }
                }
            },
            400: {
                'description': 'Bad request - image file not provided or empty'
            },
            500: {
                'description': 'Server error - upload failed'
            }
        }
    })

    def upload_image():
        """Upload an image file
        This endpoint allows uploading an image file.
        ---
        consumes:
          - multipart/form-data
        parameters:
          - name: image
            in: formData
            type: file
            required: true
            description: The image file to upload
        responses:
          200:
            description: Image successfully uploaded
          400:
            description: No image provided or no image selected
          500:
            description: Upload failed
        """

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

    #def calculate_calories(weight, duration_hours, activity_met):
    #    return activity_met * weight * duration_hours

    """
    def parse_duration(duration_str):
        hours, minutes = map(int, duration_str.split(':'))
        return timedelta(hours=hours, minutes=minutes)
    """

    @app.route('/user/activities', methods=['POST'])  # изменить на create_post
    @token_required
    @swag_from({
        'responses': {
            200: {
                'description': 'Activity successfully created',
                'examples': {
                    'application/json': {
                        'status': 200,
                        'message': 'Post created successfully'
                    }
                }
            },
            400: {
                'description': 'Bad request - activity already exists or required data is missing'
            },
            500: {
                'description': 'Server error - activity creation failed'
            }
        }
    })
    def activities():
            """Create a new activity
            This endpoint creates a new activity record for the user.
            ---
            parameters:
              - name: body
                in: body
                required: true
                schema:
                  type: object
                  properties:
                    startTime:
                      type: string
                      format: time
                      description: Start time of the activity
                    duration:
                      type: string
                      format: duration
                      description: Duration of the activity in HH:MM format
                    type:
                      type: string
                      description: Type of activity
                    description:
                      type: string
                      description: Description of the activity
                    verification:
                      type: string
                      description: Verification proof of the activity
                    image:
                      type: string
                      description: Image related to the activity
                    startDate:
                      type: string
                      format: date
                      description: Date of the activity
                    other:
                      type: string
                      description: Additional activity details (if applicable)
                description: JSON payload containing activity details
            responses:
              200:
                description: Activity successfully created
              400:
                description: Bad request
              500:
                description: Internal server error
            """

            user_id = request.user_id

            data = request.get_json()
            time_of_publication = datetime.now()
            status = False  # false пока не изменен пост
            #distance = data.get('distance')
            #calories = data.get('calories')  # км/ч/шаги
            time_beginning = data.get('startTime')
            duration = data.get('duration')
            activity_name = data.get('type')
            commentactivity = data.get('description')
            proof = data.get('verification')
            image = data.get('image')
            activity_date = data.get('startDate')
            other_activity = data.get('other')

            activity = execute_query('SELECT id, met, proportion_points FROM activities WHERE tag = %s', (activity_name,))
            if not activity:
                return jsonify({'status': 400, 'message': 'Activity not found'})

            activity_id, activity_met, proportion_points = activity[0], activity[1], activity[2]

            steps = data.get('step') if activity_id in [0, 1] else None
            distance = data.get('distance') if activity_id in [0, 1, 2, 5] else None

            time_beginning_obj = datetime.strptime(time_beginning, '%H:%M').time()

            hours, minutes = map(int, duration.split(':'))
            duration_delta = timedelta(hours=hours, minutes=minutes)

            time_ending_obj = (datetime.combine(datetime.min, time_beginning_obj) + duration_delta).time()

            overlapping_activity = execute_query(
                '''
                   SELECT id FROM feeds
                   WHERE author_id = %s
                   AND activity_date = %s
                   AND (
                     (%s::time BETWEEN time_beginning AND time_beginning + %s::interval) OR
                     (%s::time BETWEEN time_beginning AND time_beginning + %s::interval) OR
                     (time_beginning BETWEEN %s::time AND %s::time) OR
                     (time_beginning + %s::interval BETWEEN %s::time AND %s::time)
                   )
                ''',
                (user_id, activity_date, time_beginning, duration, time_beginning, duration, time_beginning, time_ending_obj, duration, time_beginning, time_ending_obj)
            )

            if overlapping_activity:
                return jsonify({'status': 400, 'message': 'Activity already exists at this time', 'error_code': 'TIME_OVERLAP'})

            try:
                # вес
                user_weight = execute_query("SELECT weight FROM users WHERE id = %s", (user_id,))
                if not user_weight:
                    return jsonify({'status': 400, 'message': 'Weight data not found for user'})
                user_weight = user_weight[0]

                #рост если Ходьба
                if activity_id in [0]:
                    user_height = execute_query("SELECT height FROM users WHERE id = %s", (user_id,))
                    if not user_height:
                        gender = execute_query("SELECT gender FROM users WHERE id = %s", (user_id,))
                        if not gender:
                            return jsonify({'status': 400, 'message': 'Height and Gender data not found for user'})
                        stride = 0.68 if gender[0] == 'Ж' else 0.73
                    else:
                        stride = user_height[0] * 0.01 * 0.414
                    distance = round(stride * float(steps) * 0.001, 2) # перевод в км

                # данные поста
                execute_query(
                    'INSERT INTO feeds (author_id, time_of_publication, status, distance, activity_id, commentactivity, time_beginning, duration, proof, image, steps, activity_date, other_activity, time_ending) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (user_id, time_of_publication, status, distance, activity_id, commentactivity,
                     time_beginning, duration, proof, image, steps, activity_date, other_activity, time_ending_obj), insert=True)

                #duration_hours = 1
                # длительность активности
                # йога, сила, танцы, кардио, игры, другое
                if activity_id in [3, 4, 6, 7, 8, 9]:
                    hours, minutes = map(int, duration.split(':'))
                    duration_hours = hours + minutes / 60.0

                # бег, вело, плавание
                if activity_id in [1, 2, 5]:
                    distance = float(distance)
                    if activity_id in [2]:
                         distance = round(distance * 0.001, 2) # перевод в км
                    avg_speed = execute_query('SELECT avg_speed FROM activities WHERE id = %s', (activity_id,))
                    #duration_hours = 2
                    duration_hours = distance / avg_speed[0] # в часах

                calories_burned = activity_met * user_weight * duration_hours
                activity_points = int(calories_burned * proportion_points / 100) # переводим калории в баллы по коэффициенту *10

                # добавление калорий в активность
                execute_query(
                    'UPDATE feeds SET calories = %s WHERE id = (SELECT id FROM feeds WHERE author_id = %s ORDER BY time_of_publication DESC LIMIT 1)',
                    (calories_burned, user_id,), update=True)

                # начисление баллов
                if activity_points:
                    execute_query('UPDATE users SET points = points + %s WHERE id = %s', (activity_points, user_id),
                                  update=True)

                author_team = execute_query('SELECT team_id FROM users WHERE id = %s', (user_id,))
                print('author_team', author_team)
                calculate_team_points(author_team)
                return jsonify({'status': 200, 'message': 'Post created successfully'})
            except Exception as e:
                print("Error creating post:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/user/posts', methods=['GET'])
    @token_required
    @swag_from({
        'responses': {
            200: {
                'description': 'List of posts for the user',
                'examples': {
                    'application/json': {
                        'status': 200,
                        'posts': [
                            {
                                'id': 1,
                                'username': 'John',
                                'name': 'Doe',
                                'fireCount': 100,
                                'miniAvatar': '/path/to/avatar.png',
                                'timestamp': '2024-12-01 14:00:00',
                                'image': '/path/to/image.jpg',
                                'type': 'Running',
                                'scorecard': 'High',
                                'color': '#FF0000',
                                'tag': 'run',
                                'time': '01:30',
                                'distance': 10.5,
                                'calories': 350,
                                'text': 'Morning run in the park!',
                                'feed_id': 123,
                                'likeCount': 25,
                                'isLiked': True,
                                'commentCount': 3,
                                'step': 10000
                            }
                        ]
                    }
                }
            },
            500: {
                'description': 'Server error - failed to retrieve posts'
            }
        }
    })
    def posts():
        """Retrieve user posts
        This endpoint retrieves all posts created by the user.
        ---
        parameters:
          - name: user_id
            in: path
            type: integer
            required: true
            description: ID of the user
        responses:
          200:
            description: List of posts
          500:
            description: Internal server error
        """

        user_id = request.user_id
        try:
            posts = execute_query("""
                SELECT
                    users.id, users.surname, users.name, users.points, users.avatar,
                    feeds.time_of_publication, feeds.image,
                    activities.name AS type, activities.scorecard,  activities.color, activities.tag,
                    feeds.time_beginning, feeds.duration, feeds.distance, feeds.calories,
                    feeds.commentactivity, feeds.id AS feed_id,
                    (SELECT COUNT(*) FROM likes WHERE likes.feed_id = feeds.id) AS like_count,
                    (SELECT COUNT(*) FROM likes WHERE likes.feed_id = feeds.id AND likes.user_id = %s) AS is_liked,
                    (SELECT COUNT(*) FROM comments WHERE comments.feed_id = feeds.id) AS comment_count,
                    feeds.steps, feeds.other_activity
                FROM feeds
                JOIN users ON feeds.author_id = users.id
                JOIN activities ON feeds.activity_id = activities.id
            """, (user_id,), fetchall=True)

            formatted_posts = []
            for post in posts:
                duration = post[12]
                hours, minutes = map(int, duration.split(':'))
                formatted_duration = f"{hours:02}:{minutes:02}"

                timestamp_obj = post[5].replace(tzinfo=pytz.UTC) + timedelta(hours=3)
                timestamp_str = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')

                activity_type = post[21] if post[10] == 'other' and post[21] is not None else post[7]

                formatted_post = {
                    'id': post[0],
                    'username': post[1],
                    'name': post[2],
                    'fireCount': post[3],
                    'miniAvatar': post[4],
                    'timestamp': timestamp_str,
                    'image': post[6],
                    'type': activity_type,
                    'scorecard': post[8],
                    'color': post[9],
                    'tag': post[10],
                    'time': formatted_duration,
                    'distance': post[13],
                    'calories': post[14],
                    'text': post[15],
                    'feed_id': post[16],
                    'likeCount': post[17],
                    'isLiked': post[18] > 0,
                    'commentCount': post[19],
                    'step': post[20]
                }
                formatted_posts.append(formatted_post)

            formatted_posts = sorted(formatted_posts, key=lambda x: x['timestamp'], reverse=True)
            return jsonify({'status': 200, 'posts': formatted_posts})
        except Exception as e:
            print("Error liking feed:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    # проверка доступа на редактирование есть у фронта?
    @app.route('/user/edit_post/<int:post_id>', methods=['PUT'])
    @token_required
    def edit_post(post_id):
        user_id = request.user_id
        try:
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
        except Exception as e:
            print("Error liking feed:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    # проверка доступа на удаление есть у фронта?
    @app.route('/user/delete_post/<int:post_id>', methods=['DELETE'])  # <int:post_id>
    @token_required
    def delete_post(post_id):
        user_id = request.user_id
        try:
            post = execute_query("SELECT * FROM feeds WHERE id = %s", args=(post_id,))

            if not post:
                return jsonify({'status': 404, 'message': 'Post not found'})

            # post_author_id = post['author_id']
            post_author_id = post[1]

            if post_author_id != user_id:
                return jsonify({'status': 403, 'message': 'Forbidden: You can only delete your own posts'})

            execute_query("DELETE FROM feeds WHERE id = %s", args=(post_id,), delete=True)  #каскадное удаление на бд

            return jsonify({'status': 200, 'message': 'Post deleted successfully'})
        except Exception as e:
            print("Error liking feed:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

