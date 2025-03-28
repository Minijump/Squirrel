from fastapi.testclient import TestClient

import pytest

from app.main import app
from app.data_sources.models import DATA_SOURCE_REGISTRY, DataSourceAPI

client = TestClient(app)

def test_generate_manifest():
    """
    Test the _generate_manifest method of DataSourceAPI
    last_sync should be an empty string
    """
    infos = {
        "source_name": "Mock source",
        "source_type": "API",
    }
    manifest = DataSourceAPI._generate_manifest(infos)
    assert manifest["name"] == "Mock source"
    assert manifest['last_sync'] == ""

def test_instance_from_manifest():
    """
    Test instance creation of DataSourceAPI from manifest (should include last_sync)
    """
    manifest = {
        "name": "Mock source",
        "directory": "mock_directory",
        "type": "API",
        "last_sync": "2021-01-01 00:00:00",
    }
    source = DataSourceAPI(manifest)
    assert source.name == "Mock source"
    assert source.last_sync == "2021-01-01 00:00:00"

def test_create_table():
    """
    Test the create_table method of DataSourceFile
    """
    form_data = {
        "name": 'mock_source',
        "type": 'csv',
        "kwargs": '{"delimiter": ";"}',
        "directory": 'mock_directory',
    }
    source = DataSourceAPI(form_data)
    table_form_data = {
        "project_dir": "mock_project",
        "table_name": "mock_table",
    }
    python_line =  source.create_table(table_form_data)
    assert " pd.read_pickle(r" in python_line, f"DataSourceAPI create table method should read the pickle file"

def test_subclass_get_data_from_api_implemented():
    """
    Assert subclasses of DataSourceFile implement the _get_data_from_api method
    """
    for source_type in DATA_SOURCE_REGISTRY:
        SourceClass = DATA_SOURCE_REGISTRY[source_type]
        if issubclass(SourceClass, DataSourceAPI):
            assert SourceClass._get_data_from_api != DataSourceAPI._get_data_from_api, f"{SourceClass.__name__} should implement _create_data_file"
