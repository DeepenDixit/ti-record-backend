from unittest.mock import MagicMock, patch

import pytest

from app.api.filter_records.models import (
    FilterRequestModel,
    FilterResponseModel,
    RecordModel,
)
from app.custom_exceptions.filter_from_mongo_exception import (
    MongoDBConnectionError,
    MongoDBOperationError,
)
from app.workers.filter_records.filter_from_mongo import FilterRecordFromMongo


class TestFilterRecordFromMongo:
    """
    Test cases to filter records from mongo
    """

    def test_mongo_db_query_builder(self):
        """
        Test case for building mongo db query
        """
        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromMongo(
            mongo_host="test",
            mongo_db_name="test",
            mongo_collection_name="test",
            mongo_port=0,
            request=request,
        )
        query = filter_record.mongo_db_query_builder()

        assert query == {"originationTime": {"$gte": 1609477200, "$lte": 1609563600}}

    def test_mongo_db_query_builder_extra_fields(self):
        """
        Test case for building mongo db query
        """
        request = FilterRequestModel(
            **{
                "dateRange": "2021-01-01 to 2021-01-02",
                "cluster": "cluster_id",
                "userId": "user_id",
            }
        )
        filter_record = FilterRecordFromMongo(
            mongo_host="test",
            mongo_db_name="test",
            mongo_collection_name="test",
            mongo_port=0,
            request=request,
        )
        query = filter_record.mongo_db_query_builder()

        assert query == {
            "originationTime": {"$gte": 1609477200, "$lte": 1609563600},
            "$or": [{"clusterId": "cluster_id"}, {"userId": "user_id"}],
        }

    @patch("app.workers.filter_records.filter_from_mongo.MongoClient")
    def test_filter_record_with_query(self, mock_mongo_client):
        """
        Test case for filtering records with given query
        """
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromMongo(
            mongo_host="test",
            mongo_db_name="test",
            mongo_collection_name="test",
            mongo_port=0,
            request=request,
        )

        mock_collection.find.return_value = [
            {
                "_id": 1,
                "originationTime": 1609459200,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
            {
                "_id": 2,
                "originationTime": 1609459200,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
        ]
        filter_record.collection = mock_collection

        query = filter_record.mongo_db_query_builder()
        result = filter_record.filter_record_with_query(query)

        assert result == [
            {
                "_id": 1,
                "originationTime": 1609459200,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
            {
                "_id": 2,
                "originationTime": 1609459200,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
        ]
        mock_collection.find.assert_called_once_with(query)

    @patch("app.workers.filter_records.filter_from_mongo.MongoClient")
    def test_filter_record_with_query_exception(self, mock_mongo_client):
        """
        Test case for exception while filtering records with given query
        """
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromMongo(
            mongo_host="test",
            mongo_db_name="test",
            mongo_collection_name="test",
            mongo_port=0,
            request=request,
        )

        mock_collection.find.side_effect = Exception("Test exception")
        filter_record.collection = mock_collection

        with pytest.raises(MongoDBOperationError):
            query = filter_record.mongo_db_query_builder()
            filter_record.filter_record_with_query(query)

    @patch("app.workers.filter_records.filter_from_mongo.MongoClient")
    def test_filter_records_from_mongo(self, mock_mongo_client):
        """
        Test case for filtering records from MongoDB
        """
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromMongo(
            mongo_host="test",
            mongo_db_name="test",
            mongo_collection_name="test",
            mongo_port=0,
            request=request,
        )

        mock_collection.find_one.return_value = {
            "_id": 1,
            "originationTime": 1609459200,
            "clusterId": "cluster_id",
            "userId": "user_id",
            "devices": {"phone": "phone", "voicemail": "voicemail"},
        }

        mock_collection.find.return_value = [
            {
                "_id": 1,
                "originationTime": 1609459200,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
            {
                "_id": 2,
                "originationTime": 1609459200,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
        ]
        filter_record.collection = mock_collection

        result = filter_record.filter_records_from_mongo()

        assert isinstance(result, FilterResponseModel)
        assert result.result == [
            RecordModel(
                **{
                    "_id": 1,
                    "originationTime": 1609459200,
                    "clusterId": "cluster_id",
                    "userId": "user_id",
                    "devices": {"phone": "phone", "voicemail": "voicemail"},
                }
            ),
            RecordModel(
                **{
                    "_id": 2,
                    "originationTime": 1609459200,
                    "clusterId": "cluster_id",
                    "userId": "user_id",
                    "devices": {"phone": "phone", "voicemail": "voicemail"},
                }
            ),
        ]
        mock_collection.find_one.assert_called_once()
        mock_collection.find.assert_called_once()

    @patch("app.workers.filter_records.filter_from_mongo.MongoClient")
    def test_filter_records_from_mongo_connection_error(self, mock_mongo_client):
        """
        Test case for connection error while filtering records from MongoDB
        """
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromMongo(
            mongo_host="test",
            mongo_db_name="test",
            mongo_collection_name="test",
            mongo_port=0,
            request=request,
        )

        mock_collection.find_one.side_effect = Exception("Connection error")
        filter_record.collection = mock_collection

        with pytest.raises(MongoDBConnectionError):
            filter_record.filter_records_from_mongo()

    @patch(
        "app.workers.filter_records.filter_from_mongo."
        "FilterRecordFromMongo.filter_record_with_query"
    )
    @patch("app.workers.filter_records.filter_from_mongo.MongoClient")
    def test_filter_records_from_mongo_with_query_exception(
        self, mock_mongo_client, mock_filter_record_with_query
    ):
        """
        Test case for filtering records from MongoDB
        """
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromMongo(
            mongo_host="test",
            mongo_db_name="test",
            mongo_collection_name="test",
            mongo_port=0,
            request=request,
        )

        mock_collection.find_one.return_value = {
            "_id": 1,
            "originationTime": 1609459200,
            "clusterId": "cluster_id",
            "userId": "user_id",
            "devices": {"phone": "phone", "voicemail": "voicemail"},
        }

        mock_filter_record_with_query.side_effect = Exception("Test exception")

        with pytest.raises(Exception):
            _ = filter_record.filter_records_from_mongo()
