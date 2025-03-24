import ast
import os
import json
import pandas as pd

from .actions_utils import table_action_type, convert_to_squirrel_action, _get_method_sig, isnt_str
from app.data_sources.models.data_source import DATA_SOURCE_REGISTRY

class Action:
    def __init__(self, request):
        self.request = request
        self.args = {}
        self.kwargs = {}

    async def _get(self, args_list):
        form_data = await self.request.form()
        return (form_data.get(arg) for arg in args_list)
    
    async def execute(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    async def _get_kwargs_str(self, kwargs):
        kwargs_str = ', '.join(
            [
                f"{key}={val}" if isnt_str(val) 
                else f"{key}='{val}'" 
            for key, val in kwargs.items()])
        return kwargs_str
    
    async def execute_advanced(self):
        raise NotImplementedError("Subclasses must implement this method")

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
            "new_rows": {
                "type": "txt", 
                "string": "New rows", 
                "info": """With format<br/> [<br/>{'Col1': Value1, 'Col2': Value2, ...},<br/> {'Col1': Value3 ...<br/>]"""},
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
class CustomAction(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "custom_action_type": {"type": "select", "string": "Value Type", 
                           "options": [("sq_action", "Squirrel action"), ("python", "Python")]},
            "custom_action_code": {"type": "txt", "string": "Python"},
            "custom_action_name": {"type": "str", "string": "Action Name"},
        }

    async def execute(self):
        custom_action_code, custom_action_name, custom_action_type, default_table_name = await self._get(["custom_action_code", "custom_action_name", "custom_action_type", "default_table_name"])
        if custom_action_type == "python":
            new_code = f"""{custom_action_code}  #sq_action: {custom_action_name}"""
        elif custom_action_type == "sq_action":
            new_code = f"""{convert_to_squirrel_action(custom_action_code, default_table_name)}  #sq_action: {custom_action_name}"""
        else:
            raise ValueError("Invalid value type")
        return new_code

@table_action_type
class MergeTables(Action):
    def __init__(self, request):
        super().__init__(request)
        self.kwargs = _get_method_sig(pd.merge, remove=['left', 'left_index', 'right_index', 'copy', 'indicator'])
        self.kwargs['suffixes'] = str(self.kwargs['suffixes']) # convert tuple to str, else parenthesis are removed in frontend
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
    
    async def execute_advanced(self):
        table_name, kwargs = await self._get(["table_name", "kwargs"])
        kwargs = ast.literal_eval(kwargs)
        table2_name = kwargs.pop("right")
        kwargs_str = await self._get_kwargs_str(kwargs)
        new_code = f"""dfs['{table_name}'] = pd.merge(dfs['{table_name}'], dfs['{table2_name}'], {kwargs_str})  #sq_action:Merge {table_name}"""
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
