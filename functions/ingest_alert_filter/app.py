import boto3
from functions.common.environment import get_environment_variable_value


def lambda_handler(event, context):
    # extracting cellarId from event
    print(f'DEBUG: Incoming event: {event}, context: {context}')
    cellar_id = event['cellarId']
    # connecting to DynamoDB
    dynamo_db = boto3.resource('dynamodb')
    eurlex_documents = dynamo_db.Table(get_dynamo_table_name())
    # checking if document exists in the table
    response = eurlex_documents.get_item(Key={
            'cellarId': cellar_id
        })
    # return back
    if 'Item' in response:
        # exists
        return {
            'cellarId': cellar_id,
            'exists': True
        }
    else:
        return {
            'cellarId': cellar_id,
            'exists': False
        }


def get_dynamo_table_name() -> str:
    """
    Returns the name of the DynamoDB table to store information about downloaded notices
    """
    return get_environment_variable_value('INGEST_DYNAMODB_TABLE_NAME', 'eurlex_documents')


if __name__ == '__main__':
    # a14bb485-038c-11eb-a511-01aa75ed71a1
    event = {
        'cellarId': 'test_doc'
    }
    result = lambda_handler(event, None)
    print(result)
