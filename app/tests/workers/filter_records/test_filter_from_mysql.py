from datetime import datetime
from unittest.mock import MagicMock, patch

import mysql.connector
import pytest

from app.api.filter_records.models import FilterRequestModel
from app.core.constants import SQL_RECORDS_TABLE
from app.custom_exceptions.filter_from_sql_exception import (
    SQLConnectionError,
    SQLOperationError,
)
from app.workers.filter_records.filter_from_mysql import FilterRecordFromSQL


class TestFilterRecordFromSQL:
    """
    Test for filtering records from SQL
    """

    @patch("app.workers.filter_records.filter_from_mysql.mysql.connector.connect")
    def test_sql_worker_initialization(self, mock_connect):
        """
        Test case for initialization of SQL worker
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        request = FilterRequestModel(
            **{
                "dateRange": "2021-01-01 to 2021-01-02",
                "cluster": "cluster_id",
                "userId": "user_id",
            }
        )
        filter_record = FilterRecordFromSQL(
            mysql_host="test",
            mysql_db_name="test",
            mysql_password="test",  # nosec
            mysql_user="test",
            request=request,
        )

        assert filter_record.request == request

    @patch("app.workers.filter_records.filter_from_mysql.mysql.connector.connect")
    def test_sql_worker_initialization_with_exception(self, mock_connect):
        """
        Test case for initialization of SQL worker
        """

        mock_connect.side_effect = mysql.connector.Error

        request = FilterRequestModel(
            **{
                "dateRange": "2021-01-01 to 2021-01-02",
                "cluster": "cluster_id",
                "userId": "user_id",
            }
        )

        with pytest.raises(SQLConnectionError):
            _ = FilterRecordFromSQL(
                mysql_host="test",
                mysql_db_name="test",  # nosec
                mysql_password="test",
                mysql_user="test",
                request=request,
            )

    @patch("app.workers.filter_records.filter_from_mysql.mysql.connector.connect")
    def test_sql_query_builder_basic(self, mock_connect):
        """
        Test case for basic SQL query building
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromSQL(
            mysql_host="test",
            mysql_db_name="test",
            mysql_password="test",  # nosec
            mysql_user="test",
            request=request,
        )

        expected_query = (
            f"SELECT * FROM {SQL_RECORDS_TABLE} WHERE originationTime "  # nosec
            "BETWEEN '2021-01-01 00:00:00' AND '2021-01-02 00:00:00'"  # nosec
        )
        assert filter_record.sql_query_builder() == expected_query

    @patch("app.workers.filter_records.filter_from_mysql.mysql.connector.connect")
    def test_sql_query_builder_with_filters(self, mock_connect):
        """
        Test case for SQL query building with additional filters
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        request = FilterRequestModel(
            **{
                "dateRange": "2021-01-01 to 2021-01-02",
                "userId": "user_id",
                "cluster": "cluster_id",
            }
        )
        filter_record = FilterRecordFromSQL(
            mysql_host="test",
            mysql_db_name="test",
            mysql_password="test",  # nosec
            mysql_user="test",
            request=request,
        )

        expected_query = (
            f"SELECT * FROM {SQL_RECORDS_TABLE} WHERE originationTime "  # nosec
            "BETWEEN '2021-01-01 00:00:00' AND '2021-01-02 00:00:00' AND "  # nosec
            "(userId = 'user_id' OR clusterId = 'cluster_id')"  # nosec
        )
        assert filter_record.sql_query_builder() == expected_query

    @patch("app.workers.filter_records.filter_from_mysql.mysql.connector.connect")
    def test_sql_query_builder_with_device_filters(self, mock_connect):
        """
        Test case for SQL query building with device filters
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        request = FilterRequestModel(
            **{"dateRange": "2021-01-01 to 2021-01-02", "phoneNumber": "1234567890"}
        )
        filter_record = FilterRecordFromSQL(
            mysql_host="test",
            mysql_db_name="test",
            mysql_password="test",  # nosec
            mysql_user="test",
            request=request,
        )

        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [{"_id": 1}, {"_id": 2}]

        expected_query = (
            f"SELECT * FROM {SQL_RECORDS_TABLE} WHERE originationTime "  # nosec
            "BETWEEN '2021-01-01 00:00:00' AND '2021-01-02 00:00:00' "  # nosec
            "AND (deviceId IN (1,2))"  # nosec
        )
        assert filter_record.sql_query_builder() == expected_query

    @patch("app.workers.filter_records.filter_from_mysql.mysql.connector.connect")
    def test_process_records(self, mock_connect):
        """
        Test case for processing records from MySQL
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromSQL(
            mysql_host="test",
            mysql_db_name="test",
            mysql_password="test",  # nosec
            mysql_user="test",
            request=request,
        )

        records = [
            {
                "_id": 1,
                "originationTime": datetime(2021, 1, 1, 12, 0, 0),
                "deviceId": 1,
                "userId": "user1",
                "clusterId": "cluster1",
            },
            {
                "_id": 2,
                "originationTime": datetime(2021, 1, 2, 12, 0, 0),
                "deviceId": 2,
                "userId": "user2",
                "clusterId": "cluster2",
            },
        ]

        mock_cursor.execute.side_effect = [None, None]
        mock_cursor.fetchone.side_effect = [
            {"phone": "1234567890", "voicemail": "voicemail1"},
            {"phone": "0987654321", "voicemail": "voicemail2"},
        ]

        processed_records = filter_record.process_records(records)

        assert len(processed_records) == 2
        assert processed_records[0].origination_time == "2021-01-01 12:00:00"
        assert processed_records[0].devices.model_dump() == {
            "phone": "1234567890",
            "voicemail": "voicemail1",
        }
        assert processed_records[1].origination_time == "2021-01-02 12:00:00"
        assert processed_records[1].devices.model_dump() == {
            "phone": "0987654321",
            "voicemail": "voicemail2",
        }

    @patch("app.workers.filter_records.filter_from_mysql.mysql.connector.connect")
    def test_filter_records_from_sql_success(self, mock_connect):
        """
        Test case for successful filtering of records from MySQL
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromSQL(
            mysql_host="test",
            mysql_db_name="test",
            mysql_password="test",  # nosec
            mysql_user="test",
            request=request,
        )

        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            {
                "_id": 1,
                "originationTime": datetime(2021, 1, 1, 12, 0, 0),
                "deviceId": 1,
                "userId": "user1",
                "clusterId": "cluster1",
            },
            {
                "_id": 2,
                "originationTime": datetime(2021, 1, 2, 12, 0, 0),
                "deviceId": 2,
                "userId": "user2",
                "clusterId": "cluster2",
            },
        ]
        mock_cursor.fetchone.side_effect = [
            {"phone": "1234567890", "voicemail": "voicemail1"},
            {"phone": "0987654321", "voicemail": "voicemail2"},
        ]

        response = filter_record.filter_records_from_sql()

        assert len(response.result) == 2
        assert response.result[0].origination_time == "2021-01-01 12:00:00"
        assert response.result[0].devices.model_dump() == {
            "phone": "1234567890",
            "voicemail": "voicemail1",
        }
        assert response.result[1].origination_time == "2021-01-02 12:00:00"
        assert response.result[1].devices.model_dump() == {
            "phone": "0987654321",
            "voicemail": "voicemail2",
        }

    @patch("app.workers.filter_records.filter_from_mysql.mysql.connector.connect")
    def test_filter_records_from_sql_sql_error(self, mock_connect):
        """
        Test case for SQL error during filtering of records from MySQL
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromSQL(
            mysql_host="test",
            mysql_db_name="test",
            mysql_password="test",  # nosec
            mysql_user="test",
            request=request,
        )

        mock_cursor.execute.side_effect = mysql.connector.Error

        with pytest.raises(SQLOperationError):
            filter_record.filter_records_from_sql()

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
