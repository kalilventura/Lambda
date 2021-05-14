import json
import os
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    try:
        response_data = put_data(event)
        print(response_data)
        return response(None, 200, response_data)
    except Exception as e:
        raise e


def put_data(item):
    try:
        table = get_dynamo_table(os.environ.get('TABLE_NAME'))
        item = {
            'Id': int(item['id']),
            'Image': item['filename'],
            'Data': {
                'CreatedAt': item['createdAt'],
                'Message': item['message']
            }
        }
        input_data = table.put_item(Item=item)

        return input_data
    except ClientError as e:
        print('Error trying to insert data in table')
        raise e


def get_dynamo_table(table_name):
    try:
        dynamo = boto3.resource('dynamodb', endpoint_url=os.environ.get('ENDPOINT_URL'))
        table = dynamo.Table(table_name)
        return table
    except ClientError as e:
        print('Error when trying to get table')
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
