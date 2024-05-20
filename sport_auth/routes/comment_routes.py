from database import execute_query
from flask import request
from routes.auth_routes import session

def init_comment_routes(app):
    @app.route('/add_comment_to_post', methods=['POST'])
    def add_comment_to_post():
        data = request.get_json()
        author_id = data.get("author_id")
        feed_id = data.get("feed_id")
        comment_text = data.get("comment_text")

        # время надо? created_at
        try:
            execute_query("INSERT INTO comments (author_id, feed_id, comment_text) VALUES (%s, %s, %s)",
                          (author_id, feed_id, comment_text),
                          insert=True)

            print("Комментарий успешно добавлен.")
        except Exception as error:
            print("Ошибка при добавлении комментария:", error)

# edit + delete