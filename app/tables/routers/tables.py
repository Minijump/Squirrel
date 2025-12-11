from fastapi import Request
from fastapi.responses import FileResponse, RedirectResponse

from app import router, templates
from app.utils.form_utils import squirrel_error, squirrel_action_error, _get_form_data_info
from app.pipelines.models.pipeline import Pipeline
from app.pipelines.models.action_factory import ActionFactory
from app.tables.models.table_manager import TableManager


@router.get("/tables/")
@squirrel_error
async def tables(request: Request, project_dir: str):
    table_manager = await TableManager.init_from_project_dir(project_dir)
    table_html, table_len_infos = table_manager.to_html()
    sources = table_manager.project.get_sources()
    return templates.TemplateResponse(
        request,
        "tables/templates/tables.html",
        {"table": table_html, "table_len_infos": table_len_infos, "project_dir": project_dir, "sources": sources}
    )

@router.get("/tables/pager/")
@squirrel_error
async def tables_pager(request: Request, project_dir: str, table_name: str, page: int, n: int):
    table_manager = await TableManager.init_from_project_dir(project_dir, lazy=True)
    table_html = table_manager.tables.get(table_name).to_html(table_manager.display_len, page=page, n=n)
    return table_html

@router.post("/tables/add_action/")
@squirrel_action_error
async def add_action(request: Request):
    form_data = await request.form()
    project_dir = form_data.get("project_dir")

    action_instance = ActionFactory.init_action(form_data)
    Pipeline(project_dir).add_action(action_instance)

    return RedirectResponse(url=f"/tables/?project_dir={project_dir}", status_code=303)                

@router.get("/tables/get_action_args/")
async def get_action_args(request: Request, action_name: str, project_dir: str = None):
    action_instance = ActionFactory.init_action({"action_name": action_name})
    args = await action_instance.get_args(kwargs={"project_dir": project_dir})
    return args

@router.get("/tables/column_infos/")
@squirrel_error
async def get_col_infos(request: Request, project_dir: str, table: str, column_name: str, column_idx: str):
    table_manager = await TableManager.init_from_project_dir(project_dir, lazy=True)
    col_infos = table_manager.get_col_info(table, column_idx)
    return col_infos

@router.get("/tables/autocomplete_data/")
@squirrel_error
async def get_autocomplete_data(request: Request, project_dir: str):
    table_manager = await TableManager.init_from_project_dir(project_dir, lazy=True)
    autocomplete_data = {}
    for table_name, table in table_manager.tables.items():
        autocomplete_data[table_name] = list(table.content.columns)
    return autocomplete_data

@router.post("/tables/export_table/")
@squirrel_error
async def export_table(request: Request):
    table_name, export_type, project_dir = await _get_form_data_info(request, ["table_name", "export_type", "project_dir"])

    table_manager = await TableManager.init_from_project_dir(project_dir, lazy=True)
    export_path = table_manager.export_table(table_name, export_type)

    return FileResponse(export_path, filename=f"{table_name}.{export_type}")
