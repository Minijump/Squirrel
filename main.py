from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

import subprocess
import os
import json
import pandas as pd
import importlib.util
import nbformat as nbf
from nbconvert import HTMLExporter

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def load_pipeline_module(project_dir):
    pipeline_path = os.path.join("projects", project_dir, "pipeline.py")
    spec = importlib.util.spec_from_file_location("pipeline", pipeline_path)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    return pipeline


@app.get("/")
async def read_root(request: Request):
    projects = []
    for project in os.listdir("./projects"):
        manifest_path = os.path.join("./projects", project, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
            projects.append(manifest_data)
    return templates.TemplateResponse("homepage.html", {"request": request, "projects": projects})


@app.post("/create_project/")
async def create_project():
    return {"message": "project created, just joking, not implemented yet"}


@app.post("/open_project/")
async def open_project(request: Request):
    form_data = await request.form()
    project_dir = form_data.get("project_directory")
    return RedirectResponse(url=f"/project/?project_dir={project_dir}", status_code=303)


@app.post("/project/")
@app.get("/project/")
async def project(request: Request, project_dir: str):
    try:
        pipeline = load_pipeline_module(project_dir)
        df = pipeline.run_pipeline()
        table_html = df.to_html(classes='df-table', index=False)
        return templates.TemplateResponse(
            "project.html",
            {"request": request, "table": table_html, "project_dir": project_dir}
        )
    except Exception as e:
        return {"message": f"Error executing pipeline for project with dir {project_dir}: {str(e)}"}


@app.get("/pipeline/")
@app.post("/pipeline/")
async def pipeline(request: Request, project_dir: str):
    # available alternative: 
    # subprocess.run(['jupyter', 'nbconvert', '--to', 'html', notebook_filename, '--output', html_filename])
    # TODO: make it editable + make it black theme
    pipeline_path = os.path.join("projects", project_dir, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        pipeline_code = file.read()

    nb = nbf.v4.new_notebook()
    code_cell = nbf.v4.new_code_cell(pipeline_code)
    nb.cells.append(code_cell)

    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'#edit here to have a black theme (custom?)
    (body, resources) = html_exporter.from_notebook_node(nb)
    
    return templates.TemplateResponse(
        "pipeline.html",
        {"request": request, "pipeline": body, "project_dir": project_dir}
    )


@app.post("/add_column/")
async def add_column(request: Request):
    form_data = await request.form()
    project_dir = form_data.get("project_dir")
    pipeline_path = os.path.join("projects", project_dir, "pipeline.py")
    new_column_code = f"""
    df['{form_data.get('col_name')}'] = {form_data.get('col_value')}
    # Add new code here (keep this comment line)"""
    with open(pipeline_path, 'r') as file:
        pipeline_code = file.read()
    new_pipeline_code = pipeline_code.replace("# Add new code here (keep this comment line)", new_column_code)
    with open(pipeline_path, 'w') as file:
        file.write(new_pipeline_code)
    return RedirectResponse(url=f"/project/?project_dir={project_dir}", status_code=303)

@app.post("/del_column/")
async def del_column(request: Request):
    form_data = await request.form()
    project_dir = form_data.get("project_dir")
    pipeline_path = os.path.join("projects", project_dir, "pipeline.py")
    del_column_code = f"""
    df = df.drop(columns=['{form_data.get('col_name')}'])
    # Add new code here (keep this comment line)"""
    with open(pipeline_path, 'r') as file:
        pipeline_code = file.read()
    new_pipeline_code = pipeline_code.replace("# Add new code here (keep this comment line)", del_column_code)
    with open(pipeline_path, 'w') as file:
        file.write(new_pipeline_code)
    return RedirectResponse(url=f"/project/?project_dir={project_dir}", status_code=303)
