from fastapi.testclient import TestClient

from app.main import app
from app.data_sources.models.data_source_file import DataSourceFile


client = TestClient(app)


def test_create_table():
    form_data = {
        "name": 'mock_source',
        "type": 'csv',
        "kwargs": '{"delimiter": ";"}',
        "directory": 'mock_directory',
        "project_dir": "mock_project"
    }
    source = DataSourceFile(form_data)

    python_line =  source.create_table({"table_name": "mock_table"})

    assert " pd.read_pickle(r" in python_line, f"DataSourceFile create table method should read the pickle file"
