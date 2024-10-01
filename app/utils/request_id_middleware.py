import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.utils.logger_helper import current_request_id_ctx


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Request ID Middleware"""

    async def dispatch(self, request: Request, call_next):
        """Method to dispatch the request with ID"""
        request_id = str(uuid.uuid4())
        current_request_id_ctx.set(request_id)
        response = await call_next(request)
        return response
