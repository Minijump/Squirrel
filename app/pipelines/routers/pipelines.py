from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from app import router, templates
from app.utils.error_handling import squirrel_error
from app.pipelines.models.pipeline import Pipeline


@router.get("/pipeline/")
@squirrel_error
async def pipeline(request: Request, project_dir: str):
    """
    Display the pipeline of the project

    * request
    * project_dir(str): The project directory

    => Returns a TemplateResponse that displays the pipeline; 
    the actions are displayed with their squirrel name if they have one
    """
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
    """
    Reorder the actions in the pipeline, edit the python file

    * request
    * project_dir(str): The project directory
    * order(str): The new order of the actions; "0-item,1-item,..."

    => Returns a JSONResponse if OK
    """
    pipeline = Pipeline(project_dir)
    await pipeline.confirm_new_order(order)

    return JSONResponse(content={"message": "Order changed successfully"}, status_code=200)

@router.post("/pipeline/edit_action/")
@squirrel_error
async def edit_action(request: Request):
    """
    Edit the code of an action in the pipeline

    * request contains:
       -action_id(str): The id of the action to edit
       -action_code(str): The new code of the action
       -project_dir(str): The project directory

    => Returns a redirect response to /pipeline
    """
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
    """
    Remove an action from the pipeline

    * request
    * project_dir(str): The project directory
    * delete_action_id(int): The id of the action to delete

    => Returns a JSONResponse if OK
    """
    pipeline = Pipeline(project_dir)
    await pipeline.delete_action(delete_action_id)

    return JSONResponse(content={"message": "Action deleted successfully"}, status_code=200)
