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

@app.delete("/notes/<id>")
def delete_note(id):
    logger.info(f"Deleting note with id {id}")
    table.delete_item(Key={"id": id})

    logger.info(f"DynamoDB: Deleted note {id}")

    return {
        "message": "Deleted",
        "id": id
    }

@app.post("/notes")
def create_note():
    body = app.current_event.json_body
    logger.info(f"Creating note for {body.get("text")}")
    note_id = str(uuid.uuid4())[:8]
    item = {
        "id": note_id,
        "text": body.get("text", "Empty Note"),
        "created_at": datetime.datetime.now().isoformat(),
    }
    table.put_item(Item=item)

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
