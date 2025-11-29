import pandas as pd
import pickle
import pytest
from unittest.mock import patch 

from app.data_sources.models.data_source_factory import DataSourceFactory
from app.data_sources.models.data_source_file import DataSourceCSV, DataSourceXLSX, DataSourceJSON, DataSourcePickle
from tests import MOCK_PROJECT
from tests.utils.tests_toolbox import MockUploadFile

# CSV Tests
def test_init_source_from_dir_csv(temp_project_dir_fixture):
    project_dir = MOCK_PROJECT
    source_dir = "Csv_ordered"

    data_source = DataSourceFactory.init_source_from_dir(project_dir, source_dir)

    assert data_source is not None
    assert data_source.name == "Csv ordered"
    assert isinstance(data_source, DataSourceCSV)

@pytest.mark.asyncio
async def test_create_source_csv(temp_project_dir_fixture):
    csv_content = "name,age,city\nJohn,25,New York\nJane,30,Paris"
    mock_source_file = MockUploadFile("test_data.csv", csv_content)
    
    form_data = {
        "source_type": "csv",
        "source_name": "Mock CSV source",
        "project_dir": MOCK_PROJECT,
        "source_file": mock_source_file,
        "kwargs": "{}"
    }
    await DataSourceFactory.create_source(form_data)

    data_source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "mock_csv_source")
    assert data_source.name == "Mock CSV source"
    assert isinstance(data_source, DataSourceCSV)

# XLSX Tests
@pytest.mark.asyncio
async def test_create_source_xlsx(temp_project_dir_fixture):
    xlsx_content = b"PK\x03\x04" + b"mock_excel_content" * 100
    mock_source_file = MockUploadFile("test_data.xlsx", xlsx_content)
    
    form_data = {
        "source_type": "xlsx",
        "source_name": "Mock Excel source",
        "project_dir": MOCK_PROJECT,
        "source_file": mock_source_file,
        "kwargs": "{}"
    }
    mock_data = pd.DataFrame({"name": ["John", "Jane"], "age": [25, 30]})
    with patch('pandas.read_excel', return_value=mock_data) as mock_read:
        await DataSourceFactory.create_source(form_data)

    data_source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "mock_excel_source")
    assert data_source.name == "Mock Excel source"
    assert isinstance(data_source, DataSourceXLSX)

# JSON Tests
@pytest.mark.asyncio
async def test_create_source_json(temp_project_dir_fixture):
    json_content = '{"data": [{"name": "John", "age": 25}, {"name": "Jane", "age": 30}]}'
    mock_source_file = MockUploadFile("test_data.json", json_content)
    
    form_data = {
        "source_type": "json",
        "source_name": "Mock JSON source",
        "project_dir": MOCK_PROJECT,
        "source_file": mock_source_file,
        "kwargs": "{}"
    }
    await DataSourceFactory.create_source(form_data)

    data_source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "mock_json_source")
    assert data_source.name == "Mock JSON source"
    assert isinstance(data_source, DataSourceJSON)

# Pickle Tests
@pytest.mark.asyncio
async def test_create_source_pickle(temp_project_dir_fixture):
    test_data = {"name": ["John", "Jane"], "age": [25, 30]}
    pickle_content = pickle.dumps(test_data)
    mock_source_file = MockUploadFile("test_data.pkl", pickle_content)
    
    form_data = {
        "source_type": "pkl",
        "source_name": "Mock Pickle source",
        "project_dir": MOCK_PROJECT,
        "source_file": mock_source_file,
        "kwargs": "{}"
    }
    await DataSourceFactory.create_source(form_data)

    data_source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "mock_pickle_source")
    assert data_source.name == "Mock Pickle source"
    assert isinstance(data_source, DataSourcePickle)
