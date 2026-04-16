from fastapi import APIRouter, UploadFile, Depends,status,Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessController
from schemas import ProcessRequestSchema
from models.db_schemas import DataChunk,Asset
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.enums.AssetTypesEnums import AssetTypesEnums
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
    
    # storing asset into the database

    asset_model =await AssetModel.create_instance(db_client=request.app.mongodb)
    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypesEnums.FILE.value,
        asset_name=file_id,
        asset_size= os.path.getsize(file_path)
    )

  
    asset_record = await asset_model.create_asset(asset_resource)


    

    
    return JSONResponse(
        content= {
            "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id" : file_id,
            "asset_id": str(asset_record.id)
        }
    )


@router.post('/process/{project_id}')
async def process_file(request: Request, project_id: str, process_request_schema: ProcessRequestSchema):
    
    chank_size = process_request_schema.chunk_size
    overlap_size = process_request_schema.ovelap_size
    do_reset = process_request_schema.do_reset
    
    chunk_model = await ChunkModel.create_instance(db_client=request.app.mongodb)
    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb)
    project = await project_model.get_projct_or_create_one(project_id=project_id)
    asset_model =await AssetModel.create_instance(db_client=request.app.mongodb)

    project_files_ids = {}
    if process_request_schema.file_id:
        asset_record = await asset_model.get_asset_record(asset_project_id=project.id, asset_name=process_request_schema.file_id)
        print("asset is :",asset_record)
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content= {
                    "signal" : ResponseSignal.FILE_NOT_FOUND_WITH_THIS_ID.value
                }
            )
        
        project_files_ids = {
            asset_record.id: asset_record.asset_name
        }
    else:
        project_files = await asset_model.get_all_project_assets(asset_project_id=project.id, asset_type=AssetTypesEnums.FILE.value)
        project_files_ids = {
            file.id: file.asset_name for file in project_files
            }

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content= {
                "signal" : ResponseSignal.NO_FILES_TO_PROCESS.value
            }
        )
    
    if do_reset == 1:
            deleted_count = await chunk_model.delete_chunks_by_projec_id(project.id)
    
    process_controller = ProcessController(project_id=project_id)
    no_of_chunks = 0
    no_of_files = 0

    for asset_id,file_id in project_files_ids.items():
        

        file_content = process_controller.get_file_content(file_id=file_id)
        if file_content is None:
            logger.error(f"File with id {file_id} not found for project {project_id}")
            continue

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
                chunk_project_id=project.id,
                chunk_assit_id=asset_id
            )

            for i, chunk in enumerate(processed_content)
        ]

        

        

        no_of_chunks += await chunk_model.insert_many_chunks(file_chunk_records)
        no_of_files += 1


    return JSONResponse(
        content= {
            "signal" : ResponseSignal.FILE_PROCESSING_SUCCESS.value,
            "file_id" : file_id,
            "inserted_chunks": no_of_chunks,
            "number_of_processed_files": no_of_files,
            "deleted_old_count":deleted_count
        }
    )



