import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    if event['routeKey'] == 'GET /visitors':
        # Get the service resource.
        dynamodb = boto3.resource('dynamodb')

        # Instantiate a table resource object without actually
        # creating a DynamoDB table.
        table = dynamodb.Table('resume-visitor')

        # get the item
        response = table.get_item(
            Key={
                'visitor': 'resume',
            }
        )

        if "Item" not in response:
            logging.info("No Visitor Counter in DynamoDB Table. Creating...")
            table.put_item(Item={"visitor": "resume", "current": 0},)
            currentTotal = 1
        else:
            item = response['Item']
            currentTotal = int(item['current']) + 1

        # update the counter
        table.update_item(
            Key={
                'visitor': 'resume',
            },
            UpdateExpression='SET #attrName = :val1',
            ExpressionAttributeNames={
                '#attrName': 'current',
            },
            ExpressionAttributeValues={
                ':val1': str(currentTotal)
            }
        )
        # return
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': 'https://vivyvuong.dev',
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': json.dumps({'total': currentTotal})
        }
    else:
        return {
            'statusCode': 403,
            'body': json.dumps({'message': 'route not found'})
        }
