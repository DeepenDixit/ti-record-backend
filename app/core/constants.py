# region Record Generator Constants

INITIAL_ID = 12344

SERVER_RANGE_START = 0
SERVER_RANGE_END = 9

USER_ID_LENGTH = 9
USER_ID_DIVIDER = 3

TIMESTAMP_START_YEAR = 2020
TIMESTAMP_END_YEAR = 2020

RECORD_STORAGE_DIR = "records"
RECORD_FILE_NAME = "current_records.json"
RECORD_BACKUP_DIR = "backup_records"

MONGO_DB_NAME = "mydatabase"
MONGO_DB_COLLECTION = "records"
MONGO_DB_BACKUP_COLLECTION = "BKP_{date_format}_records"

SQL_DB_NAME = "mydatabase"
SQL_RECORDS_TABLE = "records"
SQL_DEVICES_TABLE = "devices"
SQL_RECORDS_BKP_TABLE = "BKP_{date_format}_records"
SQL_DEVICES_BKP_TABLE = "BKP_{date_format}_devices"

# pylint: disable=line-too-long
DEVICES_TABLE_CREATE = f"CREATE TABLE IF NOT EXISTS {SQL_DEVICES_TABLE} (_id INT AUTO_INCREMENT PRIMARY KEY, phone VARCHAR(255), voicemail VARCHAR(255), UNIQUE(phone, voicemail))"
RECORDS_TABLE_CREATE = f"CREATE TABLE IF NOT EXISTS {SQL_RECORDS_TABLE} (_id INT PRIMARY KEY, userId VARCHAR(255), deviceId INT, clusterId VARCHAR(255), originationTime TIMESTAMP, FOREIGN KEY (deviceId) REFERENCES devices(_id))"

DEVICES_TABLE_INSERT = "INSERT INTO {devices_table} (phone, voicemail) VALUES ('{value_phone_number}', '{value_voicemail}') ON DUPLICATE KEY UPDATE _id=LAST_INSERT_ID(_id)"
RECORDS_TABLE_INSERT = "INSERT INTO {records_table} (_id, userId, deviceId, clusterId, originationTime) VALUES ({value_record_id}, '{value_user_id}', {value_device_id}, '{value_cluster_id}', FROM_UNIXTIME({value_origination_time}))"

# endregion

# region Test Constants

TEST_TOKEN = "valid_api_key"  # nosec

# endregion
