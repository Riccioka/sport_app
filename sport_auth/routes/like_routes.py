from flask import jsonify, request
from routes.auth_routes import session
from database import execute_query

def init_like_routes(app):
    @app.route('/like', methods=['POST'])
    def like_post():
        if 'loggedin' in session:
            data = request.get_json()
            user_id = session['id']
            feed_id = data.get('post_id')

            try:
                existing_like = execute_query("SELECT * FROM likes WHERE user_id = %s AND feed_id = %s",
                                              (user_id, feed_id))
                if existing_like:
                    return jsonify({'status': 400, 'message': 'User has already liked this feed'})

                execute_query("INSERT INTO likes (user_id, feed_id) VALUES (%s, %s)", (user_id, feed_id), insert=True)

                like_count = execute_query("SELECT COUNT(*) FROM likes WHERE feed_id = %s", (feed_id,))[0] #, fetchone=True

                return jsonify({'status': 200, 'message': 'Feed liked successfully', 'likeCount': like_count})
            except Exception as e:
                print("Error liking feed:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})
        else:
            return jsonify({'status': 401, 'message': 'Unauthorized'})

    @app.route('/unlike', methods=['POST'])
    def unlike_post():
        if 'loggedin' in session:
            data = request.get_json()
            user_id = session['id']
            feed_id = data.get('post_id')

            try:
                like_exists = execute_query("SELECT * FROM likes WHERE user_id = %s AND feed_id = %s",
                                            (user_id, feed_id), fetchall=False)

                if not like_exists:
                    return jsonify({'status': 400, 'message': 'Like not found'})

                execute_query("DELETE FROM likes WHERE user_id = %s AND feed_id = %s", (user_id, feed_id), delete=True)

                like_count = execute_query("SELECT COUNT(*) FROM likes WHERE feed_id = %s", (feed_id,))[0] #, fetchone=True

                return jsonify({'status': 200, 'message': 'Feed unliked successfully', 'likeCount': like_count})

            except Exception as e:
                print("Error unliking feed:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})
        else:
            return jsonify({'status': 401, 'message': 'Unauthorized'})

    @app.route('/post/likecount/<int:post_id>', methods=['GET'])
    def get_like_count(post_id):
        try:
            like_count = execute_query("SELECT COUNT(*) FROM likes WHERE feed_id = %s", (post_id,))
            return jsonify({'status': 200, 'likeCount': like_count})
        except Exception as e:
            print("Error fetching like count:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})
