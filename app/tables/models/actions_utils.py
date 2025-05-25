import inspect
import os
from functools import wraps

from fastapi import Request
from fastapi.responses import RedirectResponse

from app.projects.models import NEW_CODE_TAG
from app.utils.form_utils import squirrel_error


# Decorators ------------------------------------------------------------------
# On Classes, to add new actions in registry
TABLE_ACTION_REGISTRY = {}
def table_action_type(cls):
    TABLE_ACTION_REGISTRY[cls.__name__] = cls
    return cls

# On function, to add new code
def add(func):
    @squirrel_error
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        """
        Adds code returned by func to the pipeline (with the correct indentation)

        * request contains the project_dir
        * func provides the new code line(s) (str)
          (func MUST return lines splitted with '\n'
           expl: 'line1\nline2\nline3'
           else indentation will be wrong)

        => Returns a RedirectResponse to the project page
        """        
        form_data = await request.form()
        project_dir = form_data.get("project_dir")
        pipeline_path = os.path.join(os.getcwd(), "_projects", project_dir, "pipeline.py")

        # Find the line with the NEW_CODE_TAG, and get the indentation
        with open(pipeline_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if NEW_CODE_TAG in line:
                    current_indentation = len(line) - len(line.lstrip())
                    break
            
        # Edit pipeline code
        with open(pipeline_path, 'r') as file:
          pipeline_code = file.read()
          new_code = await func(request)
          new_code += """\n""" + NEW_CODE_TAG 
          new_code_list = new_code.split('\n')
          new_code = str(new_code_list[0]) + '\n' + '\n'.join((' ' * current_indentation) + l for l in new_code_list[1:])
          new_pipeline_code = pipeline_code.replace(NEW_CODE_TAG, new_code)

        # Write the new content to the file
        with open(pipeline_path, 'w') as file:
            file.write(new_pipeline_code)
        
        return RedirectResponse(url=f"/tables/?project_dir={project_dir}", status_code=303)                                                    
    return wrapper

action = type('action', (object,), {'add': add})


# Misc methods ---------------------------------------------------------------------------
def convert_sq_action_to_python(code, actual_table_name=None, is_sq_action=True):
    """
    t[t_name] means 'table with name t_name' and is accessed by dfs[t_name]
    t[t_name]c[name] means 'column with name name in table t_name' and is accessed by dfs[t_name][name]
    c[name] means 'column with name name in actual_table' and is accessed by dfs[actual_table_name][name]
    """
    if not is_sq_action:
        return code
    code = code.replace(']c[', f'][') # if a table is provided
    code = code.replace('c[', f"dfs['{actual_table_name}'][") # if a table is not provided
    code = code.replace('t[', 'dfs[')
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
