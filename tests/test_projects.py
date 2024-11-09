from fastapi.testclient import TestClient

import os
import tempfile
from unittest.mock import patch
import json
import pytest

from app.main import app
from tests import mock_project

from app.projects.models.project import Project, BASIC_PIPELINE

client = TestClient(app)

# Test models
#----------------------------------------------------------------------------------
@pytest.mark.asyncio()
async def test_create_project_directory():
    """
    Test if the project directory is created
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project = Project("Test Create Project Directory", "This is a test for project directory creation")
            await project._create_project_directory()
            assert os.path.exists(project.path), "Failed to create project directory"

@pytest.mark.asyncio()
async def test_create_pipeline_file():
    """
    Test if the pipeline file is created
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project = Project("Test Create Pipeline File", "This is a test for pipeline creation")
            await project._create_project_directory()
            await project._create_pipeline_file()
            assert os.path.exists(os.path.join(project.path, "pipeline.py")), "Failed to create project pipeline"
            assert BASIC_PIPELINE in open(os.path.join(project.path, "pipeline.py")).read(), "Failed to create project pipeline with the correct content"

@pytest.mark.asyncio()
async def test_create_data_sources_directory():
    """
    Test if the data_sources directory is created
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project = Project("Test Create Data Sources Dir", "This is a test for data_sources creation")
            await project._create_project_directory()
            await project._create_data_sources_directory()
            assert os.path.exists(os.path.join(project.path, "data_sources")), "Failed to create project data_sources directory"

@pytest.mark.asyncio()
async def test_create_manifest():
    """
    Test if the manifest file is correctly created
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project = Project("Test Create Manifest File", "This is a test for manifest creation")
            await project._create_project_directory()
            await project._create_manifest()
            assert os.path.exists(os.path.join(project.path, "__manifest__.json")), "Failed to create project manifest"
            assert {
                "name": project.name,
                "description": project.description,
                "directory": project.directory
            } == json.load(open(os.path.join(project.path, "__manifest__.json"))), "Failed to create project manifest with the correct content"


# Test routers
#----------------------------------------------------------------------------------
def test_projects():
    """
    Test if the projects endpoint is accessible and contains projects
    """
    response = client.get("/projects/")
    assert response.status_code == 200, "Failed to access the projects endpoint"
    assert response.context.get("projects"), "Response does not contain projects"

def test_fail_access_projects():
    """
    Test the case when we fail to open a project; 
    We must me redirected to projects' page, with a error message (exception)
    
    Error triggers: if os.getcwd = /../.., system won't find _projects folder
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value="/../.."):
            response = client.get("/projects/")
            assert response.status_code == 200, "Failed to access the projects endpoint"
            assert response.context.get("exception"), "Response does not contain an exception"

def test_open_project(mock_project):
    """
    Test if the open_project endpoint is accessible 
    Contains a table, the project_dir and is redirected to table endpoint
    """
    response = client.get(f"/projects/open/?project_dir={mock_project}")
    assert response.status_code == 200, "Failed to access the open_project endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"
    assert "/tables/?project_dir=" in str(response.url), "Failed to redirect to table's page"

def test_create_project():
    """
    Test if project's directory, manifest and pipeline were created
    Test we are redirected to /tables/?project_dir={project_dir} enpoint
    """
    form_data = {
        "project_name": "Test Create Project", 
        "project_description": "This is a test for project creation",
        }
    project_name_dir = form_data['project_name'].lower().replace(" ", "_")
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/projects/create/", data=form_data)
            project_dir = os.path.join(temp_dir, "_projects", project_name_dir)

            assert os.path.exists(project_dir), "Failed to create project directory"
            assert os.path.exists(os.path.join(project_dir, "__manifest__.json")), "Failed to create project manifest"
            assert os.path.exists(os.path.join(project_dir, "pipeline.py")), "Failed to create project pipeline"

            assert str(response.url).endswith(f"/tables/?project_dir={project_name_dir}"), "Failed to redirect to project's page"

            response = client.get("/projects/")
            assert response.context.get("projects"), "Response does not contain projects"
            assert any(project['directory'] == project_name_dir for project in response.context.get("projects")), "New project does not appear in root page"

def test_fail_create_project():
    """
    Test if the error page is displayed when the project creation fails due to invalid project name
    """
    form_data = {
        "project_name": "''./\"''", 
        "project_description": "This is a test for project creation",
        }
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/projects/create/", data=form_data)
            assert response.status_code == 200, "Unexpected error while failing to create project"
            assert response.context.get("exception"), "Response does not contain an exception"

