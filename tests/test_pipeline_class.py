import os
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.pipelines.models.pipeline import Pipeline
from tests import MOCK_PROJECT


client = TestClient(app)


#  Test utils
@pytest.mark.asyncio
async def test_get_file_lines(temp_project_dir_fixture):
    """
    Test if the get_file_lines function returns the correct number of actions
    Test if their format is ok
    """
    from app.pipelines.models.pipeline_utils import get_file_lines
    pipeline_path = os.path.join(os.getcwd(), "_projects", MOCK_PROJECT, "pipeline.py")
    lines = await get_file_lines(pipeline_path)
    actions = [line for line in lines if isinstance(line, tuple)]
    assert len(actions) == 3, "File should contain 3 actions"
    assert len(actions[0]) == 2, "Actions should be a tuple with following structure: (action_id, action_line(s)))"


# Test pipeline class
def test_init_pipeline(temp_project_dir_fixture):
    """
    Test if the pipeline class is initialized correctly
    """
    pipeline = Pipeline(MOCK_PROJECT)
    assert pipeline.project_path == os.path.join(os.getcwd(), "_projects", MOCK_PROJECT), "Project path is not correct"
    assert pipeline.pipeline_path == os.path.join(pipeline.project_path, "pipeline.py"), "Pipeline path is not correct"

@pytest.mark.asyncio
async def test_get_actions(temp_project_dir_fixture):
    """
    Test if the get_actions function returns the correct number of actions
    Test if their format is ok
    """
    pipeline = Pipeline(MOCK_PROJECT)
    actions = await pipeline.get_actions()
    assert len(actions) == 3, "Should contain 3 actions"
    assert len(actions[0]) == 3, "Actions should be a tuple with following structure: (action_id, action_name, action_line(s)))"
    assert actions[0][0] == 0, "First action should have id 0"
    assert "Create table ordered from Csv ordered" in actions[0][1], "First action name is not the expected one"
    assert "dfs['ordered'] = pd.read_pickle" in actions[0][2], "First action code is not the expected one"

@pytest.mark.asyncio
async def test_confirm_new_order(temp_project_dir_fixture):
    """
    Test if the confirm_new_order function reorders the actions correctly
    """
    pipeline = Pipeline(MOCK_PROJECT)
    await pipeline.confirm_new_order("2-item,0-item,1-item")
    actions = await pipeline.get_actions()
    assert len(actions) == 3, "Should still contain 3 actions after reordering"
    assert "Add column ref + price on table random" in actions[0][1], "First action name is not the expected one after reordering"
    assert "Create table ordered from Csv ordered" in actions[1][1], "Second action name is not the expected one after reordering"
    assert "Create table random from Csv random" in actions[2][1], "Third action name is not the expected one after reordering"

@pytest.mark.asyncio
async def test_delete_action(temp_project_dir_fixture):
    """
    Test if the delete_action function removes the action correctly
    """
    pipeline = Pipeline(MOCK_PROJECT)
    await pipeline.delete_action(2)
    actions = await pipeline.get_actions()
    assert len(actions) == 2, "Should contain 2 actions after deleting one"
