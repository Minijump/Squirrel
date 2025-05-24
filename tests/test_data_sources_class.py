import os
import pytest
import warnings

from fastapi.testclient import TestClient

from app.main import app
from app.data_sources.models import DATA_SOURCE_REGISTRY, DataSource
from tests import MOCK_PROJECT


client = TestClient(app)


def test_data_source_registry_format():
    """
    Test if the data source registry is a dictionary with 'key': class pairs 
    (with class a subclass of DataSource)
    """
    assert isinstance(DATA_SOURCE_REGISTRY, dict), "Expected DATA_SOURCE_REGISTRY to be a dictionary"
    for key, value in DATA_SOURCE_REGISTRY.items():
        assert isinstance(key, str), "Expected key to be a string"
        assert isinstance(value, type), "Expected value to be a class"
        assert issubclass(value, DataSource), "Expected value to be a subclass of DataSource"

def test_data_source_registry_content():
    """
    Test if the data source registry contains some expected sources (csv, xlsx, pkl)
    """
    assert "csv" in DATA_SOURCE_REGISTRY, "Expected csv in DATA_SOURCE_REGISTRY"
    assert DATA_SOURCE_REGISTRY["csv"].__name__ == "DataSourceCSV", "Expected DataSourceCSV class"
    assert "xlsx" in DATA_SOURCE_REGISTRY, "Expected xlsx in DATA_SOURCE_REGISTRY"
    assert DATA_SOURCE_REGISTRY["xlsx"].__name__ == "DataSourceXLSX", "Expected DataSourceXLSX class"
    assert "pkl" in DATA_SOURCE_REGISTRY, "Expected pkl in DATA_SOURCE_REGISTRY"
    assert DATA_SOURCE_REGISTRY["pkl"].__name__ == "DataSourcePickle", "Expected pkl class"

def test_data_source_types_required_class_attributes():
    """
    Test if the required class attributes are implemented in all data source types
    """
    for source_type in DATA_SOURCE_REGISTRY:
        source = DATA_SOURCE_REGISTRY[source_type]
        assert source.short_name != 'short_name', f"Expected short_name for {source_type}"
        assert source.display_name != 'Display name', f"Expected display_name for {source_type}"
        if not source.icon:
            warnings.warn("Missing icon for source type" + source.display_name, UserWarning)

def test_check_available_infos_error():
    """
    Test if the check_available_infos method is correctly implemented
    for an empty dictionnary, it should raise a ValueError
    """
    for source_type in DATA_SOURCE_REGISTRY:
        SourceClass = DATA_SOURCE_REGISTRY[source_type]
        with pytest.raises(ValueError):
            SourceClass.check_available_infos({})

def test_check_available_infos_with_additional_fields():
    """
    Test if the check_available_infos method is correctly implemented
    """
    infos = {
        "source_name": "Mock source",
        "source_type": "csv",
    }
    try:
        DataSource.check_available_infos(infos)
    except ValueError:
        pytest.fail("check_available_infos raised an error with required fields only")

    with pytest.raises(ValueError):
        DataSource.check_available_infos({}, additional_required_fields=["field1", "field2"])

    infos["field1"] = "value1"
    infos["field2"] = "value2"
    try:
        DataSource.check_available_infos(infos, additional_required_fields=["field1", "field2"])
    except ValueError:
        pytest.fail("check_available_infos raised an error with additional required fields")

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
            "directory": "mock_source",
            "project_dir": MOCK_PROJECT
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

@pytest.mark.asyncio
async def test_create_source(temp_project_dir_fixture):
    """
    Test if the create_source_base method is correctly implemented
    """
    form_data = {
        "project_dir": MOCK_PROJECT,
        "source_name": "Mock source",
        "source_type": "std (no type)",
        "source_description": "a mock source"
    }
    source = await DataSource._create_source(form_data)
    assert source.__class__.__name__ == "DataSource", "Expected instance of DataSource"
    assert os.path.exists(os.path.join(os.getcwd(), '_projects', MOCK_PROJECT, "data_sources", "mock_source")), "Expected mock_source directory to exist"
    assert os.path.exists(os.path.join(os.getcwd(), '_projects', MOCK_PROJECT, "data_sources", "mock_source", "__manifest__.json")), "Expected __manifest__.json to exist"

@pytest.mark.asyncio
async def test_update_source_settings(temp_project_dir_fixture):
    """
    Test if the _update_source_settings method is correctly implemented
    """
    source = {
        "name": "Mock source",
        "type": "csv",
        "description": "a mock source",
        "directory": "mock_source"
    }
    updated_data = {
        "name": "Mock source, new name",
        "type": "csv",
        "description": "a mock source, new description",
        "directory": "mock_source",
        "non_existing_arg": "should not be added"
    }
    updated_source = await DataSource._update_source_settings(source, updated_data)
    assert updated_source["name"] == "Mock source, new name", "Expected name to be Mock source, new name"
    assert updated_source["description"] == "a mock source, new description", "Expected description to be a mock source, new description"
    assert "non_existing_arg" not in updated_source, "Expected non_existing_arg to not be in updated source"
