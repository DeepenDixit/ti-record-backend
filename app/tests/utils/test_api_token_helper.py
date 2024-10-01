from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.utils.api_token_helper import get_api_key


@pytest.fixture(scope="function")
def mock_get_api_key():
    """
    Mock get_api_key
    """
    with patch("app.utils.api_token_helper.api_keys", ["valid_api_key"]):
        yield


@pytest.mark.usefixtures("mock_get_api_key")
def test_get_api_key():
    """
    Test get_api_key
    """
    assert get_api_key("valid_api_key") == "valid_api_key"

    with pytest.raises(HTTPException):
        get_api_key("invalid_api_key")
