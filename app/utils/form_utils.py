from functools import wraps
import traceback
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from app import templates


app = FastAPI()

# Used in Unit Tests
SQUIRREL_ERROR_DECORATED = set()
SQUIRREL_ACTION_ERROR_DECORATED = set()

def squirrel_error(func):
    SQUIRREL_ERROR_DECORATED.add(func.__name__)
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        try:
            return await func(request, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            form_data = await request.form()
            project_dir = form_data.get("project_dir")
            if project_dir:
                return templates.TemplateResponse(
                    request, 
                    "utils/templates/tables_error.html",
                    {"exception": str(e), "project_dir": project_dir})
            else:
                return templates.TemplateResponse(
                    request, 
                    "utils/templates/projects_error.html", 
                    {"exception": str(e)})
    return wrapper

def squirrel_action_error(func):
    SQUIRREL_ACTION_ERROR_DECORATED.add(func.__name__)
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        try:
            return await func(request, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            form_data = await request.form()
            project_dir = form_data.get("project_dir")
            if project_dir:
                error_message = str(e)
                notification_param = quote(error_message)
                return RedirectResponse(url=f"/tables/?project_dir={project_dir}&notification={notification_param}", status_code=303)
            else:
                return templates.TemplateResponse(
                    request, 
                    "utils/templates/projects_error.html", 
                    {"exception": str(e)})
    return wrapper

async def _get_form_data_info(request: Request, args_list: list):
    form_data = await request.form()
    return (form_data.get(arg) for arg in args_list)
