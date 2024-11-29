import json
import boto3
from botocore.exceptions import ClientError

# Specify the DynamoDB table name
TABLE_NAME = 'LeaseMatch_offers_table'

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    # Reference the DynamoDB table
    table = dynamodb.Table(TABLE_NAME)
    
    # Check the HTTP method
    http_method = event['httpMethod']
    
    # Handle GET request
    if http_method == 'GET':
        # Extract userId from query parameters
        offer_id = event['queryStringParameters'].get('offerId', None)
        
        if not offer_id:
            return {
                'statusCode': 400,
                'body': json.dumps('Error: userId is required for GET request.')
            }
        
        # Fetch data from DynamoDB
        try:
            response = table.get_item(Key={'id': offer_id})
            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'body': json.dumps(f'Error: No user found with id {offer_id}')
                }

            user_data = response['Item']
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST'
                },
                'body': json.dumps(user_data)
            }
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error fetching item from DynamoDB: {str(e)}')
            }
    
    # Handle POST request
    elif http_method == 'POST':
        # Parse the body of the request (assuming it's a JSON body)
        try:
            body = json.loads(event['body'])
        except KeyError:
            return {
                'statusCode': 400,
                'body': json.dumps('Error: Request body is required.')
            }
        
        identity = body.get('offer_id')
        country = body.get('country')
        city = body.get('city')
        type_document = body.get('type')
        document_number = body.get('document')
        email = body.get('email')
        telephone = body.get('telephone')
        
        # Validate required fields
        if not country or not city or not type_document or not document_number or not email or not telephone:
            return {
                'statusCode': 400,
                'body': json.dumps(f'Error: all fields are required.')
            }

        # Save or update the data
        try:
            table.put_item(
                Item={
                    'id': identity,
                    'country': country,
                    'city': city,
                    'type': type_document,
                    'document': document_number,
                    'email': email,
                    'telephone': telephone
                }
            )
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST'
                },
                'body': json.dumps({"message": "Record created/updated successfully"})
            }
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error inserting item into DynamoDB: {str(e)}')
            }
    
    # Method Not Allowed if the HTTP method is neither GET nor POST
    return {
        'statusCode': 405,
        'body': json.dumps('Error: Method Not Allowed')
    }
