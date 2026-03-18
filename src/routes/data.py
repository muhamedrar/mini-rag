from fastapi import APIRouter, UploadFile, Depends
from helpers.config import get_settings, Settings
from controllers import DataController

router = APIRouter(
    prefix = "/api/v1/data",
    tags = ['api_v1,''data']
)

@router.post('/upload/{id}')
async def upload_file(
    id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    is_valed = DataController().validate_uploaded_file(file)
    
    return is_valed