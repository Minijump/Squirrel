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

def convert_col_idx(col_idx):
    """Returns the idx of a pandas dataframe column"""
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    return col_idx
