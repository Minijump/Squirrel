from fastapi import Request
from fastapi.responses import RedirectResponse

from app import app, templates
from app.utils.form_utils import squirrel_error


@app.get("/")
@squirrel_error
async def read_root(request: Request):
    """Redirects to the projects page"""
    return RedirectResponse("/projects/")

@app.get("/app/settings/")
@squirrel_error
async def app_settings(request: Request):
    """Returns a TemplateResponse to display application settings"""
    return templates.TemplateResponse(request, "utils/templates/app_settings.html", {})
