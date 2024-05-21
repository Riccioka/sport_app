from database import execute_query
from flask import request, jsonify
from routes.auth_routes import session

def init_comment_routes(app):
    @app.route('/comment', methods=['POST'])
    def comment_post():
        if 'loggedin' in session:
            data = request.get_json()
            author_id = session['id']
            feed_id = data.get('post_id')
            comment_text = data.get("comment_text")

            # время надо? created_at
            try:
                execute_query("INSERT INTO comments (author_id, feed_id, comment_text) VALUES (%s, %s, %s)",
                              (author_id, feed_id, comment_text), insert=True)
                # comment_count = get_comment_count(id, )[0]
                comment_count = execute_query("SELECT COUNT(*) FROM comments WHERE feed_id = %s", (feed_id,))[0]
                return jsonify({'status': 200, 'message': 'Feed commented successfully', 'commentCount': comment_count})
            except Exception as e:
                print("Error commenting feed:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})
        else:
            return jsonify({'status': 401, 'message': 'Unauthorized'})

# edit + delete
    # проверка доступа на удаление есть у фронта?
    @app.route('/delete_comment/<int:post_id>', methods=['DELETE'])  # <int:post_id>
    def delete_comment(id):
        if 'loggedin' in session:
            user_id = session['user_id']
            comment = execute_query("SELECT * FROM comments WHERE id = %s", args=(id,))
            if not comment:
                return jsonify({'status': 404, 'message': 'Comment not found'})

            comment_author_id = comment[1]

            if comment_author_id != user_id:
                return jsonify({'status': 403, 'message': 'Forbidden: You can only delete your own comments'})

            execute_query("DELETE FROM comments WHERE id = %s", args=(id,), delete=True)
            comment_count = get_comment_count(id,)[0]
            # comment_count = execute_query("SELECT COUNT(*) FROM likes WHERE feed_id = %s", (id,))[0]

            return jsonify({'status': 200, 'message': 'Comment deleted successfully', 'commentCount': comment_count})
        else:
            return jsonify({'status': 401, 'message': 'Unauthorized'})

    @app.route('/post/comment_count/<int:post_id>', methods=['GET'])
    def get_comment_count(post_id):
        try:
            comment_count = execute_query("SELECT COUNT(*) FROM comments WHERE feed_id = %s", (post_id,))
            return jsonify({'status': 200, 'commentCount': comment_count})
        except Exception as e:
            print("Error fetching like count:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})
