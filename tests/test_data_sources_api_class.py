import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.data_sources.models.data_source_factory import DataSourceFactory
from app.data_sources.models.data_source_api import DataSourceAPI
from app.data_sources.models.data_source_api_odoo import DataSourceOdoo
from app.data_sources.models.data_source_api_yahoo_finance import DataSourceYahooFinance
from tests import MOCK_PROJECT


client = TestClient(app)


class MockOdooApiResponse:
    """Mock response for Odoo API calls"""
    def __init__(self, data):
        self.data = data
    
    async def json(self):
        return {"result": self.data}


class MockYahooFinanceData:
    """Mock Yahoo Finance data"""
    def __init__(self, data):
        self.data = data
        self.columns = MockMultiIndex()
    
    def reset_index(self, inplace=False):
        return self
    
    def to_pickle(self, path):
        pass


class MockMultiIndex:
    """Mock pandas MultiIndex"""
    def __init__(self):
        self.nlevels = 2
    
    def set_names(self, names):
        return self


def test_create_table():
    form_data = {
        "name": 'mock_source',
        "type": 'api (mock)',
        "directory": 'mock_directory',
        "project_dir": "mock_project"
    }
    source = DataSourceAPI(form_data)

    python_line =  source.create_table({"table_name": "mock_table"})

    assert " pd.read_pickle(r" in python_line, f"DataSourceAPI create table method should read the pickle file"

# Odoo Tests
def test_init_source_from_dir_odoo(temp_project_dir_fixture):
    import os
    import json
    project_dir = MOCK_PROJECT
    source_dir = "mock_odoo_source"
    source_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", source_dir)
    os.makedirs(source_path, exist_ok=True)
    manifest = {
        "name": "Mock Odoo source",
        "type": "odoo",
        "directory": source_dir,
        "project_dir": project_dir,
        "url": "https://mock-odoo.com",
        "db": "mock_db",
        "username": "mock_user",
        "key": "mock_key",
        "model": "res.partner",
        "fields": ["name", "email"],
        "domain": [],
        "kwargs": {},
        "last_sync": ""
    }
    manifest_path = os.path.join(source_path, "__manifest__.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f)

    data_source = DataSourceFactory.init_source_from_dir(project_dir, source_dir)

    assert data_source is not None
    assert data_source.name == "Mock Odoo source"
    assert isinstance(data_source, DataSourceOdoo)
    assert data_source.url == "https://mock-odoo.com"
    assert data_source.model == "res.partner"

@pytest.mark.asyncio
async def test_create_source_odoo(temp_project_dir_fixture):
    form_data = {
        "source_type": "odoo",
        "source_name": "Mock Odoo API source",
        "project_dir": MOCK_PROJECT,
        "url": "https://mock-odoo.com",
        "db": "mock_database",
        "username": "mock_user",
        "key": "mock_api_key",
        "model": "res.partner",
        "fields": "['name', 'email', 'phone']",
        "domain": "[]",
        "kwargs": "{}"
    }
    mock_data = [
        {"name": "Company A", "email": "contact@companya.com", "phone": "123-456-7890"},
        {"name": "Company B", "email": "info@companyb.com", "phone": "098-765-4321"}
    ]
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"result": mock_data}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with patch('pandas.DataFrame.to_pickle') as mock_pickle:
            await DataSourceFactory.create_source(form_data)

    data_source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "mock_odoo_api_source")
    assert data_source.name == "Mock Odoo API source"
    assert isinstance(data_source, DataSourceOdoo)
    assert data_source.url == "https://mock-odoo.com"
    assert data_source.model == "res.partner"


# Yahoo Finance Tests
def test_init_source_from_dir_yahoo_finance(temp_project_dir_fixture):
    import os
    import json
    project_dir = MOCK_PROJECT
    source_dir = "mock_yahoo_finance_source" 
    source_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", source_dir)
    os.makedirs(source_path, exist_ok=True)
    manifest = {
        "name": "Mock Yahoo Finance source",
        "type": "yahoo_finance",
        "directory": source_dir,
        "project_dir": project_dir,
        "tickers": ["AAPL", "GOOGL"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "interval": "1d",
        "last_sync": ""
    }
    manifest_path = os.path.join(source_path, "__manifest__.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f)

    data_source = DataSourceFactory.init_source_from_dir(project_dir, source_dir)

    assert data_source is not None
    assert data_source.name == "Mock Yahoo Finance source"
    assert isinstance(data_source, DataSourceYahooFinance)
    assert data_source.tickers == ["AAPL", "GOOGL"]
    assert data_source.interval == "1d"

@pytest.mark.asyncio
async def test_create_source_yahoo_finance(temp_project_dir_fixture):
    form_data = {
        "source_type": "yahoo_finance",
        "source_name": "Mock Yahoo Finance API source",
        "project_dir": MOCK_PROJECT,
        "tickers": "['AAPL', 'MSFT', 'GOOGL']",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "interval": "1d"
    }
    mock_data = MockYahooFinanceData({
        "Date": ["2023-01-01", "2023-01-02"],
        "Close": [150.0, 152.0],
        "Volume": [1000000, 1100000]
    })
    
    with patch('yfinance.download', return_value=mock_data) as mock_yf:
        with patch('pandas.DataFrame.to_pickle') as mock_pickle:
            await DataSourceFactory.create_source(form_data)

    data_source = DataSourceFactory.init_source_from_dir(MOCK_PROJECT, "mock_yahoo_finance_api_source")
    assert data_source.name == "Mock Yahoo Finance API source"
    assert isinstance(data_source, DataSourceYahooFinance)
    assert data_source.tickers == ['AAPL', 'MSFT', 'GOOGL']
    assert data_source.start_date == "2023-01-01"
    assert data_source.end_date == "2023-12-31"
    assert data_source.interval == "1d"
