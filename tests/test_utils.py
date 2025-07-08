from unittest.mock import patch
import warnings

from fastapi.testclient import TestClient
from fastapi.routing import APIRoute

from app.main import app
from app.utils.form_utils import SQUIRREL_ERROR_DECORATED


client = TestClient(app)


def test_squirrel_error():
    """
    Test that in case of error on the root enpoint
    """
    with patch("app.main.RedirectResponse", side_effect=Exception("Mock error")):        
        response = client.get("/")
        assert response.status_code == 200, "Error page not displayed"
        assert response.context.get("exception"), "Response does not contain an exception"

def test_squirrel_error_decorator_usage():
    """
    Test that squirrel_error decorator is applied to the expected routes.
    """    
    decorated_routes = []
    for route in app.routes:
        if isinstance(route, APIRoute) and route.endpoint.__name__ in SQUIRREL_ERROR_DECORATED:
            decorated_routes.append(route.path)
    
    app_routes = ['/', '/app/settings/']
    projects_routes = ['/projects/', '/projects/open/', '/projects/create/', '/project/settings/', '/project/update_settings/', '/project/delete/']
    data_sources_routes = ['/data_sources/', '/source/create/', '/source/settings', '/source/update_settings/', '/source/delete/']
    table_routes = ['/tables/', '/tables/pager/', '/tables/execute_action/', '/tables/column_infos/', '/tables/export_table/']
    pipeline_routes = ['/pipeline/', '/pipeline/confirm_new_order/', '/pipeline/delete_action/', '/pipeline/edit_action/']
    expected_decorated_routes = app_routes + projects_routes + data_sources_routes + table_routes + pipeline_routes
    
    missing_decoration = set(expected_decorated_routes) - set(decorated_routes)
    assert not missing_decoration, f"These routes are missing the squirrel_error decorator: {missing_decoration}"
    
    unexpected_decoration = set(decorated_routes) - set(expected_decorated_routes)
    if unexpected_decoration:
        warnings.warn(f"These routes have the squirrel_error decorator but are not expected: {unexpected_decoration}")
