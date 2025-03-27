import os
import tempfile
from unittest.mock import patch
import json

from fastapi.testclient import TestClient

from app.main import app
from app.projects.models import Project, BASIC_PIPELINE, PROJECT_TYPE_REGISTRY
from tests import mock_project

client = TestClient(app)

# Test routers
#----------------------------------------------------------------------------------
def test_projects():
    """
    Test if the projects endpoint is accessible and contains projects
    """
    response = client.get("/projects/")
    assert response.status_code == 200, "Failed to access the projects endpoint"
    assert response.context.get("projects"), "Response does not contain projects"
    assert response.context.get("PROJECT_TYPE_REGISTRY"), "Response does not contain the project type registry"

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
        "name": "Test Create Project", 
        "description": "This is a test for project creation",
        }
    project_name_dir = form_data['name'].lower().replace(" ", "_")
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

def test_project_settings(mock_project):
    """
    Test if the project settings endpoint is accessible
    Contains the project's manifest and project_dir
    """
    response = client.get(f"/project/settings/?project_dir={mock_project}")
    assert response.status_code == 200, "Failed to access the project settings endpoint"
    assert response.context.get("project"), "Response does not contain the project infos (manifest data)"
    assert response.context.get("project")['directory'] == 'mock_project', "Response does not contain the correct project"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

def test_fail_access_project_settings():
    """
    Test the case when we fail to open a project; 
    We must me redirected to project's page, with a error message (exception)
    
    Error triggers: if os.getcwd = /../.., system won't find _projects folder
    """
    response = client.get(f"/project/settings/?project_dir=wrong_dir")
    assert response.status_code == 200, "Failed to access the project settings endpoint"
    assert response.context.get("exception"), "Response does not contain an exception"

def test_update_project_settings():
    """
    Test if the project settings are correctly updated
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/projects/create/", data={"name": "Test Update Project Settings", "description": "This is a test for project settings update"})

            form_data = {
                "project_dir": "test_update_project_settings",
                "name": "Test Update Project Settings; Updated",
            }
            response = client.post("/project/update_settings/", data=form_data)
            assert response.status_code == 200, "Failed to update project settings"

            manifest_data = json.load(open(os.path.join(temp_dir, "_projects", "test_update_project_settings", "__manifest__.json")))
            assert manifest_data['name'] == form_data['name'], "Failed to update project name"

def test_fail_update_project_settings():
    """
    Test if the error page is displayed when the project settings update fails due to invalid project name
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/projects/create/", data={"name": "Test Fail Update Project Settings", "description": "This is a test for project settings update"})

            form_data = {
                "project_dir": "test_fail_update_project_settings_wrong_dir",
            }
            response = client.post("/project/update_settings/", data=form_data)
            assert response.status_code == 200, "Failed to update project settings"
            assert response.context.get("exception"), "Response does not contain an exception"
