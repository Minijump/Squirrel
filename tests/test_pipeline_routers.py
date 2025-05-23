import os

from fastapi.testclient import TestClient

from app.main import app
from tests import MOCK_PROJECT


client = TestClient(app)


def test_pipeline(temp_project_dir_fixture):
    """
    Test if the pipeline endpoint is accessible
    Test if the response contains 2 actions (Mock project contains 2 actions)
    """
    response = client.get("/pipeline/?project_dir="+ MOCK_PROJECT)
    assert response.status_code == 200, "Failed to access the pipeline endpoint"
    assert len(response.context.get("actions")) == 3, "Response does not contain 3 actions"

def test_confirm_new_order(temp_project_dir_fixture):
    """
    Test initial state (action2 should be after action1)
    Test if the confirm_new_order endpoint is accessible
    Test if the actions were reordered in python file
    """
    pipeline_path = os.path.join(os.getcwd() ,"_projects", MOCK_PROJECT, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        action2_line_id = [i for i, line in enumerate(lines) if 'sq_action:Create table random from Csv random' in line][0]
        action1_line_id = [i for i, line in enumerate(lines) if 'sq_action:Create table ordered from Csv ordered' in line][0]
        assert action2_line_id > action1_line_id, "Initial state: ordered table chould be created first"

    response = client.post("/pipeline/confirm_new_order/?project_dir="+ MOCK_PROJECT + "&order=1-item,0-item,2-item")
    assert response.status_code == 200, "Failed to access the confirm_new_order endpoint"

    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        action2_line_id = [i for i, line in enumerate(lines) if 'sq_action:Create table random from Csv random' in line][0]
        action1_line_id = [i for i, line in enumerate(lines) if 'sq_action:Create table ordered from Csv ordered' in line][0]
        assert action2_line_id < action1_line_id, "Actions should have been reordered"

def test_edit_action(temp_project_dir_fixture):
    """
    Test if the edit_action endpoint is accessible
    Test if the action was edited in python file
    """
    pipeline_path = os.path.join(os.getcwd(), "_projects", MOCK_PROJECT, "pipeline.py")
    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        action_line = [line for line in lines if 'sq_action:Add column ref + price on table random' in line][0]
        assert "dfs['random']['ref + price'] = dfs['random']['reference'] + dfs['random']['price']" in action_line, "Initial state is incorect"

    form_data = {
        "action_id": "0",
        "action_code": "    dfs['random']['ref + price'] = dfs['random']['reference'] + 2* dfs['random']['price']  #sq_action:Add column ref + 2 * price on table random\n",
        "project_dir": MOCK_PROJECT,
    }
    response = client.post("/pipeline/edit_action/", data=form_data)
    assert response.status_code == 200, "Failed to access the edit_action endpoint"

    with open(pipeline_path, 'r') as file:
        lines = file.readlines()
        action_line = [line for line in lines if 'sq_action:Add column ref + 2 * price on table random' in line][0]
        assert "dfs['random']['ref + price'] = dfs['random']['reference'] + 2* dfs['random']['price']" in action_line , "Action should have been edited"

def test_delete_action(temp_project_dir_fixture):
    """
    Test initial state (2 actions)
    Test if the delete_action endpoint is accessible
    Test if the action was deleted in python file
    """
    before_delete_response = client.get("/pipeline/?project_dir="+ MOCK_PROJECT)
    assert len(before_delete_response.context.get("actions")) == 3, "Response should contains 3 actions before deletion"

    response = client.post("/pipeline/delete_action/?project_dir="+ MOCK_PROJECT + "&delete_action_id=0")
    assert response.status_code == 200, "Failed to access the delete_action endpoint"

    after_delete_response = client.get("/pipeline/?project_dir="+ MOCK_PROJECT)
    assert len(after_delete_response.context.get("actions")) == 2, "Response should contains only 2 action after deletion"
