from datetime import datetime
from typing import List

from pymongo import MongoClient

from app.api.filter_records.models import FilterRequestModel, FilterResponseModel
from app.custom_exceptions.filter_from_mongo_exception import (
    MongoDBConnectionError,
    MongoDBOperationError,
)
from app.utils.logger_helper import app_logger


class FilterRecordFromMongo:
    """
    Class for all the services related to filtering records from MongoDB
    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        mongo_host: str,
        mongo_port: str,
        mongo_db_name: str,
        mongo_collection_name: str,
        request: FilterRequestModel,
    ) -> None:
        self.request = request

        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_db_name = mongo_db_name
        self.mongo_collection_name = mongo_collection_name

        self.client = MongoClient(self.mongo_host, self.mongo_port)
        self.db = self.client[self.mongo_db_name]
        self.collection = self.db[self.mongo_collection_name]

    def mongo_db_query_builder(self) -> dict:
        """
        Build MongoDB query
        """

        start_date = int(
            datetime.strptime(
                self.request.date_range.split("to")[0].strip(), "%Y-%m-%d"
            ).timestamp()
        )
        end_date = int(
            datetime.strptime(
                self.request.date_range.split("to")[1].strip(), "%Y-%m-%d"
            ).timestamp()
        )

        query = {"originationTime": {"$gte": start_date, "$lte": end_date}}

        filter_conditions = [
            ("cluster", "clusterId"),
            ("user_id", "userId"),
            ("phone_number", "devices.phone"),
            ("voice_mail", "devices.voicemail"),
        ]

        extra_query_params = []

        for filter_request_field, model_attribute in filter_conditions:
            value = getattr(self.request, filter_request_field, None)
            if value:
                extra_query_params.append({model_attribute: value})

        if extra_query_params:
            query.update({"$or": extra_query_params})

        return query

    def filter_record_with_query(self, query: dict) -> List:
        """
        Filter records with given query
        """
        try:
            app_logger.info("Filtering records with query: %s", query)

            filtered_records = self.collection.find(query)
            filtered_records = list(filtered_records)

            app_logger.info(
                "Records filtered successfully with given query: %d records",
                len(filtered_records),
            )

            return filtered_records

        except Exception as exc:
            app_logger.error(
                "Error occured while filtering records from MongoDB with query: %s", exc
            )
            raise MongoDBOperationError(
                message="Error occured while filtering records with given query"
            ) from exc

    def filter_records_from_mongo(self) -> FilterResponseModel:
        """
        Filter records from MongoDB
        """

        try:
            app_logger.info("Checking connection to MongoDB")
            _ = self.collection.find_one()
        except Exception as exc:
            app_logger.error("Error while connecting to MongoDB: %s", exc)
            raise MongoDBConnectionError(
                message="Error occured while connecting to MongoDB"
            ) from exc

        final_filtered_records = []

        try:
            app_logger.info("Filtering records with query")
            final_filtered_records = self.filter_record_with_query(
                self.mongo_db_query_builder()
            )
            app_logger.info(
                "Records filtered successfully with given query: %d records",
                len(final_filtered_records),
            )
        except Exception as exc:
            app_logger.error("Error while filtering records with query: %s", exc)
            raise exc

        app_logger.info(
            "Number of records found after filtering JSON file with given: %d records",
            len(final_filtered_records),
        )
        return FilterResponseModel(result=final_filtered_records)
