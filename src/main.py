from fastapi import FastAPI,__version__
from routes.base import router as base_router
print(__version__)
app = FastAPI()

app.include_router(base_router)



