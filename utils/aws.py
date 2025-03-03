import boto3


def get_configure(AWS_USER_ID, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):
    if AWS_ACCESS_KEY == None and AWS_SECRET_KEY == None:
        dynamodb = boto3.resource('dynamodb')
    else:    
        dynamodb = boto3.resource('dynamodb',
                        region_name='ap-northeast-2',
                        aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_KEY)

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
    
    item = {
        'user_id': response['Item']['user_id'],
        'api_key' : response['Item']['api_key'],
        'secret_key' : response['Item']['secret_key'],
        'sl' : response['Item']['sl'],
        'tp' : response['Item']['tp'],
        'ratio' : response['Item']['ratio'],
        'leverage' : response['Item']['leverage'],
        'type' : response['Item']['type'],
        'slack_token' : response['Item']['slack_token'],
        'slack_user' : response['Item']['slack_user'],
        'slack_channel' : response['Item']['slack_channel']
    }
    #print(json.dumps(response['Item'], indent=4))
    return item
    #return json.dumps(response['Item'], indent=4)