from fastapi import APIRouter ,status,Request
from fastapi.responses import JSONResponse
import logging
from schemas.nlp_push_schema import NlpPushSchema,NlpSchemaSearch
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NlpController
from models.enums.ResponseEnums import ResponseSignal
from stores.vectorDb.VectorDbFactory import VectorDbFactory
from helpers.config import get_settings
from bson import ObjectId
logger = logging.getLogger('uvicorn.error')


router = APIRouter(
    prefix = "/api/v1/nlp",
    tags = ['api_v1,''nlp']
)


@router.post("index/push/{project_id}")
async def index_project( request:Request,project_id:str, nlp_push_schema : NlpPushSchema):

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb)
    project = await project_model.get_projct_or_create_one(project_id=project_id)

    chunk_model = await ChunkModel.create_instance(db_client=request.app.mongodb)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    
    nlp_controller = NlpController(
        vector_db_client = request.app.vector_db_client,
        llm_client= request.app.llm_client,
        embed_client =  request.app.embed_client
    )

    page_number = 1
    inserted_chunks_count = 0
    idx = 0


    while True:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page=page_number)
        print(f"Fetched {len(page_chunks)} chunks for page {page_number}.")
        if len(page_chunks):
            logger.info(f"Fetched {len(page_chunks)} chunks for page {page_number}.")
            page_number += 1
        if not page_chunks:
            
            logger.info(f"No more chunks to fetch for page {page_number}. Ending pagination.")
            break

        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = nlp_controller.index_into_vector_db(project=project, data_chunks=page_chunks, do_reset=nlp_push_schema.do_reset,chunk_ids=chunks_ids)

        if not is_inserted:
            return JSONResponse(
                status_code=status.http_500_INTERNAL_SERVER_ERROR,
                content={
                    "signal": ResponseSignal.VECTOR_DB_INDEXING_ERROR.value
                }
            )
        inserted_chunks_count += len(page_chunks)
        
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTOR_DB_INDEXING_SUCCESS.value,
            "indexed_chunks_count": inserted_chunks_count
        }
    )


@router.get("index/info/{project_id}")
async def get_project_index_info(request:Request, project_id:str):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb)
    project = await project_model.get_projct_or_create_one(project_id=project_id)

    
    nlp_controller = NlpController(
        vector_db_client = request.app.vector_db_client,
        llm_client= request.app.llm_client,
        embed_client =  request.app.embed_client
    )

    collection_info = nlp_controller.get_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTOR_DB_COLLECTION_INFO_SUCCESS.value,
            "collection_info": collection_info
        }
    )

@router.post("index/search/{project_id}")
async def search_project_index(request:Request, project_id:str, nlp_schema_search:NlpSchemaSearch):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb)
    project = await project_model.get_projct_or_create_one(project_id=project_id)

    
    nlp_controller = NlpController(
        vector_db_client = request.app.vector_db_client,
        llm_client= request.app.llm_client,
        embed_client =  request.app.embed_client
    )

    results = nlp_controller.search_in_vector_db(project=project, query=nlp_schema_search.query, limit=nlp_schema_search.limit)

    if results is False:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.VECTOR_DB_SEARCH_ERROR.value
            }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTOR_DB_SEARCH_SUCCESS.value,
            "results": results
        }
    )