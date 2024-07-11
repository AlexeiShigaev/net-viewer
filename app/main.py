from fastapi import FastAPI
from api_router import router as api_router


app = FastAPI()

app.include_router(api_router)

