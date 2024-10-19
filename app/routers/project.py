from fastapi import Request

import os
import importlib.util
import pandas as pd
import json

from app.utils import action
from app.routers import router, templates


def load_pipeline_module(project_dir):
    """
    Loads and returns the python pipeline module for the project

    * project_dir(str): The project directory name
    
    => Returns the pipeline module
    """
    pipeline_path = os.path.join( os.getcwd(), "projects", project_dir, "pipeline.py")
    spec = importlib.util.spec_from_file_location("pipeline", pipeline_path)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    return pipeline

def get_sources(project_dir):
    """
    Returns the list of data sources in the project

    * project_dir(str): The project directory name
    
    => Returns the list of available data sources
    """
    sources = []
    projects_dir = os.path.join(os.getcwd(), "projects", project_dir, "data_sources")
    for source in os.listdir(projects_dir):
        manifest_path = os.path.join(projects_dir, source, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
            sources.append(manifest_data)
    return sources

@router.post("/project/")
@router.get("/project/")
async def project(request: Request, project_dir: str):
    """
    Run the pipeline contained in the project directory and display the result

    * project_dir(str): The project directory name
    * request 

    => Returns a TemplateResponse to display project
    """
    exception = False
    dfs = {}
    try:
        pipeline = load_pipeline_module(project_dir)
        dfs = pipeline.run_pipeline()
    except Exception as e:
        exception = e
    finally:
        table_html = {}
        table_len = {}
        for name, df in dfs.items():
            if not exception and isinstance(df, pd.DataFrame):
                table_html[name] = df.head(10).to_html(classes='df-table', index=False)
                table_len[name] = len(df.index)

        sources = get_sources(project_dir)

        return templates.TemplateResponse(
            request,
            "project.html",
            {"table": table_html, "table_len": table_len, "project_dir": project_dir, "sources": sources, "exception": exception}
        )

@router.get("/project/page/")
async def project_page(request: Request, project_dir: str, table_name: str, page: int, n: int):
    """
    Fetch a specific page of the dataframe

    * project_dir(str): The project directory name
    * table_name(str): The name of the dataframe
    * page(int): The page number
    * n(int): Number of rows per page

    => Returns HTML for the specified page of the dataframe
    """
    try:
        pipeline = load_pipeline_module(project_dir)
        dfs = pipeline.run_pipeline()
        df = dfs[table_name]
        start = page * n
        end = start + n
        table_html = df.iloc[start:end].to_html(classes='df-table', index=False)
        return table_html
    except Exception as e:
        return str(e)

@router.post("/project/add_column/")
@action.add
async def add_column(request: Request):
    """
    Add a column to the dataframe

    * request contains: col_name, col_value, project_dir
    
    => Returns a string representing the code to add the column
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    new_code = f"""dfs['{table_name}']['{col_name}'] = {form_data.get('col_value')}  #sq_action:Add column {col_name} on table {table_name}"""
    return new_code

@router.post("/project/del_column/")
@action.add
async def del_column(request: Request):
    """
    Delete a column from the dataframe
    
    * request contains: col_name, project_dir
    
    => Returns a string representing the code to drop the column
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].drop(columns=['{col_name}'])  #sq_action:Delete column {col_name} on table {table_name}"""
    return new_code

@router.post("/project/create_table/")
@action.add
async def create_table(request: Request):
    """
    Create a new dataframe

    * form_data contains: data_source_dir, project_dir
    
    =>
    """
    form_data = await request.form()
    project_dir = form_data.get("project_dir")
    table_name = form_data.get("table_name")
    data_source_dir = form_data.get("data_source_dir")
    data_source_dir = os.path.join('projects', project_dir, 'data_sources', data_source_dir)
    data_source_dir = os.path.relpath(data_source_dir, os.getcwd())

    manifest_path = os.path.join(data_source_dir, "__manifest__.json")
    with open(manifest_path, 'r') as file:
        manifest_data = json.load(file)

    if manifest_data["type"] == "csv":
        csv_path = os.path.join(data_source_dir, "data.csv")
        source_name = manifest_data["name"]
        new_code = f"""dfs['{table_name}'] = pd.read_csv(r'{csv_path}')  #sq_action:Create table {table_name} from {source_name}"""

    if manifest_data["type"] == "xlsx":
        xlsx_path = os.path.join(data_source_dir, "data.xlsx")
        source_name = manifest_data["name"]
        new_code = f"""dfs['{table_name}'] = pd.read_excel(r'{xlsx_path}')  #sq_action:Create table {table_name} from '{source_name}'"""
    
    return new_code
