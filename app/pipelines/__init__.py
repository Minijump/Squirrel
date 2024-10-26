from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import logging
logging.basicConfig(level=logging.INFO)

from app.pipelines.routers import pipelines
