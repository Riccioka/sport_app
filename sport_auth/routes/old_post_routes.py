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

        # проверка перекрытия времени
        # if check_time_overlap(user_id, activity_data['startDate'], activity_data['startTime'],
        #                       activity_data['duration']):
        #     return jsonify(
        #         {'status': 400, 'message': 'Activity already exists at this time', 'error_code': 'TIME_OVERLAP'})

        # получаем данные пользователя
        user_data = get_user_data(user_id)
        if not user_data:
            return jsonify({'status': 400, 'message': 'User data not found'})

        # вычисляем длину шага (stride)
        stride = calculate_stride(user_data['height'], user_data['gender'])

        # вычисляем энергию (E1) и общую энергию (E)
        try:
            e1 = calculate_e1(activity_id, activity_met, activity_data, stride, user_data)
            e = calculate_total_energy(e1, user_data['weight'])
            points = calculate_points(e1)
        except ValueError as e:
            return jsonify({'status': 400, 'message': str(e)})

        # сохраняем данные активности
        try:
            save_activity(
                user_id, activity_data, activity_id, e, points
            )
            return jsonify({'status': 200, 'message': 'Post created successfully'})
        except Exception as e:
            print("Error creating post:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    # вспомогательные функции

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
        result = execute_query(
            'SELECT id, met, proportion_points, avg_speed FROM activities WHERE tag = %s',
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
        user_data = execute_query("SELECT weight, height, gender FROM users WHERE id = %s", (user_id,))
        if user_data:
            return {
                'weight': user_data[0],
                'height': user_data[1],
                'gender': user_data[2]
            }
        return None

    def calculate_stride(height, gender):
        """вычисление длины шага (stride)"""
        if height > 0:
            return height * 0.00414
        elif gender == 'М':
            return 0.73
        elif gender == 'Ж':
            return 0.68
        else:
            return 0.705


    def calculate_e1(activity_id, met, activity_data, stride, user_data):
        """вычисление энергии на 1 кг веса (E1)"""
        if activity_id == 0:  # ходьба
            speed = get_activity_speed(activity_id)
            if float(activity_data['steps']) > 0:
                e1 = met * float(activity_data['steps'])  * stride * 0.001 / speed
            else:
                e1 = met * activity_data['distance'] / speed
        elif activity_id in [1, 2, 5]:  # бег, вело, плавание
            speed = get_activity_speed(activity_id)
            e1 = met * activity_data['distance'] / speed
        elif activity_id in [3, 4, 6, 7, 8, 9]:  # остальные
            duration_hours = calculate_duration_hours(activity_data['duration'])
            e1 = met * duration_hours
        else:
            raise ValueError("Invalid activity ID")

        return e1

    def calculate_duration_hours(duration):
        """преобразование длительности в часы"""
        if not duration:
            raise ValueError("Duration is required for this activity")
        try:
            hours, minutes = map(int, duration.split(':'))
            return hours + minutes / 60.0
        except ValueError:
            raise ValueError("Invalid duration format. It must be 'HH:MM'.")

    def get_activity_speed(activity_id):
        """получение скорости активности из базы данных"""
        speed = execute_query('SELECT avg_speed FROM activities WHERE id = %s', (activity_id,))
        if not speed:
            raise ValueError("Activity speed not found")
        return speed[0]

    def calculate_total_energy(e1, weight):
        """вычисление общей энергии (E)"""
        return e1 * weight

    def calculate_points(e1):
        """вычисление баллов за активность (Points)"""
        es1 = 5 / 6  # базовая энергия (ES1)
        return round(10 * e1 / es1)

    def save_activity(user_id, activity_data, activity_id, energy, points):
        """сохранение активности в базу"""
        time_beginning_obj = datetime.strptime(activity_data['startTime'], '%H:%M').time()
        duration_hours = calculate_duration_hours(activity_data['duration'])
        hours = int(duration_hours)
        minutes = int((duration_hours - hours) * 60)
        duration_formatted = f"{hours:02}:{minutes:02}"

        # вычисление времени окончания
        duration_delta = timedelta(hours=hours, minutes=minutes)
        time_ending_obj = (datetime.combine(datetime.min, time_beginning_obj) + duration_delta).time()

        # if activity_id == 2:  # плавание
        #     distance = round(distance * 1000, 2)  # в м (проверить СС в вычислениях)

        execute_query(
            '''
            INSERT INTO feeds (author_id, status, distance, activity_id, time_of_publication, commentactivity, duration, 
                              time_beginning, proof, image, steps, activity_date, other_activity, time_ending, calories, points)
            VALUES (%s, false, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                user_id, activity_data.get('distance'), activity_id, activity_data['time_of_publication'],
                activity_data['description'], duration_formatted,
                activity_data['startTime'], activity_data['verification'], activity_data['image'],
                activity_data['steps'],
                activity_data['startDate'], activity_data['other'], time_ending_obj, energy, points
            ),
            insert=True
        )

        if points:
            execute_query('UPDATE users SET points = points + %s WHERE id = %s', (points, user_id), update=True)

    @app.route('/user/preview_post', methods=['POST'])
    @token_required
    def preview_post():
        user_id = request.user_id
        data = request.get_json()

        try:
            # Проверка и извлечение данных
            activity_data = validate_activity_data(data)

            # Получение данных активности
            activity = get_activity_by_name(activity_data['type'])
            if not activity:
                return jsonify({'status': 400, 'message': 'Activity not found'})

            activity_id, activity_met, proportion_points, avg_speed = activity

            # Получение данных пользователя
            user_data = get_user_data(user_id)
            if not user_data:
                return jsonify({'status': 400, 'message': 'User data not found'})

            # Вычисление длины шага (stride)
            stride = calculate_stride(user_data['height'], user_data['gender'])

            # Вычисление энергии (E1) и общей энергии (E)
            e1 = calculate_e1(activity_id, activity_met, activity_data, stride, user_data)
            e = calculate_total_energy(e1, user_data['weight'])
            points = calculate_points(e1)

            # Преобразование длительности в формат HH:MM
            duration_hours = calculate_duration_hours(activity_data['duration'])
            hours = int(duration_hours)
            minutes = int((duration_hours - hours) * 60)
            duration_formatted = f"{hours:02}:{minutes:02}"

            # Подготовка данных для предпросмотра
            preview_data = {
                'distance': activity_data.get('distance'),
                'duration_hours': duration_formatted,
                'calories_burned': round(e),
                'activity_points': points,
                'activity_data': activity_data
            }

            return jsonify({'status': 200, 'preview_data': preview_data})

        except ValueError as e:
            return jsonify({'status': 400, 'message': str(e)})
        except Exception as e:
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

