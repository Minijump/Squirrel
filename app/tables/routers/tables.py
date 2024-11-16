from fastapi import Request

import os
import importlib.util
import pandas as pd
import json
import traceback

from utils import action
from app import router, templates

from app.data_sources.routers.data_sources import get_sources
from app.data_sources.models.data_source import DATA_SOURCE_REGISTRY

def load_pipeline_module(project_dir):
    """
    Loads and returns the python pipeline module for the project

    * project_dir(str): The project directory name
    
    => Returns the pipeline module
    """
    pipeline_path = os.path.join( os.getcwd(), "_projects", project_dir, "pipeline.py")
    spec = importlib.util.spec_from_file_location("pipeline", pipeline_path)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    return pipeline

@router.get("/tables/")
async def tables(request: Request, project_dir: str):
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

        sources = await get_sources(project_dir)

        return templates.TemplateResponse(
            request,
            "tables.html",
            {"table": table_html, "table_len": table_len, "project_dir": project_dir, "sources": sources, "exception": exception}
        )

@router.get("/tables/pager/")
async def tables_pager(request: Request, project_dir: str, table_name: str, page: int, n: int):
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
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/tables_error.html", {"exception": str(e), "project_dir": project_dir})

@router.post("/tables/add_column/")
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

@router.post("/tables/del_column/")
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

@router.post("/tables/create_table/")
@action.add
async def create_table(request: Request):
    """
    Create a new dataframe

    * form_data
    
    => Returns a string representing the code to create the dataframe
    """
    form_data = await request.form()
    data_source_path = os.path.relpath(
        os.path.join(os.getcwd(), '_projects', form_data.get("project_dir"), 'data_sources', form_data.get("data_source_dir")), 
        os.getcwd()) # Use relative path to enable collaboration

    manifest_path = os.path.join(data_source_path, "__manifest__.json")
    with open(manifest_path, 'r') as file:
        manifest_data = json.load(file)

    SourceClass = DATA_SOURCE_REGISTRY[manifest_data["type"]]
    source = SourceClass(manifest_data, form_data)
    new_code = source.create_table(form_data)
    
    return new_code
