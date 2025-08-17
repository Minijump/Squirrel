import inspect

# Decorators ------------------------------------------------------------------
# On Classes, to add new actions in registry
TABLE_ACTION_REGISTRY = {}
def table_action_type(cls):
    TABLE_ACTION_REGISTRY[cls.__name__] = cls
    return cls

# Misc methods ---------------------------------------------------------------------------
def convert_sq_action_to_python(code, actual_table_name=None, is_sq_action=True):
    """
    t[t_name] means 'table with name t_name' and is accessed by tables[t_name]
    t[t_name]c[name] means 'column with name name in table t_name' and is accessed by tables[t_name][name]
    c[name] means 'column with name name in actual_table' and is accessed by tables[actual_table_name][name]
    """
    if not is_sq_action:
        return code
    code = code.replace(']c[', f'][') # if a table is provided
    code = code.replace('c[', f"tables['{actual_table_name}'][") # if a table is not provided
    code = code.replace('t[', 'tables[')
    return code

def isnt_str(val):
    """Checks whether val should be considered as a string (return False) or not (return True)"""
    if val in ['True', 'False']:
        return True
    elif val == 'None':
        return True
    elif isinstance(val, int) or isinstance(val, float) or (isinstance(val, str) and val.isdigit()):
        return True
    elif val[:1] == '[' and val[-1:] == ']':
        return True
    elif val[:1] == '{' and val[-1:] == '}':
        return True
    elif val[:1] == '(' and val[-1:] == ')':
        return True
    return False

def _get_method_sig(function, keep=False, remove=False):
    """
    Returns the method signature of the class
    Remove all or keep only the specified args

    => returns a dictionary with the args and their default values
    """
    sig = inspect.signature(function)
    args_dict = {}
    
    for param in sig.parameters.values():
        if param.name != 'self':
            args_dict[param.name] = param.default if param.default is not inspect.Parameter.empty else None
    
    if keep:
        args_dict = {k: v for k, v in args_dict.items() if k in keep}
    if remove:
        args_dict = {k: v for k, v in args_dict.items() if k not in remove}
            
    return args_dict

def convert_col_idx(col_idx):
    """Returns the idx of a pandas dataframe column"""
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    return col_idx
