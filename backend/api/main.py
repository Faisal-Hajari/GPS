# api/main.py
from fastapi import FastAPI
from titiler.core.factory import TilerFactory
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers

app = FastAPI()

cog = TilerFactory()
app.include_router(cog.router, prefix="/tiles")
add_exception_handlers(app, DEFAULT_STATUS_CODES)