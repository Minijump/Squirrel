import os
import tempfile
from unittest.mock import patch
import json

from fastapi.testclient import TestClient

from app.main import app
from tests import mock_project


client = TestClient(app)


def test_access_projects():
    """
    Test if the projects endpoint is accessible and contains projects
    """
    response = client.get("/projects/")
    assert response.status_code == 200, "Failed to access the projects endpoint"
    assert response.context.get("projects"), "Response does not contain projects"
    assert response.context.get("PROJECT_TYPE_REGISTRY"), "Response does not contain the project type registry"

def test_fail_access_projects():
    """
    Test the case when we fail to open projects page; 
    We must me redirected to projects' page, with a error message (exception)
    
    Error triggers: if os.getcwd = /this_is_not_a_valid_path, system won't find _projects folder
    """
    with patch('os.getcwd', return_value="/this_is_not_a_valid_path"):
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

def test_fail_open_project():
    response = client.get(f"/projects/open/?project_dir=not_existing_project_name")
    assert response.status_code == 200, "Failed deal with error while opening project"
    assert response.context.get("exception"), "Response does not contain an exception"

def test_create_project(temp_project_dir_fixture):
    """
    Test if project's directory, manifest and pipeline were created
    Test we are redirected to /tables/?project_dir={project_dir} enpoint
    """
    form_data = {
        "name": "Test Create Project", 
        "description": "This is a test for project creation",
        }
    project_name_dir = form_data['name'].lower().replace(" ", "_")
    response = client.post("/projects/create/", data=form_data)
    project_dir = os.path.join(os.getcwd(), "_projects", project_name_dir)

    assert os.path.exists(project_dir), "Failed to create project directory"
    assert os.path.exists(os.path.join(project_dir, "__manifest__.json")), "Failed to create project manifest"
    assert os.path.exists(os.path.join(project_dir, "pipeline.py")), "Failed to create project pipeline"

    assert str(response.url).endswith(f"/tables/?project_dir={project_name_dir}"), "Failed to redirect to project's page"

    response = client.get("/projects/")
    assert any(project['directory'] == project_name_dir for project in response.context.get("projects")), "New project is not available"

def test_fail_create_project(temp_project_dir_fixture):
    """
    Test if the error page is displayed when the project creation fails due to invalid project name
    """
    form_data = {
        "project_name": "''./\"''", 
        "project_description": "This is a test for project creation",
        }
    response = client.post("/projects/create/", data=form_data)
    assert response.status_code == 200, "Unexpected error while failing to create project"
    assert response.context.get("exception"), "Response does not contain an exception"

def test_access_project_settings(mock_project):
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
    """
    response = client.get(f"/project/settings/?project_dir=wrong_dir")
    assert response.status_code == 200, "Failed to access the project settings endpoint"
    assert response.context.get("exception"), "Response does not contain an exception"

def test_update_project_settings(temp_project_dir_fixture):
    """
    Test if the project settings are correctly updated
    """
    response = client.post(
        "/projects/create/", 
        data={"name": "Test Update Project Settings", "description": "This is a test for project settings update"}
    )

    form_data = {
        "project_dir": "test_update_project_settings",
        "name": "Test Update Project Settings; Updated",
    }
    response = client.post("/project/update_settings/", data=form_data)
    assert response.status_code == 200, "Failed to update project settings"

    manifest_data = json.load(open(os.path.join(os.getcwd(), "_projects", "test_update_project_settings", "__manifest__.json")))
    assert manifest_data['name'] == form_data['name'], "Failed to update project name"

def test_fail_update_project_settings(temp_project_dir_fixture):
    """
    Test if the error page is displayed when the project settings update fails due to invalid project name
    """
    response = client.post(
        "/projects/create/", 
        data={"name": "Test Fail Update Project Settings", "description": "This is a test for project settings update"}
    )

    form_data = {
        "project_dir": "test_fail_update_project_settings_wrong_dir",
    }
    response = client.post("/project/update_settings/", data=form_data)
    assert response.status_code == 200, "Failed to deal with error while updating project settings"
    assert response.context.get("exception"), "Response does not contain an exception"

def test_access_app_settings():
    """
    Test if the application settings endpoint is accessible
    """
    response = client.get("/app/settings/")
    assert response.status_code == 200, "Failed to access the application settings endpoint"
