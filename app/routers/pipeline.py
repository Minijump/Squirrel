from fastapi import Request
from fastapi.responses import JSONResponse

import os
import nbformat as nbf
from nbconvert import HTMLExporter

from app.routers import router, templates
from app.utils import PIPELINE_START_TAG, PIPELINE_END_TAG, NEW_CODE_TAG

#TODO: add edit functionality
#TODO: list of actions (notebook cell), name, deal with multiple lines action, ...
#TODO: add drag and drop of actions (buttons up, buttons down?)

@router.post("/pipeline")
@router.get("/pipeline")
async def pipeline(request: Request, project_dir: str):
    """
    Display the pipeline of the project
    """
    pipeline_path = os.path.join("projects", project_dir, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        actions = []
        in_pipeline = False
        action_id = 0
        for line in file.readlines():
            if PIPELINE_START_TAG in line:
                in_pipeline = True
                continue
            elif PIPELINE_END_TAG in line:
                in_pipeline = False
                break
            elif in_pipeline and NEW_CODE_TAG not in line and line.strip() != "":
                actions.append((action_id, line))
                action_id += 1
       
    return templates.TemplateResponse(
        request,
        "pipeline.html",
        {"actions": actions, "project_dir": project_dir}
    )

@router.post("/pipeline/delete_action")
@router.get("/pipeline/delete_action")
async def delete_action(request: Request, project_dir: str, delete_action_id: int):
    """
    Delete an action from the pipeline
    """
    pipeline_path = os.path.join("projects", project_dir, "pipeline.py")
    new_lines = []
    with open(pipeline_path, 'r') as file:
        in_pipeline = False
        action_id = 0
        for line in file.readlines():          
            if PIPELINE_START_TAG in line:
                new_lines.append(line)
                in_pipeline = True
            elif PIPELINE_END_TAG in line:
                new_lines.append(line)
                in_pipeline = False
            elif in_pipeline and NEW_CODE_TAG not in line and line.strip() != "":
                if action_id != delete_action_id:
                    new_lines.append(line)
                action_id += 1
            else:
                new_lines.append(line)
    with open(pipeline_path, 'w') as file:
        file.writelines(new_lines)

    return JSONResponse(content={"message": "Action deleted successfully"}, status_code=200)
