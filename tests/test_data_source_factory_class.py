from fastapi.testclient import TestClient

from app.main import app
from app.data_sources.models.data_source_factory import DataSourceFactory
from tests import MOCK_PROJECT


client = TestClient(app)
# Test to init_source_from_dir and create_source are in subclasses tests


def test_get_available_type(temp_project_dir_fixture):
    available_types = DataSourceFactory.get_available_type()

    assert ('csv', 'CSV') in available_types
    assert ('odoo', 'Odoo') in available_types
    assert ('yahoo_finance', 'Yahoo Finance') in available_types
    assert ('xlsx', 'Excel') in available_types
    assert ('json', 'JSON') in available_types
    assert ('pkl', 'Pickle') in available_types

def test_get_source_csv_class(temp_project_dir_fixture):
    csv_source_class = DataSourceFactory.get_source_class('csv')
    assert csv_source_class.__name__ == 'DataSourceCSV'
