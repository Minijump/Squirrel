import pytest

from app.tables.models.table_manager import TableManager
from tests import MOCK_PROJECT


@pytest.mark.asyncio
async def test_init_from_project_dir_not_lazy(temp_project_dir_fixture):
    project_dir = MOCK_PROJECT
    
    table_manager = await TableManager.init_from_project_dir(project_dir, lazy=False)

    assert isinstance(table_manager, TableManager)

@pytest.mark.asyncio
async def test_init_from_project_dir_lazy(temp_project_dir_fixture):
    project_dir = MOCK_PROJECT
    table_manager_pipeline_run = await TableManager.init_from_project_dir(project_dir, lazy=False)

    table_manager_file = await TableManager.init_from_project_dir(project_dir, lazy=True)

    assert set(table_manager_file.tables.keys()) == set(table_manager_pipeline_run.tables.keys())

@pytest.mark.asyncio
async def test_to_html_default(temp_project_dir_fixture):
    project_dir = MOCK_PROJECT
    table_manager = await TableManager.init_from_project_dir(project_dir, lazy=False)
    
    table_html, table_len_infos = table_manager.to_html()
    
    assert isinstance(table_html, dict)
    assert isinstance(table_len_infos, dict)
    assert "ordered" in table_html

@pytest.mark.asyncio
async def test_get_col_info(temp_project_dir_fixture):
    project_dir = MOCK_PROJECT
    table_manager = await TableManager.init_from_project_dir(project_dir, lazy=False)
    
    col_info = table_manager.get_col_info("ordered", "mock_name")
    
    assert isinstance(col_info, dict)
    assert "dtype" in col_info
    assert "unique" in col_info
    assert "null" in col_info
    assert "count" in col_info
    assert "is_numeric" in col_info

@pytest.mark.asyncio
async def test_get_autocomplete_data(temp_project_dir_fixture):
    project_dir = MOCK_PROJECT
    table_manager = await TableManager.init_from_project_dir(project_dir, lazy=False)
    
    autocomplete_data = table_manager.get_autocomplete_data()
    
    assert isinstance(autocomplete_data, dict)
    assert "ordered" in autocomplete_data
    assert "random" in autocomplete_data
    assert isinstance(autocomplete_data["ordered"], list)
    assert isinstance(autocomplete_data["random"], list)
    assert "mock_name" in autocomplete_data["ordered"]
    assert "mock_price" in autocomplete_data["ordered"]
    assert "name" in autocomplete_data["random"]
    assert "price" in autocomplete_data["random"]
