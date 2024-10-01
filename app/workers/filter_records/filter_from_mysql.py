from datetime import datetime
from typing import List

import mysql.connector

from app.api.filter_records.models import (
    FilterRequestModel,
    FilterResponseModel,
    RecordModel,
)
from app.core.constants import SQL_DEVICES_TABLE, SQL_RECORDS_TABLE
from app.custom_exceptions.filter_from_sql_exception import (
    SQLConnectionError,
    SQLOperationError,
)
from app.utils.logger_helper import app_logger


class FilterRecordFromSQL:
    """
    Class for all the services related to filtering records from MySQL
    """

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        mysql_host: str,
        mysql_user: str,
        mysql_password: str,
        mysql_db_name: str,
        request: FilterRequestModel,
    ) -> None:
        self.request = request

        self.mysql_host = mysql_host
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_db_name = mysql_db_name

        self.conn, self.cursor = self.__get_sql_connection_cursor()

    def __get_sql_connection_cursor(self):
        """
        Get MySQL cursor
        """
        try:
            app_logger.info("Establishing a connection with MySQL")
            conn = mysql.connector.connect(
                host=self.mysql_host,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_db_name,
            )
            cursor = conn.cursor(dictionary=True)
            app_logger.info("Successful connection established with MySQL")

            return conn, cursor
        except mysql.connector.Error as exc:
            app_logger.error("Error occurred while connecting to MySQL: %s", exc)
            raise SQLConnectionError(message="MySQL connection error") from exc

    def sql_query_builder(self) -> str:
        """
        Build MySQL query
        """
        start_date = datetime.strptime(
            self.request.date_range.split("to")[0].strip(), "%Y-%m-%d"
        ).strftime("%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(
            self.request.date_range.split("to")[1].strip(), "%Y-%m-%d"
        ).strftime("%Y-%m-%d %H:%M:%S")

        query = (
            f"""SELECT * FROM {SQL_RECORDS_TABLE} WHERE """  # nosec
            f"""originationTime BETWEEN '{start_date}' AND '{end_date}'"""  # nosec
        )

        if any(
            [
                self.request.user_id,
                self.request.cluster,
                self.request.phone_number,
                self.request.voice_mail,
            ]
        ):
            extra_query_params = []

            if self.request.user_id:
                extra_query_params.append(f"userId = '{self.request.user_id}'")

            if self.request.cluster:
                extra_query_params.append(f"clusterId = '{self.request.cluster}'")

            if self.request.phone_number or self.request.voice_mail:
                app_logger.info(
                    "Fetching device ids for phone number or voicemail"
                    " as required by requested filters"
                )
                device_ids_query = (
                    f"""SELECT _id FROM {SQL_DEVICES_TABLE} WHERE """  # nosec
                    f"""phone = '{self.request.phone_number}' OR """  # nosec
                    f"""voicemail = '{self.request.voice_mail}'"""  # nosec
                )
                self.cursor.execute(device_ids_query)
                device_ids = self.cursor.fetchall()
                app_logger.info(
                    "Device ids fetched successfully with requested filters"
                )

                device_ids = [str(device["_id"]) for device in device_ids]
                if device_ids:
                    extra_query_params.append(f"deviceId IN ({','.join(device_ids)})")

            query += " AND " + f"({' OR '.join(extra_query_params)})"

        app_logger.debug("query built for filtering records from MySQL: %s", query)

        return query

    def process_records(self, records: List[dict]) -> List[RecordModel]:
        """
        Process records from MySQL
        """
        app_logger.info("Processing records fetched from MySQL")
        processed_records = []

        for record in records:
            record["originationTime"] = record["originationTime"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            app_logger.info("Fetching device details from MySQL for response model")
            _ = self.cursor.execute(
                f"SELECT phone,voicemail FROM {SQL_DEVICES_TABLE} "  # nosec
                f"WHERE _id = {record['deviceId']}"  # nosec
            )
            device_details = self.cursor.fetchone()
            app_logger.info("Device details fetched successfully for response model")

            record["devices"] = device_details

            processed_records.append(record)

        return [RecordModel(**record) for record in processed_records]

    def filter_records_from_sql(self) -> List[RecordModel]:
        """
        Get filtered records from MySQL
        """
        try:
            app_logger.info("Building Query for filtering records from MySQL")
            query = self.sql_query_builder()
            app_logger.info("Query built successfully for filtering records from MySQL")

            app_logger.info(
                "Executing query for filtering records from MySQL: %s", query
            )
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            app_logger.info(
                "Query executed successfully for filtering "
                "records from MySQL: %d records found",
                len(records),
            )

            app_logger.info("Processing records fetched from MySQL for final response")
            records = self.process_records(records)
            app_logger.info("Records processed successfully for final response")

            return FilterResponseModel(result=records)

        except mysql.connector.Error as err:
            app_logger.error("Error occurred while querying MySQL: %s", err)
            raise SQLOperationError(message="MySQL operation error") from err

        finally:
            self.cursor.close()
            self.conn.close()
