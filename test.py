import unittest
import json
from unittest.mock import MagicMock, patch
# Replace with the actual module name
from apis.lambda_function import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('apis.lambda_function.boto3.resource')
    @patch('apis.lambda_function.boto3.client')
    def test_get_visitors_route(self, mock_dynamodb_client, mock_dynamodb_resource):
        # Mock DynamoDB resource and client
        mock_table = MagicMock()
        mock_dynamodb_resource.return_value.Table.return_value = mock_table

        # Mock DynamoDB get_item response
        mock_table.get_item.return_value = {
            'Item': {'visitors': 'resume', 'current': '1'}
        }

        # Mock DynamoDB update_item response
        mock_table.update_item.return_value = {}

        # Mock event for the "GET /visitors" route
        event = {'httpMethod': 'GET'}

        # Call the Lambda handler
        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Access-Control-Allow-Headers', response['headers'])
        self.assertIn('Access-Control-Allow-Origin', response['headers'])
        self.assertIn('Access-Control-Allow-Methods', response['headers'])
        self.assertIn('total', json.loads(response['body']))

    def test_unknown_route(self):
        # Mock event for an unknown route
        event = {'httpMethod': 'POST'}

        # Call the Lambda handler
        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 403)
        self.assertIn('message', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])[
                         'message'], 'route not found')

    @patch('apis.lambda_function.boto3.resource')
    @patch('apis.lambda_function.boto3.client')
    def test_no_visitor_data(self, mock_dynamodb_client, mock_dynamodb_resource):
        # Mock DynamoDB resource and client
        mock_table = MagicMock()
        mock_dynamodb_resource.return_value.Table.return_value = mock_table

        # Mock DynamoDB get_item response for no item
        mock_table.get_item.return_value = {}

        # Mock DynamoDB put_item response
        mock_table.put_item.return_value = {}

        # Mock DynamoDB update_item response
        mock_table.update_item.return_value = {}

        # Mock event for the "GET /visitors" route
        event = {'httpMethod': 'GET'}

        # Call the Lambda handler
        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Access-Control-Allow-Headers', response['headers'])
        self.assertIn('Access-Control-Allow-Origin', response['headers'])
        self.assertIn('Access-Control-Allow-Methods', response['headers'])
        self.assertIn('total', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['total'], 1)

        # Additional assertions for the case when no item is found initially
        mock_table.put_item.assert_called_once_with(
            Item={'visitors': 'resume', 'current': 0})
        mock_table.update_item.assert_called_once_with(
            Key={'visitors': 'resume'},
            UpdateExpression='SET #attrName = :val1',
            ExpressionAttributeNames={'#attrName': 'current'},
            ExpressionAttributeValues={':val1': '1'}
        )


if __name__ == '__main__':
    unittest.main()
