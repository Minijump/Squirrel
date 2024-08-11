from fastapi.testclient import TestClient

from app.main import app
from app.tests import mock_project

client = TestClient(app)

def test_get_home_page():
    """
    Test if the homepage is accessible
    """
    response = client.get("/")
    assert response.status_code == 200, "Failed to access the homepage"

def test_open_project(mock_project):
    """
    Test if the open_project endpoint is accessible
    Test if the response contains a table
    """
    form_data = {"project_directory": mock_project}
    response = client.post("/open_project/", data=form_data)
    assert response.status_code == 200, "Failed to access the open_project endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"
