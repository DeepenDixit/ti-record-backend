from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.api.filter_records.models import DeviceModel, FilterResponseModel, RecordModel
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="function")
def mock_get_api_key():
    """
    Mock get_api_key
    """
    with patch("app.utils.api_token_helper.api_keys", ["valid_api_key"]):
        yield


@patch("app.api.filter_records.services.filter_record_from_json")
def test_json_record_filter_unauthorized(mock_filter_record_from_json) -> None:
    """
    Test JSON record filter unauthorized access
    """
    mock_filter_record_from_json.return_value = {
        "records": [
            {
                "cluster": "test",
                "user_id": "test",
                "phone_number": "test",
                "voice_mail": "test",
                "originationTime": 1609459200,
            }
        ]
    }

    request_body = {
        "date_range": "2021-01-01 to 2021-01-31",
        "cluster": "cluster1",
        "user_id": "user1",
        "phone_number": "1234567890",
        "voice_mail": "true",
    }

    response = client.post("/filterRecords/fromJson", json=request_body)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Unauthorized to access this endpoint, please provide a valid api key"
    }


@pytest.mark.usefixtures("mock_get_api_key")
@patch("app.api.filter_records.controller.filter_record_from_json")
def test_json_record_filter(mock_filter_record_from_json) -> None:
    """
    Test JSON record filter with valid API key
    """
    mock_filter_record_from_json.return_value = FilterResponseModel(
        result=[
            RecordModel(
                _id=987983,
                clusterId="test",
                userId="test",
                devices=DeviceModel(phone="test", voicemail="test"),
                originationTime=1609459200,
            )
        ],
        number_of_filtered_records=1,
    )

    mock_get_api_key.return_value = "valid_api_key"

    request_body = {
        "dateRange": "2021-01-01 to 2021-01-31",
        "cluster": "cluster1",
        "userId": "user1",
        "phoneNumber": "1234567890",
        "voiceMail": "true",
    }

    headers = {"x-api-key": "valid_api_key"}

    response = client.post(
        "/filterRecords/fromJson", json=request_body, headers=headers
    )

    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {
                "_id": 987983,
                "originationTime": "2020-12-31 19:00:00",
                "clusterId": "test",
                "userId": "test",
                "devices": {"phone": "test", "voicemail": "test"},
            }
        ],
        "numberOfFilteredRecords": 1,
    }


@pytest.mark.usefixtures("mock_get_api_key")
def test_json_record_filter_bad_request() -> None:
    """
    Test JSON record filter with bad request
    """
    request_body = {
        "cluster": "cluster1",
        "userId": "user1",
        "phoneNumber": "1234567890",
        "voiceMail": "true",
    }

    headers = {"x-api-key": "valid_api_key"}

    response = client.post(
        "/filterRecords/fromJson", json=request_body, headers=headers
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "dateRange"],
                "msg": "Field required",
                "input": {
                    "cluster": "cluster1",
                    "userId": "user1",
                    "phoneNumber": "1234567890",
                    "voiceMail": "true",
                },
            }
        ]
    }


@pytest.mark.usefixtures("mock_get_api_key")
@patch("app.api.filter_records.controller.filter_record_from_mongo")
def test_mongo_db_record_filter(mock_filter_record_from_mongo) -> None:
    """
    Test Mongo DB record filter with valid API key
    """
    mock_filter_record_from_mongo.return_value = FilterResponseModel(
        result=[
            RecordModel(
                _id=987983,
                clusterId="test",
                userId="test",
                devices=DeviceModel(phone="test", voicemail="test"),
                originationTime=1609459200,
            )
        ],
        number_of_filtered_records=1,
    )

    mock_get_api_key.return_value = "valid_api_key"

    request_body = {
        "dateRange": "2021-01-01 to 2021-01-31",
        "cluster": "cluster1",
        "userId": "user1",
        "phoneNumber": "1234567890",
        "voiceMail": "true",
    }

    headers = {"x-api-key": "valid_api_key"}

    response = client.post(
        "/filterRecords/fromMongo", json=request_body, headers=headers
    )

    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {
                "_id": 987983,
                "originationTime": "2020-12-31 19:00:00",
                "clusterId": "test",
                "userId": "test",
                "devices": {"phone": "test", "voicemail": "test"},
            }
        ],
        "numberOfFilteredRecords": 1,
    }


@pytest.mark.usefixtures("mock_get_api_key")
@patch("app.api.filter_records.controller.filter_record_from_sql")
def test_sql_db_record_filter(mock_filter_record_from_sql) -> None:
    """
    Test MySQL DB record filter with valid API key
    """
    mock_filter_record_from_sql.return_value = FilterResponseModel(
        result=[
            RecordModel(
                _id=987983,
                clusterId="test",
                userId="test",
                devices=DeviceModel(phone="test", voicemail="test"),
                originationTime=1609459200,
            )
        ],
        number_of_filtered_records=1,
    )

    mock_get_api_key.return_value = "valid_api_key"

    request_body = {
        "dateRange": "2021-01-01 to 2021-01-31",
        "cluster": "cluster1",
        "userId": "user1",
        "phoneNumber": "1234567890",
        "voiceMail": "true",
    }

    headers = {"x-api-key": "valid_api_key"}

    response = client.post("/filterRecords/fromSQL", json=request_body, headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {
                "_id": 987983,
                "originationTime": "2020-12-31 19:00:00",
                "clusterId": "test",
                "userId": "test",
                "devices": {"phone": "test", "voicemail": "test"},
            }
        ],
        "numberOfFilteredRecords": 1,
    }
