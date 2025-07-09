from fastapi import Request
from fastapi.responses import RedirectResponse

from app import app
from app.utils.form_utils import squirrel_error


@app.get("/")
@squirrel_error
async def read_root(request: Request):
    """Redirects to the projects page"""
    return RedirectResponse("/projects/")
