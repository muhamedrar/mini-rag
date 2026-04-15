from fastapi import FastAPI,__version__,APIRouter, UploadFile
from routes import info ,data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager
from stores.llms.LLmFactory import LLmFactory
from stores.vectorDb.VectorDbFactory import VectorDbFactory
from stores.llms.templates import TemplateParser

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_conn[settings.MONGODB_db]
    print("mongo db startup complete.")

    llm_factory = LLmFactory(settings)
    vector_db_factory = VectorDbFactory(settings)


    app.llm_client = llm_factory.create_provider(provider_name= settings.GENERATION_BACKEND)
    app.llm_client.set_generation_model(settings.GENERATION_MODEL_ID)
    print("LLM startup complete")

    app.embed_client = llm_factory.create_provider(provider_name= settings.EMBEDING_BACKEND)
    app.embed_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)
    print("embeding model startup complete")


    app.vector_db_client = vector_db_factory.create_provider(provider_name= settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()
    print("vector db startup complete")

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_langauge=settings.DEFAULT_LANG
    )

    yield


    app.mongodb_conn.close()
    print("mongo db connection closed.")

    app.vector_db_client.disconnect()
    print("vector db connection closed.")


app = FastAPI(lifespan=lifespan, title="Mini RAG API", version=__version__)

app.include_router(info.router)
app.include_router(data.router)
app.include_router(nlp.router)



