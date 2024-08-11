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
async def create_project():
    """
    TODO: Implement the creation of a project
    """
    return {"message": "project created, just joking, not implemented yet"}


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
