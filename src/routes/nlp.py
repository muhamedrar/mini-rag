from fastapi import APIRouter ,status,Request
from fastapi.responses import JSONResponse
import logging
from schemas.nlp_push_schema import NlpPushSchema
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NlpController
from models.enums.ResponseEnums import ResponseSignal
from stores.vectorDb.VectorDbFactory import VectorDbFactory
from helpers.config import get_settings
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

    collection_name = nlp_controller.create_collection_name(project_id=project_id)
    settings = get_settings()

    vector_db = VectorDbFactory(settings=settings)

    if not vector_db.is_collection_exist(collection_name=collection_name):
        _ = vector_db.create_collection(
            collection_name=collection_name,
            embedding_dimension=request.app.embed_client.embedding_model_size,
            do_reset=False
        )
    

 
    has_reset = True
    page_number = 1
    inserted_chunks_count = 0
    while has_reset:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page=page_number)
        if len(page_chunks):
            page_number += 1

        if len(page_chunks) == 0:
            has_reset = False
            break
        is_inserted = nlp_controller.index_into_vector_db(project=project, data_chunks=page_chunks, do_reset=nlp_push_schema.do_reset)

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