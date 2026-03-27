import boto3
import json
import os
import datetime
import uuid

dynamodb = boto3.resource("dynamodb")
s3 = boto3.resource("s3")
table = dynamodb.Table(os.environ["TABLE_NAME"])
bucket = s3.Bucket(os.environ["LOGS_BUCKET"])


def handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method")
    path = event.get("rawPath", "").rstrip("/")

    path_parts = path.strip("/").split("/")
    note_id = path_parts[1] if len(path_parts) > 1 else None

    log_msg = f"Time: {datetime.datetime.now()} | Method: {method} | Path: {path} | ID: {note_id}"

    try:
        if method == "POST" and path == "/notes":
            body = json.loads(event.get("body", "{}"))
            new_id = str(uuid.uuid4())[:8]

            item = {
                "id": new_id,
                "text": body.get("text", "Empty Note"),
                "created_at": datetime.datetime.now().isoformat(),
            }
            table.put_item(Item=item)
            res = {"message": "Created", "item": item}

        elif method == "GET" and note_id:
            response = table.get_item(Key={"id": note_id})
            res = response.get("Item")
            if not res:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Not found"}),
                }

        elif method == "DELETE" and note_id:
            table.delete_item(Key={"id": note_id})
            res = {"message": "Deleted", "id": note_id}

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unsupported {method} on {path}"}),
            }

        bucket.put_object(
            Key=f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{method}.txt",
            Body=log_msg,
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(res),
        }

    except Exception as e:
        print(f"Error: {str(e)}")  # Visible in CloudWatch
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)}),
        }
