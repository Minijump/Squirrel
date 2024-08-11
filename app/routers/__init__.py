from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()
router.mount("/../../static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
