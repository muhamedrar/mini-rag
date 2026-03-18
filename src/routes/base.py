from fastapi import APIRouter,FastAPI
import os


router = APIRouter(
    prefix="/base",
    tags=["base"]
)

@router.get("/")
async def root():
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")
    return {
        "message": f"This is the base route of {app_name} version {app_version}"
        }