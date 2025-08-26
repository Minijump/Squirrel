from fastapi.testclient import TestClient

from app.main import app
from app.data_sources.models.data_source_api import DataSourceAPI

client = TestClient(app)


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
        "project_dir": "mock_fake_dir",
        "table_name": "mock_table",
    }
    python_line =  source.create_table(table_form_data)
    assert " pd.read_pickle(r" in python_line, f"DataSourceAPI create table method should read the pickle file"
