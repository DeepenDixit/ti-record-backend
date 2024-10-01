from unittest.mock import mock_open, patch

import pytest

from app.api.filter_records.models import (
    FilterRequestModel,
    FilterResponseModel,
    RecordModel,
)
from app.custom_exceptions.filter_from_json_exceptions import JSONFileNotFoundError
from app.workers.filter_records.filter_from_json import FilterRecordFromJSON


class TestFilterRecordFromJSON:
    # pylint: disable=redefined-outer-name, unused-argument
    """
    Test cases for the Filter From JSON worker functions.
    """

    @patch("app.workers.filter_records.filter_from_json.os.path.exists")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"_id": 1, "originationTime": 1234567890, '
        '"clusterId": "cluster_id", "userId": "user_id", '
        '"devices": {"phone": "phone", '
        '"voicemail": "voicemail"}}]',
    )
    def test_load_json_file(self, mock_open, mock_path_exists):
        """
        Test case for loading JSON file
        """
        mock_path_exists.return_value = True

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromJSON(request)
        records = filter_record.load_json_file()

        assert len(records) == 1
        assert records[0].cluster_id == "cluster_id"

    @patch("app.workers.filter_records.filter_from_json.os.path.exists")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"_id": 1, "originationTime": 1234567890, '
        '"clusterId": "cluster_id", "userId": "user_id", '
        '"devices": {"phone": "phone", '
        '"voicemail": "voicemail"}}]',
    )
    def test_load_json_file_not_exist(self, mock_open, mock_path_exists):
        """
        Test case for loading JSON file
        """
        mock_path_exists.return_value = False

        request = FilterRequestModel(**{"dateRange": "2021-01-01 to 2021-01-02"})
        filter_record = FilterRecordFromJSON(request)

        with pytest.raises(JSONFileNotFoundError):
            _ = filter_record.load_json_file()

    @pytest.mark.parametrize(
        "date_range, expected_number_of_records",
        [
            ("2021-01-01 to 2021-01-02", 1),
            ("2021-01-10 to 2021-02-02", 0),
            ("2021-01-12 to 2021-12-02", 0),
            ("2021-10-01 to 2022-01-02", 0),
        ],
    )
    def test_filter_record_with_date(self, date_range, expected_number_of_records):
        """
        Test case for filtering records with date range
        """
        request = FilterRequestModel(**{"dateRange": date_range})
        filter_record = FilterRecordFromJSON(request)
        records = [
            {
                "_id": 1,
                "originationTime": 1609459200,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
            {
                "_id": 2,
                "originationTime": 1609545600,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
            {
                "_id": 3,
                "originationTime": 1609632000,
                "clusterId": "cluster_id",
                "userId": "user_id",
                "devices": {"phone": "phone", "voicemail": "voicemail"},
            },
        ]
        records = [RecordModel(**record) for record in records]

        filtered_records = filter_record.filter_record_with_date(records)
        assert len(filtered_records) == expected_number_of_records

    @patch("app.workers.filter_records.filter_from_json.os.path.exists")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"_id": 1, "originationTime": 1609459200, '
        '"clusterId": "cluster_id", "userId": "user_id", '
        '"devices": {"phone": "phone", '
        '"voicemail": "voicemail"}}]',
    )
    def test_filter_records_from_json(self, mock_open, mock_path_exists):
        """
        Test case for filtering records from JSON
        """
        mock_path_exists.return_value = True

        request = FilterRequestModel(
            **{"dateRange": "2020-12-31 to 2021-01-02", "cluster": "cluster_id"}
        )
        filter_record = FilterRecordFromJSON(request)
        response = filter_record.filter_records_from_json()

        assert isinstance(response, FilterResponseModel)
        assert len(response.result) == 1
        assert response.result[0].cluster_id == "cluster_id"

    @patch("app.workers.filter_records.filter_from_json.os.path.exists")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"_id": 1, "originationTime": 1609459200, '
        '"clusterId": "cluster_id", "userId": "user_id", '
        '"devices": {"phone": "phone", '
        '"voicemail": "voicemail"}}]',
    )
    def test_filter_records_from_json_no_filters(self, mock_open, mock_path_exists):
        """
        Test case for filtering records from JSON with no extra filters
        """
        mock_path_exists.return_value = True

        request = FilterRequestModel(**{"dateRange": "2020-12-31 to 2021-01-02"})
        filter_record = FilterRecordFromJSON(request)
        response = filter_record.filter_records_from_json()

        assert isinstance(response, FilterResponseModel)
        assert len(response.result) == 1
        assert response.result[0].cluster_id == "cluster_id"

    @patch("app.workers.filter_records.filter_from_json.os.path.exists")
    def test_filter_records_from_json_no_file_found(self, mock_path_exists):
        """
        Test case for filtering records from JSON with no extra filters
        """
        mock_path_exists.return_value = False

        request = FilterRequestModel(**{"dateRange": "2020-12-31 to 2021-01-02"})
        filter_record = FilterRecordFromJSON(request)
        with pytest.raises(JSONFileNotFoundError):
            _ = filter_record.filter_records_from_json()

    @patch(
        "app.workers.filter_records.filter_from_json."
        "FilterRecordFromJSON.filter_record_with_date"
    )
    @patch("app.workers.filter_records.filter_from_json.os.path.exists")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"_id": 1, "originationTime": 1609459200, '
        '"clusterId": "cluster_id", "userId": "user_id", '
        '"devices": {"phone": "phone", '
        '"voicemail": "voicemail"}}]',
    )
    def test_filter_records_from_json_with_date_exception(
        self, mock_open, mock_path_exists, mock_filter_record_with_date
    ):
        """
        Test case for filtering records from JSON with no extra filters
        """
        mock_path_exists.return_value = True
        mock_filter_record_with_date.side_effect = Exception(
            "Error while filtering records with date range"
        )

        request = FilterRequestModel(**{"dateRange": "2020-12-31 to 2021-01-02"})
        filter_record = FilterRecordFromJSON(request)
        with pytest.raises(Exception):
            _ = filter_record.filter_records_from_json()
