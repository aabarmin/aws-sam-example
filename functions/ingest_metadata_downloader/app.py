import requests
import boto3
import sys
from datetime import datetime
from functions.common.environment import get_environment_variable_value


def lambda_handler(event, context):
    print(f'Debug: event: {event}')

    cellar_id = event['cellarId']
    print(f'Downloading notice with cellar {cellar_id}')

    try:
        url = f'https://eur-lex.europa.eu/download-notice.html?legalContentId=cellar:{cellar_id}&noticeType=branch&callingUrl=&lng=EN'
        response = requests.get(url)
        if response.status_code == 200:
            print('Notice was downloaded successfully')
            upload_content(response.content, cellar_id)
            save_record(cellar_id)
        
        event['downloaded'] = True
    except Exception:
        error = sys.exc_info()[2]
        print(f'Error while downloading {error}')
        event['error'] = error
        event['downloaded'] = False

    return event


def upload_content(content: str, cellar_id: str):
    """
    This function downloads the notice from EurLex and uploads it to S3
    """
    s3_client = boto3.client('s3')
    object_key = f'notice_{cellar_id}.xml'
    bucket_name = get_s3_bucket_name()
    existing_objects = s3_client.list_objects(Bucket=bucket_name, Prefix=object_key)
    
    if ('Contents' in existing_objects):
        print('Object with a given name already exists, to be removed')
        for item in existing_objects['Contents']:
            remove_key = item['Key']
            print(f'Removing {remove_key} from bucket {bucket_name}')
            s3_client.delete_object(Bucket=bucket_name, Key=remove_key)
    
    upload_response = s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=content)
    print(f'Object {object_key} was uploaded to bucket {bucket_name}')


def save_record(cellar_id: str):
    """
    This function creates a record in the DynamoDB about a downloaded notice
    """
    dynamo_client = boto3.client('dynamodb')
    dynamo_table = get_dyname_table_name()
    current_date = datetime.now()
    created_item = dynamo_client.put_item(TableName=dynamo_table, Item={
        'cellarId': {
            'S': cellar_id
        },
        'created': {
            'S': current_date.strftime('%m/%d/%y %H:%M:%S')
        }
    })
    print(f'Item with cellar {cellar_id} created')


def get_s3_bucket_name() -> str:
    """
    Returns the name of bucket to store downloaded notices
    """
    return get_environment_variable_value('INGEST_S3_BUCKET_NAME', 'abarmins3bucket')


def get_dyname_table_name() -> str:
    """
    Returns the name of the DynamoDB table to store information about downloaded notices
    """
    return get_environment_variable_value('INGEST_DYNAMODB_TABLE_NAME', 'eurlex_documents')

    

if __name__ == '__main__':
    event = {
        'cellarId': 'a14bb485-038c-11eb-a511-01aa75ed71a1'
    }
    lambda_handler(event, {})