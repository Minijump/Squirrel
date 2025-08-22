import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.pipelines.models.pipeline import Pipeline
from tests import MOCK_PROJECT


client = TestClient(app)


def test_get_actions(temp_project_dir_fixture):
    pipeline = Pipeline(MOCK_PROJECT)

    actions = pipeline.get_actions()

    assert len(actions) > 0, "Should contain actions"
    assert type(actions[0]).__name__ == "PipelineAction", "Actions should be of type PipelineAction"

def test_get_action_data(temp_project_dir_fixture):
    pipeline = Pipeline(MOCK_PROJECT)

    action = pipeline.get_action_data(0)

    assert action['table_name'] == 'ordered', "Should contain  actions"

def test_confirm_new_order(temp_project_dir_fixture):
    pipeline = Pipeline(MOCK_PROJECT)

    pipeline.confirm_new_order("2-item,0-item,1-item")

    actions = pipeline.actions
    assert len(actions) == 3, "Should still contain 3 actions after reordering"
    assert actions[0].action.__class__.__name__ == "AddColumn", "First action should now be a 'AddColumn' action"

def test_edit_action(temp_project_dir_fixture):
    pipeline = Pipeline(MOCK_PROJECT)

    pipeline.edit_action(0, {"table_name": "updated"})

    action = pipeline.get_action_data(0)
    assert action['table_name'] == 'updated', "Should contain updated action"

def test_delete_action(temp_project_dir_fixture):
    pipeline = Pipeline(MOCK_PROJECT)

    pipeline.delete_action(2)

    actions = pipeline.actions
    assert len(actions) == 2, "Should contain 2 actions after deleting one"

def test_add_action(temp_project_dir_fixture):
    pipeline = Pipeline(MOCK_PROJECT)
    from app.tables.models.actions import AddColumn
    from app.pipelines.models.pipeline_action import PipelineAction
    action_3 = AddColumn(
        {
            "col_name": "price (copy)",
            "value_type": "python",
            "table_name": "random",
            "col_value": "'price'"
        }
    )
    pipeline_action_3 = PipelineAction(pipeline, action_3)

    pipeline.add_action(pipeline_action_3)

    actions = pipeline.actions
    assert len(actions) == 4, "Should contain 4 actions after adding one"
    assert actions[-1].action.__class__.__name__ == "AddColumn", "Last action should be a 'AddColumn' action"

@pytest.mark.asyncio
async def test_run_pipeline(temp_project_dir_fixture):
    pipeline = Pipeline(MOCK_PROJECT)

    tables = await pipeline.run_pipeline()

    assert tables is not None, "Should return tables"
    assert isinstance(tables, dict), "Should return a dict of tables"
    assert tables.get("ordered") is not None, "Should contain 'ordered' table"
