import requests
import boto3
from datetime import datetime
import os

def lambda_handler(event, context):
    print(f'Debug: event: {event}')

    cellarId = event['cellarId']
    print(f'Downloading notice with cellar {cellarId}')

    try:
        url = f'https://eur-lex.europa.eu/download-notice.html?legalContentId=cellar:{cellarId}&noticeType=branch&callingUrl=&lng=EN'
        response = requests.get(url)
        if (response.status_code == 200):
            print('Notice was downloaded successfully')
            upload_content(response.content, cellarId)
            save_record(cellarId)
        
        event['downloaded'] = True
    except Exception:
        event['downloaded'] = False

    return event


def upload_content(content: str, cellarId: str):
    """
    This function downloads the notice from EurLex and uploads it to S3
    """
    s3_client = boto3.client('s3')
    object_key = f'notice_{cellarId}.xml'
    bucket_name = get_s3_bucke_name()
    existing_objects = s3_client.list_objects(Bucket=bucket_name, Prefix=object_key)
    
    if ('Contents' in existing_objects):
        print('Object with a given name already exists, to be removed')
        for item in existing_objects['Contents']:
            remove_key = item['Key']
            print(f'Removing {remove_key} from bucket {bucket_name}')
            s3_client.delete_object(Bucket=bucket_name, Key=remove_key)
    
    upload_response = s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=content)
    print(f'Object {object_key} was uploaded to bucket {bucket_name}')

def save_record(cellarId: str):
    """
    This function creates a record in the DynamoDB about a downloaded notice
    """
    dynamo_client = boto3.client('dynamodb')
    dynamo_table = get_dyname_table_name()
    current_date = datetime.now()
    created_item = dynamo_client.put_item(TableName=dynamo_table, Item={
        'cellarId': {
            'S': cellarId
        },
        'created': {
            'S': current_date.strftime('%m/%d/%y %H:%M:%S')
        }
    })
    print(f'Item with cellar {cellarId} created')

def get_s3_bucke_name() -> str: 
    """
    Returns the name of bucket to store downloaded notices
    """
    return get_environment_variable_value('INGEST_S3_BUCKET_NAME', 'abarmins3bucket')

def get_dyname_table_name() -> str:
    """
    Returns the name of the DynamoDB table to store information about downloaded notices
    """
    return get_environment_variable_value('INGEST_DYNAMODB_TABLE_NAME', 'eurlex_documents')

def get_environment_variable_value(variable_name: str, default_value: str) -> str:
    """
    Returns an environment variable's value or default value if the app is started locally
    """
    value = os.environ.get(variable_name)

    if value is None:
        if __name__ == '__main__':
            print(f'Getting default value for env variable {variable_name}')
            value = default_value
        else:
            raise EnvironmentError(f'No environment variable {variable_name}')
    
    return value
    

if __name__ == '__main__':
    event = {
        'cellarId': 'a14bb485-038c-11eb-a511-01aa75ed71a1'
    }
    lambda_handler(event, {})