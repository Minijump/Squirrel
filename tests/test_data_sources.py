from fastapi.testclient import TestClient

import pandas as pd
import os
import tempfile
from unittest.mock import patch

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
