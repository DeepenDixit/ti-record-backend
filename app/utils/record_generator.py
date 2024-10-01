import argparse
import json
import os
from datetime import datetime
from random import SystemRandom
from typing import List

import mysql.connector
from pymongo import MongoClient
from randomtimestamp import randomtimestamp

from app.core.config import settings
from app.core.constants import (
    DEVICES_TABLE_CREATE,
    DEVICES_TABLE_INSERT,
    INITIAL_ID,
    MONGO_DB_BACKUP_COLLECTION,
    MONGO_DB_COLLECTION,
    MONGO_DB_NAME,
    RECORD_BACKUP_DIR,
    RECORD_FILE_NAME,
    RECORD_STORAGE_DIR,
    RECORDS_TABLE_CREATE,
    RECORDS_TABLE_INSERT,
    SERVER_RANGE_END,
    SERVER_RANGE_START,
    SQL_DB_NAME,
    SQL_DEVICES_BKP_TABLE,
    SQL_DEVICES_TABLE,
    SQL_RECORDS_BKP_TABLE,
    SQL_RECORDS_TABLE,
    TIMESTAMP_END_YEAR,
    TIMESTAMP_START_YEAR,
    USER_ID_DIVIDER,
    USER_ID_LENGTH,
)
from app.custom_exceptions.filter_from_mongo_exception import (
    MongoDBConnectionError,
    MongoDBOperationError,
)
from app.custom_exceptions.filter_from_sql_exception import (
    SQLConnectionError,
    SQLOperationError,
)
from app.utils.logger_helper import app_logger


def generate_long_random_int(required_length: int) -> str:
    """
    Generates long random intiger for given length
    required_length: length, of which the number is required
    """

    return "".join(
        [str(SystemRandom().randint(1, 9)) for _ in range(0, required_length)]
    )


def generate_records(number_of_records: int) -> List[dict]:
    """
    Generates the given number of dummy records
    """
    app_logger.info("Generating %d dummy records", number_of_records)

    records = []
    user_ids = [
        generate_long_random_int(USER_ID_LENGTH)
        for _ in range(number_of_records // USER_ID_DIVIDER)
    ]

    for record_id in range(number_of_records):
        records.append(
            {
                "_id": INITIAL_ID + record_id,
                "originationTime": int(
                    randomtimestamp(
                        start_year=TIMESTAMP_START_YEAR, end_year=TIMESTAMP_END_YEAR
                    ).timestamp()
                ),
                "clusterId": f"domainserver"
                f"{SystemRandom().randint(SERVER_RANGE_START, SERVER_RANGE_END)}",
                "userId": SystemRandom().choice(user_ids),
                "devices": {
                    "phone": f"SEP{generate_long_random_int(10)}",
                    "voicemail": f"{generate_long_random_int(9)}VM",
                },
            }
        )

    app_logger.info("Successfully generated %d dummy records", number_of_records)

    return records


def store_records_to_json(records: List[dict]):
    """
    Save the generated records to the pre-defined file.
    Also, keep track of older record by keeping backup of the same.
    """
    app_logger.info("Handeling the record storage")

    if not os.path.exists(RECORD_STORAGE_DIR):
        app_logger.error(
            "Main record storage directory %s not found", RECORD_STORAGE_DIR
        )
        os.makedirs(f"{RECORD_STORAGE_DIR}/{RECORD_BACKUP_DIR}")
        app_logger.info(
            "Created record storage directories: %s/%s",
            RECORD_STORAGE_DIR,
            RECORD_BACKUP_DIR,
        )
    else:
        app_logger.info(
            "Validated the existance of main record storage directory: %s",
            RECORD_STORAGE_DIR,
        )
        if not os.path.exists(f"{RECORD_STORAGE_DIR}/{RECORD_BACKUP_DIR}"):
            app_logger.error(
                "Backup record storage directory: %s/%s not found",
                RECORD_STORAGE_DIR,
                RECORD_BACKUP_DIR,
            )
            os.makedirs(f"{RECORD_STORAGE_DIR}/{RECORD_BACKUP_DIR}")
            app_logger.info(
                "Created backup record storage directory: %s/%s",
                RECORD_STORAGE_DIR,
                RECORD_BACKUP_DIR,
            )

    if os.path.exists(f"{RECORD_STORAGE_DIR}/{RECORD_FILE_NAME}"):
        app_logger.info(
            "Existing set of records found in file: %s/%s",
            RECORD_STORAGE_DIR,
            RECORD_FILE_NAME,
        )
        backup_file_name = (
            f"BKUP_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_{RECORD_FILE_NAME}"
        )
        os.rename(
            f"{RECORD_STORAGE_DIR}/{RECORD_FILE_NAME}",
            f"{RECORD_STORAGE_DIR}/{RECORD_BACKUP_DIR}/{backup_file_name}",
        )
        app_logger.info(
            "Existing set of records are saved in backup file: %s/%s/%s",
            RECORD_STORAGE_DIR,
            RECORD_BACKUP_DIR,
            backup_file_name,
        )

    with open(
        f"{RECORD_STORAGE_DIR}/{RECORD_FILE_NAME}", "w", encoding="UTF-8"
    ) as record_file:
        json.dump(records, record_file)

    app_logger.info(
        "New dummy records are successfully stored in: %s/%s",
        RECORD_STORAGE_DIR,
        RECORD_FILE_NAME,
    )


def store_record_to_mongo(records: List[dict]):
    """
    Function to store recors in mongodb as well on user request
    """
    try:
        mongo_client = MongoClient(settings.MONGO_DB_HOST, settings.MONGO_DB_PORT)
        db = mongo_client[MONGO_DB_NAME]
        collection = db[MONGO_DB_COLLECTION]
        existin_collection = collection.find()
        if existin_collection:
            app_logger.info(
                "Existing records found in MongoDB, moving them to backup collection"
            )
            collection.aggregate(
                [
                    {"$match": {}},
                    {
                        "$out": MONGO_DB_BACKUP_COLLECTION.format(
                            date_format=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                        )
                    },
                ]
            )
            app_logger.info(
                "Successfully moved existing records moved to backup collection"
            )

            app_logger.info("Droping records from the existing collection")
            collection.delete_many({})
            app_logger.info("Successfully dropped records from the collection")
    except Exception as exc:
        app_logger.error(
            "Error occured while connecting to MongoDB to Store the records: %s", exc
        )
        raise MongoDBConnectionError(
            message="MongoDB connection Error while storing the records"
        ) from exc

    try:
        collection.insert_many(records)
    except Exception as exc:
        app_logger.error("Error occured while storing records in MongoDB: %s", exc)
        raise MongoDBOperationError(
            message="MongoDB Operation Error while writing records to MongoDB"
        ) from exc

    return True


def store_record_to_sql(records: List[dict]):
    # pylint: disable=too-many-statements
    """
    Function to store recors in sql as well on user request
    """
    try:
        conn = mysql.connector.connect(
            host=settings.SQL_DB_HOST,
            user=settings.SQL_DB_USERNAME,
            password=settings.SQL_DB_PASSWORD,
            database=SQL_DB_NAME,
        )
        cursor = conn.cursor()
    except Exception as exc:
        app_logger.error(
            "Error occured while connecting to SQL to Store the records: %s", exc
        )
        raise SQLConnectionError(
            message="SQL connection Error while storing the records"
        ) from exc

    try:
        app_logger.info("Checking for existence of %s table", SQL_RECORDS_TABLE)
        cursor.execute(
            f"""SELECT COUNT(*) FROM information_schema.tables WHERE table_schema """
            f"""= '{SQL_DB_NAME}' AND table_name = '{SQL_RECORDS_TABLE}'"""  # nosec
        )
        if cursor.fetchone()[0] > 0:
            app_logger.info(
                "Existing table found in MySQL: %s; taking backup of the same",
                SQL_RECORDS_TABLE,
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS "  # nosec
                f"{SQL_RECORDS_BKP_TABLE.format(date_format=datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))}"  # nosec  # pylint: disable=line-too-long
                " AS SELECT * FROM {SQL_RECORDS_TABLE}"  # nosec
            )
            app_logger.info("Successfully moved existing records moved to backup table")

            app_logger.info(
                "Droping records from the existing table: %s", SQL_RECORDS_TABLE
            )
            cursor.execute(f"DELETE FROM {SQL_RECORDS_TABLE}")  # nosec
            app_logger.info(
                "Successfully dropped records from the table: %s", SQL_RECORDS_TABLE
            )

        app_logger.info("Checking for existence of %s table", SQL_DEVICES_TABLE)
        cursor.execute(
            f"""SELECT COUNT(*) FROM information_schema.tables WHERE """
            f"""table_schema = '{SQL_DB_NAME}' AND table_name = '{SQL_DEVICES_TABLE}'"""  # nosec # pylint: disable=line-too-long
        )
        if cursor.fetchone()[0] > 0:
            app_logger.info(
                "Existing table found in MySQL: %s; taking backup of the same",
                SQL_DEVICES_TABLE,
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS "  # nosec
                f"{SQL_DEVICES_BKP_TABLE.format(date_format=datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))}"  # nosec  # pylint: disable=line-too-long
                " AS SELECT * FROM {SQL_DEVICES_TABLE}"  # nosec
            )
            app_logger.info("Successfully moved existing records moved to backup table")

            app_logger.info(
                "Droping records from the existing table: %s", SQL_DEVICES_TABLE
            )
            cursor.execute(f"DELETE FROM {SQL_DEVICES_TABLE}")  # nosec
            app_logger.info(
                "Successfully dropped records from the table: %s", SQL_DEVICES_TABLE
            )
    except Exception as exc:
        app_logger.error(
            "Error occured while creating backup of existing records in SQL: %s", exc
        )
        raise SQLOperationError(
            message="SQL operation error occured while "
            "creating backup of existing records"
        ) from exc

    try:
        app_logger.info("Creating tables if not exists")
        cursor.execute(DEVICES_TABLE_CREATE)
        cursor.execute(RECORDS_TABLE_CREATE)
    except Exception as exc:
        app_logger.error("Error occured while creating tables in SQL: %s", exc)
        raise SQLOperationError(
            message="SQL operation error occured while creating tables"
        ) from exc

    try:
        for record in records:
            record_id = record["_id"]
            origination_time = record["originationTime"]
            cluster_id = record["clusterId"]
            user_id = record["userId"]
            phone_number = record["devices"]["phone"]
            voicemail = record["devices"]["voicemail"]

            cursor.execute(
                DEVICES_TABLE_INSERT.format(
                    devices_table=SQL_DEVICES_TABLE,
                    value_phone_number=phone_number,
                    value_voicemail=voicemail,
                )
            )
            device_id = cursor.lastrowid

            cursor.execute(
                RECORDS_TABLE_INSERT.format(
                    records_table=SQL_RECORDS_TABLE,
                    value_record_id=record_id,
                    value_user_id=user_id,
                    value_device_id=device_id,
                    value_cluster_id=cluster_id,
                    value_origination_time=origination_time,
                )
            )
        conn.commit()
    except Exception as exc:
        app_logger.error("Error occurred while storing records in SQL: %s", exc)
        conn.rollback()
        raise SQLOperationError(
            message="SQL operation error while storing the records"
        ) from exc
    finally:
        cursor.close()
        conn.close()


def main():
    """Main function to generate records"""
    parser = argparse.ArgumentParser(
        prog="Record generator script",
        description="Generate given number of dummy records",
    )
    parser.add_argument("--number_of_records", required=True, type=int)
    parser.add_argument("--store_to_mongodb", required=False, type=bool, default=False)
    parser.add_argument("--store_to_sql", required=False, type=bool, default=False)

    args = parser.parse_args()

    dummy_records = generate_records(args.number_of_records)

    store_records_to_json(dummy_records)

    if args.store_to_mongodb:
        app_logger.info("Storing the generated records to MongoDB")
        store_record_to_mongo(dummy_records)
        app_logger.info("Successfully stored generated records in MongoDB")

    if args.store_to_sql:
        app_logger.info("Storing the generated records to SQL")
        store_record_to_sql(dummy_records)
        app_logger.info("Successfully stored generated records in SQL")


if __name__ == "__main__":
    main()  # pragma: no cover
