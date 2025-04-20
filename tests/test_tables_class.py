import pandas as pd
import pytest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

# Test the action utils + classes (Action, ActionColumn)

# Utils ----------------------------------------------------------------------------------------
def test_table_action_registry():
    """
    Test if the table action registry is correctly populated
    """
    from app.tables.models.actions_utils import TABLE_ACTION_REGISTRY
    from app.tables.models.actions import Action
    assert len(TABLE_ACTION_REGISTRY) > 0, "No table action registered"
    assert all([isinstance(v, type) for v in TABLE_ACTION_REGISTRY.values()]), "Not all values in registry are classes"
    assert all([issubclass(v, Action) for v in TABLE_ACTION_REGISTRY.values()]), "Not all values in registry are subclasses of Action"

def test_convert_sq_action_to_python():
    """
    Test if the convert_sq_action_to_python function is correctly converting the sq_action to python code
    """
    from app.tables.models.actions_utils import convert_sq_action_to_python
    
    # Test with python code (is_sq_action=False)
    code = "t[users]c[name] + c[age]"
    assert convert_sq_action_to_python(code, "users", is_sq_action=False) == code, "Code should be returned as is when is_sq_action=False"

    # Test with empty string
    assert convert_sq_action_to_python("", "users") == "", "Empty string should be returned as is"
    
    # Test t[table]c[column] pattern
    code = "t[users]c[name]"
    expected = "dfs[users][name]"
    assert convert_sq_action_to_python(code, "users") == expected, f"Code should be converted to {expected}"
    assert convert_sq_action_to_python(code) == expected, f"Code should be converted to {expected}"
    
    # Test c[column] pattern with actual_table_name
    code = "c[age]"
    expected = "dfs['users'][age]"
    assert convert_sq_action_to_python(code, "users") == expected, f"Code should be converted to {expected}"
    
    # Test t[table] pattern
    code = "t[users]"
    expected = "dfs[users]"
    assert convert_sq_action_to_python(code, "users") == expected, f"Code should be converted to {expected}"
    
    # Test complex example with multiple patterns
    code = "t[users]c[name] + ' is ' + str(c[age]) + ' years old from ' + t[cities]c[name]"
    expected = "dfs[users][name] + ' is ' + str(dfs['users'][age]) + ' years old from ' + dfs[cities][name]"
    assert convert_sq_action_to_python(code, "users") == expected, f"Code should be converted to {expected}"

def test_isnt_str():
    """
        Test the isnt_str function's behavior with various input types.
    """
    from app.tables.models.actions_utils import isnt_str
    
    # Test special string values that should be considered non-strings
    assert isnt_str('True') == True, "Expected 'True' to be non-string"
    assert isnt_str('False') == True, "Expected 'False' to be non-string"
    assert isnt_str('None') == True, "Expected 'None' to be non-string"
    
    # Test numeric types and digit strings
    assert isnt_str(42) == True, "Expected 42 to be non-string"
    assert isnt_str(3.14) == True, "Expected 3.14 to be non-string"
    assert isnt_str('123') == True, "Expected '123' to be non-string"
    
    # Test collection-like strings
    assert isnt_str('[1, 2, 3]') == True, "Expected '[1, 2, 3]' to be non-string"
    assert isnt_str('{"key": "value"}') == True, "Expected dict to be non-string"
    assert isnt_str('(1, 2, 3)') == True, "Expected '(1, 2, 3)' to be non-string"
    
    # Test regular strings that should be identified as strings
    assert isnt_str('hello') == False, "Expected 'hello' to be string"
    assert isnt_str('') == False, "Expected empty string to be string"
    assert isnt_str('True1') == False, "Expected 'True1' to be string"
    assert isnt_str('123abc') == False, "Expected '123abc' to be string"
    assert isnt_str('[incomplete') == False, "Expected '[incomplete' to be string"
    assert isnt_str('incomplete]') == False, "Expected 'incomplete]' to be string"
    assert isnt_str('{incomplete') == False, "Expected '{incomplete' to be string"
    assert isnt_str('incomplete}') == False, "Expected 'incomplete}' to be string"
    assert isnt_str('(incomplete') == False, "Expected '(incomplete' to be string"
    assert isnt_str('incomplete)') == False, "Expected 'incomplete)' to be string"

def test_get_method_sig():
    """
    Test the _get_method_sig function for extracting function parameters.
    """
    from app.tables.models.actions_utils import _get_method_sig
    
    # Test function with default arguments
    def func1(a, b=1, c="test"):
        pass
    
    # Basic functionality - all parameters
    result = _get_method_sig(func1)
    assert result == {'a': None, 'b': 1, 'c': "test"}, "Expected all parameters to be returned"
    
    # Test keep functionality
    result = _get_method_sig(func1, keep=['a', 'b'])
    assert result == {'a': None, 'b': 1}, "Expected only 'a' and 'b' to be returned"
    
    # Test remove functionality
    result = _get_method_sig(func1, remove=['c'])
    assert result == {'a': None, 'b': 1}, "Expected 'c' to be removed from the result"
    
    # Test with class method (self parameter should be ignored)
    class TestClass:
        def method(self, x, y=2):
            pass
    result = _get_method_sig(TestClass().method)
    assert result == {'x': None, 'y': 2}, "Expected 'self' to be ignored and other parameters to be returned"
    
    # Test with complex signature
    def func2(a, b=1, *args, d=3, **kwargs):
        pass  
    result = _get_method_sig(func2)
    assert result == {'a': None, 'b': 1, 'args': None, 'd': 3, 'kwargs': None}, "Expected all parameters to be returned args and kwargs included"
    
    # Test empty keep/remove lists => no filtering
    result = _get_method_sig(func1, keep=[])
    assert result == {'a': None, 'b': 1, 'c': "test"}, "Expected all parameters to be returned, empty keep has no effect"
    result = _get_method_sig(func1, remove=[])
    assert result == {'a': None, 'b': 1, 'c': "test"}, "Expected all parameters to be returned, empty remove has no effect"

def test_convert_col_idx():
    """
    Test the convert_col_idx function for formatting pandas dataframe column indices.
    """
    from app.tables.models.actions_utils import convert_col_idx
    
    # Create test dataframes with different types of indices
    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({('level1', 'A'): [1, 2], ('level1', 'B'): [3, 4]})
    
    df1_col1_idx = str(df1.columns[0])
    assert convert_col_idx(df1_col1_idx) == f"'A'", "Expected string column name to be formatted with quotes"

    df2_col1_idx = str(df2.columns[0])
    assert convert_col_idx(df2_col1_idx) == f"('level1', 'A')", "Expected multi-index column name to be formatted correctly"


# Action class ------------------------------------------------------------------------
def test_table_action_registry_execute():
    """
    Test if all classes in the table action registry have an execute method that is different from the Action class.
    """
    from app.tables.models.actions_utils import TABLE_ACTION_REGISTRY
    from app.tables.models.actions import Action
    
    for action_name, action_class in TABLE_ACTION_REGISTRY.items():
        assert hasattr(action_class, "execute"), f"{action_name} does not have an execute method"
        assert action_class.execute != Action.execute, f"{action_name} execute method was not implemented"

def test_table_action_registry_execute_advanced():
    """
    Test if all classes that have kwrags in the table action registry have an execute_advanced method.
    """
    from app.tables.models.actions_utils import TABLE_ACTION_REGISTRY
    from app.tables.models.actions import Action
    
    for action_name, action_class in TABLE_ACTION_REGISTRY.items():
        class_object = action_class(request=None)
        if class_object.kwargs:
            assert hasattr(action_class, "execute_advanced"), f"{action_name} does not have an execute_advanced method"
            assert action_class.execute_advanced != Action.execute_advanced, f"{action_name} execute_advanced method was not implemented"

@pytest.mark.asyncio
async def test_action_get_method():
    """
    Test that the Action._get method correctly extracts values from form data.
    """
    from app.tables.models.actions import Action
    action_object = Action(request=None)

    mock_kwargs = {
        "arg1": "value1",
        "arg2": "value2",
        "arg3": "value3"
    }
    expected = "arg1='value1', arg2='value2', arg3='value3'"
    result = await action_object._get_kwargs_str(mock_kwargs)
    assert result == expected, f"Expected string representation of kwargs to be {expected}"

    mock_kwargs_with_no_str = {
        "arg1": 1,
        "arg2": 2.5,
        "arg3": True
    }
    expected = "arg1=1, arg2=2.5, arg3=True"
    result_no_str = await action_object._get_kwargs_str(mock_kwargs_with_no_str)
    assert result_no_str == expected, f"Expected string representation of kwargs to be {expected}"
