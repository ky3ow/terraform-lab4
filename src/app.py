import boto3
import json
import os
import datetime

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table(os.environ['TABLE_NAME'])
bucket_name = os.environ['LOGS_BUCKET']

def handler(event, context):
    method = event.get('requestContext', {}).get('http', {}).get('method')
    
    path = event.get('rawPath', '') 
    path_parts = path.strip('/').split('/')
    note_id = path_parts[-1] if len(path_parts) > 1 else None
    
    log_msg = f"Operation: {method} on Path: {path} | ID: {note_id}"
    
    try:
        if method == 'POST':
            body = json.loads(event.get('body', '{}'))
            item = {
                'id': body.get('id'),
                'text': body.get('text'),
                'created_at': datetime.datetime.now().isoformat()
            }
            table.put_item(Item=item)
            res = {"message": "Created", "item": item}
            
        elif method == 'GET' and note_id:
            response = table.get_item(Key={'id': note_id})
            res = response.get('Item', {"error": "Note not found"})
            
        elif method == 'DELETE' and note_id:
            table.delete_item(Key={'id': note_id})
            res = {"message": "Deleted", "id": note_id}
        
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Unsupported method or missing ID"})}

        # 3. Log to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
            Body=log_msg
        )
        
        return {
            "statusCode": 200, 
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(res)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500, 
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)})
        }
