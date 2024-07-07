from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.routers import project, pipeline, data_sources

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(project.router, tags=["project"])
app.include_router(pipeline.router, tags=["pipeline"])
app.include_router(data_sources.router, tags=["data_sources"])
