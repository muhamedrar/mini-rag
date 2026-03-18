from fastapi import APIRouter,FastAPI, Depends
import os
from helpers.config import get_settings, Settings


router = APIRouter(
    prefix="/base",
    tags=["base"]
)

@router.get("/")
async def base(app_settings: Settings = Depends(get_settings)):
    
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "message": f"This is the base route of {app_name} version {app_version}"
        }