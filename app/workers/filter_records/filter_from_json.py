import json
import os
from typing import List

from app.api.filter_records.models import (
    FilterRequestModel,
    FilterResponseModel,
    RecordModel,
)
from app.core.constants import RECORD_FILE_NAME, RECORD_STORAGE_DIR
from app.custom_exceptions.filter_from_json_exceptions import JSONFileNotFoundError
from app.utils.logger_helper import app_logger


class FilterRecordFromJSON:
    """
    Class for all the services related to filtering records from JSON
    """

    def __init__(self, request: FilterRequestModel):
        self.request = request

    def load_json_file(self) -> List[RecordModel]:
        """
        Check if JSON file is available
        """
        json_file_path = f"{RECORD_STORAGE_DIR}/{RECORD_FILE_NAME}"

        if not os.path.exists(json_file_path):
            app_logger.error("JSON file not found at location %s", json_file_path)
            raise JSONFileNotFoundError(f"File not found: {json_file_path}")

        with open(json_file_path, "r", encoding="UTF-8") as json_file:
            records = json.load(json_file)
            return [RecordModel(**record) for record in records]

    def filter_record_with_date(self, records: List[RecordModel]) -> List:
        """
        Filter records with date range
        """
        start_date, end_date = [
            date.strip() for date in self.request.date_range.split(" to ")
        ]
        filtered_records = []

        for record in records:
            if start_date <= record.origination_time <= end_date:
                filtered_records.append(record)

        return filtered_records

    def filter_records_from_json(self) -> FilterResponseModel:
        """
        Filter records from JSON
        """

        final_filtered_records = []

        try:
            app_logger.info("Loading the JSON file to filter the records")
            records = self.load_json_file()
            app_logger.info(
                "JSON file found successfully with %d records", len(records)
            )
        except JSONFileNotFoundError as exc:
            app_logger.error("Error while loading JSON file: %s", exc)
            raise JSONFileNotFoundError(
                message="No JSON file found to filter the records"
            ) from exc

        try:
            app_logger.info("Filtering records with date range")
            date_filtered_records = self.filter_record_with_date(records)
            app_logger.info(
                "Records filtered successfully with given date range: %d records",
                len(date_filtered_records),
            )
        except Exception as exc:
            app_logger.error("Error while filtering records with date range: %s", exc)
            raise exc

        filter_conditions = [
            ("cluster", "cluster_id"),
            ("user_id", "user_id"),
            ("phone_number", "devices.phone"),
            ("voice_mail", "devices.voicemail"),
        ]

        for filter_request_field, model_attribute in filter_conditions:
            value = getattr(self.request, filter_request_field, None)
            if value:
                app_logger.info(
                    "Filtering records with field: %s", filter_request_field
                )
                filtered_records = [
                    record
                    for record in date_filtered_records
                    if eval(  # nosec # pylint: disable=eval-used
                        f"record.{model_attribute}"
                    )
                    == value
                ]

                final_filtered_records.extend(filtered_records)

                app_logger.info(
                    "Records filtered successfully with %s filed: %d",
                    filter_request_field,
                    len(filtered_records),
                )

        if not any(
            getattr(self.request, filter_request_field, None)
            for filter_request_field, _ in filter_conditions
        ):
            app_logger.info(
                "No extra fields filter found in "
                "request; returning records with date range only"
            )
            final_filtered_records.extend(date_filtered_records)

        app_logger.info(
            "Number of records found after filtering JSON file with given: %d records",
            len(final_filtered_records),
        )
        return FilterResponseModel(result=final_filtered_records)
