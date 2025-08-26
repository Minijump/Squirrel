import os
import shutil
import traceback

from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse

from app import router, templates
from app.data_sources.models.data_source import DataSource
from app.data_sources.models.data_source_factory import DataSourceFactory
from app.projects.models.project import Project
from app.utils.form_utils import squirrel_error, _get_form_data_info


@router.get("/data_sources/get_available_data_sources_type/")
async def get_available_data_sources_type(request: Request):
    available_types = DataSourceFactory.get_available_type()
    return JSONResponse(content={"available_types": available_types}, status_code=200)

@router.get("/data_sources/get_source_creation_specific_args/{source_type}")
@router.get("/data_sources/get_source_settings_specific_args/{source_type}")
async def get_source_specific_args(request: Request, source_type):
    is_settings = "settings" in str(request.url.path)
    SourceClass = DataSourceFactory.get_source_class(source_type)
    specific_args = SourceClass.get_source_specific_args(is_settings=is_settings)
    return JSONResponse(content=specific_args, status_code=200)

@router.get("/data_sources/")
@squirrel_error
async def data_sources(request: Request, project_dir: str):
    project = Project.instantiate_from_dir(project_dir)
    return templates.TemplateResponse(request, "data_sources/templates/data_sources.html", 
        {   
            "project_dir": project_dir, 
            "sources": project.get_sources(),
            "source_factory": DataSourceFactory
        }
    )

@router.post("/source/create/")
@squirrel_error
async def create_source(request: Request):
    form_data = await request.form()
    project_dir = form_data.get("project_dir")

    await DataSourceFactory.create_source(form_data)

    return RedirectResponse(url=f"/data_sources/?project_dir={project_dir}", status_code=303)

@router.get("/source/settings") 
@squirrel_error   
async def source_settings(request: Request, project_dir: str, source_dir: str):
    source = DataSource.get_manifest(project_dir, source_dir)
    return templates.TemplateResponse(request, "data_sources/templates/data_source_settings.html",
        {   
            "project_dir": project_dir,
            "source": source
        }
    )

@router.post("/source/update_settings/")
@squirrel_error
async def update_source_settings(request: Request):
    form_data = await request.form()
    project_dir, source_dir = await _get_form_data_info(request, ["project_dir", "source_dir"])

    source = DataSourceFactory.init_source_from_dir(project_dir, source_dir)
    await source.update_source_settings(form_data)

    return RedirectResponse(url=f"/data_sources/?project_dir={project_dir}", status_code=303)
    
@router.post("/source/sync")
async def sync_source(request: Request):
    try:
        project_dir, source_dir = await _get_form_data_info(request, ["project_dir", "source_dir"])
        source = DataSourceFactory.init_source_from_dir(project_dir, source_dir)
        await source.sync(project_dir)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
@router.post("/source/delete/")
@squirrel_error
async def delete_source(request: Request):
    project_dir, source_dir = await _get_form_data_info(request, ["project_dir", "source_dir"])

    source_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", source_dir)
    shutil.rmtree(source_path)

    return RedirectResponse(url=f"/data_sources/?project_dir={project_dir}", status_code=303)
