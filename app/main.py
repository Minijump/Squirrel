from fastapi import Request
from fastapi.responses import RedirectResponse

import os
import json

from app import app, templates


@app.get("/")
async def read_root(request: Request):
    """
    This returns the homepage of the application
    The homepage displays all the 'project' in the ./projects directory, 
    informations about a project are read from its manifest

    * request

    => Returns a TemplateResponse to display homepage
    """
    projects = []
    base_dir = os.getcwd()
    projects_dir = os.path.join(base_dir, "projects")

    for project in os.listdir(projects_dir):
        manifest_path = os.path.join(projects_dir, project, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
            projects.append(manifest_data)

    return templates.TemplateResponse(request, "homepage.html", {"projects": projects})


@app.post("/create_project/")
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

    # Create project's folder
    os.makedirs(project_path, exist_ok=True)

    # Create project's manifest
    with open(os.path.join(project_path , "__manifest__.json"), 'w') as file:
        json.dump({
            "name": project_name,
            "description": project_description,
            "directory": project_dir # can use a path from root
        }, file)

    # Create project's data_sources folder
    os.makedirs(os.path.join(project_path , "data_sources"), exist_ok=True)

    # Create the pipeline file
    with open(os.path.join(project_path , "pipeline.py"), 'w') as file:
        base_pipeline = """
import pandas as pd


def run_pipeline():
    dfs = {}
    
    # Squirrel Pipeline start
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    # No edit under
    return dfs
 """
        file.write(base_pipeline)

    return RedirectResponse(url=f"/project/?project_dir={project_dir}", status_code=303)


@app.post("/open_project/")
async def open_project(request: Request):
    """ 
    This function is called when a user clicks on a project in the homepage, it redirects the correct project page

    * request contains project diretory

    => Returns a RedirectResponse to the project page
    """
    form_data = await request.form()
    project_dir = form_data.get("project_directory")
    return RedirectResponse(url=f"/project/?project_dir={project_dir}", status_code=303)
