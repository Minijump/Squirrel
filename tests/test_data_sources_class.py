import os
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.data_sources.models.data_source import DataSource
from tests import MOCK_PROJECT


client = TestClient(app)


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
    source = await DataSource.create_source(form_data)
    assert source.__class__.__name__ == "DataSource", "Expected instance of DataSource"
    assert os.path.exists(os.path.join(os.getcwd(), '_projects', MOCK_PROJECT, "data_sources", "mock_source")), "Expected mock_source directory to exist"
    assert os.path.exists(os.path.join(os.getcwd(), '_projects', MOCK_PROJECT, "data_sources", "mock_source", "__manifest__.json")), "Expected __manifest__.json to exist"
