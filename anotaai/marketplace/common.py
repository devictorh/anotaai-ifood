import boto3
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
AWS_URL_SQS = os.getenv('AWS_URL_SQS')


class AwsUtils:
    def __init__(self) -> None:        
        self.sqs = boto3.client(
            "sqs",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    def _send_message_to_sqs(self, message: dict):
        try:
            self.sqs.send_message(
                QueueUrl=AWS_URL_SQS,
                MessageBody=json.dumps(message)
            )
            logging.info("message sent successfully")
        except Exception as err:
            logging.error(f"error sending message: {err}")
