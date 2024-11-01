from fastapi import Request
from fastapi.responses import RedirectResponse

import os
import json
import traceback

from app import router, templates
from app.data_sources.models import DATA_SOURCE_REGISTRY


async def get_sources(project_dir):
    """
    Returns the list of data sources in the project

    * project_dir(str): The project directory name
    
    => Returns the list of available data sources
    """
    sources = []
    project_data_sources_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources")
    for source in os.listdir(project_data_sources_path):
        manifest_path = os.path.join(project_data_sources_path, source, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
            sources.append(manifest_data)
    return sources

@router.get("/data_sources")
async def data_sources(request: Request, project_dir: str):
    """
    This returns the data sources page
    It displays all sources of contained in data_sources folder, 

    * request
    * project_dir(str): project directory

    => Returns a TemplateResponse to display data_sources page
    """
    try:
        sources = await get_sources(project_dir)
        return templates.TemplateResponse(
            request, 
            "data_sources.html", 
            {
                "project_dir": project_dir, 
                "sources": sources,
                "DATA_SOURCE_REGISTRY": DATA_SOURCE_REGISTRY})

    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "tables_error.html", {"exception": str(e), "project_dir": project_dir})

@router.post("/create_source/")
async def create_source(request: Request):
    """
    Create of a new data source

    * request: contains the form data, required to create the source

    => Returns a RedirectResponse to the data source page
    """
    try:
        form_data = await request.form()
        project_dir = form_data.get("project_dir")
        source_type = form_data.get("source_type")

        SourceClass = DATA_SOURCE_REGISTRY[source_type]
        SourceClass.check_available_infos(form_data)
        source = await SourceClass._create_source(form_data)
        await source._create_data_file(form_data)

        return RedirectResponse(url=f"/data_sources/?project_dir={project_dir}", status_code=303)

    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "tables_error.html", {"exception": str(e), "project_dir": project_dir})
