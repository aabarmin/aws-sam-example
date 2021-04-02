import os
from unittest.mock import patch, call, MagicMock
from unittest.mock import Mock
from functions.ingest_alert_filter import app


class TestIngestAlertFilter():
    dynamo_mock = Mock()
    dynamo_table = Mock()

    @classmethod
    def setup_class(cls):
        os.environ.setdefault('INGEST_DYNAMODB_TABLE_NAME', 'test_table')

    def test_handle_unknown(self):
        event = {
            'cellarId': 'unknown_cellarId'
        }
        context = {}

        self.dynamo_mock.Table = MagicMock(return_value=self.dynamo_table)
        self.dynamo_table.get_item = MagicMock(return_value={})

        with patch('boto3.resource') as boto_mock:
            boto_mock.return_value = self.dynamo_mock

            response = app.lambda_handler(event, context)

            boto_mock.assert_has_calls([call('dynamodb')])

        assert 'cellarId' in response
        assert 'exists' in response
        assert response['cellarId'] == 'unknown_cellarId'
        assert response['exists'] == False
