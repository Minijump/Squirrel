import os
import pytest
import warnings

from fastapi.testclient import TestClient

from app.main import app
from app.data_sources.models.data_source import DataSource
from tests import MOCK_PROJECT


client = TestClient(app)


def test_check_available_infos_with_additional_fields():
    """
    Test if the check_available_infos method is correctly implemented
    """
    infos = {
        "source_name": "Mock source",
        "source_type": "csv",
    }
    try:
        DataSource.check_available_infos(infos)
    except ValueError:
        pytest.fail("check_available_infos raised an error with required fields only")

    with pytest.raises(ValueError):
        DataSource.check_available_infos({}, additional_required_fields=["field1", "field2"])

    infos["field1"] = "value1"
    infos["field2"] = "value2"
    try:
        DataSource.check_available_infos(infos, additional_required_fields=["field1", "field2"])
    except ValueError:
        pytest.fail("check_available_infos raised an error with additional required fields")

def test_generate_manifest():
    """
    Test if the manifest is correctly generated
    """
    form_data = {
        "source_name": "Mock source",
        "source_type": "csv",
        "source_description": "a mock source"
    }
    manifest = DataSource._generate_manifest(form_data)
    assert manifest["name"] == "Mock source", "Expected name to be Mock source"
    assert manifest["type"] == "csv", "Expected type to be csv"
    assert manifest["description"] == "a mock source", "Expected description to be a mock source"
    assert manifest["directory"] == "Mock_source", "Expected directory to be Mock_source"

@pytest.mark.asyncio
async def test_create_source(temp_project_dir_fixture):
    """
    Test if the create_source_base method is correctly implemented
    """
    form_data = {
        "project_dir": MOCK_PROJECT,
        "source_name": "Mock source",
        "source_type": "std (no type)",
        "source_description": "a mock source"
    }
    source = await DataSource._create_source(form_data)
    assert source.__class__.__name__ == "DataSource", "Expected instance of DataSource"
    assert os.path.exists(os.path.join(os.getcwd(), '_projects', MOCK_PROJECT, "data_sources", "mock_source")), "Expected mock_source directory to exist"
    assert os.path.exists(os.path.join(os.getcwd(), '_projects', MOCK_PROJECT, "data_sources", "mock_source", "__manifest__.json")), "Expected __manifest__.json to exist"

@pytest.mark.asyncio
async def test_update_source_settings(temp_project_dir_fixture):
    """
    Test if the _update_source_settings method is correctly implemented
    """
    source = {
        "name": "Mock source",
        "type": "csv",
        "description": "a mock source",
        "directory": "mock_source"
    }
    updated_data = {
        "name": "Mock source, new name",
        "type": "csv",
        "description": "a mock source, new description",
        "directory": "mock_source",
        "non_existing_arg": "should not be added"
    }
    updated_source = await DataSource._update_source_settings(source, updated_data)
    assert updated_source["name"] == "Mock source, new name", "Expected name to be Mock source, new name"
    assert updated_source["description"] == "a mock source, new description", "Expected description to be a mock source, new description"
    assert "non_existing_arg" not in updated_source, "Expected non_existing_arg to not be in updated source"
