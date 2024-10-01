import pytest

from app.api.filter_records.models import (
    DeviceModel,
    FilterRequestModel,
    FilterResponseModel,
    RecordModel,
)


class TestFilterRequestModel:
    """
    Test for FilterRequestModel
    """

    def test_filter_request_model(self):
        """
        Test FilterRequestModel with valid request
        """
        model_data = {
            "dateRange": "2021-01-01 to 2021-01-31",
            "phoneNumber": "1234567890",
            "voiceMail": "true",
            "userId": "user1",
            "cluster": "cluster",
        }
        filter_request = FilterRequestModel(**model_data)
        assert filter_request.date_range == "2021-01-01 to 2021-01-31"

    def test_filter_request_model_bad_request(self):
        """
        Test FilterRequestModel with invalid request
        """
        model_data = {
            "phoneNumber": "1234567890",
            "voiceMail": "true",
            "userId": "user1",
            "cluster": "cluster",
        }
        with pytest.raises(ValueError):
            FilterRequestModel(**model_data)

    @pytest.mark.parametrize(
        "date_range",
        ["some random", "2021-01-01 to 2021-01-01", "2021-01-31 to 2021-01-01"],
    )
    def test_filter_request_model_bad_date_range(self, date_range):
        """
        Test FilterRequestModel with invalid date range
        """
        model_data = {
            "dateRange": date_range,
            "phoneNumber": "1234567890",
            "voiceMail": "true",
            "userId": "user1",
            "cluster": "cluster",
        }
        with pytest.raises(ValueError):
            FilterRequestModel(**model_data)


class TestDeviceModel:
    """
    Test for DeviceModel
    """

    def test_device_model(self):
        """Test DeviceModel with valid request"""
        model_data = {"phone": "1234567890", "voicemail": "true"}
        device = DeviceModel(**model_data)
        assert device.phone == "1234567890"

    def test_device_model_bad_request(self):
        """Test DeviceModel with invalid request"""
        model_data = {"phone": "1234567890"}
        with pytest.raises(ValueError):
            DeviceModel(**model_data)


class TestRecordModel:
    """Test for RecordModel"""

    def test_record_model(self):
        """Test RecordModel with valid request"""
        model_data = {
            "_id": 1,
            "originationTime": "2021-01-01 00:00:00",
            "clusterId": "cluster",
            "userId": "user1",
            "devices": {"phone": "1234567890", "voicemail": "true"},
        }
        record = RecordModel(**model_data)
        assert record.id == 1

    def test_record_model_with_date_int(self):
        """Test RecordModel with originationTime as int"""
        model_data = {
            "_id": 1,
            "originationTime": 1610428800,
            "clusterId": "cluster",
            "userId": "user1",
            "devices": {"phone": "1234567890", "voicemail": "true"},
        }
        record = RecordModel(**model_data)
        assert record.origination_time == "2021-01-12 00:20:00"

    def test_record_model_bad_request(self):
        """Test RecordModel with invalid request"""
        model_data = {
            "originationTime": "2021-01-01 00:00:00",
            "clusterId": "cluster",
            "userId": "user1",
            "devices": {"phone": "1234567890", "voicemail": "true"},
        }
        with pytest.raises(ValueError):
            RecordModel(**model_data)


class TestFilterResponseModel:
    """Test for FilterResponseModel"""

    def test_filter_response_model(self):
        """Test FilterResponseModel with valid request"""
        model_data = {
            "result": [
                {
                    "_id": 1,
                    "originationTime": "2021-01-01 00:00:00",
                    "clusterId": "cluster",
                    "userId": "user1",
                    "devices": {"phone": "1234567890", "voicemail": "true"},
                },
                {
                    "_id": 2,
                    "originationTime": "2021-01-02 00:00:00",
                    "clusterId": "cluster",
                    "userId": "user2",
                    "devices": {"phone": "1234567890", "voicemail": "true"},
                },
            ]
        }
        filter_response = FilterResponseModel(**model_data)
        assert filter_response.number_of_filtered_records == 2

    def test_filter_response_model_duplicate(self):
        """Test FilterResponseModel with duplicate records"""
        model_data = {
            "result": [
                {
                    "_id": 1,
                    "originationTime": "2021-01-01 00:00:00",
                    "clusterId": "cluster",
                    "userId": "user1",
                    "devices": {"phone": "1234567890", "voicemail": "true"},
                },
                {
                    "_id": 1,
                    "originationTime": "2021-01-01 00:00:00",
                    "clusterId": "cluster",
                    "userId": "user1",
                    "devices": {"phone": "1234567890", "voicemail": "true"},
                },
            ]
        }
        filter_response = FilterResponseModel(**model_data)
        assert filter_response.number_of_filtered_records == 1
