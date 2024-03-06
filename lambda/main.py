import boto3
import json
import logging

from typing import Final

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

S3_BUCKET: Final[str] = "mktplace-catalog-anotaai"
KEY: Final[str] = "catalogs"

TYPES: Final[list[str]] = ["categories", "products"]
ACTIONS: Final[list[str]] = ["create", "update", "delete"]

S3_CLIENT = boto3.client("s3")


def upload_catalog_to_s3(catalog: dict, owner_id: str) -> None:
    file: str = f"{KEY}/{owner_id}.json"
    try:
        body = json.dumps(catalog)
        S3_CLIENT.put_object(
            Body=body,
            Bucket=S3_BUCKET,
            Key=file
        )
        logger.info("catalog updated successfully")
    except Exception as e:
        logger.error(e)


def run_create(obj_catalog: dict, item: dict, type_msg: str) -> None:
    try:
        if obj_catalog:
            if type_msg not in obj_catalog:
                obj_catalog[type_msg] = []
            obj_catalog[type_msg].append(item)
        else:
            obj_catalog = {}
            obj_catalog[type_msg] = []
            obj_catalog[type_msg].append(item)

        upload_catalog_to_s3(obj_catalog, item["ownerid"])
    except Exception as e:
        logger.error(
            f"An error occurred while completing create process: {e}"
        )


def run_update(obj_catalog: dict, item: dict, type_msg: str) -> None:
    try:
        if not obj_catalog:
            run_create(obj_catalog, item, type_msg)
        else:
            if len(obj_catalog[type_msg]) > 0:
                for idx, item_obj in enumerate(obj_catalog[type_msg]):
                    if item_obj["_id"] == item["_id"]:
                        obj_catalog[type_msg][idx] = item
                        upload_catalog_to_s3(obj_catalog, item["ownerid"])
                        break
    except Exception as e:
        logger.error(
            f"An error occurred while completing upload process: {e}"
        )


def run_delete(
        obj_catalog: dict,
        id: str,
        owner_id: str,
        type_msg: str
) -> None:
    try:
        if obj_catalog:
            if len(obj_catalog[type_msg]) > 0:
                for idx, item_obj in enumerate(obj_catalog[type_msg]):
                    if item_obj["_id"] == id:
                        obj_catalog[type_msg].pop(idx)
                        break
                upload_catalog_to_s3(obj_catalog, owner_id)
            else:
                logger.error(f"Not found items in {type_msg} for this owner")
        else:
            logger.error(f"Not found {type_msg} for this owner")
    except Exception as e:
        logger.error(
            f"An error occurred while completing delete process: {e}"
        )


def check_if_file_owner_exists(ownerid: str) -> dict:
    file: str = f"{KEY}/{ownerid}.json"
    try:
        catalog_obj = S3_CLIENT.get_object(Bucket=S3_BUCKET, Key=file)
        return json.loads(catalog_obj['Body'].read().decode('utf-8'))
    except Exception as e:
        logger.error(e)
    return None


def execute_update(body: dict, type_msg: str, action: str) -> None:
    try:
        if action != "delete":
            item = body["category"] if type_msg == "categories" \
                                    else body["product"]

        owner_id = item["ownerid"] if action != "delete" else body["ownerid"]

        obj_catalog = check_if_file_owner_exists(owner_id)

        match action:
            case "create":
                logger.info("creating new item")
                run_create(obj_catalog, item, type_msg)
            case "update":
                logger.info("updating item")
                run_update(obj_catalog, item, type_msg)
            case "delete":
                logger.info("deleting item")
                id = body["id"]
                run_delete(obj_catalog, id, owner_id, type_msg)
            case _:
                logger.error("invalid action")

    except Exception as e:
        logger.error(e)


def handler(context, event):
    logger.info("started consumer")
    records = context["Records"]
    if len(records) > 0:
        try:
            for record in records:
                body: dict = json.loads(record["body"])
                logger.info(f"Body : {body}")

                type_msg = body.get('type', None)
                action: str = body.get('action', None)

                if type_msg not in TYPES:
                    logger.error("Invalid type of message.")
                elif action not in ACTIONS:
                    logger.error("Invalid action of message.")
                else:
                    execute_update(body, type_msg, action)

        except Exception as e:
            logger.error(e)
        finally:
            logger.info("end process")
