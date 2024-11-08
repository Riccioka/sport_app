from flask import jsonify
import boto3
import botocore

# AWS S3 configuration
endpoint = 'https://storage.yandexcloud.net'

s3 = boto3.client('s3',
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name='ru-central1',
                  endpoint_url=endpoint,
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

