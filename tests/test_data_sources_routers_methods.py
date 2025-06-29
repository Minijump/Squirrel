import pytest

from fastapi.testclient import TestClient

from app.main import app
from tests import MOCK_PROJECT


client = TestClient(app)


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
        "kwargs": {}
    }
    source_instance = await init_source_instance(manifest_data)
    assert isinstance(source_instance, DATA_SOURCE_REGISTRY["csv"]), "Expected source instance to be of type 'csv'"
    assert source_instance.name == "Mock init source instance", "Expected source name is incorrect"
