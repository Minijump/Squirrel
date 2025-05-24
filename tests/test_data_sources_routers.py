import json
import os
import pytest

from fastapi.testclient import TestClient

from app.main import app
from tests import MOCK_PROJECT


client = TestClient(app)


# Test methods used by controllers
@pytest.mark.asyncio
async def test_get_sources(temp_project_dir_fixture):
    """
    Test the get_sources function
    """
    from app.data_sources.routers.data_sources import get_sources
    sources = await get_sources(MOCK_PROJECT)
    assert len(sources) == 2, "Expected 2 sources in the project"
    assert sources[0]["name"] == "Csv ordered", "Expected first source to be 'Csv ordered'"
    assert sources[1]["name"] == "Csv random", "Expected second source to be 'Csv unordered'"

@pytest.mark.asyncio
async def test_get_manifest(temp_project_dir_fixture):
    """
    Test the get_manifest function
    """
    from app.data_sources.routers.data_sources import get_manifest
    manifest = await get_manifest(MOCK_PROJECT, "Csv_ordered")
    assert manifest["name"] == "Csv ordered", "Expected source name to be 'Csv ordered'"
    assert manifest["type"] == "csv", "Expected source type to be 'csv'"
    assert manifest["description"] == "a csv data source, with ordered date", "Expected source description to be correct"

@pytest.mark.asyncio
async def test_init_source_instance(temp_project_dir_fixture):
    """
    Test the init_source_instance function
    """
    from app.data_sources.routers.data_sources import init_source_instance
    from app.data_sources.models import DATA_SOURCE_REGISTRY

    manifest_data = {
        "name": "Mock init source instance",
        "type": "csv",
        "description": "a csv data source, with ordered date",
        "directory": "Csv_ordered",
        "kwargs": {},
        "project_dir": MOCK_PROJECT
    }
    source_instance = await init_source_instance(manifest_data)
    assert isinstance(source_instance, DATA_SOURCE_REGISTRY["csv"]), "Expected source instance to be of type 'csv'"
    assert source_instance.name == "Mock init source instance", "Expected source name is incorrect"

# Test controllers
def test_access_data_sources(temp_project_dir_fixture):
    """
    Test if the data_sources endpoint is accessible
    Test if the response contains the correct sources
    """
    response = client.get("/data_sources/?project_dir="+MOCK_PROJECT,)
    assert response.status_code == 200, "Failed to access the data_sources endpoint"

    expected_source = {
        "name": "Csv ordered",
        "type": "csv",
        "description": "a csv data source, with ordered date",
        "directory": "Csv_ordered",
        "kwargs": {},
        "project_dir": MOCK_PROJECT
    }
    assert expected_source in response.context.get("sources"), "Expected one mock source csv"

def test_create_data_source(temp_project_dir_fixture):
    """
    Test the creation of a data source (with demo_random_data.csv from utils/mock_datas)
    """
    with open("tests/utils/mock_datas/demo_random_data.csv", "rb") as f:
        file_content = f.read()

    response = client.post(
        "/create_source/",
        files={"source_file": ("demo_random_data.csv", file_content, "text/csv")},
        data={
            "project_dir": MOCK_PROJECT,
            "source_name": "test create source",
            "source_type": "csv",
            "source_description": "a mock csv source, to test creation",
        }
    )
    assert response.status_code == 200, "Failed to create data source"
    expected_source = {
        'name': 'test create source', 
        'type': 'csv', 
        'description': 'a mock csv source, to test creation', 
        'directory': 'test_create_source', 
        'kwargs': {},
        'project_dir': MOCK_PROJECT}
    assert expected_source in response.context.get("sources"), "Expected one test create source"

def test_access_source_settings(temp_project_dir_fixture): 
    """
    Test if the source_settings endpoint is accessible
    Test if the response contains the correct source
    """
    response = client.get("/source/settings?project_dir="+MOCK_PROJECT+"&source_dir=Csv_ordered")
    assert response.status_code == 200, "Failed to access the source_settings endpoint"

    expected_source = {
        "name": "Csv ordered",
        "type": "csv",
        "description": "a csv data source, with ordered date",
        "directory": "Csv_ordered",
        "kwargs": {},
        "project_dir": MOCK_PROJECT
    }
    assert response.context.get("source") == expected_source, "Expected one mock source csv"

def test_update_source_settings(temp_project_dir_fixture):
    """
    Test if the update_source_settings endpoint is accessible
    """
    form_data = {
        "project_dir": MOCK_PROJECT,
        "source_dir": "Csv_ordered",
        "name": "Csv ordered, new name",
        "source_type": "csv",
        "description": "a csv data source, with ordered date, new description",
        "arg_not_in_manifest": "test_update_settings"
    }
    response = client.post("/source/update_settings", data=form_data)
    assert response.status_code == 200, "Failed to access the update_source_settings endpoint"

    mock_manifest_path = os.path.join(os.getcwd(), "_projects", MOCK_PROJECT, "data_sources", "Csv_ordered", "__manifest__.json")
    with open(mock_manifest_path, 'r') as file:
        mock_manifest_data = json.load(file)
    assert mock_manifest_data["name"] == form_data['name'], "Name was not updated"
    assert mock_manifest_data["description"] == form_data['description'], "Description was not updated"
    assert "arg_not_in_manifest" not in mock_manifest_data, "arg_not_in_manifest should not have been added into manifest"

def test_sync_source(temp_project_dir_fixture):
    """
    Test if the sync_source endpoint is accessible
    """
    form_data = {
        "project_dir": MOCK_PROJECT,
        "source_dir": "Csv_ordered"
    }
    response = client.post("/source/sync", data=form_data)
    assert response.status_code == 200, "Failed to access the sync_source endpoint"

def test_delete_source(temp_project_dir_fixture):
    """
    Test if the delete_source endpoint is accessible
    """
    with open("tests/utils/mock_datas/demo_random_data.csv", "rb") as f:
        file_content = f.read()
    response = client.post(
        "/create_source/",
        files={"source_file": ("demo_random_data.csv", file_content, "text/csv")},
        data={
            "project_dir": MOCK_PROJECT,
            "source_name": "test delete source",
            "source_type": "csv",
            "source_description": "a source to delete",
        }
    )

    mock_source_path = os.path.join(os.getcwd(), "_projects", MOCK_PROJECT, "data_sources", "test_delete_source")
    assert os.path.exists(mock_source_path), "Source directory was not created"

    form_data = {
        "project_dir": MOCK_PROJECT,
        "source_dir": "test_delete_source"
    }
    response = client.post("/source/delete", data=form_data)

    assert response.status_code == 200, "Failed to access the delete_source endpoint"
    assert not os.path.exists(mock_source_path), "Source directory was not deleted"
