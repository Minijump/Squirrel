from fastapi import FastAPI, Request
from app import templates
import traceback
from functools import wraps

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
