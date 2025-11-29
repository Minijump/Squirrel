import pytest
import pandas as pd

from app.data_sources.models.data_source_factory import DataSourceFactory
from tests import MOCK_PROJECT

# Note: create_source, create_table, ... is not tested here; see subclasses tests

def test_get_settings(temp_project_dir_fixture):
    source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "Csv_ordered")

    settings = source.get_settings()

    assert settings['project_dir'] == MOCK_PROJECT
    assert settings['name'] == "Csv ordered"

@pytest.mark.asyncio
async def test_update_source_settings(temp_project_dir_fixture):
    source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "Csv_ordered")
    new_settings = {
        'name': "Csv ordered - Updated",
    }

    await source.update_source_settings(new_settings)

    source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "Csv_ordered")
    settings = source.get_settings()
    assert settings['name'] == "Csv ordered - Updated"

def test_create_table(temp_project_dir_fixture):
    source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "Csv_ordered")

    dataframe =  source.create_table()

    assert isinstance(dataframe, pd.DataFrame), "DataSourceFile create table method should return a DataFrame"
