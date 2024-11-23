from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
# TODO: group all static into one /projects, directory="projects" name='static) Need to import them in router too?????
app.mount("/templates/base/static", StaticFiles(directory="templates/base/static"), name="base_static")
app.mount("/templates/projects/static", StaticFiles(directory="templates/projects/static"), name="projects_static")
app.mount("/templates/data_sources/static", StaticFiles(directory="templates/data_sources/static"), name="data_sources_static")
app.mount("/templates/tables/static", StaticFiles(directory="templates/tables/static"), name="tables_static")
app.mount("/templates/pipeline/static", StaticFiles(directory="templates/pipeline/static"), name="pipeline_static")
templates = Jinja2Templates(directory="templates")

from fastapi import APIRouter
router = APIRouter()
app.mount("/templates/base/static", StaticFiles(directory="templates/base/static"), name="base_static")
router.mount("/templates/projects/static", StaticFiles(directory="templates/projects/static"), name="projects_static")

templates = Jinja2Templates(directory="templates")


from app.projects import projects
from app.tables import tables
from app.data_sources import data_sources
from app.pipelines import pipelines
app.include_router(projects.router, tags=["projects"])
app.include_router(tables.router, tags=["tables"])
app.include_router(data_sources.router, tags=["data_sources"])
app.include_router(pipelines.router, tags=["pipelines"])
