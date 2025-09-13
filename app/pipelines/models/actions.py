from .actions_utils import convert_sq_action_to_python
from .action_factory import table_action_type
from app.data_sources.models.data_source_factory import DataSourceFactory
from app.tables.models.table_manager import TableManager
from app.projects.models.project import Project

class Action:
    def __init__(self, form_data):
        self.form_data = dict(form_data)
        self.args = {}
        self.icons = []

    def get_name(self):
        return False

    async def _get(self, args_list):
        return (self.form_data.get(arg) for arg in args_list)
    
    async def get_code(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    async def get_args(self, kwargs=False):
        return self.args

@table_action_type
class AddColumn(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-plus", "fas fa-columns"]
        self.args = {
            "col_name": {"type": "text", "label": "Col. Name"},
            "value_type": {"type": "select", "label": "Value Type", 
                           "select_options": [("sq_action", "Squirrel action"), ("python", "Python")]},
            "col_value": {"type": "textarea", "label": "Col. Value"},
        }

    def get_name(self):
        return f"Add column '{self.form_data.get('col_name', '?')}' in table '{self.form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, col_name, col_value, value_type = await self._get(["table_name", "col_name", "col_value", "value_type"])
        code = convert_sq_action_to_python(col_value, actual_table_name=table_name, is_sq_action=(value_type == "sq_action"))
        new_code = f"""tables['{table_name}']['{col_name}'] = {code}"""
        return new_code

@table_action_type
class AddRow(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-plus", "fas fa-table-list"]
        self.args = {
            "new_rows": {
                "type": "textarea", 
                "label": "New rows", 
                "info": """With format<br/> [<br/>{'Col1': Value1, 'Col2': Value2, ...},<br/> {'Col1': Value3 ...<br/>]"""},
        }

    def get_name(self):
        return f"Add rows in table '{self.form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, new_rows = await self._get(["table_name", "new_rows"])
        new_rows = f"pd.DataFrame({new_rows})" if new_rows else "pd.DataFrame()"
        new_code = f"""tables['{table_name}'] = pd.concat([tables['{table_name}'], {new_rows}], ignore_index=True)"""
        return new_code

@table_action_type
class DeleteRow(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-trash", "fas fa-table-list"]
        self.args = {
            "delete_domain": {"type": "textarea", "label": "Domain", "info": "With format Col1 &lt; Col2, Colx == 'Value',...."},
        }

    def get_name(self):
        return f"Delete rows with domain: '{self.form_data.get('delete_domain', '?')}' in table '{self.form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, delete_domain = await self._get(["table_name", "delete_domain"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].query("not ({delete_domain})")"""
        return new_code
    
@table_action_type
class KeepRow(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-filter", "fas fa-table-list"]
        self.args = {
            "keep_domain": {"type": "textarea", "label": "Domain", "info": "With format Col1 &lt; Col2, Colx == 'Value',...."},
        }

    def get_name(self):
        return f"Keep rows with domain: '{self.form_data.get('keep_domain', '?')}' in table '{self.form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, keep_domain = await self._get(["table_name", "keep_domain"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].query("({keep_domain})")"""
        return new_code

@table_action_type
class CreateTable(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-table", "fas fa-plus-circle"]
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

    def get_name(self):
        return f"""Create table '{self.form_data.get('table_name', '?')}'"""

    async def get_args(self, kwargs=False):
        args = await super().get_args(kwargs)
        project_dir = kwargs.get("project_dir")
        if not project_dir:
            return args

        project = Project.instantiate_from_dir(project_dir)
        sources = project.get_sources()
        available_data_sources = [(s.directory, s.name) for s in sources]

        table_manager = await TableManager.init_from_project_dir(project_dir, lazy=True)
        available_tables = [(name, name) for name in table_manager.tables.keys()]

        args['data_source_dir']['select_options'] = available_data_sources
        args['table_df']['select_options'] = available_tables
        return args

    async def get_code(self):
        table_name, project_dir, data_source_dir, source_creation_type, table_df = await self._get(
            ["table_name", "project_dir", "data_source_dir", "source_creation_type", "table_df"])
        
        if source_creation_type == "data_source":
            source = DataSourceFactory.init_source_from_dir(project_dir, data_source_dir)
            new_code = source.create_table(self.form_data)
        elif source_creation_type == "other_tables":
            new_code = f"tables['{table_name}'] = tables['{table_df}']"
        else:
            raise ValueError("Invalid source_creation_type")
        
        return new_code
    
@table_action_type
class CustomAction(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-code", "fas fa-cog"]
        self.args = {
            "custom_action_type": {"type": "select", "label": "Value Type", 
            "select_options": [("sq_action", "Squirrel action"), ("python", "Python")]},
            "custom_action_code": {"type": "textarea", "label": "Python"},
            "custom_action_name": {"type": "text", "label": "Action Name"},
        }

    def get_name(self):
        return f"Custom action '{self.form_data.get('custom_action_name', '?')}'"

    async def get_code(self):
        custom_action_code, custom_action_name, custom_action_type, default_table_name = await self._get(["custom_action_code", "custom_action_name", "custom_action_type", "default_table_name"])
        code = convert_sq_action_to_python(custom_action_code, actual_table_name=default_table_name, is_sq_action=(custom_action_type == "sq_action"))
        new_code = f"""{code}"""
        return new_code

@table_action_type
class MergeTables(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-code-merge", "fas fa-table"]
        self.args = {
            "table2": {"type": "text", "label": "Table to merge"},
            "on": {"type": "text", "label": "On", "info": "Column name (must be in both tables)"},
            "how": {"type": "select", "label": "How", 
                    "select_options": [("inner", "Inner"), ("outer", "Outer"), ("left", "Left"), ("right", "Right")],
                    "info": "Type of merge, see pandas merge doc (similar to SQL JOIN)"},
        }

    def get_name(self):
        return f"Merge table '{self.form_data.get('table_name', '?')}' with '{self.form_data.get('table2', '?')}'"

    async def get_code(self):
        table_name, table2, on, how = await self._get(["table_name", "table2", "on", "how"])
        new_code = f"""tables['{table_name}'] = pd.merge(tables['{table_name}'], tables['{table2}'], on='{on}', how='{how}')"""
        return new_code

@table_action_type
class ConcatenateTables(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-link", "fas fa-table"]
        self.args = {
            "table": {"type": "text", "label": "Table to concat", "info": "Table name to concatenate (SQL UNION) into actual table"},
        }

    def get_name(self):
        return f"Concatenate table '{self.form_data.get('table_name', '?')}' with '{self.form_data.get('table', '?')}'"

    async def get_code(self):
        table_name, table = await self._get(["table_name", "table"])
        new_code = f"""tables['{table_name}'] = pd.concat([tables['{table_name}'], tables['{table}']], ignore_index=True)"""
        return new_code

@table_action_type
class GroupBy(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-layer-group", "fas fa-chart-bar"]
        # agg is mandatory, without agg it returns a dfGroupBy object whiwh can not be displayed yet
        self.args = {
            "groupby": {"type": "textarea", "label": "Group by", 
                        "info": "Column name or list of column names </br> i.e. col1 or ['col1', 'col2']"},
            "agg": {"type": "dict", "label": "Aggregation",
                    "info": "Aggregation functions to apply to each group </br> i.e. sum or {'col1': 'sum', 'col2': 'mean'}"},
        }

    def get_name(self):
        return f"Group by '{self.form_data.get('groupby', '?')}' in table '{self.form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, groupby, agg = await self._get(["table_name", "groupby", "agg"])

        groupby_str = groupby if groupby.startswith('[') else f"'{groupby}'"
        agg_str = f".agg({agg})" if agg.startswith('{') else f".agg('{agg}')"

        new_code = f"""tables['{table_name}'] = tables['{table_name}'].groupby({groupby_str}){agg_str if agg else ''}.reset_index()"""
        return new_code
