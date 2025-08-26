import os
import shutil

from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse

from app import router, templates
from app.projects.models.project import PROJECT_TYPE_REGISTRY, Project
from app.utils.form_utils import squirrel_error


@router.get("/projects/get_type_options/")
async def project_type_options(request: Request):
    """Returns a JSONResponse with the different project types"""
    options = [(key, value.display_name) for key, value in PROJECT_TYPE_REGISTRY.items()]
    return JSONResponse(content={"options": options}, status_code=200)

@router.get("/projects/")
@squirrel_error
async def projects(request: Request):
    projects_path = os.path.join(os.getcwd(), "_projects")
    projects = Project.get_available_projects(projects_path)
    return templates.TemplateResponse(
        request, 
        "projects/templates/projects.html", 
        {"projects": projects, "PROJECT_TYPE_REGISTRY": PROJECT_TYPE_REGISTRY})

@router.post("/projects/create/")
@squirrel_error
async def create_project(request: Request):
    form_data = await request.form()
    project_type = form_data.get("project_type", "std")
    
    ProjectClass = PROJECT_TYPE_REGISTRY[project_type]
    project = ProjectClass(form_data)
    await project.create()

    return RedirectResponse(url=f"/projects/open/?project_dir={project.directory}", status_code=303)

@router.get("/projects/open/")
@squirrel_error
async def open_project(request: Request):
    project_dir = request.query_params.get("project_dir")
    return RedirectResponse(url=f"/tables/?project_dir={project_dir}", status_code=303)

@router.get("/project/settings/")
@squirrel_error
async def project_settings(request: Request, project_dir: str):
    project = Project.instantiate_from_dir(project_dir)
    project_settings = project.get_settings()

    return templates.TemplateResponse(
        request,
        "projects/templates/project_settings.html",
        {"project": project_settings, "project_dir": project_dir}
    )

@router.post("/project/update_settings/")
@squirrel_error
async def update_project_settings(request: Request):
    form_data = await request.form()
    project_dir = form_data.get("project_dir")
    project = Project.instantiate_from_dir(project_dir)

    project.update_settings(form_data)

    return RedirectResponse(url=f"/tables/?project_dir={project_dir}", status_code=303)

@router.post("/project/delete/")
@squirrel_error
async def delete_project(request: Request):
    """Delete the project (not in the class because it the _projects directory)"""
    form_data = await request.form()
    project_dir = form_data.get("project_dir")

    project_path = os.path.join(os.getcwd(), "_projects", project_dir)
    shutil.rmtree(project_path)

    return RedirectResponse(url="/projects/", status_code=303)
