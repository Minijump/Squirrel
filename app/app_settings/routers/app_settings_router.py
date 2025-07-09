from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

from app.utils.form_utils import squirrel_error

router = APIRouter()
templates = Jinja2Templates(directory="app")

@router.get("/app/settings/")
@squirrel_error
async def app_settings(request: Request):
    """Returns a TemplateResponse to display application settings"""
    return templates.TemplateResponse(request, "app_settings/templates/app_settings.html", {})
