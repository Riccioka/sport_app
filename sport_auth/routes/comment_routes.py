# from database import execute_query
from flask import request, jsonify
from routes.auth_routes import session

def init_comment_routes(app):
    @app.route('/comment', methods=['POST'])
    def comment_post():
        if 'loggedin' in session:

            comment_count = 1
            print("hi,comment_post", comment_count)
            return jsonify({'status': 200, 'message': 'Feed commented successfully', 'commentCount': comment_count})

    @app.route('/get_comments/<int:feed_id>', methods=['GET'])
    def get_comments(feed_id):
            comments_list = [{
                'surname': "Алешин",
                'name': "Сергей",
                'text': "Комментарий от сережки",
                'created_at': "2024-05-21 14:29:34.913323"
            }]

            return jsonify({'status': 200, 'comments': comments_list})

# edit + delete
    # проверка доступа на удаление есть у фронта?
    @app.route('/delete_comment/<int:post_id>', methods=['DELETE'])  # <int:post_id>
    def delete_comment(id):
        return jsonify({'status': 200, 'message': 'Comment deleted successfully', 'commentCount': 1})
        # else:
        #     return jsonify({'status': 401, 'message': 'Unauthorized'})

    @app.route('/post/comment_count', methods=['GET']) #/<int:post_id>
    def get_comment_count(post_id):
        comment_count = 1
        return jsonify({'status': 200, 'commentCount': comment_count})
