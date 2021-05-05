import json
import base64
import boto3
from datetime import datetime
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    try:
        if event['httpMethod'] == 'POST':
            get_file_content = event['body']
            file_content = base64.b64decode(get_file_content)
            content_type = event['headers']['Content-Type']
            return upload(file_content, content_type)
        elif event['httpMethod'] == 'GET':
            path = event['pathParameters']
            filename = path['filename']

            if not filename:
                return response('Bad Request', 404)

            return download(filename)
    except Exception as e:
        return response(e, 500)


def upload(file_content, content_type):
    """
    Upload one file in s3 bucket \n
    :param file_content: File in base 64
    :param content_type: Content Type
    :return: response body
    """
    try:
        s3 = get_s3_client()
        name = f'{datetime.timestamp(datetime.now())}.{get_extension(content_type)}'

        s3_uploaded = put_object(s3, 'files', name, file_content)

        message = {
            'name': name,
            'data': s3_uploaded
        }
        return response(None, 201, message)
    except Exception as e:
        raise e


def get_extension(content_type: str) -> str:
    """
    get file extension \n
    :param content_type: Content-Type for application
    :return: Return file extension
    """
    try:
        mime_types = {
            'text/html': 'html',
            'image/jpeg': 'jpeg',
            'image/png': 'png',
            'application/json': 'json',
            'application/pdf': 'pdf',
            'application/vnd.ms-powerpoint': 'ppt',
            'application/rtf': 'rtf'
        }
        return mime_types[content_type]
    except Exception as e:
        raise e


def download(filename):
    """
    Download one file in s3 bucket \n
    :param filename: File in base 64
    :return: response body
    """
    try:
        s3 = get_s3_client()
        file = get_object(s3, 'files', filename)
        return response_file(code=200, content_type='application/pdf', file_content=file, filename=filename)
    except Exception as e:
        raise e


def get_s3_client():
    return boto3.client('s3', endpoint_url='http://172.25.224.1:4566')


def get_object(s3, bucket, key):
    """
    Get file in s3 bucket \n
    :param s3: Client to connect in s3
    :param bucket: Bucket name
    :param key: Name and extension we want to download
    :return: file
    """
    try:
        file = s3.get_object(Bucket=bucket, Key=key)
        file_content = file['Body'].read()
        return file_content
    except ClientError as e:
        raise e


def put_object(s3, bucket, key, content):
    try:
        return s3.put_object(Bucket=bucket, Key=key, Body=content)
    except ClientError as e:
        raise e


def response(err=None, code=404, res=None):
    message = err if err else res
    body = json.dumps({
        'message': message
    })

    return {
        'statusCode': str(code),
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }


def response_file(code: int, content_type: str, filename: str, file_content):
    return {
        'statusCode': str(code),
        'headers': {
            'Content-Type': content_type,
            'Access-Control-Allow-Origin': '*',
            'Content-Disposition': 'attachment; filename={}'.format(filename)
        },
        'body': base64.b64encode(file_content),
        'isBase64Encoded': True
    }
