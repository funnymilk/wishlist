from fastapi import FastAPI

from core.config import get_settings
from api.router import api_router

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)
app.include_router(api_router)
