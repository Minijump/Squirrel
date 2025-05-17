from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from app import router, templates
from app.utils.error_handling import squirrel_error
from app.pipelines.models.pipeline import Pipeline


@router.get("/pipeline/")
@squirrel_error
async def pipeline(request: Request, project_dir: str):
    """ Returns a TemplateResponse that displays the pipeline"""
    pipeline = Pipeline(project_dir)
    actions = await pipeline.get_actions()
    
    return templates.TemplateResponse(
        request,
        "pipelines/templates/pipeline.html",
        {"actions": actions, "project_dir": project_dir}
    )

@router.post("/pipeline/confirm_new_order/")
@squirrel_error
async def confirm_new_order(request: Request, project_dir: str, order: str):
    """Reorder the actions in the pipeline + Returns a JSONResponse"""
    pipeline = Pipeline(project_dir)
    await pipeline.confirm_new_order(order)

    return JSONResponse(content={"message": "Order changed successfully"}, status_code=200)

@router.post("/pipeline/edit_action/")
@squirrel_error
async def edit_action(request: Request):
    """Edit the code of an action in the pipeline and RedirectResponse to the pipeline"""
    form_data = await request.form()
    action_id = int(form_data["action_id"])
    action_code = form_data["action_code"].replace("\r\n", "\n") # Temp fix (for windows?), avoid a new empty line
    project_dir = form_data["project_dir"]

    pipeline = Pipeline(project_dir)
    await pipeline.edit_action(action_id, action_code)

    return RedirectResponse(url=f"/pipeline?project_dir={project_dir}", status_code=303)

@router.post("/pipeline/delete_action/")
@squirrel_error
async def delete_action(request: Request, project_dir: str, delete_action_id: int):
    """Remove an action from the pipeline + Returns a JSONResponse"""
    pipeline = Pipeline(project_dir)
    await pipeline.delete_action(delete_action_id)

    return JSONResponse(content={"message": "Action deleted successfully"}, status_code=200)
