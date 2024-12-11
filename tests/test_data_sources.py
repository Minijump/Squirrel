from fastapi.testclient import TestClient

import tempfile
from unittest.mock import patch
import pytest
import os

from app.main import app
from tests import mock_project

from app.data_sources.models import DATA_SOURCE_REGISTRY, DataSource, DataSourceCSV, DataSourceXLSX

client = TestClient(app)

# Test models
#----------------------------------------------------------------------------------
def test_data_source_registry():
    """
    Test if the data source registry is correctly defined
    """
    assert "csv" in DATA_SOURCE_REGISTRY, "Expected csv in DATA_SOURCE_REGISTRY"
    assert DATA_SOURCE_REGISTRY["csv"].__name__ == "DataSourceCSV", "Expected DataSourceCSV class"
    assert "xlsx" in DATA_SOURCE_REGISTRY, "Expected xlsx in DATA_SOURCE_REGISTRY"
    assert DATA_SOURCE_REGISTRY["xlsx"].__name__ == "DataSourceXLSX", "Expected DataSourceXLSX class"
    assert "pkl" in DATA_SOURCE_REGISTRY, "Expected pkl in DATA_SOURCE_REGISTRY"
    assert DATA_SOURCE_REGISTRY["pkl"].__name__ == "DataSourcePickle", "Expected pkl class"

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

def test_init_data_source_from_manifest():
    """
    Test if a data source can be initialized from a manifest
    """
    for source_type in DATA_SOURCE_REGISTRY:
        manifest = {
            "name": "Mock source",
            "type": source_type,
            "description": "a mock source",
            "directory": "mock_source"
        }
        try:
            source = DataSource(manifest)
        except Exception as e:
            pytest.fail(f"Failed to initialize source from manifest: {e}")
        assert source.name == "Mock source", "Expected name to be Mock source"
        assert source.type == source_type, f"Expected type to be {source_type}"
        assert source.description == "a mock source", "Expected description to be a mock source"
        assert source.directory == "mock_source", "Expected directory to be mock_source"

def test_data_sources_specific_methods_implemented():
    """
    Test if the specific methods of a data source are implemented
    """
    for source_type in DATA_SOURCE_REGISTRY:
        source = DATA_SOURCE_REGISTRY[source_type]
        assert source._create_data_file != DataSource._create_data_file, f"_create_data_file not implemented for {source_type}"
        assert source.create_table != DataSource.create_table, f"create_table not implemented for {source_type}"

def test_check_available_infos():
    """
    Test if the check_available_infos method is correctly implemented
    """
    with pytest.raises(ValueError):
        DataSource.check_available_infos({})

@pytest.mark.asyncio
async def test_create_source(mock_project):
    """
    Test if the create_source_base method is correctly implemented
    """
    form_data = {
        "project_dir": mock_project,
        "source_name": "Mock source",
        "source_type": "std (no type)",
        "source_description": "a mock source"
    }
    source = await DataSource._create_source(form_data)
    assert source.__class__.__name__ == "DataSource", "Expected instance of DataSource"
    

# Test routers
#----------------------------------------------------------------------------------
def test_data_sources(mock_project):
    """
    Test if the data_sources endpoint is accessible
    Test if the response contains the correct sources
    """
    response = client.get("/data_sources/?project_dir="+mock_project,)
    assert response.status_code == 200, "Failed to access the data_sources endpoint"

    expected_source = {
        "name": "Mock source csv",
        "type": "csv",
        "description": "a mock csv source",
        "directory": "mock_source_csv"
    }
    assert expected_source in response.context.get("sources"), "Expected one mock source csv"
    
def test_fail_data_source_creation(mock_project):
    """
    Test if in case of a failing source creation, page is displayed correctly
    """
    form_data = {
        "source_name": "Other arguments are missing=> will raise an error", 
        }
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/create_source/", data=form_data)
            assert response.status_code == 200, "Unexpected error while failing to create data source"
            assert response.context.get("exception"), "Response does not contain an exception"

def test_source_settings(mock_project): 
    """
    Test if the source_settings endpoint is accessible
    Test if the response contains the correct source
    """
    response = client.get("/source/settings?project_dir="+mock_project+"&source_dir=mock_source_csv")
    assert response.status_code == 200, "Failed to access the source_settings endpoint"

    expected_source = {
        "name": "Mock source csv",
        "type": "csv",
        "description": "a mock csv source",
        "directory": "mock_source_csv"
    }
    assert response.context.get("source") == expected_source, "Expected one mock source csv"

def test_fail_source_settings(mock_project):
    """
    Test if in case of a failing source settings, page is displayed correctly
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.get("/source/settings?project_dir="+mock_project+"&source_dir=non_existing")
            assert response.status_code == 200, "Failed to access the source_settings endpoint"
            assert response.context.get("exception"), "Response does not contain an exception"
 