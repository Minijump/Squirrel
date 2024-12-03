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

        sources = await get_sources(project_dir) # Necessary to be able to get the available sources for table creation

        return templates.TemplateResponse(
            request,
            "tables/tables.html",
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

@router.get("/tables/column_infos/")
async def get_col_infos(request: Request, project_dir: str, table: str, column: str):
    """
    Get the column 'column' from table 'tables' informations

    * request: The request object
    * project_dir(str): The project directory name
    * tables(str): The name of the dataframe
    * column(str): The name of the column
    
    => Returns the column informations (dict)
    """
    try:
        pipeline = load_pipeline_module(project_dir)
        dfs = pipeline.run_pipeline()
        df = dfs[table]

        dtype = str(df[column].dtype)
        col_infos = {
            "dtype": str(df[column].dtype),
            "unique": str(df[column].nunique()),
            "null": str(df[column].isna().sum()),
            "count": str(len(df[column].index)),
            "is_numeric": False,
        }

        if dtype == "float64" or dtype == "int64":
            col_infos["is_numeric"] = True
            col_infos["mean"] = str(df[column].mean())
            col_infos["std"] = str(df[column].std())
            col_infos["min"] = str(df[column].min())
            col_infos["max"] = str(df[column].max())
            col_infos["25"] = str(df[column].quantile(0.25))
            col_infos["50"] = str(df[column].quantile(0.5))
            col_infos["75"] = str(df[column].quantile(0.75))

        return col_infos
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

@router.post("/tables/missing_values/")
@action.add
async def handle_missing_values(request: Request):
    """
    Handle missing values in the dataframe

    * request contains: action (delete, replace,...), table_name
    
    => Returns a string representing the code to handle missing values
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    action = form_data.get("action")
    
    if action == "delete":
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].dropna(subset=['{col_name}'])  #sq_action:Delete rows with missing values in column {col_name} of table {table_name}"""
    elif action == "replace":
        replace_value = form_data.get("replace_value")
        new_code = f"""dfs['{table_name}']['{col_name}'] = dfs['{table_name}']['{col_name}'].fillna({replace_value})  #sq_action:Replace missing values with {replace_value} in column {col_name} of table {table_name}"""
    elif action == "interpolate":
        new_code = f"""dfs['{table_name}']['{col_name}'] = dfs['{table_name}']['{col_name}'].interpolate()  #sq_action:Interpolate missing values in column {col_name} of table {table_name}"""
    else:
        raise ValueError("Invalid action for handling missing values")

    return new_code

@router.post("/tables/replace_values/")
@action.add
async def replace_values(request: Request):
    """
    Replace values in the dataframe

    * request contains: table_name, col_name, replace_vals, project_dir
    
    => Returns a string representing the code to replace the values
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    replace_vals = form_data.get("replace_vals")

    new_code = f"""dfs['{table_name}']['{col_name}'] = dfs['{table_name}']['{col_name}'].replace({replace_vals})  #sq_action:Replace values in column {col_name} of table {table_name}"""
    return new_code

@router.post("/tables/normalize_column/")
@action.add
async def normalize_column(request: Request):
    """
    Normalize a column in the dataframe

    * request contains: table_name, col_name, project_dir
    
    => Returns a string representing the code to normalize the column
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    method = form_data.get("methods")

    if method == "min_max":
        new_code = f"""dfs['{table_name}']['{col_name}'] = (dfs['{table_name}']['{col_name}'] - dfs['{table_name}']['{col_name}'].min()) / (dfs['{table_name}']['{col_name}'].max() - dfs['{table_name}']['{col_name}'].min())  #sq_action:Normalize (min-max) column {col_name} of table {table_name}"""
    elif method == "mean":
        new_code = f"""dfs['{table_name}']['{col_name}'] = (dfs['{table_name}']['{col_name}'] - dfs['{table_name}']['{col_name}'].mean()) / dfs['{table_name}']['{col_name}'].std()  #sq_action:Normalize (mean) column {col_name} of table {table_name}"""

    return new_code

@router.post("/tables/remove_under_over/")
@action.add
async def remove_under_over(request: Request):
    """
    Remove under/over values in the dataframe

    * request contains: table_name, col_name, lower_bound, upper_bound, project_dir
    
    => Returns a string representing the code to remove under/over values
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    lower_bound = form_data.get("lower_bound")
    upper_bound = form_data.get("upper_bound")
    new_code = f"""dfs['{table_name}'] = dfs['{table_name}'][(dfs['{table_name}']['{col_name}'] >= {lower_bound}) & (dfs['{table_name}']['{col_name}'] <= {upper_bound})]  #sq_action:Remove vals out of [{lower_bound}, {upper_bound}] in column {col_name} of table {table_name}"""
    return new_code

@router.post("/tables/rename_column/")
@action.add
async def rename_column(request: Request):
    """
    Rename a column in the dataframe

    * request contains: table_name, col_name, new_col_name, project_dir
    
    => Returns a string representing the code to rename the column
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    new_col_name = form_data.get("new_col_name")
    new_code = f"""dfs['{table_name}'].rename(columns={{'{col_name}': '{new_col_name}'}}, inplace=True)  #sq_action:Rename column {col_name} to {new_col_name} in table {table_name}"""
    return new_code

@router.post("/tables/edit_column_type/")
@action.add
async def edit_column_type(request: Request):
    """
    Edit the type of a column in the dataframe

    * request contains: table_name, col_name, new_col_type, project_dir
    
    => Returns a string representing the code to edit the column type
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    new_col_type = form_data.get("new_col_type")
    new_code = f"""dfs['{table_name}']['{col_name}'] = dfs['{table_name}']['{col_name}'].astype('{new_col_type}')  #sq_action:Change type of column {col_name} to {new_col_type} in table {table_name}"""
    return new_code

@router.post("/tables/sort_column/")
@action.add
async def sort_column(request: Request):
    """
    Sort a column in the dataframe

    * request contains: table_name, col_name, sort_order, sort_key, project_dir
    
    => Returns a string representing the code to sort the column
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    sort_order = form_data.get("sort_order")
    sort_key = form_data.get("sort_key")

    if sort_order == "custom":
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].sort_values(by=['{col_name}'], key=lambda x: {sort_key})  #sq_action:Sort {col_name} of table {table_name} with custom key"""
    elif sort_order == "ascending":
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].sort_values(by=['{col_name}'], ascending=True)  #sq_action:Sort(asc) {col_name} of table {table_name}"""
    elif sort_order == "descending":
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].sort_values(by=['{col_name}'], ascending=False)  #sq_action:Sort(desc) {col_name} of table {table_name}"""
    else:
        raise ValueError("Invalid sort order")
    
    return new_code

@router.post("/tables/cut_values/")
@action.add
async def cut_values(request: Request):
    """
    Cut values in the dataframe

    * request contains: table_name, col_name, cut_values, cut_labels, project_dir
    
    => Returns a string representing the code to cut the values
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    col_name = form_data.get("col_name")
    cut_values = form_data.get("cut_values").split(',')
    cut_labels = form_data.get("cut_labels").split(',')

    int_cut_values = [int(val) for val in cut_values]
    new_code = f"""dfs['{table_name}']['{col_name}'] = pd.cut(dfs['{table_name}']['{col_name}'], bins={int_cut_values}, labels={cut_labels})  #sq_action:Cut values in column {col_name} of table {table_name}"""
    return new_code
