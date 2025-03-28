import json
import os

from fastapi import Request
from fastapi.responses import RedirectResponse

from app import router, templates
from app.projects.models import PROJECT_TYPE_REGISTRY
from app.utils.error_handling import squirrel_error

@router.get("/projects/")
@squirrel_error
async def projects(request: Request):
    """
    The homepage of the application, displays all the 'project' in the ./_projects directory, 
    Informations about a project are read from their manifests

    * request

    => Returns a TemplateResponse to display homepage
    """
    projects = []
    projects_path = os.path.join(os.getcwd(), "_projects")

    for project in os.listdir(projects_path):
        manifest_path = os.path.join(projects_path, project, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
            projects.append(manifest_data)

    return templates.TemplateResponse(
        request, 
        "projects/templates/projects.html", 
        {"projects": projects, "PROJECT_TYPE_REGISTRY": PROJECT_TYPE_REGISTRY})

@router.post("/projects/create/")
@squirrel_error
async def create_project(request: Request):
    """
    Creates a new project directory in the ./_projects directory, with the necessary files

    * request contains form data

    => Returns a RedirectResponse to the project page
    """
    form_data = await request.form()
    project_type = form_data.get("project_type", "std")
    
    ProjectClass = PROJECT_TYPE_REGISTRY[project_type]
    project = ProjectClass(form_data)
    await project.create()

    return RedirectResponse(url=f"/projects/open/?project_dir={project.directory}", status_code=303)

@router.get("/projects/open/")
@squirrel_error
async def open_project(request: Request):
    """ 
    Function called when a user clicks on a project in the homepage, it redirects the correct project page

    * request contains project diretory

    => Returns a RedirectResponse to the project page
    """
    project_dir = request.query_params.get("project_dir")
    return RedirectResponse(url=f"/tables/?project_dir={project_dir}", status_code=303)

@router.get("/project/settings/")
@squirrel_error
async def project_settings(request: Request, project_dir: str):
    """
    Display and edit the project settings

    * request
    * project_dir(str): The project directory

    => Returns a TemplateResponse to display project settings
    """
    manifest_path = os.path.join(os.getcwd(), "_projects", project_dir, "__manifest__.json")
    with open(manifest_path, 'r') as file:
        manifest_data = json.load(file)

    return templates.TemplateResponse(
        request, 
        "projects/templates/project_settings.html", 
        {"project": manifest_data, "project_dir": project_dir}
    )

@router.post("/project/update_settings/")
@squirrel_error
async def update_project_settings(request: Request):
    """
    Update the project settings

    * request: contains the form data

    => Returns a JSONResponse indicating success or failure
    """
    form_data = await request.form()
    project_dir = form_data.get("project_dir")

    manifest_path = os.path.join(os.getcwd(), "_projects", project_dir, "__manifest__.json")
    with open(manifest_path, 'r') as file:
        manifest_data = json.load(file)
    
    ProjectClass = PROJECT_TYPE_REGISTRY[manifest_data['project_type']]
    project = ProjectClass(manifest_data)
    await project.update_settings(form_data)

    return RedirectResponse(url=f"/tables/?project_dir={project_dir}", status_code=303) 

@router.get("/app/settings/")
@squirrel_error
async def app_settings(request: Request):
    """
    Display the application settings

    * request

    => Returns a TemplateResponse to display application settings (empty for now)
    """
    return templates.TemplateResponse(request, "projects/templates/app_settings.html", {})                                                   
