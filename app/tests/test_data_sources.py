from fastapi.testclient import TestClient

import pandas as pd
import os
from unittest.mock import patch

from app.main import app
from app.tests import mock_project

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
