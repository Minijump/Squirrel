from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse

import os
import importlib.util
import pandas as pd
import json
import traceback

from utils import action
from app import router, templates

from app.data_sources.routers.data_sources import get_sources
from app.tables.models.actions import TABLE_ACTION_REGISTRY

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

def generate_column_identifier(columns):
    """Convert MultiIndex columns into a string identifier."""
    if isinstance(columns, tuple):
        return "[" + ", ".join(f"'{c}'" for c in columns) + "]"
    return f"['{columns}']"

def to_html_with_identifiers(df):
    html = df.to_html(classes='df-table', index=False)
    
    column_identifiers = [generate_column_identifier(col) for col in df.columns]
    header_html = ""
    for idx, col_id in enumerate(column_identifiers):
        if isinstance(df.columns, pd.MultiIndex):
            header_html += f"""<th data-columnidentifier="{col_id}" data-columnidx="{df.columns[idx]}">{df.columns[idx][-1]}</th>\n"""
        else:
            header_html += f"""<th data-columnidentifier="{col_id}" data-columnidx="{df.columns[idx]}">{df.columns[idx]}</th>\n"""

    header_start = html.find('<thead>')
    header_end = html.find('</thead>')
    header_rows = html[header_start:header_end]
    modified_header = header_rows.rsplit('<tr', 1)
    modified_header = f"{modified_header[0]}<tr>{header_html}</tr>"
    return html[:header_start] + modified_header + html[header_end:]

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
        table_len_infos = {}
        for name, df in dfs.items():
            if not exception and isinstance(df, pd.DataFrame):
                manifest_path = os.path.join(os.getcwd(), "_projects", project_dir, "__manifest__.json")
                with open(manifest_path, 'r') as file:
                    manifest_data = json.load(file)
                display_len = manifest_data.get('misc', {}).get("table_len", 10)
                table_html[name] = to_html_with_identifiers(df.head(display_len))
                table_len_infos[name] = {'total_len': len(df.index), 'display_len': display_len}

        sources = await get_sources(project_dir) # Necessary to be able to get the available sources for table creation

        return templates.TemplateResponse(
            request,
            "tables/tables.html",
            {"table": table_html, "table_len_infos": table_len_infos, "project_dir": project_dir, "sources": sources, "exception": exception}
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
        table_html = to_html_with_identifiers(df.iloc[start:end])
        return table_html
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/tables_error.html", {"exception": str(e), "project_dir": project_dir})

@router.post("/tables/execute_action/")
@action.add
async def execute_action(request: Request):
    form_data = await request.form()
    action_name = form_data.get("action_name")
    ActionClass = TABLE_ACTION_REGISTRY.get(action_name)
    if not ActionClass:
        raise ValueError(f"Action {action_name} not found")

    action_instance = ActionClass(request)
    new_code = await action_instance.execute()
    return new_code

@router.get("/tables/get_action_args/")
async def get_action_args(request: Request, action_name: str):
    ActionClass = TABLE_ACTION_REGISTRY.get(action_name)
    if not ActionClass:
        raise ValueError(f"Action {action_name} not found")

    action_instance = ActionClass(request)
    args = action_instance.args
    return args

@router.get("/tables/column_infos/")
async def get_col_infos(request: Request, project_dir: str, table: str, column_name: str, column_identifier: str):
    """
    Get the column 'column' from table 'tables' informations

    * request: The request object
    * project_dir(str): The project directory name
    * tables(str): The name of the dataframe
    * column_name(str): The name of the column
    * column_identifier(str): The column identifier. i.e. "['col1']['col2']" or "['col1']
    
    => Returns the column informations (dict)
    """
    try:
        pipeline = load_pipeline_module(project_dir)
        dfs = pipeline.run_pipeline()
        df = dfs[table]
        column = eval(f"df{column_identifier}")

        dtype = str(column.dtype)
        col_infos = {
            "dtype": dtype,
            "unique": str(column.nunique()),
            "null": str(column.isna().sum()),
            "count": str(len(column.index)),
            "is_numeric": False,
        }

        if dtype == "float64" or dtype == "int64":
            col_infos["is_numeric"] = True
            col_infos["mean"] = str(column.mean())
            col_infos["std"] = str(column.std())
            col_infos["min"] = str(column.min())
            col_infos["max"] = str(column.max())
            col_infos["25"] = str(column.quantile(0.25))
            col_infos["50"] = str(column.quantile(0.5))
            col_infos["75"] = str(column.quantile(0.75))

        return col_infos
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/tables_error.html", {"exception": str(e), "project_dir": project_dir})

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
    col_idx = form_data.get("col_idx")
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"

    new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].drop(columns=[{col_idx}])  #sq_action:Delete column {col_name} on table {table_name}"""
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
    col_identifier = form_data.get("col_identifier")
    col_idx = form_data.get("col_idx")
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    
    if action == "delete":
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].dropna(subset=[{col_idx}])  #sq_action:Delete rows with missing values in column {col_name} of table {table_name}"""
    elif action == "replace":
        replace_value = form_data.get("replace_value")
        new_code = f"""dfs['{table_name}']{col_identifier} = dfs['{table_name}']{col_identifier}.fillna({replace_value})  #sq_action:Replace missing values with {replace_value} in column {col_name} of table {table_name}"""
    elif action == "interpolate":
        new_code = f"""dfs['{table_name}']{col_identifier} = dfs['{table_name}']{col_identifier}.interpolate()  #sq_action:Interpolate missing values in column {col_name} of table {table_name}"""
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
    col_identifier = form_data.get("col_identifier")
    col_idx = form_data.get("col_idx")
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"

    new_code = f"""dfs['{table_name}']{col_identifier} = dfs['{table_name}']{col_identifier}.replace({replace_vals})  #sq_action:Replace values in column {col_name} of table {table_name}"""
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
    col_identifier = form_data.get("col_identifier")
    col_idx = form_data.get("col_idx")
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"

    if method == "min_max":
        new_code = f"""dfs['{table_name}']{col_identifier} = (dfs['{table_name}']{col_identifier} - dfs['{table_name}']{col_identifier}.min()) / (dfs['{table_name}']{col_identifier}.max() - dfs['{table_name}']{col_identifier}.min())  #sq_action:Normalize (min-max) column {col_name} of table {table_name}"""
    elif method == "mean":
        new_code = f"""dfs['{table_name}']{col_identifier} = (dfs['{table_name}']{col_identifier} - dfs['{table_name}']{col_identifier}.mean()) / dfs['{table_name}']{col_identifier}.std()  #sq_action:Normalize (mean) column {col_name} of table {table_name}"""

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
    col_identifier = form_data.get("col_identifier")
    col_idx = form_data.get("col_idx")
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    lower_bound = form_data.get("lower_bound")
    upper_bound = form_data.get("upper_bound")
    new_code = f"""dfs['{table_name}'] = dfs['{table_name}'][(dfs['{table_name}']{col_identifier} >= {lower_bound}) & (dfs['{table_name}']{col_identifier} <= {upper_bound})]  #sq_action:Remove vals out of [{lower_bound}, {upper_bound}] in column {col_name} of table {table_name}"""
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
    col_identifier = form_data.get("col_identifier")
    col_idx = form_data.get("col_idx")
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    new_col_name = form_data.get("new_col_name")
    new_code = f"""dfs['{table_name}'].rename(columns={{{col_idx}: '{new_col_name}'}}, inplace=True)  #sq_action:Rename column {col_name} to {new_col_name} in table {table_name}"""
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
    col_identifier = form_data.get("col_identifier")
    col_idx = form_data.get("col_idx")
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    new_col_type = form_data.get("new_col_type")
    new_code = f"""dfs['{table_name}'][{col_idx}] = dfs['{table_name}'][{col_idx}].astype('{new_col_type}')  #sq_action:Change type of column {col_name} to {new_col_type} in table {table_name}"""
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
    col_identifier = form_data.get("col_identifier")
    col_idx = form_data.get("col_idx")
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    sort_order = form_data.get("sort_order")
    sort_key = form_data.get("sort_key")

    if sort_order == "custom":
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].sort_values(by=[{col_idx}], key=lambda x: {sort_key})  #sq_action:Sort {col_name} of table {table_name} with custom key"""
    elif sort_order == "ascending":
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].sort_values(by=[{col_idx}], ascending=True)  #sq_action:Sort(asc) {col_name} of table {table_name}"""
    elif sort_order == "descending":
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].sort_values(by=[{col_idx}], ascending=False)  #sq_action:Sort(desc) {col_name} of table {table_name}"""
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
    col_identifier = form_data.get("col_identifier")
    col_idx = form_data.get("col_idx")
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    cut_values = form_data.get("cut_values").split(',')
    cut_labels = form_data.get("cut_labels").split(',')

    int_cut_values = [int(val) for val in cut_values]
    new_code = f"""dfs['{table_name}']{col_identifier} = pd.cut(dfs['{table_name}']{col_identifier}, bins={int_cut_values}, labels={cut_labels})  #sq_action:Cut values in column {col_name} of table {table_name}"""
    return new_code

@router.post("/tables/export_table/")
async def export_table(request: Request):
    """
    Export the table in the specified format

    * request contains: table_name, export_type, project_dir
    
    => Returns a FileResponse to download the exported file
    """
    form_data = await request.form()
    table_name = form_data.get("table_name")
    export_type = form_data.get("export_type")
    project_dir = form_data.get("project_dir")

    try:
        pipeline = load_pipeline_module(project_dir)
        dfs = pipeline.run_pipeline()
        df = dfs[table_name]

        export_dir = os.path.join(os.getcwd(), "_projects", project_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, f"{table_name}.{export_type}")

        if export_type == "csv":
            df.to_csv(export_path, index=False)
        elif export_type == "xlsx":
            df.to_excel(export_path, index=False)
        elif export_type == "pkl":
            df.to_pickle(export_path)
        elif export_type == "json":
            df.to_json(export_path, orient='records')

        return FileResponse(export_path, filename=f"{table_name}.{export_type}")

    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/tables_error.html", {"exception": str(e), "project_dir": project_dir})
