import pandas as pd

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_convert_sq_action_to_python():
    """
    Test if the convert_sq_action_to_python function is correctly converting the sq_action to python code
    """
    from app.pipelines.models.actions_utils import convert_sq_action_to_python
    
    # Test with python code (is_sq_action=False)
    code = "t[users]c[name] + c[age]"
    assert convert_sq_action_to_python(code, "users", is_sq_action=False) == code, "Code should be returned as is when is_sq_action=False"

    # Test with empty string
    assert convert_sq_action_to_python("", "users") == "", "Empty string should be returned as is"
    
    # Test t[table]c[column] pattern
    code = "t[users]c[name]"
    expected = "tables[users][name]"
    assert convert_sq_action_to_python(code, "users") == expected, f"Code should be converted to {expected}"
    assert convert_sq_action_to_python(code) == expected, f"Code should be converted to {expected}"
    
    # Test c[column] pattern with actual_table_name
    code = "c[age]"
    expected = "tables['users'][age]"
    assert convert_sq_action_to_python(code, "users") == expected, f"Code should be converted to {expected}"
    
    # Test t[table] pattern
    code = "t[users]"
    expected = "tables[users]"
    assert convert_sq_action_to_python(code, "users") == expected, f"Code should be converted to {expected}"
    
    # Test complex example with multiple patterns
    code = "t[users]c[name] + ' is ' + str(c[age]) + ' years old from ' + t[cities]c[name]"
    expected = "tables[users][name] + ' is ' + str(tables['users'][age]) + ' years old from ' + tables[cities][name]"
    assert convert_sq_action_to_python(code, "users") == expected, f"Code should be converted to {expected}"

def test_convert_col_idx():
    """
    Test the convert_col_idx function for formatting pandas dataframe column indices.
    """
    from app.pipelines.models.actions_utils import convert_col_idx
    
    # Create test dataframes with different types of indices
    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({('level1', 'A'): [1, 2], ('level1', 'B'): [3, 4]})
    
    df1_col1_idx = str(df1.columns[0])
    assert convert_col_idx(df1_col1_idx) == f"'A'", "Expected string column name to be formatted with quotes"

    df2_col1_idx = str(df2.columns[0])
    assert convert_col_idx(df2_col1_idx) == f"('level1', 'A')", "Expected multi-index column name to be formatted correctly"
