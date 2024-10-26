from fastapi.testclient import TestClient

import os
import tempfile
from unittest.mock import patch

from app.main import app
from app.tests import mock_project

client = TestClient(app)

def test_open_project(mock_project):
    """
    Test if the open_project endpoint is accessible
    Test if the response contains a table
    """
    form_data = {"project_dir": mock_project}
    response = client.post("/projects/open/", data=form_data)
    assert response.status_code == 200, "Failed to access the open_project endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

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
            project_dir = os.path.join(temp_dir, "projects", project_name_dir)

            assert os.path.exists(project_dir), "Failed to create project directory"
            assert os.path.exists(os.path.join(project_dir, "__manifest__.json")), "Failed to create project manifest"
            assert os.path.exists(os.path.join(project_dir, "pipeline.py")), "Failed to create project pipeline"

            assert str(response.url).endswith(f"/tables/?project_dir={project_name_dir}"), "Failed to redirect to project's page"

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
