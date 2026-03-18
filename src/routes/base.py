from fastapi import APIRouter,FastAPI
import os
from helpers.config import get_settings


router = APIRouter(
    prefix="/base",
    tags=["base"]
)

@router.get("/")
async def root():
    settings = get_settings()
    app_name = settings.APP_NAME
    app_version = settings.APP_VERSION
    
    return {
        "message": f"This is the base route of {app_name} version {app_version}"
        }