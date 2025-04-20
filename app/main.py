from fastapi import Request
from fastapi.responses import RedirectResponse

from app import app, templates
from app.utils.error_handling import squirrel_error


@app.get("/")
@squirrel_error
async def read_root(request: Request):
    """
    This returns to projects's homepage
    """
    return RedirectResponse("/projects/")

@app.get("/app/settings/")
@squirrel_error
async def app_settings(request: Request):
    """
    Display the application settings

    * request

    => Returns a TemplateResponse to display application settings (empty for now)
    """
    return templates.TemplateResponse(request, "utils/templates/app_settings.html", {})
