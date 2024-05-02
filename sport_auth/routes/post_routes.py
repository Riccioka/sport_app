from flask import jsonify, request, session
from database import execute_query
import datetime

def init_post_routes(app):
    @app.route('/create_post', methods=['POST'])
    def create_post():
        if 'loggedin' in session:
            author_id = session['id']

            data = request.json
            time_of_publication = datetime.datetime.now()
            status = False  # false пока не изменен пост
            progress = data.get('progress')  # км/ч/шаги
            databeginning = data.get('databeginning')
            dataending = data.get('dataending')
            activity_id = data.get('activity_id')
            commentactivity = data.get('commentactivity')
            proof = data.get('proof')

            try:
                execute_query(
                    'INSERT INTO posts (author_id, time_of_publication, status, progress, databeginning, dataending, activity_id, commentactivity, proof) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (author_id, time_of_publication, status, progress, databeginning, dataending, activity_id,
                     commentactivity, proof), insert=True)
                return jsonify({'status': 200, 'message': 'Post created successfully'})
            except Exception as e:
                print("Error creating post:", e)
                return jsonify({'status': 500, 'message': 'Internal server error'})
        return jsonify({'status': 401, 'message': 'Unauthorized'})

    # @app.route('/edit_post/<int:post_id>', methods=['PUT'])
    # def edit_post(post_id):
    #     pass
    #
    # @app.route('/delete_post/<int:post_id>', methods=['DELETE'])
    # def delete_post(post_id):
    #     pass
