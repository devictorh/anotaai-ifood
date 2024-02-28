import boto3
import json
import logging

from typing import Final

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

S3_BUCKET: Final[str] = "mktplace-catalog-anotaai"
KEY: Final[str] = "catalogs/"

S3_CLIENT = boto3.client("s3")


def upload_catalog_to_s3(catalog: dict) -> None:
    try:
        body = json.dumps(catalog)
        S3_CLIENT.put_obj(
            Body=body,
            Bucket=S3_BUCKET,
            Key=KEY
        )
        logger.info("catalog updated successfully")
    except Exception as e:
        logger.erro(e)


def run_create(product, catalog) -> None:
    try:
        if catalog:
            ...
        else:
            ...
    except Exception as e:
        logger.error(
            f"An error occurred while completing create process: {e}"
        )


def run_update(product, file_obj) -> None:
    try:
        ...
    except Exception as e:
        logger.error(
            f"An error occurred while completing upload process: {e}"
        )


def run_delete(product, catalog) -> None:
    try:
        if catalog:
            catalog_obj = json.loads(catalog)
            catalog_obj.pop(product["id"])

            upload_catalog_to_s3(catalog_obj)
        else:
            logger.error("Not found product for this owner")
    except Exception as e:
        logger.error(
            f"An error occurred while completing delete process: {e}"
        )


def check_if_file_owner_exists(ownerid: str) -> dict:
    file: str = f"{KEY}{ownerid}.json"
    try:
        catalog_obj = S3_CLIENT.get_object(Bucket=S3_BUCKET, Key=file)
        return catalog_obj['Body'].read().decode('utf-8')
    except Exception as e:
        logger.error(e)
    return None


def handler(context, event):
    logger.info("started consumer")

    records = context["Records"]
    if len(records) > 0:
        for record in records:
            body: dict = json.loads(record["body"])
            msg_type = body.get('type', None)
            product: dict = body.get('product', None)
            catalog = check_if_file_owner_exists(product["ownerid"])

            if product:
                match msg_type:
                    case "create":
                        run_create(product, catalog)
                    case "update":
                        run_update(product, catalog)
                    case "delete":
                        run_delete(product, catalog)
                    case _:
                        logger.error("Invalid value for field 'type'")
            else:
                logger.error("It's missing product")
