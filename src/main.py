from fastapi import FastAPI,__version__
from routes import info ,data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager




@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_conn[settings.MONGODB_db]
    print("mongo db startup complete.")


    yield


    app.mongodb_conn.close()
    print("mongo db connection closed.")


app = FastAPI(lifespan=lifespan, title="Mini RAG API", version=__version__)

app.include_router(info.router)
app.include_router(data.router)



