from functools import wraps
import traceback
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from app import templates


app = FastAPI()


def squirrel_error(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        try:
            return await func(request, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            form_data = await request.form()
            project_dir = form_data.get("project_dir")
            template_path = "utils/templates/tables_error.html" if project_dir else "utils/templates/projects_error.html"
            additional_context = {"exception": str(e), "project_dir": project_dir} if project_dir else {"exception": str(e)}
            return templates.TemplateResponse(request, template_path, additional_context)
    return wrapper

def squirrel_action_error(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        try:
            return await func(request, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            form_data = await request.form()
            project_dir = form_data.get("project_dir")
            notification_param = quote(str(e))
            url = f"/tables/?project_dir={project_dir}&notification={notification_param}"
            return RedirectResponse(url=url, status_code=303)
    return wrapper

async def _get_form_data_info(request: Request, args_list: list):
    form_data = await request.form()
    return (form_data.get(arg) for arg in args_list)
