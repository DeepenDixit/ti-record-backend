from fastapi import APIRouter

from app.api.filter_records.controller import record_filter_router

api_router = APIRouter()

api_router.include_router(
    record_filter_router,
    prefix="/filterRecords",
    tags=["Record Filter"],
)
