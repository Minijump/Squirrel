TABLE_ACTION_REGISTRY = {}
def table_action_type(cls):
    TABLE_ACTION_REGISTRY[cls.__name__] = cls
    return cls

from fastapi import Request
from fastapi.responses import RedirectResponse

import os
import json
import inspect
from functools import wraps

from app.projects.models.project import NEW_CODE_TAG
from app.data_sources.models.data_source import DATA_SOURCE_REGISTRY
from app.utils.error_handling import squirrel_error

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

def convert_to_squirrel_action(code, actual_table_name=None):
    """
    t[t_name] means 'table with name t_name' and is accessed by dfs[t_name]
    t[t_name]c[name] means 'column with name name in table t_name' and is accessed by dfs[t_name][name]
    c[name[] means 'column with name name in actual_table' and is accessed by dfs[actual_table_name][name]
    """
    code = code.replace(']c[', f'][') # if a table id provided
    code = code.replace('c[', f"dfs['{actual_table_name}'][") # if a table id not provided
    code = code.replace('t[', 'dfs[')
    return code

class Action:
    def __init__(self, request):
        self.request = request
        self.args = {}

    async def _get(self, args_list):
        form_data = await self.request.form()
        return (form_data.get(arg) for arg in args_list)
    
    async def execute(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    def _get_method_sig(self, function, keep=False, remove=False):
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

@table_action_type
class AddColumn(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "col_name": {"type": "str", "string": "Col. Name"},
            "value_type": {"type": "select", "string": "Value Type", 
                           "options": [("sq_action", "Squirrel action"), ("python", "Python")]},
            "col_value": {"type": "txt", "string": "Col. Value"},
        }

    async def execute(self):
        table_name, col_name, col_value, value_type = await self._get(["table_name", "col_name", "col_value", "value_type"])
        if value_type == "python":
            new_code = f"""dfs['{table_name}']['{col_name}'] = {col_value}  #sq_action:Add column {col_name} on table {table_name}"""
        elif value_type == "sq_action":
            sq_action = convert_to_squirrel_action(col_value, table_name)
            new_code = f"""dfs['{table_name}']['{col_name}'] = {sq_action}  #sq_action:Add column {col_name} on table {table_name}"""
        else:
            raise ValueError("Invalid value type")
        return new_code

@table_action_type
class AddRow(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "new_rows": {"type": "txt", "string": "New rows", "info": """With format<br/> [<br/>{'Col1': Value1, 'Col2': Value2, ...},<br/> {'Col1': Value3 ...<br/>]"""},
        }

    async def execute(self):
        table_name, new_rows = await self._get(["table_name", "new_rows"])
        new_rows = f"pd.DataFrame({new_rows})" if new_rows else "pd.DataFrame()"
        new_code = f"""dfs['{table_name}'] = pd.concat([dfs['{table_name}'], {new_rows}], ignore_index=True)  #sq_action:Add rows in table {table_name}"""
        return new_code

@table_action_type
class DeleteRow(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "delete_domain": {"type": "txt", "string": "Domain", "info": "With format Col1 &lt; Col2, Colx == 'Value',...."},
        }

    async def execute(self):
        table_name, delete_domain = await self._get(["table_name", "delete_domain"])
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].query("not ({delete_domain})")  #sq_action:Delete rows in table {table_name}"""
        return new_code
    
@table_action_type
class KeepRow(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "keep_domain": {"type": "txt", "string": "Domain", "info": "With format Col1 &lt; Col2, Colx == 'Value',...."},
        }

    async def execute(self):
        table_name, keep_domain = await self._get(["table_name", "keep_domain"])
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].query("({keep_domain})")  #sq_action:Keep rows in table {table_name}"""
        return new_code

@table_action_type
class CreateTable(Action):
    async def execute(self):
        table_name, project_dir, data_source_dir, source_creation_type, table_df = await self._get(
            ["table_name", "project_dir", "data_source_dir", "source_creation_type", "table_df"])
        
        if source_creation_type == "data_source":
            data_source_path = os.path.relpath(
                os.path.join(os.getcwd(), '_projects', project_dir, 'data_sources', data_source_dir), 
                os.getcwd())

            manifest_path = os.path.join(data_source_path, "__manifest__.json")
            with open(manifest_path, 'r') as file:
                manifest_data = json.load(file)

            SourceClass = DATA_SOURCE_REGISTRY[manifest_data["type"]]
            source = SourceClass(manifest_data)
            new_code = source.create_table(await self.request.form())

        elif source_creation_type == "other_tables":
            new_code = f"dfs['{table_name}'] = dfs['{table_df}']  #sq_action:Create table {table_name}"

        else:
            raise ValueError("Invalid source_creation_type")
        
        return new_code
    
@table_action_type
class CustomPythonAction(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "python_action_code": {"type": "txt", "string": "Python"},
            "python_action_name": {"type": "str", "string": "Action Name"},
        }

    async def execute(self):
        python_action_code, python_action_name = await self._get(["python_action_code", "python_action_name"])
        new_code = f"""{python_action_code}  #sq_action: {python_action_name}"""
        return new_code

@table_action_type
class MergeTables(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "table2": {"type": "str", "string": "Table to merge"},
            "on": {"type": "str", "string": "On", "info": "Column name (must be in both tables)"},
            "how": {"type": "select", "string": "How", 
                    "options": [("inner", "Inner"), ("outer", "Outer"), ("left", "Left"), ("right", "Right")],
                    "info": "Type of merge, see pandas merge doc (similar to SQL JOIN)"},
        }

    async def execute(self):
        table_name, table2, on, how = await self._get(["table_name", "table2", "on", "how"])
        new_code = f"""dfs['{table_name}'] = pd.merge(dfs['{table_name}'], dfs['{table2}'], on='{on}', how='{how}')  #sq_action:Merge {table_name} with {table2}"""
        return new_code

@table_action_type
class ConcatenateTables(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "table": {"type": "str", "string": "Table to concat", "info": "Table name to concatenate (SQL UNION) into actual table"},
        }

    async def execute(self):
        table_name, table = await self._get(["table_name", "table"])
        new_code = f"""dfs['{table_name}'] = pd.concat([dfs['{table_name}'], dfs['{table}']], ignore_index=True)  #sq_action:Concatenate tables {table_name} and {table}"""
        return new_code

@table_action_type
class GroupBy(Action):
    def __init__(self, request):
        super().__init__(request)
        # agg is mandatory, without agg it returns a dfGroupBy object whiwh can not be displayed yet
        self.args = {
            "groupby": {"type": "txt", "string": "Group by", 
                        "info": "Column name or list of column names </br> i.e. col1 or ['col1', 'col2']"},
            "agg": {"type": "dict", "string": "Aggregation",
                    "info": "Aggregation functions to apply to each group </br> i.e. sum or {'col1': 'sum', 'col2': 'mean'}"},
        }

    async def execute(self):
        table_name, groupby, agg = await self._get(["table_name", "groupby", "agg"])

        groupby_str = groupby if groupby.startswith('[') else f"'{groupby}'"
        agg_str = f".agg({agg})" if agg.startswith('{') else f".agg('{agg}')"

        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].groupby({groupby_str}){agg_str if agg else ''}.reset_index()  #sq_action:Group by {groupby} {('aggr' + agg) if agg else ''} table {table_name}"""
        return new_code
