import json
import os
import tempfile
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from tests import mock_project


client = TestClient(app)


def test_data_sources(mock_project):
    """
    Test if the data_sources endpoint is accessible
    Test if the response contains the correct sources
    """
    response = client.get("/data_sources/?project_dir="+mock_project,)
    assert response.status_code == 200, "Failed to access the data_sources endpoint"

    expected_source = {
        "name": "Mock source csv",
        "type": "csv",
        "description": "a mock csv source",
        "directory": "mock_source_csv"
    }
    assert expected_source in response.context.get("sources"), "Expected one mock source csv"
    
def test_fail_data_source_creation(mock_project):
    """
    Test if in case of a failing source creation, page is displayed correctly
    """
    form_data = {
        "source_name": "Other arguments are missing=> will raise an error", 
        }
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/create_source/", data=form_data)
            assert response.status_code == 200, "Unexpected error while failing to create data source"
            assert response.context.get("exception"), "Response does not contain an exception"

def test_source_settings(mock_project): 
    """
    Test if the source_settings endpoint is accessible
    Test if the response contains the correct source
    """
    response = client.get("/source/settings?project_dir="+mock_project+"&source_dir=mock_source_csv")
    assert response.status_code == 200, "Failed to access the source_settings endpoint"

    expected_source = {
        "name": "Mock source csv",
        "type": "csv",
        "description": "a mock csv source",
        "directory": "mock_source_csv"
    }
    assert response.context.get("source") == expected_source, "Expected one mock source csv"

def test_fail_source_settings(mock_project):
    """
    Test if in case of a failing source settings, page is displayed correctly
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.get("/source/settings?project_dir="+mock_project+"&source_dir=non_existing")
            assert response.status_code == 200, "Failed to access the source_settings endpoint"
            assert response.context.get("exception"), "Response does not contain an exception"

def test_update_source_settings(mock_project):
    """
    Test if the update_source_settings endpoint is accessible
    """
    form_data = {
        "project_dir": mock_project,
        "source_dir": "mock_source_csv",
        "name": "Mock source csv, new name",
        "source_type": "csv",
        "description": "a mock csv source, new description",
        "arg_not_in_manifest": "test_update_settings"
    }
    response = client.post("/source/update_settings", data=form_data)
    assert response.status_code == 200, "Failed to access the update_source_settings endpoint"

    mock_manifest_path = os.path.join(os.getcwd(), "_projects", mock_project, "data_sources", "mock_source_csv", "__manifest__.json")
    with open(mock_manifest_path, 'r') as file:
        mock_manifest_data = json.load(file)
    assert mock_manifest_data["name"] == form_data['name'], "Name was not updated"
    assert mock_manifest_data["description"] == form_data['description'], "Description was not updated"
    assert "arg_not_in_manifest" not in mock_manifest_data, "arg_not_in_manifest should not have been added into manifest"

def test_fail_update_source_settings(mock_project):
    """
    Test if in case of a failing update source settings, page is displayed correctly
    """
    form_data = {
        "project_dir": mock_project,
        "source_dir": "non_existing",
        "name": "Not existing source",
        "source_type": "csv",
        "description": "Should raise an error, source does not exist",
    }
    response = client.post("/source/update_settings", data=form_data)
    assert response.status_code == 200, "Failed to access the update_source_settings endpoint"
    assert response.context.get("exception"), "Response does not contain an exception"

def test_sync_source(mock_project):
    """
    Test if the sync_source endpoint is accessible
    """
    form_data = {
        "project_dir": mock_project,
        "source_dir": "mock_source_csv"
    }
    response = client.post("/source/sync", data=form_data)
    assert response.status_code == 200, "Failed to access the sync_source endpoint"
