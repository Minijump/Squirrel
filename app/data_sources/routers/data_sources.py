from fastapi import Request
from fastapi.responses import RedirectResponse

import os
import json

from app import router, templates
from app.tables.routers.tables import get_sources



@router.get("/data_sources")
async def data_sources(request: Request, project_dir: str):
    """
    This returns the data sources page
    It displays all sources of contained in data_sources folder, 

    * request
    * project_dir(str): project directory

    => Returns a TemplateResponse to display data_sources page
    """
    sources = get_sources(project_dir)
    return templates.TemplateResponse(
        request, 
        "data_sources.html", 
        {"project_dir": project_dir, "sources": sources})

async def _create_source_base(source_path, source_name, source_description, source_type, source_dir):
    """
    Creates the base structure of a data source

    * source_path(str): The path to the source
    * source_name(str): The name of the source
    * source_description(str): The description of the source
    * source_type(str): The type of the source
    * source_dir(str): The data source directory

    =>
    """
    os.makedirs(source_path, exist_ok=True)
    with open(os.path.join(source_path, "__manifest__.json"), 'w') as file:
        json.dump({
            "type": source_type,
            "name": source_name,
            "description": source_description,
            "directory": source_dir
        }, file)

async def _create_data_file(source_path, source_file, source_type):
    """
    Creates (copy) the data file for the source

    * source_path(str): The path to the source
    * source_file: The file object
    * source_type(str): The type of the source

    =>
    """
    data_file_name = 'data.' + source_type
    source_file_path = os.path.join(source_path, data_file_name)
    with open(source_file_path, 'wb') as file:
        file.write(await source_file.read())

@router.post("/create_source/")
async def create_source(request: Request):
    """
    Create of a new data source

    * request contains: - project_dir, source_type, source_description and source_name
                        - it also contains other infos specific to the type of source
                           ie: source_file for csv and xlsx

    => Returns a RedirectResponse to the data source page
    """
    try:
        form_data = await request.form()
        project_dir = form_data.get("project_dir")
        source_name = form_data.get("source_name")
        source_description = form_data.get("source_description")
        source_type = form_data.get("source_type")
        source_dir = source_name.replace(" ", "_")
        source_path = os.path.join(os.getcwd(), "projects", project_dir, "data_sources", source_dir)

        if source_type == "csv":
            if not form_data.get("source_file").filename.endswith('.csv'):
                return {"message": "File must be a csv file"}
            await _create_source_base(source_path, source_name, source_description, source_type, source_dir)
            source_file = form_data.get("source_file")
            await _create_data_file(source_path, source_file, source_type)
        
        if source_type == "xlsx":
            if not form_data.get("source_file").filename.endswith('.xlsx'):
                return {"message": "File must be a xlsx file"}
            await _create_source_base(source_path, source_name, source_description, source_type, source_dir)
            source_file = form_data.get("source_file")
            await _create_data_file(source_path, source_file, source_type)
    except Exception as e:
        return templates.TemplateResponse(request, "project_error.html", {"exception": str(e), "project_dir": project_dir})
    
    return RedirectResponse(url=f"/data_sources/?project_dir={project_dir}", status_code=303)
