from fastapi import APIRouter,FastAPI, Depends
from helpers.config import get_settings, Settings


router = APIRouter(
    prefix="/info",
    tags=["base"]
)

@router.get("/")
async def info(app_settings: Settings = Depends(get_settings)):
    
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "message": f"{app_name} version {app_version}"
        }