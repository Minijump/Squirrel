from fastapi.testclient import TestClient

import pandas as pd
import os

from app.main import app
from app.tests import mock_project

client = TestClient(app)


def test_load_pipeline_module(mock_project):
    """
    Test if pipeline is loaded correctly 
    Test wether the pipeline is 'runable'
    """
    from app.routers.project import load_pipeline_module
    pipeline = load_pipeline_module(mock_project)
    df = pipeline.run_pipeline()
    try:
        df = pipeline.run_pipeline()
    except Exception as e:
        raise AssertionError("Not able to run 'run_pipeline' from pipeline") from e
    assert isinstance(df, pd.DataFrame), "'run_pipeline' response should be a dataframe"

def test_project(mock_project):
    """
    Test if the project endpoint is accessible
    Test if the response contains a table and the correct project_dir
    """
    response = client.post("/project/?project_dir=" + mock_project)
    assert response.status_code == 200, "Failed to access the project endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

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
    response = client.post("/project/add_column", data={"col_name": "test_add_del_column", "col_value": "1", 'project_dir': mock_project})
    assert response.status_code == 200, "Failed to access the add_column endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

    pipeline_path = os.path.join(mock_project, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        assert any("df['test_add_del_column'] = 1" in line for line in lines), "Column not added to pipeline"

    # Test del_column
    response = client.post("/project/del_column", data={"col_name": "test_add_del_column", 'project_dir': mock_project})
    assert response.status_code == 200, "Failed to access the del_column endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

    pipeline_path = os.path.join(mock_project, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        assert any("df = df.drop(columns=['test_add_del_column'])" in line for line in lines), "Column not removed from pipeline"
