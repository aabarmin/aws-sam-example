import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # extracting cellarId from event
    cellarId = event['cellarId']
    # connecting to DynamoDB
    dynamoDb = boto3.resource('dynamodb')
    eurlex_documents = dynamoDb.Table('eurlex_documents')
    # checking if document exists in the table
    response = eurlex_documents.get_item(Key={
            'cellarId': cellarId
        })
    # return back
    if ('Item' in response):
        # exists
        return {
            'cellarId': cellarId,
            'exists': True
        }
    else:
        return {
            'cellarId': cellarId,
            'exists': False
        }

if __name__ == '__main__':
    # a14bb485-038c-11eb-a511-01aa75ed71a1
    event = {
        'cellarId': 'test_doc'
    }
    lambda_handler(event, None)