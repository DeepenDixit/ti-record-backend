from humps import camel
from pydantic import BaseModel


def to_camel(string):
    """function to convert string to camel case"""
    return camel.case(string)


class CamelModel(BaseModel):
    """
    Class for CamelModel
    """

    class Config:
        """Config class for CamelModel"""

        alias_generator = to_camel
        populated_by_name = True
