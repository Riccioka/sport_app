from flask import jsonify, request
from routes.auth_routes import session
# from database import execute_query

def init_like_routes(app):
    @app.route('/like', methods=['POST'])
    def like_post():
        if 'loggedin' in session:

            like_count = 7

            print("like", like_count)
            return jsonify({'status': 200, 'message': 'Feed liked successfully', 'likeCount': like_count})

    @app.route('/unlike', methods=['POST'])
    def unlike_post():
        if 'loggedin' in session:

            like_count = 6 #, fetchone=True

            return jsonify({'status': 200, 'message': 'Feed unliked successfully', 'likeCount': like_count})

