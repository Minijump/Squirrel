from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Squirrel", version="0.1.0")
router = APIRouter()
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/utils/templates/static/img/favicon.ico")

app.mount("/static/base", StaticFiles(directory="app/utils/templates/static"), name="base_static")
app.mount("/static/projects", StaticFiles(directory="app/projects/templates/static"), name="projects_static")
app.mount("/static/data_sources", StaticFiles(directory="app/data_sources/templates/static"), name="data_sources_static")
app.mount("/static/tables", StaticFiles(directory="app/tables/templates/static"), name="tables_static")
app.mount("/static/pipeline", StaticFiles(directory="app/pipelines/templates/static"), name="pipeline_static")
templates = Jinja2Templates(directory="app")


from app.projects import projects
from app.tables import tables
from app.data_sources import data_sources
from app.pipelines import pipelines
app.include_router(projects.router, tags=["projects"])
app.include_router(tables.router, tags=["tables"])
app.include_router(data_sources.router, tags=["data_sources"])
app.include_router(pipelines.router, tags=["pipelines"])
