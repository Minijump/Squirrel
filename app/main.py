from fastapi import Request
from fastapi.responses import RedirectResponse

import os
import json

from app import app, templates

from app.utils import PIPELINE_START_TAG, PIPELINE_END_TAG, NEW_CODE_TAG
BASIC_PIPELINE = """
import pandas as pd


def run_pipeline():
    dfs = {}
    
    %s
    %s
    %s

    return dfs
 """ % (PIPELINE_START_TAG, NEW_CODE_TAG, PIPELINE_END_TAG)


@app.get("/")
async def read_root(request: Request):
    """
    This returns the homepage of the application
    The homepage displays all the 'project' in the ./projects directory, 
    informations about a project are read from its manifest

    * request

    => Returns a TemplateResponse to display homepage
    """
    projects = []
    projects_path = os.path.join(os.getcwd(), "projects")

    for project in os.listdir(projects_path):
        manifest_path = os.path.join(projects_path, project, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
            projects.append(manifest_data)

    return templates.TemplateResponse(request, "homepage.html", {"projects": projects})
