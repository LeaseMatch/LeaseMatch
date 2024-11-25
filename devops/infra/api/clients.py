import json
import boto3
from botocore.exceptions import ClientError

# Specify the DynamoDB table name
TABLE_NAME = 'LeaseMatch_clients_table'

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    # Reference the DynamoDB table
    table = dynamodb.Table(TABLE_NAME)
    
    # Parse the body of the request (assuming it's a JSON body)
    try:
        body = json.loads(event['body'])
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps('Error: Request body is required.')
        }
    identity = body.get('id')
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
    
    # Save the data
    try:
        table.put_item(
            Item={
                'id': identity,
                'country': country,
                'city': city,
                'type': type_document,
                'document':document_number,
                'email':email,
                'telephone':telephone
            }
        )
        
        # Prepare the successful response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({"message": "Record created successfully"})
        }
    except ClientError as e:
        # Handle DynamoDB errors
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error inserting item into DynamoDB: {str(e)}')
        }