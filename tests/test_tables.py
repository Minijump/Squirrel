from fastapi.testclient import TestClient

import pandas as pd
import os
from unittest.mock import patch
import pytest

from app.main import app
from tests import mock_project

client = TestClient(app)


def test_load_pipeline_module(mock_project):
    """
    Test if pipeline is loaded correctly 
    Test wether the pipeline is 'runable'
    """
    from app.tables.routers.tables import load_pipeline_module
    pipeline = load_pipeline_module(mock_project)
    try:
        dfs = pipeline.run_pipeline()
    except Exception as e:
        raise AssertionError("Not able to run 'run_pipeline' from pipeline") from e
    # check that dfs is a dictionarry of dataframes
    assert isinstance(dfs, dict) and isinstance(dfs['df'], pd.DataFrame), "'run_pipeline' response should be a dictionary"

def test_tables(mock_project):
    """
    Test if the table endpoint is accessible
    Test if the response contains a table and the correct project_dir
    """
    response = client.get("/tables/?project_dir=" + mock_project)
    assert response.status_code == 200, "Failed to access the table endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

def test_fail_pipeline(mock_project):
    """
    Test if the table endpoint is accessible
    Test if in case of failing pipeline, page is displayed correctly
    """
    with patch("app.tables.load_pipeline_module") as mock_load_pipeline_module:
        mock_load_pipeline_module.side_effect = Exception("Mock exception")
        response = client.get("/tables/?project_dir=" + mock_project)
        assert response.status_code == 200, "Failed to access the table endpoint"
        assert response.context.get("exception"), "Response does not contain an exception"
