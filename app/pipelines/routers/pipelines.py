from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from app import router, templates
from app.pipelines.models.pipeline import Pipeline
from app.utils.form_utils import squirrel_error


@router.get("/pipeline/")
@squirrel_error
async def pipeline(request: Request, project_dir: str):
    pipeline = Pipeline(project_dir)
    actions = pipeline.get_actions()
    
    return templates.TemplateResponse(
        request,
        "pipelines/templates/pipeline.html",
        {"actions": actions, "project_dir": project_dir}
    )

@router.post("/pipeline/confirm_new_order/")
@squirrel_error
async def confirm_new_order(request: Request, project_dir: str, order: str):
    pipeline = Pipeline(project_dir)
    pipeline.confirm_new_order(order)
    return JSONResponse(content={"message": "Order changed successfully"}, status_code=200)

@router.post("/pipeline/edit_action/")
@squirrel_error
async def edit_action(request: Request):
    form_data = await request.form()
    action_data = {key: value for key, value in form_data.items()}
    action_id = int(action_data.get("action_id"))
    project_dir = action_data.get("project_dir")

    pipeline = Pipeline(project_dir)
    pipeline.edit_action(action_id, action_data)

    return RedirectResponse(url=f"/pipeline?project_dir={project_dir}", status_code=303)

@router.get("/pipeline/get_action_data/")
@squirrel_error
async def get_action_data(request: Request, project_dir: str, action_id: int):
    pipeline = Pipeline(project_dir)
    action_data = pipeline.get_action_data(action_id)
    return action_data

@router.post("/pipeline/delete_action/")
@squirrel_error
async def delete_action(request: Request, project_dir: str, delete_action_id: int):
    pipeline = Pipeline(project_dir)
    pipeline.delete_action(delete_action_id)
    return JSONResponse(content={"message": "Action deleted successfully"}, status_code=200)
