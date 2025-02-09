from flask import request, jsonify
from database import execute_query
from datetime import datetime, time
import logging
from routes.auth_routes import token_required

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

def init_comment_routes(app):
    @app.route('/user/comment', methods=['POST'])
    @token_required
    def comment_post():
        user_id = request.user_id
        data = request.get_json()
        feed_id = data.get('post_id')
        comment_text = data.get("comment_text")
        time_of_publication = datetime.now()

        if not feed_id:
            return jsonify({'status': 400, 'message': 'post id is required'})

        if not comment_text:
            return jsonify({'status': 400, 'message': 'comment text is required'})

        try:
            execute_query(
                "INSERT INTO comments (author_id, feed_id, comment_text, created_at) VALUES (%s, %s, %s, %s)",
                (user_id, feed_id, comment_text, time_of_publication), insert=True
            )
            #logging.debug("Comment count result: %s", comment_count_result)
            comment_count_result = execute_query(
                "SELECT COUNT(*) FROM comments WHERE feed_id = %s",
                (feed_id,), fetchall=False
            )
            comment_count = comment_count_result[0] if comment_count_result else 0

            return jsonify({'status': 200, 'message': 'Feed commented successfully', 'commentCount': comment_count})
        except Exception as e:
            print("Error commenting feed:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/get_comments/<int:feed_id>', methods=['GET'])
    @token_required
    def get_comments(feed_id):
        current_user_id = request.user_id
        try:
            comments = execute_query('''
                 SELECT u.surname, u.name, c.id AS comment_id, c.author_id, c.comment_text, c.created_at,
                        EXISTS(SELECT 1 FROM comment_likes cl WHERE cl.comment_id = c.id AND cl.user_id = %s) AS is_liked,
                        (SELECT COUNT(*) FROM comment_likes cl WHERE cl.comment_id = c.id) AS like_count
                 FROM comments c
                 JOIN users u ON c.author_id = u.id
                 WHERE c.feed_id = %s
                 ORDER BY c.created_at ASC, c.id ASC
            ''', (current_user_id, feed_id), fetchall=True)

            comments_list = []
            for comment in comments:
                comments_list.append({
                    'surname': comment[0],
                    'name': comment[1],
                    'comment_id': comment[2],
                    'author_id': comment[3],
                    'text': comment[4],
                    'created_at': comment[5],
                    'is_current_user': comment[3] == current_user_id,
                    'is_liked': comment[6],
                    'likeCountComment': comment[7]
                })

            return jsonify({'status': 200, 'comments': comments_list})
        except Exception as e:
            print("Error fetching comments:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/user/delete_comment/<int:comment_id>', methods=['DELETE'])
    @token_required
    def delete_comment(comment_id):
        user_id = request.user_id
        try:
            comments = execute_query("SELECT * FROM comments WHERE id = %s", (comment_id,), fetchall=True)

            if not comments or len(comments) == 0:
                return jsonify({'status': 404, 'message': 'Comment not found'})

            comment = comments[0]
            comment_author_id = comment[1]
            if comment_author_id != user_id:
                return jsonify({'status': 403, 'message': 'You can only delete your own comments'})

            execute_query("DELETE FROM comment_likes WHERE comment_id = %s", (comment_id,), delete=True)

            execute_query("DELETE FROM comments WHERE id = %s", (comment_id,), delete=True)

            feed_id = comment[2]

            comment_count_result = execute_query("SELECT COUNT(*) FROM comments WHERE feed_id = %s", (feed_id,), fetchall=False)
            comment_count = comment_count_result[0] if comment_count_result else 0

            return jsonify({'status': 200, 'message': 'Comment deleted successfully', 'commentCount': comment_count})
        except Exception as e:
            print("Error deleting comment:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})

    @app.route('/post/comment_count/<int:post_id>', methods=['GET'])
    def get_comment_count(post_id):
        try:
            comment_count_result = execute_query(
                "SELECT COUNT(*) FROM comments WHERE feed_id = %s",
                (post_id,),
                fetchall=False
            )
            comment_count = comment_count_result[0]

            return jsonify({'status': 200, 'commentCount': comment_count})
        except Exception as e:
            print("Error fetching comment count:", e)
            return jsonify({'status': 500, 'message': 'Internal server error'})
