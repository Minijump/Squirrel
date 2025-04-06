from fastapi.testclient import TestClient

import os

from app.main import app
from tests import mock_project
import pytest

client = TestClient(app)

@pytest.mark.asyncio()
async def test_get_file_lines(mock_project):
    """
    Test if the get_file_lines function returns the correct number of actions
    Test if their format is ok
    """
    from app.pipelines.models.pipeline_utils import get_file_lines
    pipeline_path = os.path.join(mock_project, "pipeline.py")
    lines = await get_file_lines(pipeline_path)
    actions = [line for line in lines if isinstance(line, tuple)]
    assert len(actions) == 2, "File should contain 2 actions"
    assert len(actions[0]) == 2, "Actions should be a tuple with following structure: (action_id, action_line(s)))"

def test_pipeline(mock_project):
    """
    Test if the pipeline endpoint is accessible
    Test if the response contains 2 actions (mock_project contains 2 actions)
    """
    response = client.get("/pipeline/?project_dir="+ mock_project)
    assert response.status_code == 200, "Failed to access the pipeline endpoint"
    assert len(response.context.get("actions")) == 2, "Response does not contain 2 actions"

def test_fail_access_pipeline():
    """
    Test if error in pipeline enpoint is correctly managed
    """
    incorrect_project_dir = "incorrect_project_dir"
    response = client.get("/pipeline/?project_dir="+ incorrect_project_dir)  
    assert response.status_code == 200, "Failed to redirect to correct page in case of failing to access pipeline"
    assert response.context.get("exception"), "Missing exception"

def test_delete_action(mock_project):
    """
    Test initial state (2 actions)
    Test if the delete_action endpoint is accessible
    Test if the action was deleted in python file
    """
    before_delete_response = client.get("/pipeline/?project_dir="+ mock_project)
    assert len(before_delete_response.context.get("actions")) == 2, "Response should contains 2 actions before deletion"

    response = client.post("/pipeline/delete_action/?project_dir="+ mock_project + "&delete_action_id=0")
    assert response.status_code == 200, "Failed to access the delete_action endpoint"

    after_delete_response = client.get("/pipeline/?project_dir="+ mock_project)
    assert len(after_delete_response.context.get("actions")) == 1, "Response should contains only 1 action after deletion"

def test_confirm_new_order(mock_project):
    """
    Test initial state (action2 should be after action1)
    Test if the confirm_new_order endpoint is accessible
    Test if the actions were reordered in python file
    """
    pipeline_path = os.path.join("_projects", mock_project, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        action2_line_id = [i for i, line in enumerate(lines) if 'sq_action: action2' in line][0]
        action1_line_id = [i for i, line in enumerate(lines) if 'sq_action: action1' in line][0]
        assert action2_line_id > action1_line_id, "Initial state: action2 should be after action1"

    response = client.post("/pipeline/confirm_new_order/?project_dir="+ mock_project + "&order=1-item,0-item")
    assert response.status_code == 200, "Failed to access the confirm_new_order endpoint"

    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        action2_line_id = [i for i, line in enumerate(lines) if 'sq_action: action2' in line][0]
        action1_line_id = [i for i, line in enumerate(lines) if 'sq_action: action1' in line][0]
        assert action2_line_id < action1_line_id, "Actions should have been reordered"

def test_edit_action(mock_project):
    """
    Test initial state (action1 = dfs['df']['action1'] = 1  #sq_action: action1)
    Test if the edit_action endpoint is accessible
    Test if the action was edited in python file
    """
    pipeline_path = os.path.join("_projects", mock_project, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        action1_line = [line for line in lines if 'sq_action: action1' in line][0]
        assert action1_line == "    dfs['df']['action1'] = 1  #sq_action: action1\n", "Initial state should be: action1 = dfs['df']['action1'] = 1  #sq_action: action1"

    form_data = {
        "action_id": "0",
        "action_code": "    dfs['df']['action1'] = 2  #sq_action: action1\n",
        "project_dir": mock_project
    }
    response = client.post("/pipeline/edit_action/", data=form_data)
    assert response.status_code == 200, "Failed to access the edit_action endpoint"

    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        action1_line = [line for line in lines if 'sq_action: action1' in line][0]
        assert action1_line == "    dfs['df']['action1'] = 2  #sq_action: action1\n", "Action should have been edited"
