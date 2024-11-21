from flask import jsonify, request
from database import execute_query
from routes.auth_routes import token_required

def init_like_routes(app):
    @app.route('/user/like', methods=['POST'])
    @token_required
    def like_post():
        user_id = request.user_id

        data = request.get_json()
        feed_id = data.get('post_id')

        if not feed_id:
            return jsonify({'status': 400, 'message': 'post id is required'})

        try:
            existing_like = execute_query(
                "SELECT * FROM likes WHERE user_id = %s AND feed_id = %s",
                (user_id, feed_id),
                fetchall=True
            )
            if existing_like:
                return jsonify({'status': 400, 'message': 'User has already liked this feed'})

            execute_query(
                "INSERT INTO likes (user_id, feed_id) VALUES (%s, %s)",
                (user_id, feed_id),
                insert=True
            )

            like_count_result = execute_query(
                "SELECT COUNT(*) FROM likes WHERE feed_id = %s",
                (feed_id,),
                fetchall=False
            )
            like_count = like_count_result[0] if like_count_result else 0

            return jsonify({'status': 200, 'message': 'Feed liked successfully', 'likeCount': like_count})
        except Exception as e:
            print("Error liking feed:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/user/unlike', methods=['POST'])
    @token_required
    def unlike_post():
        user_id = request.user_id

        data = request.get_json()
        feed_id = data.get('post_id')

        if not feed_id:
            return jsonify({'status': 400, 'message': 'post id is required'})

        try:
            like_exists = execute_query(
                "SELECT * FROM likes WHERE user_id = %s AND feed_id = %s",
                (user_id, feed_id),
                fetchall=True
            )

            if not like_exists or len(like_exists) == 0:
                return jsonify({'status': 400, 'message': 'Like not found'})

            execute_query(
                "DELETE FROM likes WHERE user_id = %s AND feed_id = %s",
                (user_id, feed_id),
                delete=True
            )

            like_count_result = execute_query(
                "SELECT COUNT(*) FROM likes WHERE feed_id = %s",
                (feed_id,),
                fetchall=False
            )
            like_count = like_count_result[0] if like_count_result else 0

            return jsonify({'status': 200, 'message': 'Feed unliked successfully', 'likeCount': like_count})

        except Exception as e:
            print("Error unliking feed:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/post/like_count/<int:post_id>', methods=['GET'])
    def get_like_count(post_id):
        try:
            like_count_result = execute_query(
                "SELECT COUNT(*) FROM likes WHERE feed_id = %s",
                (post_id,),
                fetchall=False
            )
            like_count = like_count_result[0] if like_count_result else 0

            return jsonify({'status': 200, 'likeCount': like_count})
        except Exception as e:
            print("Error fetching like count:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

