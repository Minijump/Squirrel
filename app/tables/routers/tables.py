import os

from fastapi import Request
from fastapi.responses import FileResponse, RedirectResponse

from app import router, templates
from app.projects.models.project import Project
from app.pipelines.models.actions_utils import TABLE_ACTION_REGISTRY
from app.utils.form_utils import squirrel_error, squirrel_action_error, _get_form_data_info
from app.pipelines.models.pipeline import Pipeline
from app.pipelines.models.pipeline_action import PipelineAction
from app.tables.models.table_manager import TableManager


@router.get("/tables/")
@squirrel_error
async def tables(request: Request, project_dir: str):
    exception = False
    tables = {}
    try:
        pipeline = Pipeline(project_dir)
        tables = await pipeline.run_pipeline()
    except Exception as e:
        exception = e
        table_html = {}
        table_len_infos = {}
    finally:
        if not exception:
            tables.save_tables()
            table_html, table_len_infos = tables.to_html()

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
    table_manager = TableManager.load_tables(project_dir)
    if not table_manager:
        pipeline = Pipeline(project_dir)
        table_manager = await pipeline.run_pipeline()
    table = table_manager.tables.get(table_name)
    start = page * n
    end = start + n
    table_html = table.to_html(table_manager.display_len, start=start, end=end)
    return table_html

@router.post("/tables/add_action/")
@squirrel_action_error
async def add_action(request: Request):
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
    ActionClass = TABLE_ACTION_REGISTRY.get(action_name)
    if not ActionClass:
        raise ValueError(f"Action {action_name} not found")

    action_instance = ActionClass({})
    args = await action_instance.get_args(kwargs={"project_dir": project_dir})

    return args

@router.get("/tables/column_infos/")
@squirrel_error
async def get_col_infos(request: Request, project_dir: str, table: str, column_name: str, column_idx: str):
    table_manager = TableManager.load_tables(project_dir)
    if not table_manager:
        pipeline = Pipeline(project_dir)
        table_manager = await pipeline.run_pipeline()
    col_infos = table_manager.get_col_info(table, column_idx)

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
