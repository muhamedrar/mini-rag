from fastapi import APIRouter, UploadFile, Depends,status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController,ProjectController
import aiofiles
import os
from models import ResponseSignal



router = APIRouter(
    prefix = "/api/v1/data",
    tags = ['api_v1,''data']
)

@router.post('/upload/{project_id}')
async def upload_file(
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    is_valid, signal = DataController().validate_uploaded_file(file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content= {
                "signal" : signal
            }
        )
    
    project_dir_path = ProjectController().get_project_path(project_id)
    file_path= os.path.join(project_dir_path,file.filename)

    async with aiofiles.open(file=file_path,mode="wb") as f:
        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
            await f.write(chunk)

    
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {
            "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value
        }
    )