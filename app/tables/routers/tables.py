import json
import os
import pandas as pd
import pickle

from fastapi import Request
from fastapi.responses import FileResponse, RedirectResponse

from app import router, templates
from app.projects.models.project import Project
from app.pipelines.models.actions_column import convert_col_idx
from app.pipelines.models.actions_utils import TABLE_ACTION_REGISTRY
from app.utils.form_utils import squirrel_error, squirrel_action_error, _get_form_data_info
from app.pipelines.models.pipeline import Pipeline
from app.pipelines.models.pipeline_action import PipelineAction


def to_html_with_idx(df):
    """Convert a dataframe to HTML with custom 'data-columnidx'"""
    html = df.to_html(classes='df-table', index=False)
    
    header_html = ""
    for idx, col_id in enumerate(df.columns):
        if isinstance(df.columns, pd.MultiIndex):
            header_html += f"""<th data-columnidx="{df.columns[idx]}">{df.columns[idx][-1]}</th>\n"""
        else:
            header_html += f"""<th data-columnidx="{df.columns[idx]}">{df.columns[idx]}</th>\n"""

    header_start = html.find('<thead>')
    header_end = html.find('</thead>')
    header_rows = html[header_start:header_end]
    modified_header = header_rows.rsplit('<tr', 1)
    modified_header = f"{modified_header[0]}<tr>{header_html}</tr>"
    return html[:header_start] + modified_header + html[header_end:]

@router.get("/tables/")
@squirrel_error
async def tables(request: Request, project_dir: str):
    """Run the pipeline contained in the project directory and Returns a TemplateResponse to display the tables"""
    exception = False
    tables = {}
    try:
        pipeline = Pipeline(project_dir)
        tables = await pipeline.run_pipeline()
    except Exception as e:
        exception = e
    finally:
        # save tables as a pickle file (will increase speed of things that does not read the whole pipeline to be run)
        datatables_path = os.path.join( os.getcwd(), "_projects", project_dir, "data_tables.pkl")
        with open(datatables_path, 'wb') as f:
            pickle.dump(tables, f)
        # Convert them to html (first lines)
        table_html = {}
        table_len_infos = {}
        for name, df in tables.items():
            if not exception and isinstance(df, pd.DataFrame):
                manifest_path = os.path.join(os.getcwd(), "_projects", project_dir, "__manifest__.json")
                with open(manifest_path, 'r') as file:
                    manifest_data = json.load(file)
                display_len = manifest_data.get('misc', {}).get("table_len", 10)
                table_html[name] = to_html_with_idx(df.head(display_len))
                table_len_infos[name] = {'total_len': len(df.index), 'display_len': display_len}

        project = Project.instantiate_from_dir(project_dir)
        sources = project.get_sources()

        return templates.TemplateResponse(
            request,
            "tables/templates/tables.html",
            {"table": table_html, "table_len_infos": table_len_infos, "project_dir": project_dir, "sources": sources, "exception": exception}
        )

@router.get("/tables/pager/")
@squirrel_error
async def tables_pager(request: Request, project_dir: str, table_name: str, page: int, n: int):
    """Fetch a specific page of the dataframe and returns an HTML table"""
    data_tables_path = os.path.join( os.getcwd(), "_projects", project_dir, "data_tables.pkl")
    if os.path.exists(data_tables_path):
        with open(data_tables_path, 'rb') as f:
            tables = pickle.load(f)
    else:
        pipeline = Pipeline(project_dir)
        tables = await pipeline.run_pipeline()
    df = tables[table_name]
    start = page * n
    end = start + n
    table_html = to_html_with_idx(df.iloc[start:end])
    return table_html

@router.post("/tables/add_action/")
@squirrel_action_error
async def add_action(request: Request):
    """ 
    Execute the selected action selected by the user. 
    The function returns the corresponding code, which is added in the python pipeline file via the decorator
    """
    form_data = await request.form()
    project_dir = form_data.get("project_dir")
    action_name = form_data.get("action_name")

    ActionClass = TABLE_ACTION_REGISTRY.get(action_name)
    if not ActionClass:
        raise ValueError(f"Action {action_name} not found")
    action_instance = ActionClass(form_data)

    pipeline = Pipeline(project_dir)
    pipeline_action = PipelineAction(pipeline, action_instance)
    await pipeline_action.add_to_pipeline()

    return RedirectResponse(url=f"/tables/?project_dir={project_dir}", status_code=303)                

@router.get("/tables/get_action_args/")
async def get_action_args(request: Request, action_name: str, project_dir: str = None):
    """Returns the arguments of the action selected by the user"""
    ActionClass = TABLE_ACTION_REGISTRY.get(action_name)
    if not ActionClass:
        raise ValueError(f"Action {action_name} not found")

    action_instance = ActionClass({})
    args = action_instance.args

    # TODO: move this logic outside of controller ------------------------------------------
    # (add a method in ActionClass, that will do nothing for most)

    # If the CreateTable action is requested and a project_dir is provided,
    # populate the select_options for data_source_dir and table_df from the
    # project's data sources and previously computed tables (if available).
    if action_name == 'CreateTable' and project_dir:
        # available data sources
        try:
            project = Project.instantiate_from_dir(project_dir)
            sources = project.get_sources()
            available_data_sources = [(s.get('directory'), s.get('name')) for s in sources]
        except Exception:
            available_data_sources = []

        # available tables (try to read the cached pickle file first)
        available_tables = []
        data_tables_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_tables.pkl")
        try:
            if os.path.exists(data_tables_path):
                with open(data_tables_path, 'rb') as f:
                    tables = pickle.load(f)
            else:
                pipeline = Pipeline(project_dir)
                tables = await pipeline.run_pipeline()

            if isinstance(tables, dict):
                available_tables = [(k, k) for k in tables.keys()]
        except Exception:
            available_tables = []

        # inject into args if the expected keys exist
        if 'data_source_dir' in args:
            args['data_source_dir']['select_options'] = available_data_sources
        if 'table_df' in args:
            args['table_df']['select_options'] = available_tables
    #----------------------------------------------------------------------------------------

    return args

@router.get("/tables/column_infos/")
@squirrel_error
async def get_col_infos(request: Request, project_dir: str, table: str, column_name: str, column_idx: str):
    """Returns the column informations (dict)"""
    data_tables_path = os.path.join( os.getcwd(), "_projects", project_dir, "data_tables.pkl")
    if os.path.exists(data_tables_path):
        with open(data_tables_path, 'rb') as f:
            tables = pickle.load(f)
            df = tables[table]
    else:
        pipeline = Pipeline(project_dir)
        df = await pipeline.run_pipeline()[table]
    column = df[eval(convert_col_idx(column_idx))]

    col_infos = {
        "dtype": str(column.dtype),
        "unique": str(column.nunique()),
        "null": str(column.isna().sum()),
        "count": str(len(column.index)),
        "is_numeric": column.dtype in ["float64", "int64"],
        "is_string": column.dtype == "object" or isinstance(column.dtype, pd.StringDtype),
        "top_values": column.value_counts().head(5).to_dict()
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
    
    if col_infos["is_string"]:
        col_infos["is_string"] = True
        string_lengths = column.str.len()
        col_infos["avg_length"] = str(string_lengths.mean())
        col_infos["min_length"] = str(string_lengths.min())
        col_infos["max_length"] = str(string_lengths.max())
        col_infos["empty_strings"] = str((column == "").sum())

    return col_infos

@router.post("/tables/export_table/")
@squirrel_error
async def export_table(request: Request):
    """ Returns a FileResponse to export the selected file"""
    table_name, export_type, project_dir = await _get_form_data_info(request, ["table_name", "export_type", "project_dir"])

    pipeline = Pipeline(project_dir)
    tables = await pipeline.run_pipeline()
    df = tables[table_name]

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
