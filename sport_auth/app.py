from flask import Flask
from flask_cors import CORS
from routes import (auth_routes, post_routes, user_routes, like_routes, comment_routes, rating_routes,
                    challenges_routes, activities_routes, aws_routes)
from admin import create_teams, recalc_points, import_db, create_leagues
import os
import boto3
import botocore

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.secret_key = 'qwerty'

auth_routes.init_auth_routes(app)
post_routes.init_post_routes(app)
user_routes.init_user_routes(app)
like_routes.init_like_routes(app)
comment_routes.init_comment_routes(app)
rating_routes.init_rating_routes(app)
challenges_routes.init_challenges_routes(app)
activities_routes.init_activities_routes(app)
aws_routes.init_aws_routes(app)

# create_leagues.create_leagues()
#create_teams.create_teams()
# recalc_points.recalculate_all_users_points()
# import_db.import_csv_to_users_table('C:/Users/User/PycharmProjects/sport_auth/admin/test_users.csv')

if __name__ == '__main__':
    app.run(debug=True)
