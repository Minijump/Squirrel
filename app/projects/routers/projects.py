from fastapi import Request
from fastapi.responses import RedirectResponse

import os
import json
import traceback

from app import router, templates
from app.projects.models import Project

@router.get("/projects/")
async def projects(request: Request):
    """
    The homepage of the application, displays all the 'project' in the ./_projects directory, 
    Informations about a project are read from their manifests

    * request

    => Returns a TemplateResponse to display homepage
    """
    try:
        projects = []
        projects_path = os.path.join(os.getcwd(), "_projects")

        for project in os.listdir(projects_path):
            manifest_path = os.path.join(projects_path, project, "__manifest__.json")
            with open(manifest_path, 'r') as file:
                manifest_data = json.load(file)
                projects.append(manifest_data)

        return templates.TemplateResponse(request, "projects/projects.html", {"projects": projects})
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/projects_error.html", {"exception": str(e)})

@router.post("/projects/create/")
async def create_project(request: Request):
    """
    Creates a new project directory in the ./_projects directory, with the necessary files

    * request contains form data

    => Returns a RedirectResponse to the project page
    """
    try:
        form_data = await request.form()
        project_name = form_data.get("project_name")
        project_description = form_data.get("project_description")
        
        project = Project(project_name, project_description)
        await project.create()
        return RedirectResponse(url=f"/projects/open/?project_dir={project.directory}", status_code=303)
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/projects_error.html", {"exception": str(e)})

@router.get("/projects/open/")
async def open_project(request: Request):
    """ 
    Function called when a user clicks on a project in the homepage, it redirects the correct project page

    * request contains project diretory

    => Returns a RedirectResponse to the project page
    """
    try:
        project_dir = request.query_params.get("project_dir")
        return RedirectResponse(url=f"/tables/?project_dir={project_dir}", status_code=303)
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/projects_error.html", {"exception": str(e)})
