import unittest
import os
from unittest.mock import MagicMock, Mock
from unittest.mock import patch, call
from functions.ingest_metadata_downloader import app


class TestIngestMetadataDownloader(unittest.TestCase):
    s3_client = Mock()
    dynamo_client = Mock()

    @classmethod
    def setUpClass(cls):
        os.environ.setdefault('INGEST_S3_BUCKET_NAME', 'test_bucket')
        os.environ.setdefault('INGEST_DYNAMODB_TABLE_NAME', 'test_table')

    def boto_client_config(self, client_name):
        if client_name == 's3':
            return self.s3_client
        elif client_name == 'dynamodb':
            return self.dynamo_client
        else:
            raise Exception(f'Unknown client {client_name}')

    def test_download_notice(self):
        # Configuring mocks
        empty_s3_response = {
            'Contents': []
        }
        self.s3_client.list_objects = MagicMock(return_value=empty_s3_response)
        self.s3_client.put_object = MagicMock(return_value=True)
        self.dynamo_client.put_item = MagicMock(return_value={})

        context = {}
        event = {'cellarId': 'a14bb485-038c-11eb-a511-01aa75ed71a1'}

        # Executing the code
        with patch('boto3.client') as boto_mock:
            boto_mock.side_effect = self.boto_client_config

            response = app.lambda_handler(event, context)

            boto_mock.assert_has_calls([
                call('s3'),
                call('dynamodb')
            ], any_order=True)

        # Assertions
        assert response is not None
        assert 'cellarId' in response
        assert 'downloaded' in response
        assert response['cellarId'] == 'a14bb485-038c-11eb-a511-01aa75ed71a1'

        # Checking mocks calls
        self.s3_client.put_object.assert_called_once()
        self.s3_client.list_objects.assert_called_once()
        self.dynamo_client.put_item.assert_called_once()
