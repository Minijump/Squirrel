from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

import os
import traceback

from app import router, templates
from utils import PIPELINE_START_TAG, PIPELINE_END_TAG, NEW_CODE_TAG

async def get_file_lines(file_path):
    """
    Returns the lines contained in the file at file_path

    * file_path(str): The path to the file

    => Returns a list of lines; if the line(s) is an action, it is represented as a tuple (action_id, line)
    """
    lines = []
    with open(file_path, 'r') as file:
        in_pipeline = False
        action_id = 0
        temp_action_lines = "" # Enables to deal with multi-line actions
        for line in file.readlines():
            if PIPELINE_START_TAG in line:
                lines.append(line)
                in_pipeline = True
            elif PIPELINE_END_TAG in line:
                lines.append(line)
                in_pipeline = False
            elif in_pipeline and NEW_CODE_TAG not in line and line.strip() != "":
                if "#sq_action:" not in line:
                    temp_action_lines += line
                    continue
                else:
                    temp_action_lines += line
                    lines.append((action_id, temp_action_lines))
                    temp_action_lines = ""
                    action_id += 1
            else:
                lines.append(line)
    return lines

@router.get("/pipeline")
async def pipeline(request: Request, project_dir: str):
    """
    Display the pipeline of the project

    * request
    * project_dir(str): The project directory

    => Returns a TemplateResponse that displays the pipeline; 
    the actions are displayed with their squirrel name if they have one
    """
    try:
        pipeline_path = os.path.join(os.getcwd(), "_projects", project_dir, "pipeline.py")
        lines = await get_file_lines(pipeline_path)

        actions = []
        for line in lines:
            if isinstance(line, tuple):
                if "#sq_action:" in line[1]:
                    actions.append((line[0], line[1].split("#sq_action:")[1].strip(), line[1]))
                else:
                    actions.append(line)
        
        return templates.TemplateResponse(
            request,
            "pipeline/pipeline.html",
            {"actions": actions, "project_dir": project_dir}
        )
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/tables_error.html", {"exception": str(e), "project_dir": project_dir})


@router.post("/pipeline/delete_action")
async def delete_action(request: Request, project_dir: str, delete_action_id: int):
    """
    Remove an action from the pipeline

    * request
    * project_dir(str): The project directory
    * delete_action_id(int): The id of the action to delete

    => Returns a JSONResponse if OK
    """
    try:
        pipeline_path = os.path.join(os.getcwd(), "_projects", project_dir, "pipeline.py")
        lines = await get_file_lines(pipeline_path)

        new_lines = []
        for line in lines:
            if not isinstance(line, tuple):
                new_lines.append(line)
            elif line[0] != delete_action_id:
                new_lines.append(line[1])

        with open(pipeline_path, 'w') as file:
            file.writelines(new_lines)

        return JSONResponse(content={"message": "Action deleted successfully"}, status_code=200)
    except Exception as e:
        # Not working
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/tables_error.html", {"exception": str(e), "project_dir": project_dir})

@router.post("/pipeline/confirm_new_order")
async def confirm_new_order(request: Request, project_dir: str, order: str):
    """
    Reorder the actions in the pipeline, edit the python file

    * request
    * project_dir(str): The project directory
    * order(str): The new order of the actions; "0-item,1-item,..."

    => Returns a JSONResponse if OK
    """
    try:
        pipeline_path = os.path.join(os.getcwd(), "_projects", project_dir, "pipeline.py")
        lines = await get_file_lines(pipeline_path)
        new_order = [int(action_str[0]) for action_str in order.split(",")] # the old ids in the new order
        old_actions = [line for line in lines if isinstance(line, tuple)]  # the actions in the old order
        new_lines = []
        action_id = 0
        for line in lines:
            if isinstance(line, tuple):
                id_of_old_order = new_order[action_id]  # Action that had id_of_old_order must now have action_id id
                new_line = old_actions[id_of_old_order][1]  # [1] because (action_id, line)
                new_lines.append(new_line)
                action_id += 1
            else:
                new_lines.append(line)

        with open(pipeline_path, 'w') as file:
            file.writelines(new_lines)

        return JSONResponse(content={"message": "Order changed successfully"}, status_code=200)
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/tables_error.html", {"exception": str(e), "project_dir": project_dir})

@router.post("/pipeline/edit_action")
async def edit_action(request: Request):
    """
    Edit the code of an action in the pipeline

    * request contains:
       -action_id(str): The id of the action to edit
       -action_code(str): The new code of the action
       -project_dir(str): The project directory

    => Returns a redirect response to /pipeline
    """
    try:
        form_data = await request.form()
        action_id = int(form_data["action_id"])
        action_code = form_data["action_code"].replace("\r\n", "\n") # Temp fix (for windows?), avoid a new empty line
        project_dir = form_data["project_dir"]

        pipeline_path = os.path.join(os.getcwd(), "_projects", project_dir, "pipeline.py")
        lines = await get_file_lines(pipeline_path)

        new_lines = []
        for line in lines:
            if isinstance(line, tuple):
                if line[0] == action_id:
                    new_lines.append(action_code)
                else:
                    new_lines.append(line[1])
            else:
                new_lines.append(line)
        
        with open(pipeline_path, 'w') as file:
            file.writelines(new_lines)

        return RedirectResponse(url=f"/pipeline?project_dir={project_dir}", status_code=303)
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(request, "base/html/tables_error.html", {"exception": str(e), "project_dir": project_dir})
