import boto3
import json
import os
import datetime
import uuid

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.event_handler.exceptions import NotFoundError


logger = Logger()

app = APIGatewayHttpResolver()

dynamodb = boto3.resource("dynamodb")
s3 = boto3.resource("s3")
table = dynamodb.Table(os.environ["TABLE_NAME"])
bucket = s3.Bucket(os.environ["LOGS_BUCKET"])


@app.get("/notes/<id>")
def get_note(id):
    logger.info(f"Fetching note with id {id}")
    item = table.get_item(Key={"id": id}).get("Item")

    if not item:
        logger.warning(f"DynamoDB: Note {id} not found")
        raise NotFoundError(f"Note {id} not found")

    logger.info(f"Found note {str(item)}")

    return item

def log_to_s3(event, response):
    method = event.get("requestContext", {}).get("http", {}).get("method")
    s3_key = (
        f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{method}.txt"
    )
    bucket.put_object(Key=s3_key, Body=json.dumps(response))
    logger.info(f"S3: Logged audit file to {s3_key}")

def handler(event, context):
    response = app.resolve(event, context)

    log_to_s3(event, response)

    return response

    # log_msg = f"Time: {datetime.datetime.now()} | Method: {method} | Path: {path} | ID: {note_id}"

    # try:
    #     if method == "POST" and path == "/notes":
    #         body = json.loads(event.get("body", "{}"))
    #         new_id = str(uuid.uuid4())[:8]

    #         item = {
    #             "id": new_id,
    #             "text": body.get("text", "Empty Note"),
    #             "created_at": datetime.datetime.now().isoformat(),
    #         }
    #         table.put_item(Item=item)
    #         logger.info(f"DynamoDB: Created item {new_id}")
    #         res = {"message": "Created", "item": item}

    #     elif method == "GET" and note_id:
    #         response = table.get_item(Key={"id": note_id})
    #         res = response.get("Item")
    #         if not res:
    #             logger.warning(f"DynamoDB: Note {note_id} not found")
    #             return {
    #                 "statusCode": 404,
    #                 "body": json.dumps({"error": "Not found"}),
    #             }
    #         logger.info(f"DynamoDB: Retrieved note {note_id}")

    #     elif method == "DELETE" and note_id:
    #         table.delete_item(Key={"id": note_id})
    #         logger.info(f"DynamoDB: Deleted note {note_id}")
    #         res = {"message": "Deleted", "id": note_id}

    #     else:
    #         logger.warning(f"Routing: Unsupported {method} on {path}")
    #         return {
    #             "statusCode": 400,
    #             "body": json.dumps({"error": f"Unsupported {method} on {path}"}),
    #         }

    #     s3_key = (
    #         f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{method}.txt"
    #     )
    #     bucket.put_object(Key=s3_key, Body=log_msg)
    #     logger.info(f"S3: Logged audit file to {s3_key}")

    #     return {
    #         "statusCode": 200,
    #         "headers": {"Content-Type": "application/json"},
    #         "body": json.dumps(res),
    #     }

    # except Exception as e:
    #     logger.exception("A critical error occurred during execution")
    #     return {
    #         "statusCode": 500,
    #         "body": json.dumps({"error": "Internal Server Error", "details": str(e)}),
    #     }
