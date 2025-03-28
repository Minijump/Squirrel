from fastapi.testclient import TestClient

import pytest

from app.main import app
from app.data_sources.models import DATA_SOURCE_REGISTRY, DataSourceFile

client = TestClient(app)

def test_data_source_file_check_available_infos():
    """
    Test the check_available_infos method of DataSourceFile
    """
    infos = {
        "source_name": "Mock source",
        "source_type": "csv",
    }
    with pytest.raises(ValueError):
        DataSourceFile.check_available_infos(infos) #file is required

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

def test_subclass_create_pickle_file_implemented():
    """
    Assert subclasses of DataSourceFile implement the _create_pickle_file method
    """
    for source_type in DATA_SOURCE_REGISTRY:
        SourceClass = DATA_SOURCE_REGISTRY[source_type]
        if issubclass(SourceClass, DataSourceFile):
            assert SourceClass._create_pickle_file != DataSourceFile._create_pickle_file, f"{SourceClass.__name__} should implement _create_pickle_file"

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
        "project_dir": "mock_project",
        "table_name": "mock_table",
    }
    python_line =  source.create_table(table_form_data)
    assert " pd.read_pickle(r" in python_line, f"DataSourceFile create table method should read the pickle file"
