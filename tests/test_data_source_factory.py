import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.data_sources.models.data_source_factory import DataSourceFactory
from tests import MOCK_PROJECT
from tests.utils.tests_toolbox import MockUploadFile


client = TestClient(app)
# TODO: test init_source_from_dir and create_source for all DataSourceType (instead of one here)

def test_init_source_from_dir(temp_project_dir_fixture):
    project_dir = MOCK_PROJECT
    source_dir = "Csv_ordered"

    data_source = DataSourceFactory.init_source_from_dir(project_dir, source_dir)

    assert data_source is not None
    assert data_source.name == "Csv ordered"

@pytest.mark.asyncio
async def test_create_source(temp_project_dir_fixture):
    csv_content = "name,age,city\nJohn,25,New York\nJane,30,Paris"
    mock_source_file = MockUploadFile("test_data.csv", csv_content)
    
    form_data = {
        "source_type": "csv",
        "source_name": "Mock source",
        "project_dir": MOCK_PROJECT,
        "source_file": mock_source_file
    }

    await DataSourceFactory.create_source(form_data)

    data_source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "mock_source")
    assert data_source.name == "Mock source", "Expected a new source"

def test_get_available_type(temp_project_dir_fixture):
    available_types = DataSourceFactory.get_available_type()

    assert ('csv', 'CSV') in available_types
    assert ('odoo', 'Odoo') in available_types

def test_get_source_class(temp_project_dir_fixture):
    source_class = DataSourceFactory.get_source_class('csv')

    assert source_class.__name__ == 'DataSourceCSV'
