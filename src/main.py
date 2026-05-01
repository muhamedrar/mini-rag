from fastapi import FastAPI,__version__,APIRouter, UploadFile
from routes import info ,data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager
from stores.llms.LLmFactory import LLmFactory
from stores.vectorDb.VectorDbFactory import VectorDbFactory
from stores.llms.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.metrics import setup_metrics



@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine =  create_async_engine(postgres_conn)

    app.db_client = sessionmaker(
        app.db_engine,
        class_=AsyncSession,
        expire_on_commit = False
    )
    
    print("postgres db startup complete.")

    llm_factory = LLmFactory(settings)
    vector_db_factory = VectorDbFactory(settings, db_client=app.db_client)


    app.llm_client = llm_factory.create_provider(provider_name= settings.GENERATION_BACKEND)
    app.llm_client.set_generation_model(settings.GENERATION_MODEL_ID)
    print("LLM startup complete")

    app.embed_client = llm_factory.create_provider(provider_name= settings.EMBEDING_BACKEND)
    app.embed_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)
    print("embeding model startup complete")


    app.vector_db_client = vector_db_factory.create_provider(provider_name= settings.VECTOR_DB_BACKEND)
    await app.vector_db_client.connect()
    print("vector db startup complete")

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_langauge=settings.DEFAULT_LANG
    )

    yield


    await app.db_engine.dispose()
    print("postgres db connection closed.")

    await app.vector_db_client.disconnect()
    print("vector db connection closed.")


app = FastAPI(lifespan=lifespan, title="Mini RAG API", version=__version__)
setup_metrics(app)

app.include_router(info.router)
app.include_router(data.router)
app.include_router(nlp.router)



