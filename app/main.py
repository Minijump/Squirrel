from fastapi import Request
from fastapi.responses import RedirectResponse

from app import app


@app.get("/")
async def read_root(request: Request):
    """
    This returns to projects's homepage
    """
    return RedirectResponse("/projects/")
