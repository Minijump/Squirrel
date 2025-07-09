import importlib.resources
import os

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Squirrel", version="0.1.0")
router = APIRouter()
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/utils/templates/static/img/favicon.ico")

# Find the fontawesome package installation path + mount it (so that it works offline)
try:
    with importlib.resources.path('fontawesome-free', '') as path:
        fontawesome_path = str(path)
    
    app.mount("/fontawesome-assets", StaticFiles(directory=os.path.join(fontawesome_path, 'static', 'fontawesome_free')), name="fontawesome")
except ImportError:
    print("Warning: fontawesome_free package not found")

app.mount("/static/utils", StaticFiles(directory="app/utils"), name="utils_static")
app.mount("/static/base", StaticFiles(directory="app/utils/templates/static"), name="base_static")
app.mount("/static/projects", StaticFiles(directory="app/projects/templates/static"), name="projects_static")
app.mount("/static/data_sources", StaticFiles(directory="app/data_sources/templates/static"), name="data_sources_static")
app.mount("/static/tables", StaticFiles(directory="app/tables/templates/static"), name="tables_static")
app.mount("/static/pipeline", StaticFiles(directory="app/pipelines/templates/static"), name="pipeline_static")
app.mount("/static/app_settings", StaticFiles(directory="app/app_settings/templates/static"), name="app_settings_static")
templates = Jinja2Templates(directory="app")


from app.projects import projects
from app.tables import tables
from app.data_sources import data_sources
from app.pipelines import pipelines
from app.app_settings.routers import app_settings_router
app.include_router(projects.router, tags=["projects"])
app.include_router(tables.router, tags=["tables"])
app.include_router(data_sources.router, tags=["data_sources"])
app.include_router(pipelines.router, tags=["pipelines"])
app.include_router(app_settings_router.router, tags=["app_settings"])
