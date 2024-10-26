from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# from app.routers import pipeline, data_sources

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

from fastapi import APIRouter
router = APIRouter()
router.mount("/../static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# app.include_router(project.router, tags=["project"])
# app.include_router(pipeline.router, tags=["pipeline"])
# app.include_router(data_sources.router, tags=["data_sources"])

from app.projects import projects
from app.tables import tables
from app.data_sources import data_sources
from app.pipelines import pipelines
app.include_router(projects.router, tags=["projects"])
app.include_router(tables.router, tags=["tables"])
app.include_router(data_sources.router, tags=["data_sources"])
app.include_router(pipelines.router, tags=["pipelines"])
