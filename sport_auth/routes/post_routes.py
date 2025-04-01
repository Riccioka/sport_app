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
    def create_post():
        user_id = request.user_id
        data = request.get_json()

        # проверка и извлечение данных
        try:
            activity_data = validate_activity_data(data)
        except ValueError as e:
            return jsonify({'status': 400, 'message': str(e)})

        # проверка существования активности
        activity = get_activity_by_name(activity_data['type'])
        if not activity:
            return jsonify({'status': 400, 'message': 'Activity not found'})

        activity_id, activity_met, proportion_points = activity[0], activity[1], activity[2]
        #activity_id, activity_met, proportion_points = activity

        # проверка перекрытия времени
        # if check_time_overlap(user_id, activity_data['startDate'], activity_data['startTime'],
        #                       activity_data['duration']):
        #     return jsonify(
        #         {'status': 400, 'message': 'Activity already exists at this time', 'error_code': 'TIME_OVERLAP'})

        # вычисляем расстояние, длительность и калории
        user_data = get_user_data(user_id)
        if not user_data:
            return jsonify({'status': 400, 'message': 'User data not found'})

        # Расчёт эталонного значения калорий для 1 км ходьбы
        walking_activity = get_activity_by_name('walk')
        if not walking_activity:
            return jsonify({'status': 500, 'message': 'Walking activity not configured'})

        walking_met, walking_speed = walking_activity[1], execute_query(
            'SELECT avg_speed FROM activities WHERE id = %s', (walking_activity[0],))[0]
        calories_per_km = calculate_calories_per_km(user_data['weight'], walking_met, walking_speed)

        distance, duration_hours = calculate_activity_metrics(activity_id, activity_data, user_data, user_id)
        calories_burned, activity_points = calculate_calories_and_points(
            activity_id, activity_met, activity_data, user_data, duration_hours, calories_per_km, user_id)

        # сохраняем данные активности
        try:
            save_activity(
                user_id, activity_data, activity_id, distance, calories_burned, activity_points, duration_hours
            )
            return jsonify({'status': 200, 'message': 'Post created successfully'})
        except Exception as e:
            print("Error creating post:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    # Вспомогательные функции

    def validate_activity_data(data):
        """Проверка и извлечение данных активности"""
        required_fields = ['startTime', 'type', 'startDate']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')

        return {
            'startTime': data['startTime'],
            'duration': calculate_duration(data),
            'type': data['type'],
            'startDate': data['startDate'],
            'steps': calculate_steps(data),
            'description': data.get('description'),
            'verification': data.get('verification'),
            'image': data.get('image'),
            'other': data.get('other'),
            'distance': data.get('distance'),
            'time_of_publication': datetime.now(),
        }

    def calculate_duration(data):
        """вычисление длительности, если ее нет"""
        return None if not data.get('duration') else data['duration']

    def calculate_steps(data):
        """вычисление шагов, если их нет"""
        return 0 if not data.get('step') else data['step']


    def get_activity_by_name(activity_name):
        """получение активности из базы данных"""
        return execute_query(
            'SELECT id, met, proportion_points FROM activities WHERE tag = %s',
            (activity_name,)
        )


    def check_time_overlap(user_id, activity_date, time_beginning, duration):
        """проверка перекрытия времени с другими активностями"""
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
                (%s::time BETWEEN time_beginning AND time_ending) OR
                (%s::time BETWEEN time_beginning AND time_ending) OR
                (time_beginning BETWEEN %s::time AND %s::time)
            )
            ''',
            (user_id, activity_date, time_beginning, time_ending_obj, time_beginning, time_ending_obj)
        )
        return bool(overlapping_activity)

    def get_user_data(user_id):
        """получение данных пользователя"""
        user_weight = execute_query("SELECT weight FROM users WHERE id = %s", (user_id,))
        user_height = execute_query("SELECT height, gender FROM users WHERE id = %s", (user_id,))
        if user_weight and user_height:
            return {
                'weight': user_weight[0],
                'height': user_height[0],
                'gender': user_height[1]
            }
        return None

    def get_user_speed(user_id, activity_id):
        """получение скорости пользователя в зависимости от лиги"""
        user_league = execute_query("SELECT league FROM users WHERE id = %s", (user_id,))
        if user_league[0] == 'silver':
            user_speed = execute_query("SELECT avg_speed FROM activities WHERE id = %s", (activity_id,))
        elif user_league[0] == 'gold':
            user_speed = execute_query("SELECT high_speed FROM activities WHERE id = %s", (activity_id,))
        else:
            user_speed = execute_query("SELECT low_speed FROM activities WHERE id = %s", (activity_id,))
        return user_speed[0]

    def calculate_activity_metrics(activity_id, activity_data, user_data, user_id):
        """вычисление метрик активности"""
        # если пользователь ввёл длительность, используем её

        try:
            duration = activity_data['duration']
        except Exception as e:
            print("Error creating post:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

        if duration:
            try:
                hours, minutes = map(int, activity_data['duration'].split(':'))
                duration_hours = hours + minutes / 60.0
            except ValueError:
                raise ValueError("Invalid duration format. It must be 'HH:MM'.")
        else:
            duration_hours = None

        if activity_id == 0:  # ходьба
            # если пользователь указал расстояние, используем его
            if activity_data.get('distance'):
                distance = float(activity_data['distance'])
            else:
                stride = user_data['height'] * 0.01 * 0.414
                distance = stride * float(activity_data['steps']) * 0.001  # расчет по шагам

            if not duration_hours:
                avg_speed = execute_query('SELECT avg_speed FROM activities WHERE id = %s', (activity_id,))
                duration_hours = distance / avg_speed[0]

        elif activity_id in [1, 2, 5]:  # бег, вело, плавание
            distance = float(activity_data['distance'])
            if activity_id == 2:  # плавание
                # distance = round(distance * 0.001, 5)  # в км
                distance = distance * 0.001
            if not duration_hours:
                avg_speed = get_user_speed(user_id, activity_id)
                duration_hours = distance / avg_speed
        else:
            if duration_hours is None:  # для остальных активностей длительность обязательна
                hours, minutes = map(int, activity_data['duration'].split(':'))
                duration_hours = hours + minutes / 60.0
            distance = None

        if activity_id == 2:  # плавание
            return (distance,
                    +duration_hours)
        return round(distance, 2) if distance else None, duration_hours
        # return distance if distance else None, duration_hours

    def calculate_stride(height, gender):
        """вычисление длины шага"""
        if height > 0:
            return height * 0.00414
        elif gender == 'М':
            return 0.73
        elif gender == 'Ж':
            return 0.68
        else:
            return 0.705


    def calculate_calories_and_points(activity_id, met, activity_data, user_data, duration_hours, calories_per_km, user_id):
        """вычисление калорий и очков активности"""
        # calories_burned = met * weight * duration_hours

        avg_speed = execute_query('SELECT avg_speed FROM activities WHERE id = %s', (activity_id,))
        avg_speed = avg_speed[0]

        if activity_id == 0:  # ходьба
            if float(activity_data['steps']) > 0:
                stride = calculate_stride(user_data['height'], user_data['gender'])
                calories_burned_per_kg = met * float(activity_data['steps']) * stride * 0.001/ avg_speed
            else:
                calories_burned_per_kg = met * float(activity_data['distance']) / avg_speed

        elif activity_id in [1, 5]:  # бег, вело
            avg_speed = get_user_speed(user_id, activity_id)
            calories_burned_per_kg = met * float(activity_data['distance']) / avg_speed
        elif activity_id == 2:
            avg_speed = get_user_speed(user_id, activity_id)
            calories_burned_per_kg = met * (float(activity_data['distance']) / 1000) / avg_speed
        else:
            calories_burned_per_kg = met * duration_hours

        calories_burned = calories_burned_per_kg * user_data['weight']

        # if activity_id == 2:
        #     activity_points = int((calories_burned / calories_per_km / 1000 )  * 10)
        # else:
        activity_points = int((calories_burned / calories_per_km) * 10)

        return calories_burned, activity_points


    def calculate_calories_per_km(weight, walking_met, walking_speed):
        """эталонное количество калорий для 1 км ходьбы"""
        duration_per_km = 60 / walking_speed  # время в минутах на 1 км
        calories_per_km = walking_met * weight * (duration_per_km / 60)  # калории для 1 км
        return calories_per_km

    def save_activity(user_id, activity_data, activity_id, distance, calories_burned, activity_points, duration_hours):
        """сохранение активности в базу"""

        time_beginning_obj = datetime.strptime(activity_data['startTime'], '%H:%M').time()

        hours = int(duration_hours)
        minutes = int((duration_hours - hours) * 60) #minutes = int((duration_hours - hours) * 100)
        duration_delta = timedelta(hours=hours, minutes=minutes)
        duration_formatted = f"{hours:02}:{minutes:02}"

        # вычисление времени окончания
        time_ending_obj = (datetime.combine(datetime.min, time_beginning_obj) + duration_delta).time()

        if activity_id == 2:  # плавание
            distance = round(distance * 1000, 2)  # в м (проверить СС в вычислениях)

        execute_query(
            '''
            INSERT INTO feeds (author_id, status, distance, activity_id, time_of_publication, commentactivity, duration, 
                                time_beginning, proof, image, steps, activity_date, other_activity, time_ending, calories, points)
            VALUES (%s, false, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                user_id, distance, activity_id, activity_data['time_of_publication'], activity_data['description'], duration_formatted,
                activity_data['startTime'], activity_data['verification'], activity_data['image'], activity_data['steps'],
                activity_data['startDate'], activity_data['other'], time_ending_obj, calories_burned, activity_points
            ),
            insert=True
        )

        if activity_points:
            execute_query('UPDATE users SET points = points + %s WHERE id = %s', (activity_points, user_id),
                          update=True)

    @app.route('/user/preview_post', methods=['POST'])
    @token_required
    def preview_post():
        user_id = request.user_id
        data = request.get_json()

        try:
            activity_data = validate_activity_data(data)
        except ValueError as e:
            return jsonify({'status': 400, 'message': str(e)})

        activity = get_activity_by_name(activity_data['type'])
        if not activity:
            return jsonify({'status': 400, 'message': 'Activity not found'})

        activity_id, activity_met, proportion_points = activity

        user_data = get_user_data(user_id)
        if not user_data:
            return jsonify({'status': 400, 'message': 'User data not found'})

        walking_activity = get_activity_by_name('walk')
        if not walking_activity:
            return jsonify({'status': 500, 'message': 'Walking activity not configured'})

        walking_met, walking_speed = walking_activity[1], execute_query(
            'SELECT avg_speed FROM activities WHERE id = %s', (walking_activity[0],))[0]
        calories_per_km = calculate_calories_per_km(user_data['weight'], walking_met, walking_speed)

        distance, duration_hours = calculate_activity_metrics(activity_id, activity_data, user_data, user_id)

        if activity_id == 2:  # плавание
            distance = round(distance * 1000, 2) # в м

        calories_burned, activity_points = calculate_calories_and_points(
            activity_id, activity_met, activity_data, user_data, duration_hours, calories_per_km, user_id)

        hours = int(duration_hours)
        minutes = int((duration_hours - hours) * 60)
        duration_formatted = f"{hours:02}:{minutes:02}"

        preview_data = {
            'distance': distance,
            'duration_hours': duration_formatted,
            #'time': duration_formatted,
            'calories_burned': round(calories_burned),
            'activity_points': activity_points,
            'activity_data': activity_data
        }

        return jsonify({'status': 200, 'preview_data': preview_data})


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
                    feeds.steps, feeds.other_activity, feeds.points, feeds.activity_date
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
                    'postfireCount': post[22],
                    'activityDate': post[23].strftime('%Y-%m-%d'),
                    'timeBeginning': post[11].strftime('%H:%M')
                    # 'step': post[20]
                }
                if post[20] > 0:
                    formatted_post['step'] = post[20]

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

