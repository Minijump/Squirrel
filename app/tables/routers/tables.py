from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse

import os
import importlib.util
import pandas as pd
import json
import traceback

from app.tables.models.actions import action
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
        df = pipeline.run_pipeline()[table]
        column = eval(f"df{column_identifier}")

        col_infos = {
            "dtype": str(column.dtype),
            "unique": str(column.nunique()),
            "null": str(column.isna().sum()),
            "count": str(len(column.index)),
            "is_numeric": column.dtype in ["float64", "int64"],
        }

        if col_infos["is_numeric"]:
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
