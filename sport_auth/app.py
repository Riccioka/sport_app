from flask import Flask, send_from_directory
from flask_cors import CORS
from routes import auth_routes, post_routes, user_routes, team_routes, like_routes
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.secret_key = 'qwerty'

auth_routes.init_auth_routes(app)
post_routes.init_post_routes(app)
user_routes.init_user_routes(app)
like_routes.init_like_routes(app)

# team_routes.create_teams()

# @app.route('/uploads/<path:filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
