from fastapi import FastAPI,__version__
from routes import info ,data

print(__version__)
app = FastAPI()

app.include_router(info.router)
app.include_router(data.router)



