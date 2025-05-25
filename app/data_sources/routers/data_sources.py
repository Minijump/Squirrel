import json
import os
import shutil
import traceback

from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse

from app import router, templates
from app.data_sources.models import DATA_SOURCE_REGISTRY
from app.utils.form_utils import squirrel_error, _get_form_data_info


async def get_sources(project_dir):
    """Returns the list of data sources in the project"""
    sources = []
    project_data_sources_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources")
    for source in os.listdir(project_data_sources_path):
        manifest_path = os.path.join(project_data_sources_path, source, "__manifest__.json")
        if os.path.isfile(manifest_path):
            with open(manifest_path, 'r') as file:
                manifest_data = json.load(file)
                sources.append(manifest_data)
    return sources

async def get_manifest(project_dir, source_dir):
    """Returns the manifest content"""
    manifest_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", source_dir, "__manifest__.json")
    with open(manifest_path, 'r') as file:
        return json.load(file)
    
async def init_source_instance(manifest_data):
    """Initialize the source instance"""
    SourceClass = DATA_SOURCE_REGISTRY[manifest_data["type"]]
    return SourceClass(manifest_data)

@router.get("/data_sources/")
@squirrel_error
async def data_sources(request: Request, project_dir: str):
    """Returns a TemplateResponse to display data_sources page"""
    sources = await get_sources(project_dir)
    return templates.TemplateResponse(request, "data_sources/templates/data_sources.html", 
        {   "project_dir": project_dir, 
            "sources": sources,
            "DATA_SOURCE_REGISTRY": DATA_SOURCE_REGISTRY})

@router.post("/create_source/")
@squirrel_error
async def create_source(request: Request):
    """Create a new data source + returns a RedirectResponse to the data sources page"""
    form_data = await request.form()
    project_dir, source_type = await _get_form_data_info(request, ["project_dir", "source_type"])

    SourceClass = DATA_SOURCE_REGISTRY[source_type]
    SourceClass.check_available_infos(form_data)
    source = await SourceClass._create_source(form_data)
    await source._create_required_files(form_data)

    return RedirectResponse(url=f"/data_sources/?project_dir={project_dir}", status_code=303)

@router.get("/source/settings") 
@squirrel_error   
async def source_settings(request: Request, project_dir: str, source_dir: str):
    """Returns a TemplateResponse to display data_sources settings page"""
    source = await get_manifest(project_dir, source_dir)
    return templates.TemplateResponse(request, "data_sources/templates/data_source_settings.html",
        {"project_dir": project_dir, "source": source})

@router.post("/source/update_settings/")
@squirrel_error
async def update_source_settings(request: Request):
    """Update the settings of a data source + Returns a RedirectResponse to the source settings page"""
    form_data = await request.form()
    project_dir, source_dir = await _get_form_data_info(request, ["project_dir", "source_dir"])

    manifest_data = await get_manifest(project_dir, source_dir)
    source = await init_source_instance(manifest_data)
    await source.update_source_settings(form_data)

    return RedirectResponse(url=f"/data_sources/?project_dir={project_dir}", status_code=303)
    
@router.post("/source/sync")
async def sync_source(request: Request):
    """Sync the data source + Returns a JSONResponse with the sync status"""
    try:
        project_dir, source_dir = await _get_form_data_info(request, ["project_dir", "source_dir"])

        manifest_data = await get_manifest(project_dir, source_dir)
        source = await init_source_instance(manifest_data)
        await source.sync(project_dir)

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
@router.post("/source/delete/")
@squirrel_error
async def delete_source(request: Request):
    """Delete the data source + Returns a RedirectResponse to the data sources page"""
    project_dir, source_dir = await _get_form_data_info(request, ["project_dir", "source_dir"])

    source_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", source_dir)
    shutil.rmtree(source_path)

    return RedirectResponse(url=f"/data_sources/?project_dir={project_dir}", status_code=303)
