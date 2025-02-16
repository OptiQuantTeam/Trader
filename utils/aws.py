import boto3
from dotenv import load_dotenv
import os
import json

load_dotenv()
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_USER_ID = os.getenv('AWS_USER_ID')


def get_configure():
    dynamodb = boto3.resource('dynamodb',
                        region_name='ap-northeast-2',
                        aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY)

    table = dynamodb.Table('User')
    '''
    # Scan the table
    response = table.scan()
    data = response['Items']
    # Continue scanning if necessary
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
        print(data)
    for item in data:
        print(json.dumps(item, indent=4))
    '''
        
    response = table.get_item(
        Key={
            'user_id': AWS_USER_ID
        })
    print(json.dumps(response['Item'], indent=4))
    
    return json.dumps(response['Item'], indent=4)