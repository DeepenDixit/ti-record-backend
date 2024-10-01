from app.api.filter_records.models import FilterRequestModel, FilterResponseModel
from app.core.config import settings
from app.core.constants import MONGO_DB_COLLECTION, MONGO_DB_NAME, SQL_DB_NAME
from app.workers.filter_records.filter_from_json import FilterRecordFromJSON
from app.workers.filter_records.filter_from_mongo import FilterRecordFromMongo
from app.workers.filter_records.filter_from_mysql import FilterRecordFromSQL


def filter_record_from_json(request: FilterRequestModel) -> FilterResponseModel:
    """
    Filter records from JSON
    """
    filter_from_json_worker = FilterRecordFromJSON(request)
    return filter_from_json_worker.filter_records_from_json()


def filter_record_from_mongo(request: FilterRequestModel) -> FilterResponseModel:
    """
    Filter records from MongoDB
    """

    filter_from_mongo_worker = FilterRecordFromMongo(
        mongo_host=settings.MONGO_DB_HOST,
        mongo_port=settings.MONGO_DB_PORT,
        mongo_db_name=MONGO_DB_NAME,
        mongo_collection_name=MONGO_DB_COLLECTION,
        request=request,
    )
    return filter_from_mongo_worker.filter_records_from_mongo()


def filter_record_from_sql(request: FilterRequestModel) -> FilterResponseModel:
    """
    Filter records from MySQL
    """

    filter_from_sql_worker = FilterRecordFromSQL(
        mysql_host=settings.SQL_DB_HOST,
        mysql_user=settings.SQL_DB_USERNAME,
        mysql_password=settings.SQL_DB_PASSWORD,
        mysql_db_name=SQL_DB_NAME,
        request=request,
    )
    return filter_from_sql_worker.filter_records_from_sql()
