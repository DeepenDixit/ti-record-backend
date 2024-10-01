import argparse
import json
import os
from unittest.mock import MagicMock, patch

import pytest

from app.core.constants import RECORD_FILE_NAME, RECORD_STORAGE_DIR, USER_ID_LENGTH
from app.custom_exceptions.filter_from_mongo_exception import (
    MongoDBConnectionError,
    MongoDBOperationError,
)
from app.custom_exceptions.filter_from_sql_exception import (
    SQLConnectionError,
    SQLOperationError,
)
from app.utils.record_generator import (
    generate_long_random_int,
    generate_records,
    main,
    store_record_to_mongo,
    store_record_to_sql,
    store_records_to_json,
)


@pytest.mark.parametrize("length", [1, 2, 3, 4, 5, 6, 7, 8, 9])
def test_generate_long_random_int(length):
    """Test generate_long_random_int function"""
    random_int = generate_long_random_int(length)
    assert isinstance(random_int, str)
    assert len(random_int) == length
    assert random_int != "0" * length


@patch("app.utils.record_generator.generate_long_random_int")
def test_generate_records(mock_generate_long_random_int):
    """
    Test generate_records function
    """
    mock_generate_long_random_int.return_value = "1" * USER_ID_LENGTH

    records = generate_records(10)
    assert len(records) == 10

    for record in records:
        assert isinstance(record, dict)

        assert "_id" in record
        assert "originationTime" in record
        assert "clusterId" in record
        assert "userId" in record
        assert "devices" in record
        assert "phone" in record["devices"]
        assert "voicemail" in record["devices"]

        assert isinstance(record["_id"], int)
        assert isinstance(record["originationTime"], int)
        assert isinstance(record["clusterId"], str)
        assert isinstance(record["userId"], str)
        assert isinstance(record["devices"], dict)
        assert isinstance(record["devices"]["phone"], str)
        assert isinstance(record["devices"]["voicemail"], str)

        assert record["devices"]["phone"].startswith("SEP")
        assert record["devices"]["voicemail"].endswith("VM")


class TestStoreRecordsToJson:
    """
    Test store_records_to_json function
    """

    def test_store_records_to_json(self):
        """
        Test store_records_to_json function
        """
        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        store_records_to_json(records)

        with open(
            f"{RECORD_STORAGE_DIR}/{RECORD_FILE_NAME}", "r", encoding="UTF-8"
        ) as file:
            stored_records = json.load(file)

        assert os.path.exists(f"{RECORD_STORAGE_DIR}/{RECORD_FILE_NAME}")
        assert stored_records == records

    @patch("app.utils.record_generator.os.path.exists")
    @patch("app.utils.record_generator.os.makedirs")
    def test_store_records_to_json_with_dir_creation(self, mock_makedirs, mock_exists):
        """
        Test store_records_to_json function
        """
        mock_exists.return_value = False
        mock_makedirs.return_value = None

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        store_records_to_json(records)

        with open(
            f"{RECORD_STORAGE_DIR}/{RECORD_FILE_NAME}", "r", encoding="UTF-8"
        ) as file:
            stored_records = json.load(file)

        assert stored_records == records

    @patch("app.utils.record_generator.os.path.exists")
    @patch("app.utils.record_generator.os.makedirs")
    def test_store_records_to_json_with_sub_dir_creation(
        self, mock_makedirs, mock_exists
    ):
        """
        Test store_records_to_json function
        """
        mock_exists.side_effect = [True, False, False]
        mock_makedirs.return_value = None

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        store_records_to_json(records)

        with open(
            f"{RECORD_STORAGE_DIR}/{RECORD_FILE_NAME}", "r", encoding="UTF-8"
        ) as file:
            stored_records = json.load(file)

        assert stored_records == records


class TestStoreRecordsToMongoDB:
    """
    Test store_records_to_mongodb function
    """

    @patch("app.utils.record_generator.MongoClient")
    def test_store_records_to_mongodb_success(self, mock_mongo_client):
        """
        Test successful storage of records to MongoDB
        """
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_mongo_client.return_value = mock_db
        mock_db.return_value.__getitem__.return_value = mock_collection
        mock_collection.find.return_value = True

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
            {
                "_id": 2,
                "originationTime": 1234567820,
                "clusterId": "cluster_id2",
                "userId": "user_id2",
                "devices": {"phone": "phone2", "voicemail": "voicemail2"},
            },
        ]

        result = store_record_to_mongo(records)

        assert result is True

    @patch("app.utils.record_generator.MongoClient")
    def test_store_records_to_mongodb_connection_error(self, mock_mongo_client):
        """
        Test MongoDB connection error
        """
        mock_mongo_client.side_effect = Exception("Connection error")

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        with pytest.raises(MongoDBConnectionError):
            store_record_to_mongo(records)

    @patch("app.utils.record_generator.MongoClient")
    def test_store_records_to_mongodb_operation_error(self, mock_mongo_client):
        """
        Test MongoDB operation error
        """
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_mongo_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.insert_many.side_effect = Exception("Operation error")

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        with pytest.raises(MongoDBOperationError):
            store_record_to_mongo(records)


class TestStoreRecordsToSQL:
    """
    Test store_record_to_sql function
    """

    @patch("app.utils.record_generator.mysql.connector.connect")
    def test_store_record_to_sql_success(self, mock_connect):
        """
        Test successful storage of records to SQL
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        store_record_to_sql(records)

        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("app.utils.record_generator.mysql.connector.connect")
    def test_store_record_to_sql_connection_error(self, mock_connect):
        """
        Test SQL connection error
        """
        mock_connect.side_effect = Exception("Connection error")

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        with pytest.raises(SQLConnectionError):
            store_record_to_sql(records)

    @patch("app.utils.record_generator.mysql.connector.connect")
    def test_store_record_to_sql_operation_error(self, mock_connect):
        """
        Test SQL operation error
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Operation error")

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        with pytest.raises(SQLOperationError):
            store_record_to_sql(records)

    @patch("app.utils.record_generator.mysql.connector.connect")
    def test_store_record_to_sql_execution_error(self, mock_connect):
        """
        Test SQL operation error
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]
        mock_cursor.execute.side_effect = [
            True,
            True,
            True,
            True,
            True,
            True,
            Exception("Execution error"),
        ]

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        with pytest.raises(Exception):
            store_record_to_sql(records)

    @patch("app.utils.record_generator.mysql.connector.connect")
    def test_store_record_to_sql_execution_error_2(self, mock_connect):
        """
        Test SQL operation error
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]
        mock_cursor.execute.side_effect = [
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            Exception("Execution error"),
        ]

        records = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        with pytest.raises(Exception):
            store_record_to_sql(records)
            mock_conn.rollback.assert_called_once()


class TestRecordGenerator:
    """
    Test the main record generator functions
    """

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    @patch("argparse.ArgumentParser.parse_args")
    @patch("app.utils.record_generator.generate_records")
    @patch("app.utils.record_generator.store_records_to_json")
    @patch("app.utils.record_generator.store_record_to_mongo")
    @patch("app.utils.record_generator.store_record_to_sql")
    def test_main(
        self,
        mock_store_record_to_sql,
        mock_store_record_to_mongo,
        mock_store_records_to_json,
        mock_generate_records,
        mock_parse_args,
    ):
        """
        Test the main function
        """
        mock_parse_args.return_value = argparse.Namespace(
            number_of_records=10, store_to_mongodb=True, store_to_sql=True
        )
        mock_generate_records.return_value = [
            {
                "_id": 1,
                "originationTime": 1234567890,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            }
        ]

        main()

        mock_generate_records.assert_called_once_with(10)
        mock_store_records_to_json.assert_called_once()
        mock_store_record_to_mongo.assert_called_once()
        mock_store_record_to_sql.assert_called_once()
