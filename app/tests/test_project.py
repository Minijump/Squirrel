from fastapi.testclient import TestClient

import pandas as pd
import os
from unittest.mock import patch

from app.main import app
from app.tests import mock_project

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

def test_get_sources(mock_project):
    """
    Test if the get_sources function returns the correct sources
    """
    from app.tables.routers.tables import get_sources
    sources = get_sources(mock_project)
    expected_source = {
        "name": "Mock source csv",
        "type": "csv",
        "description": "a mock csv source",
        "directory": "mock_source_csv"
    }
    assert expected_source in sources, "Expected one mock source csv"

def test_project(mock_project):
    """
    Test if the project endpoint is accessible
    Test if the response contains a table and the correct project_dir
    """
    response = client.post("/project/?project_dir=" + mock_project)
    assert response.status_code == 200, "Failed to access the project endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

def test_fail_pipeline(mock_project):
    """
    Test if the project endpoint is accessible
    Test if in case of failing pipeline, page is displayed correctly
    """
    with patch("app.tables.load_pipeline_module") as mock_load_pipeline_module:
        mock_load_pipeline_module.side_effect = Exception("Mock exception")
        response = client.post("/project/?project_dir=" + mock_project)
        assert response.status_code == 200, "Failed to access the project endpoint"
        assert response.context.get("exception"), "Response does not contain an exception"

def test_add_del_column(mock_project):
    """
    Test if the add_column endpoint is accessible
    Test if the response contains a table and the correct project_dir
    Test that the new line was added in python file

    Test if the del_column endpoint is accessible
    Test if the response contains a table and the correct project_dir
    Test that the new line was added in python file
    """
    # Test add_column
    response = client.post("/project/add_column", data={"col_name": "test_add_del_column", "col_value": "1", 'project_dir': mock_project, "table_name": "df"})
    assert response.status_code == 200, "Failed to access the add_column endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

    pipeline_path = os.path.join(mock_project, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        assert any("dfs['df']['test_add_del_column'] = 1" in line for line in lines), "Column not added to pipeline"

    # Test del_column
    response = client.post("/project/del_column", data={"col_name": "test_add_del_column", 'project_dir': mock_project, "table_name": "df"})
    assert response.status_code == 200, "Failed to access the del_column endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

    pipeline_path = os.path.join(mock_project, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        assert any("dfs['df'] = dfs['df'].drop(columns=['test_add_del_column'])" in line for line in lines), "Column not removed from pipeline"

def test_create_table_from_csv(mock_project):
    """
    For the creation of a table from a csv:
    Test if the create_table endpoint is accessible and response contains the correct project_dir
    Test that the new line was added in python file
    Test if response contains a Table, with the correct columns
    """ 
    response = client.post("/project/create_table", data={"data_source_dir": "mock_source_csv", 'project_dir': mock_project, "table_name": "df"})
    assert response.status_code == 200, "Failed to access the create_table endpoint"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

    pipeline_path = os.path.join(mock_project, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        assert any("dfs['df'] = pd.read_csv(" in line for line in lines), "Table not created in pipeline"

    assert response.context.get("table"), "Response does not contain a table"
    assert "mock_name" in response.context.get("table")['df'], "Table 'df' should contain a 'mock_name' column"
    assert "mock_price" in response.context.get("table")['df'], "Table 'df' should contain a 'mock_price' column"
