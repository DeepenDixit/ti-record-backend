from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.utils.request_id_middleware import RequestIDMiddleware

# root_path for fixxing api version and all

#  overriding openapi considering we would
# have different api_str in different env

app = FastAPI(
    debug=settings.APP_DEBUG,
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    root_path=settings.APP_ROOT_PATH,
    openapi_url=f"{settings.API_STR}/openapi.json",
    docs_url="/docs/swagger",
    redoc_url="/docs/redoc",
)

app.add_middleware(RequestIDMiddleware)
app.include_router(api_router, prefix=settings.API_STR)
