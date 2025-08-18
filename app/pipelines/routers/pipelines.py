from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from app import router, templates
from app.pipelines.models.pipeline import Pipeline
from app.utils.form_utils import squirrel_error, _get_form_data_info


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
    """Edit an action in the pipeline and RedirectResponse to the pipeline"""
    #TODO editaction: imp -------------------------------------------------------------------
    form_data = await request.form()
    action_id = int(form_data.get("action_id"))
    project_dir = form_data.get("project_dir")
    
    # Convert form data to dict, excluding system fields
    action_data = {}
    for key, value in form_data.items():
        if key not in ["action_id", "project_dir"]:
            action_data[key] = value

    pipeline = Pipeline(project_dir)
    await pipeline.edit_action(action_id, action_data)

    return RedirectResponse(url=f"/pipeline?project_dir={project_dir}", status_code=303)

@router.post("/pipeline/delete_action/")
@squirrel_error
async def delete_action(request: Request, project_dir: str, delete_action_id: int):
    """Remove an action from the pipeline + Returns a JSONResponse"""
    pipeline = Pipeline(project_dir)
    await pipeline.delete_action(delete_action_id)

    return JSONResponse(content={"message": "Action deleted successfully"}, status_code=200)
