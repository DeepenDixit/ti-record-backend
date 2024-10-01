from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.utils.logger_helper import app_logger

api_keys = [settings.API_TOKEN]
header_for_api_key = APIKeyHeader(name="x-api-key", auto_error=False)


def get_api_key(api_key_header: str = Security(header_for_api_key)) -> str:
    """Function to get  and validate API Key"""
    if api_key_header in api_keys:
        app_logger.info(
            "Access has been granted with api key: %s*****",
            api_key_header[:3] if api_key_header else "API Key is not provided",
        )
        return api_key_header
    app_logger.info(
        "Unauthorized activity detected with api key: %s*****",
        api_key_header[:3] if api_key_header else "API Key is not provided",
    )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized to access this endpoint, please provide a valid api key",
    )
