from fastapi import Request
from fastapi.responses import RedirectResponse

import os
import json

from app import router, templates

from app.utils import PIPELINE_START_TAG, PIPELINE_END_TAG, NEW_CODE_TAG
BASIC_PIPELINE = """
import pandas as pd


def run_pipeline():
    dfs = {}
    
    %s
    %s
    %s

    return dfs
 """ % (PIPELINE_START_TAG, NEW_CODE_TAG, PIPELINE_END_TAG)


@router.post("/create_project/")
async def create_project(request: Request):
    """
    Create a new project

    * request contains: - project_name and project_description

    => Returns a RedirectResponse to the new project page
    """
    form_data = await request.form()
    project_name = form_data.get("project_name")
    project_description = form_data.get("project_description")
    project_dir = project_name.lower().replace(" ", "_")
    project_path = os.path.join(os.getcwd(), "projects", project_dir)

    try:
        # Create project's folder
        os.makedirs(project_path, exist_ok=True)

        # Create project's manifest
        manifest_path = os.path.join(project_path , "__manifest__.json")
        manifest_content = { 
                "name": project_name,
                "description": project_description,
                "directory": project_dir
            }  
        with open(manifest_path, 'w') as file:
            json.dump(manifest_content, file, indent=4) 

        # Create project's data_sources folder
        os.makedirs(os.path.join(project_path , "data_sources"), exist_ok=True)

        # Create the pipeline file
        with open(os.path.join(project_path , "pipeline.py"), 'w') as file:
            file.write(BASIC_PIPELINE)
    except Exception as e:
        return templates.TemplateResponse(request, "homepage_error.html", {"exception": str(e)})

    return RedirectResponse(url=f"/project/?project_dir={project_dir}", status_code=303)


@router.post("/open_project/")
async def open_project(request: Request):
    """ 
    This function is called when a user clicks on a project in the homepage, it redirects the correct project page

    * request contains project diretory

    => Returns a RedirectResponse to the project page
    """
    form_data = await request.form()
    project_dir = form_data.get("project_directory")
    return RedirectResponse(url=f"/project/?project_dir={project_dir}", status_code=303)
