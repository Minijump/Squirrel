import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.data_sources.models.data_source_file import DataSourceFile

client = TestClient(app)

def test_generate_manifest():
    """
    Test the _generate_manifest method of DataSourceFile
    kwargs should be converted into a dictionnary
    If no kwargs, should be an empty dic
    """
    form_data = {
        "source_name": "Mock source",
        "kwargs": '{"delimiter": ";"}'
    }
    manifest = DataSourceFile._generate_manifest(form_data)
    assert manifest["kwargs"] == {"delimiter": ";"}

    form_data = {
        "source_name": "Mock source",
    }
    manifest = DataSourceFile._generate_manifest(form_data)
    assert manifest["kwargs"] == {}

def test_instance_from_manifest():
    """
    Test instance creation of DataSourceFile from manifest
    """
    manifest = {
        "name": "Mock source",
        "directory": "mock_directory",
        "type": "csv",
        "kwargs": {}
    }
    source = DataSourceFile(manifest)
    assert source.name == "Mock source"

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
    source = DataSourceFile(form_data)
    table_form_data = {
        "project_dir": "mock_fake_dir",
        "table_name": "mock_table",
    }
    python_line =  source.create_table(table_form_data)
    assert " pd.read_pickle(r" in python_line, f"DataSourceFile create table method should read the pickle file"
