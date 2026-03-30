from fastapi import APIRouter, UploadFile, Depends,status,Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessController
from schemas import ProcessRequestSchema
from models.db_schemas import DataChunk
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel

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
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb)
    project = await project_model.get_projct_or_create_one(project_id=project_id)

    is_valid, signal = data_controller.validate_uploaded_file(file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content= {
                "signal" : signal
            }
        )
    

    file_path, file_id= data_controller.generate_unique_filePath(file.filename, project_id)

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
            "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id" : file_id,
            
        }
    )


@router.post('/process/{project_id}')
async def process_file(request: Request, project_id: str, process_request_schema: ProcessRequestSchema):
    file_id = process_request_schema.file_id
    chank_size = process_request_schema.chunk_size
    overlap_size = process_request_schema.ovelap_size
    do_reset = process_request_schema.do_reset

    chunk_model = await ChunkModel.create_instance(db_client=request.app.mongodb)
    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb)
    project = await project_model.get_projct_or_create_one(project_id=project_id)


    process_controller = ProcessController(project_id=project_id)

    file_content = process_controller.get_file_content(file_id=file_id)
    processed_content = process_controller.process_file_content(file_id=file_id,file_content=file_content,chunk_size=chank_size,overlap_size=overlap_size)

    if processed_content is None or len(processed_content) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content= {
                "signal" : ResponseSignal.FILE_PROCESSING_FAILED.value
            }
        )
    
    file_chunk_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunck_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_object_id=project.id,
        )

        for i, chunk in enumerate(processed_content)
    ]

    if do_reset == 1:
        await chunk_model.delete_chunks_by_projec_id(project.id)

    

    no_of_chunks = await chunk_model.insert_many_chunks(file_chunk_records)

    return JSONResponse(
        content= {
            "signal" : ResponseSignal.FILE_PROCESSING_SUCCESS.value,
            "file_id" : file_id,
            "number_of_chunks": no_of_chunks
        }
    )



