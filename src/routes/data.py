from fastapi import APIRouter, UploadFile, Depends,status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController,ProjectController
import aiofiles
import os
from models import ResponseSignal
import logging

logger = logging.getLogger('uvicorn.error')

router = APIRouter(
    prefix = "/api/v1/data",
    tags = ['api_v1,''data']
)
data_controller = DataController()


@router.post('/upload/{project_id}')
async def upload_file(
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    is_valid, signal = data_controller.validate_uploaded_file(file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content= {
                "signal" : signal
            }
        )
    

    file_path= data_controller.generate_unique_filename(file.filename, project_id)

    try : 
        async with aiofiles.open(file=file_path,mode="wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content= {
                "signal" : ResponseSignal.FILE_UPLOAD_FAILED.value
               
            }
        )

    
    
    return JSONResponse(
        content= {
            "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value
        }
    )