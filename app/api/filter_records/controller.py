from fastapi import APIRouter, Body, Security, status

from app.api.filter_records.models import FilterRequestModel, FilterResponseModel
from app.api.filter_records.services import (
    filter_record_from_json,
    filter_record_from_mongo,
    filter_record_from_sql,
)
from app.utils.api_token_helper import get_api_key

record_filter_router = APIRouter()


# pylint: disable=unused-argument
@record_filter_router.post(
    path="/fromJson",
    status_code=status.HTTP_200_OK,
    response_model=FilterResponseModel,
    description="Filter Record from JSON using required body",
    responses={
        200: {
            "description": "Request for filtering records from json is completed",
            "model": FilterResponseModel,
        },
        400: {"description": "Bad Request"},
        422: {"description": "Unprocessable entity in request"},
        500: {"description": "Runtime error"},
        401: {"description": "Unauthorized"},
    },
)
def json_record_filter(
    filter_request: FilterRequestModel = Body(
        title="Filter Request for JSON filter",
        description="Request body to filter the records from JSON. "
        "Make sure to include date range as it is mandatory",
    ),
    api_key: str = Security(get_api_key),
) -> FilterResponseModel:
    """Controller of JSON record filter"""
    return filter_record_from_json(filter_request)


# pylint: disable=unused-argument
@record_filter_router.post(
    path="/fromMongo",
    status_code=status.HTTP_200_OK,
    response_model=FilterResponseModel,
    description="Filter Record from MongoDB using required body",
    responses={
        200: {
            "description": "Request for filtering records from MongoDB is completed",
            "model": FilterResponseModel,
        },
        400: {"description": "Bad Request"},
        422: {"description": "Unprocessable entity in request"},
        500: {"description": "Runtime error"},
        401: {"description": "Unauthorized"},
    },
)
def mongo_db_record_filter(
    filter_request: FilterRequestModel = Body(
        title="Filter Request for MongoDB filter",
        description="Request body to filter the records from MongoDB. "
        "Make sure to include date range as it is mandatory",
    ),
    api_key: str = Security(get_api_key),
) -> FilterResponseModel:
    """Controller of MongoDB record filter"""
    return filter_record_from_mongo(filter_request)


# pylint: disable=unused-argument
@record_filter_router.post(
    path="/fromSQL",
    status_code=status.HTTP_200_OK,
    response_model=FilterResponseModel,
    description="Filter Record from MySQL using required body",
    responses={
        200: {
            "description": "Request for filtering records from MySQL is completed",
            "model": FilterResponseModel,
        },
        400: {"description": "Bad Request"},
        422: {"description": "Unprocessable entity in request"},
        500: {"description": "Runtime error"},
        401: {"description": "Unauthorized"},
    },
)
def my_sql_db_record_filter(
    filter_request: FilterRequestModel = Body(
        title="Filter Request for MySQL DB",
        description="Request body to filter the records from MySQL. "
        "Make sure to include date range as it is mandatory",
    ),
    api_key: str = Security(get_api_key),
) -> FilterResponseModel:
    """Controller of MySQL DB record filter"""
    return filter_record_from_sql(filter_request)
