from flask import jsonify
import boto3
import botocore
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ENDPOINT

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name='ru-central1',
                  endpoint_url=AWS_ENDPOINT,
                  config=botocore.client.Config(signature_version='s3v4'))

def init_aws_routes(app):
    @app.route('/img_keys', methods=['GET'])
    def get_img_keys():
        key = 'users/uploads/${filename}'
        bucket = 'team2go'
        conditions = [{"acl": "public-read"}, ["starts-with", "$key", "users/uploads"]]
        fields = {'success_action_redirect': ''}

        prepared_form_fields = s3.generate_presigned_post(Bucket=bucket,
                                                          Key=key,
                                                          Conditions=conditions,
                                                          Fields=fields,
                                                          ExpiresIn=60 * 60)

        return jsonify(prepared_form_fields)

