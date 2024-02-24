import boto3
import json
import logging
import botocore.exceptions as ClientError

from typing import Final

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

S3: Final[str] = "mktplace-catalog-anotaai"


def upload_catalog_to_s3(catalog: dict):
    s3_client = boto3.client("s3")
    try:
        ...
    except ClientError as e:
        logger.erro(e)


def get_file_from_s3_by_owner(owner: str):
    ...


def run_create(product, file_obj):
    try:
        ...
    except Exception as e:
        logger.error(
            f"An error occurred while completing create process: {e}"
        )


def run_update(product, file_obj):
    try:
        ...
    except Exception as e:
        logger.error(
            f"An error occurred while completing upload process: {e}"
        )


def run_delete(product, file_obj):
    try:
        if file_obj:
            catalog = file_obj['Body'].read().decode('utf-8')
            catalog_obj = json.loads(catalog)
            catalog_obj.pop(product["id"])

            upload_catalog_to_s3(catalog_obj)
        else:
            logger.error("Not found product for this owner")
    except Exception as e:
        logger.error(
            f"An error occurred while completing delete process: {e}"
        )


def check_if_file_owner_exists(owner: str) -> bool:
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=S3, Key=owner)
    return response if response else None


def handler(context, event):
    logger.info("started consumer")

    records = context["Records"]
    if len(records) > 0:
        for record in records:
            body: dict = record["body"]
            product: dict = body.get('product', None)
            file_obj = check_if_file_owner_exists(product["owner"])

            if product:
                match body["msgtype"]:
                    case "create":
                        run_create(product, file_obj)
                    case "update":
                        run_update(product, file_obj)
                    case "delete":
                        run_delete(product, file_obj)
                    case _:
                        logger.error("Invalid value for field 'msgtype'")
            else:
                logger.error("It's missing product")
