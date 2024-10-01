from datetime import datetime
from typing import List, Union

from pydantic import Field, computed_field, field_validator

from app.utils.model_helper import CamelModel


class FilterRequestModel(CamelModel):
    """
    Model for incoming request to filter the records
    """

    date_range: str = Field(
        description="Please pass date range in format of 'YYYY-MM-DD to YYYY-MM-DD'",
        example="YYYY-MM-DD to YYYY-MM-DD",
    )
    phone_number: str = Field(description="Phone Number", default="")
    voice_mail: str = Field(description="Voice Mail", default="")
    user_id: str = Field(description="User ID", default="")
    cluster: str = Field(description="Cluster Name", default="")

    @field_validator("date_range", mode="before")
    def _validate_date_range(cls, value: str) -> str:
        # pylint: disable=no-self-argument
        """Field validator for date range"""
        if isinstance(value, str):
            try:
                assert (  # nosec
                    value.split(" to ")[0] != value.split(" to ")[1]
                ), "Start date and end date should not be same"
                assert datetime.strptime(  # nosec
                    value.split(" to ")[0], "%Y-%m-%d"
                ) <= datetime.strptime(
                    value.split(" to ")[1], "%Y-%m-%d"
                ), "Start date should be less than or equal to end date"
            except Exception as e:
                raise ValueError(
                    "Please pass date range in format of 'YYYY-MM-DD to YYYY-MM-DD'"
                ) from e
        return value


class DeviceModel(CamelModel):
    """
    Device model
    """

    phone: str
    voicemail: str


class RecordModel(CamelModel):
    """
    Model for record
    """

    id: int = Field(alias="_id")
    origination_time: Union[int, str]
    cluster_id: str
    user_id: str
    devices: DeviceModel

    @field_validator("origination_time", mode="before")
    def _date_converter(cls, value: int):
        # pylint: disable=no-self-argument
        """date converter function"""
        if isinstance(value, int):
            return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
        return value


class FilterResponseModel(CamelModel):
    """
    Filter Response
    """

    result: List[RecordModel]

    def __init__(self, **data):
        super().__init__(**data)
        unique_record_mapping = {record.id: record for record in self.result}
        self.result = list(unique_record_mapping.values())

    @computed_field
    @property
    def number_of_filtered_records(self) -> int:
        """calculated property for number of filtered records"""
        return len(self.result)
