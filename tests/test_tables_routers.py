import os
import pandas as pd
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from tests import mock_project


client = TestClient(app)


# Test methods used in the enpoints --------------------------------------------------
def test_load_pipeline_module(mock_project):
    """
    Test if pipeline is loaded correctly 
    Test wether the pipeline is 'runable'
    """
    from app.tables.routers.tables import load_pipeline_module
    pipeline = load_pipeline_module(mock_project)
    try:
        dfs = pipeline.run_pipeline()
    except Exception as e:
        raise AssertionError("Not able to run 'run_pipeline' from pipeline") from e
    assert isinstance(dfs, dict) and isinstance(dfs['df'], pd.DataFrame), "'run_pipeline' response should be a dictionary"

def test_to_html_with_idx():
    """
    Test that to_html_with_idx correctly adds data-columnidx attributes to table headers.
    """
    from app.tables.routers.tables import to_html_with_idx
    import pandas as pd
    
    # Test case 1: Simple DataFrame with single-level columns
    df1 = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c']
    })
    html1 = to_html_with_idx(df1)
    
    assert 'df-table' in html1
    assert 'data-columnidx="A"' in html1
    assert 'data-columnidx="B"' in html1
    assert '>A<' in html1
    assert '>B<' in html1
    
    # Test case 2: DataFrame with MultiIndex columns
    columns = pd.MultiIndex.from_tuples([('Group1', 'A'), ('Group1', 'B'), ('Group2', 'C')])
    df2 = pd.DataFrame([[1, 'a', 4], [2, 'b', 5], [3, 'c', 6]], columns=columns)
    html2 = to_html_with_idx(df2)
    
    assert 'df-table' in html2
    for col_tuple in df2.columns:
        col_str = str(col_tuple)
        assert f'data-columnidx="{col_str}"' in html2
    for _, col_name in df2.columns:
        assert f">{col_name}<" in html2

# Test the endpoints ---------------------------------------------------------------
def test_access_tables(mock_project):
    """
    Test if the table endpoint is accessible
    Test if the response contains a table and the correct project_dir
    """
    response = client.get("/tables/?project_dir=" + mock_project)
    assert response.status_code == 200, "Failed to access the table endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"
    assert os.path.exists(os.path.join(os.getcwd(), "_projects", mock_project, "data_tables.pkl")), "No data_tables.pkl file in project directory"

def test_fail_access_tables():
    """
    Test we have a correct error page in case of a non-existing project_dir
    """
    response = client.get("/tables/?project_dir=non_existing_project")
    assert response.status_code == 200, "Failed to access the table endpoint"
    assert response.context.get("exception"), "Response does not contain an exception"

def test_fail_pipeline(mock_project):
    """
    Test if the table endpoint is accessible
    Test if in case of failing pipeline, page is displayed correctly
    """
    with patch("app.tables.load_pipeline_module") as mock_load_pipeline_module:
        mock_load_pipeline_module.side_effect = Exception("Mock exception")
        response = client.get("/tables/?project_dir=" + mock_project)
        assert response.status_code == 200, "Failed to access the table endpoint"
        assert response.context.get("exception"), "Response does not contain an exception"

def test_tables_pager(mock_project):
    """
    Test if the tables_pager endpoint functions correctly:
    """
    # First, make sure the data_tables.pkl file exists by calling the tables endpoint
    response = client.get(f"/tables/?project_dir={mock_project}")
    assert response.status_code == 200
    
    response = client.get(f"/tables/pager/?project_dir={mock_project}&table_name=df&page=0&n=5")
    assert response.status_code == 200
    assert "<table " in response.text, "Response does not contain a table"
    assert response.text.count("<tr>") <= 6, "Table should have at most 6 rows (header + 5 data rows)"
    table_html = response.text
    
    response = client.get(f"/tables/pager/?project_dir={mock_project}&table_name=df&page=1&n=5")
    assert response.status_code == 200
    assert "<table " in response.text, "Response does not contain a table"
    assert response.text != table_html, "Table should be different from the first page"
    
    response = client.get(f"/tables/pager/?project_dir={mock_project}&table_name=df&page=0&n=10")
    assert response.status_code == 200
    assert "<table " in response.text, "Response does not contain a table"
    assert response.text.count("<tr>") <= 11, "Table should have at most 11 rows (header + 10 data rows)"

def test_get_action_args():
    """
    Test if the get_action_args endpoint correctly returns args for all actions in the registry.
    """
    from app.tables.models.actions_utils import TABLE_ACTION_REGISTRY
    
    for action_name in TABLE_ACTION_REGISTRY.keys():
        response = client.get(f"/tables/get_action_args/?action_name={action_name}")
        args = response.json()
        
        assert response.status_code == 200, f"Failed to get args for action {action_name}"
        assert isinstance(args, dict), f"Args for action {action_name} is not a dictionary"
        
        action_class = TABLE_ACTION_REGISTRY[action_name]
        action_instance = action_class(request=None)
        expected_args = action_instance.args

        assert len(args) == len(expected_args), f"Number of args doesn't match for action {action_name}"
        for key in expected_args:
            assert str(key) in args, f"Missing key '{key}' for action {action_name}"

def test_get_action_kwargs():
    """
    Test if the get_action_kwargs endpoint correctly returns kwargs for all actions in the registry.
    """
    from app.tables.models.actions_utils import TABLE_ACTION_REGISTRY
    
    for action_name in TABLE_ACTION_REGISTRY.keys():
        response = client.get(f"/tables/get_action_kwargs/?action_name={action_name}")
        kwargs = response.json()
        
        assert response.status_code == 200, f"Failed to get kwargs for action {action_name}"
        assert isinstance(kwargs, dict), f"Kwargs for action {action_name} is not a dictionary"
        
        action_class = TABLE_ACTION_REGISTRY[action_name]
        action_instance = action_class(request=None)
        expected_kwargs = action_instance.kwargs

        assert len(kwargs) == len(expected_kwargs), f"Number of kwargs doesn't match for action {action_name}"
        for key in expected_kwargs:
            assert str(key) in kwargs, f"Missing key '{key}' for action {action_name}"

def test_get_col_infos(mock_project):
    """
    Test if the column_infos endpoint correctly returns column information.
    """
    # First, make sure the data_tables.pkl file exists by calling the tables endpoint
    client.get(f"/tables/?project_dir={mock_project}")
    
    # Test with a numeric column
    response = client.get(f"/tables/column_infos/?project_dir={mock_project}&table=df&column_name=price&column_idx=price")
    assert response.status_code == 200, "Failed to get column info"
    col_info = response.json()
    
    assert col_info['is_numeric'] is True, "Column should be numeric"
    basic_fields = ["dtype", "count", "unique", "null", "is_numeric"]
    for field in basic_fields:
        assert field in col_info, f"Missing basic field '{field}' in column info"
    numeric_fields = ["mean", "std", "min", "max", "25", "50", "75"]
    for field in numeric_fields:
        assert field in col_info, f"Missing numeric field '{field}' in column info"
    
    # Test with a non-numeric column
    response = client.get(f"/tables/column_infos/?project_dir={mock_project}&table=df&column_name=name&column_idx=name")
    assert response.status_code == 200
    col_info = response.json()

    assert col_info["is_numeric"] is False, "Column should not be numeric"
    basic_fields = ["dtype", "count", "unique", "null", "is_numeric"]
    for field in basic_fields:
        assert field in col_info, f"Missing basic field '{field}' in column info"
    numeric_fields = ["mean", "std", "min", "max", "25", "50", "75"]
    for field in numeric_fields:
        assert field not in col_info, f"Non-numeric column should not have '{field}' field"
