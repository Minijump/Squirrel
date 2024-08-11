from fastapi import Request

import os
import importlib.util

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

@router.post("/project/")
@router.get("/project/")
async def project(request: Request, project_dir: str):
    """
    Run the pipeline contained in the project directory and display the result

    * project_dir(str): The project directory name
    * request 

    => Returns a TemplateResponse to display project
    """
    pipeline = load_pipeline_module(project_dir)
    df = pipeline.run_pipeline()
    table_html = df.to_html(classes='df-table', index=False)# Do not convert all df to html? pass it as an argument?
    return templates.TemplateResponse(
        request,
        "project.html",
        {"table": table_html, "project_dir": project_dir}
    )


@router.post("/project/add_column/")
@action.add
async def add_column(request: Request):
    """
    Add a column to the dataframe

    * request contains: col_name, col_value, project_dir
    
    => Returns a string representing the code to add the column
    """
    form_data = await request.form()
    new_code = f"""df['{form_data.get('col_name')}'] = {form_data.get('col_value')}"""
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
    new_code = f"""df = df.drop(columns=['{form_data.get('col_name')}'])"""
    return new_code
