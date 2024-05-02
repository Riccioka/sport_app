from flask import Flask
from flask_cors import CORS
from routes import auth_routes, post_routes, user_routes

session = {}

app = Flask(__name__)
CORS(app)
app.secret_key = 'qwerty'

auth_routes.init_auth_routes(app)
post_routes.init_post_routes(app)
user_routes.init_user_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
