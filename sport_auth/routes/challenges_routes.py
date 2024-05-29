from flask import jsonify
from database import execute_query
from routes.auth_routes import session

def init_challenges_routes(app):
    @app.route('/challenges', methods=['GET'])
    def challenges():
        return