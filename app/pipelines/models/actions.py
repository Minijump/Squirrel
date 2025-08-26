import json
import os
import pickle

from .actions_utils import table_action_type, convert_sq_action_to_python
from app.data_sources.models import DataSourceFactory
from app.projects.models.project import Project

class Action:
    def __init__(self, request):
        self.form_data = dict(request)
        self.args = {}

    async def _get(self, args_list):
        form_data = self.form_data
        return (form_data.get(arg) for arg in args_list)
    
    async def get_code(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    async def get_args(self, kwargs=False):
        return self.args

@table_action_type
class AddColumn(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "col_name": {"type": "text", "label": "Col. Name"},
            "value_type": {"type": "select", "label": "Value Type", 
                           "select_options": [("sq_action", "Squirrel action"), ("python", "Python")]},
            "col_value": {"type": "textarea", "label": "Col. Value"},
        }

    async def get_code(self):
        table_name, col_name, col_value, value_type = await self._get(["table_name", "col_name", "col_value", "value_type"])
        code = convert_sq_action_to_python(col_value, actual_table_name=table_name, is_sq_action=(value_type == "sq_action"))
        new_code = f"""tables['{table_name}']['{col_name}'] = {code}  #sq_action:Add column {col_name} on table {table_name}"""
        return new_code

@table_action_type
class AddRow(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "new_rows": {
                "type": "textarea", 
                "label": "New rows", 
                "info": """With format<br/> [<br/>{'Col1': Value1, 'Col2': Value2, ...},<br/> {'Col1': Value3 ...<br/>]"""},
        }

    async def get_code(self):
        table_name, new_rows = await self._get(["table_name", "new_rows"])
        new_rows = f"pd.DataFrame({new_rows})" if new_rows else "pd.DataFrame()"
        new_code = f"""tables['{table_name}'] = pd.concat([tables['{table_name}'], {new_rows}], ignore_index=True)  #sq_action:Add rows in table {table_name}"""
        return new_code

@table_action_type
class DeleteRow(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "delete_domain": {"type": "textarea", "label": "Domain", "info": "With format Col1 &lt; Col2, Colx == 'Value',...."},
        }

    async def get_code(self):
        table_name, delete_domain = await self._get(["table_name", "delete_domain"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].query("not ({delete_domain})")  #sq_action:Delete rows in table {table_name}"""
        return new_code
    
@table_action_type
class KeepRow(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "keep_domain": {"type": "textarea", "label": "Domain", "info": "With format Col1 &lt; Col2, Colx == 'Value',...."},
        }

    async def get_code(self):
        table_name, keep_domain = await self._get(["table_name", "keep_domain"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].query("({keep_domain})")  #sq_action:Keep rows in table {table_name}"""
        return new_code

@table_action_type
class CreateTable(Action):
    def __init__(self, request):
        super().__init__(request)
        # Selections choices are set afterward (in get_action_args) (because we need the project_dir)
        self.args = {
            "table_name": {"type": "text", "label": "Table Name", "placeholder": 'Enter the new table name'},
            "source_creation_type": {"type": "select", "label": "Source Creation Type", 
                           "select_options": [("data_source", "Data Source"), ("other_tables", "Other Tables")],
                           "onchange": "onchangeFormValue('TableCreation_source_creation_type', event)"},
            "data_source_dir": {"type": "select", "label": "Data Source Directory", 
                                "select_options": [],
                                "onchange_visibility": ["TableCreation_source_creation_type", "data_source"]},
            "table_df": {"type": "select", "label": "Table",
                          "select_options": [],
                          "onchange_visibility": ["TableCreation_source_creation_type", "other_tables"]}
        }
    
    async def get_args(self, kwargs=False):
        from app.pipelines.models.pipeline import Pipeline # !! 'circular' dependency

        args = await super().get_args(kwargs)
        project_dir = kwargs.get("project_dir")
        if not project_dir:
            return args
        try:
            project = Project.instantiate_from_dir(project_dir)
            sources = project.get_sources()
            available_data_sources = [(s.get('directory'), s.get('name')) for s in sources]
        except Exception:
            available_data_sources = []

        # available tables (try to read the cached pickle file first)
        available_tables = []
        data_tables_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_tables.pkl")
        try:
            if os.path.exists(data_tables_path):
                with open(data_tables_path, 'rb') as f:
                    table_manager = pickle.load(f)
            else:
                pipeline = Pipeline(project_dir)
                table_manager = await pipeline.run_pipeline()

            for table_name, table in table_manager.tables.items():
                available_tables.append((table_name, table_name))
        except Exception:
            available_tables = []

        # inject into args if the expected keys exist
        if 'data_source_dir' in args:
            args['data_source_dir']['select_options'] = available_data_sources
        if 'table_df' in args:
            args['table_df']['select_options'] = available_tables

        return args

    async def get_code(self):
        table_name, project_dir, data_source_dir, source_creation_type, table_df = await self._get(
            ["table_name", "project_dir", "data_source_dir", "source_creation_type", "table_df"])
        
        if source_creation_type == "data_source":
            source = DataSourceFactory.init_source_from_dir(project_dir, data_source_dir)
            new_code = source.create_table(self.form_data)
        elif source_creation_type == "other_tables":
            new_code = f"tables['{table_name}'] = tables['{table_df}']  #sq_action:Create table {table_name}"
        else:
            raise ValueError("Invalid source_creation_type")
        
        return new_code
    
@table_action_type
class CustomAction(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "custom_action_type": {"type": "select", "label": "Value Type", 
            "select_options": [("sq_action", "Squirrel action"), ("python", "Python")]},
            "custom_action_code": {"type": "textarea", "label": "Python"},
            "custom_action_name": {"type": "text", "label": "Action Name"},
        }

    async def get_code(self):
        custom_action_code, custom_action_name, custom_action_type, default_table_name = await self._get(["custom_action_code", "custom_action_name", "custom_action_type", "default_table_name"])
        code = convert_sq_action_to_python(custom_action_code, actual_table_name=default_table_name, is_sq_action=(custom_action_type == "sq_action"))
        new_code = f"""{code}  #sq_action: {custom_action_name}"""
        return new_code

@table_action_type
class MergeTables(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "table2": {"type": "text", "label": "Table to merge"},
            "on": {"type": "text", "label": "On", "info": "Column name (must be in both tables)"},
            "how": {"type": "select", "label": "How", 
                    "select_options": [("inner", "Inner"), ("outer", "Outer"), ("left", "Left"), ("right", "Right")],
                    "info": "Type of merge, see pandas merge doc (similar to SQL JOIN)"},
        }

    async def get_code(self):
        table_name, table2, on, how = await self._get(["table_name", "table2", "on", "how"])
        new_code = f"""tables['{table_name}'] = pd.merge(tables['{table_name}'], tables['{table2}'], on='{on}', how='{how}')  #sq_action:Merge {table_name} with {table2}"""
        return new_code

@table_action_type
class ConcatenateTables(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "table": {"type": "text", "label": "Table to concat", "info": "Table name to concatenate (SQL UNION) into actual table"},
        }

    async def get_code(self):
        table_name, table = await self._get(["table_name", "table"])
        new_code = f"""tables['{table_name}'] = pd.concat([tables['{table_name}'], tables['{table}']], ignore_index=True)  #sq_action:Concatenate tables {table_name} and {table}"""
        return new_code

@table_action_type
class GroupBy(Action):
    def __init__(self, request):
        super().__init__(request)
        # agg is mandatory, without agg it returns a dfGroupBy object whiwh can not be displayed yet
        self.args = {
            "groupby": {"type": "textarea", "label": "Group by", 
                        "info": "Column name or list of column names </br> i.e. col1 or ['col1', 'col2']"},
            "agg": {"type": "dict", "label": "Aggregation",
                    "info": "Aggregation functions to apply to each group </br> i.e. sum or {'col1': 'sum', 'col2': 'mean'}"},
        }

    async def get_code(self):
        table_name, groupby, agg = await self._get(["table_name", "groupby", "agg"])

        groupby_str = groupby if groupby.startswith('[') else f"'{groupby}'"
        agg_str = f".agg({agg})" if agg.startswith('{') else f".agg('{agg}')"

        new_code = f"""tables['{table_name}'] = tables['{table_name}'].groupby({groupby_str}){agg_str if agg else ''}.reset_index()  #sq_action:Group by {groupby} {('aggr' + agg) if agg else ''} table {table_name}"""
        return new_code
