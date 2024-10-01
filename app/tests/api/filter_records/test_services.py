from unittest.mock import patch

from app.api.filter_records.models import FilterRequestModel, FilterResponseModel
from app.api.filter_records.services import (
    filter_record_from_json,
    filter_record_from_mongo,
    filter_record_from_sql,
)


@patch("app.api.filter_records.services.FilterRecordFromJSON.filter_records_from_json")
def test_filter_record_from_json(mock_filter_records_from_json):
    """
    Test filter_record_from_json
    """
    mock_filter_records_from_json.return_value = FilterResponseModel(result=[])
    filter_request = FilterRequestModel(**{"dateRange": "2022-01-01 to 2022-01-02"})
    response = filter_record_from_json(filter_request)
    assert not response.result


@patch(
    "app.api.filter_records.services.FilterRecordFromMongo.filter_records_from_mongo"
)
def test_filter_record_from_mongo(mock_filter_records_from_mongo):
    """
    Test filter_record_from_mongo
    """
    mock_filter_records_from_mongo.return_value = FilterResponseModel(result=[])
    filter_request = FilterRequestModel(**{"dateRange": "2022-01-01 to 2022-01-02"})
    response = filter_record_from_mongo(filter_request)
    assert not response.result


@patch("app.api.filter_records.services.FilterRecordFromSQL.filter_records_from_sql")
def test_filter_record_from_sql(mock_filter_records_from_sql):
    """
    Test filter_record_from_sql
    """
    mock_filter_records_from_sql.return_value = FilterResponseModel(result=[])
    filter_request = FilterRequestModel(**{"dateRange": "2022-01-01 to 2022-01-02"})
    response = filter_record_from_sql(filter_request)
    assert not response.result
