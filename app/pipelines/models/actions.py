import ast
import numpy as np
import pandas as pd

from app.data_sources.models.data_source_factory import DataSourceFactory
from app.tables.models.table_manager import TableManager
from app.projects.models.project import Project

TABLE_ACTION_REGISTRY = {}
def table_action_type(cls):
    TABLE_ACTION_REGISTRY[cls.__name__] = cls
    return cls

def convert_sq_action_to_python(code, actual_table_name=None):
    """
    t[t_name] means 'table with name t_name' and is accessed by tables[t_name]
    t[t_name]c[name] means 'column with name name in table t_name' and is accessed by tables[t_name][name]
    c[name] means 'column with name name in actual_table' and is accessed by tables[actual_table_name][name]
    """
    code = code.replace(']c[', f'][') # if a table is provided
    code = code.replace('c[', f"tables['{actual_table_name}'][") # if a table is not provided
    code = code.replace('t[', 'tables[')
    return code

class Action:
    def __init__(self, form_data):
        self.form_data = dict(form_data)
        self.args = {}
        self.icons = []

    def get_name(self):
        return False

    async def _get(self, args_list):
        result = []
        for arg in args_list:
            val = await self._field_post_process(arg, self.form_data.get(arg))
            result.append(val)
        return tuple(result)
    
    async def _field_post_process(self, field_name, field_value):
        if self.args.get(field_name, {}).get('type') in ['list', 'dict']:
            field_value = ast.literal_eval(field_value)
        elif self.args.get(field_name, {}).get('type') == 'sq_action':
            table_name = self.form_data.get('table_name')
            field_value = convert_sq_action_to_python(field_value, actual_table_name=table_name)
        return field_value
    
    async def execute(self, tables):
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
            "col_value": {"type": "sq_action", "label": "Col. Value"},
        }

    def get_name(self):
        return f"Add column '{self.form_data.get('col_name', '?')}' in table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, col_value = await self._get(["table_name", "col_name", "col_value"])
        exec(f"tables['{table_name}']['{col_name}'] = {col_value}", {'tables': tables, 'pd': pd, 'np': np})
        return tables

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

    async def execute(self, tables):
        table_name, new_rows = await self._get(["table_name", "new_rows"])
        new_rows_df = pd.DataFrame(eval(new_rows)) if new_rows else pd.DataFrame()
        tables[table_name] = pd.concat([tables[table_name], new_rows_df], ignore_index=True)
        return tables

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

    async def execute(self, tables):
        table_name, delete_domain = await self._get(["table_name", "delete_domain"])
        tables[table_name] = tables[table_name].query(f"not ({delete_domain})")
        return tables
    
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

    async def execute(self, tables):
        table_name, keep_domain = await self._get(["table_name", "keep_domain"])
        tables[table_name] = tables[table_name].query(f"({keep_domain})")
        return tables

@table_action_type
class DropDuplicates(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-trash", "fas fa-copy"]
        self.args = {
            "subset": {"type": "list", "label": "Subset Columns", 
                       "info": "Column names to consider for duplicates. Leave empty to consider all columns."},
            "keep": {"type": "select", "label": "Keep", 
                     "select_options": [("first", "First"), ("last", "Last"), ("false", "False")],
                     "info": "Which duplicate to keep: First, Last, 'False' drops all duplicates."},
        }

    def get_name(self):
        subset_list = ast.literal_eval(self.form_data.get('subset', '[]'))
        subset = ', '.join(subset_list) or 'all'
        keep = self.form_data.get('keep', 'first')
        return f"Drop duplicates in table '{self.form_data.get('table_name', '?')}' (columns: {subset} | keep: {keep})"

    async def execute(self, tables):
        table_name, subset, keep = await self._get(["table_name", "subset", "keep"])
        keep_val = keep if keep != 'false' else False
        tables[table_name] = tables[table_name].drop_duplicates(subset=subset or None, keep=keep_val)
        return tables

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

    async def execute(self, tables):
        table_name, project_dir, data_source_dir, source_creation_type, table_df = await self._get(
            ["table_name", "project_dir", "data_source_dir", "source_creation_type", "table_df"])
        
        if source_creation_type == "data_source":
            source = DataSourceFactory.init_source_from_dir(project_dir, data_source_dir)
            tables[table_name] = source.create_table()
        elif source_creation_type == "other_tables":
            tables[table_name] = tables[table_df].copy()
        else:
            raise ValueError("Invalid source_creation_type")
        
        return tables
    
@table_action_type
class CustomAction(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-code", "fas fa-cog"]
        self.args = {
            "custom_action_code": {"type": "sq_action", "label": "Action Code"},
            "custom_action_name": {"type": "text", "label": "Action Name"},
        }

    def get_name(self):
        return f"Custom action '{self.form_data.get('custom_action_name', '?')}'"

    async def execute(self, tables):
        table_name, custom_action_code = await self._get(["table_name", "custom_action_code"])
        exec(custom_action_code, {'tables': tables, 'pd': pd, 'np': np})
        return tables

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

    async def execute(self, tables):
        table_name, table2, on, how = await self._get(["table_name", "table2", "on", "how"])
        tables[table_name] = pd.merge(tables[table_name], tables[table2], on=on, how=how)
        return tables

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

    async def execute(self, tables):
        table_name, table = await self._get(["table_name", "table"])
        tables[table_name] = pd.concat([tables[table_name], tables[table]], ignore_index=True)
        return tables

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

    async def execute(self, tables):
        table_name, groupby, agg = await self._get(["table_name", "groupby", "agg"])

        groupby_val = eval(groupby) if groupby.startswith('[') else groupby
        grouped = tables[table_name].groupby(groupby_val)
        
        if agg:
            tables[table_name] = grouped.agg(agg).reset_index()
        else:
            tables[table_name] = grouped.reset_index()
        
        return tables

# ACTION FOR COLUMNS --------------------------------------------------------------------------------------------------------

class ActionColumn(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.args.update({
            "col_name": {"type": "text", "invisible": True},
            "col_idx": {"type": "text", "invisible": True},
            "col_dtype": {"type": "text", "invisible": True},
        })

    async def _field_post_process(self, field_name, field_value):
        val = await super()._field_post_process(field_name, field_value)
        if field_name == "col_idx":
            val = eval(val) if val.startswith('(') else val
        return val
    
@table_action_type
class DropColumn(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-trash", "fas fa-columns"]

    def get_name(self):
        return f"Drop column '{self.form_data.get('col_name', '?')}' in table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, col_idx = await self._get(["table_name", "col_name", "col_idx"])
        tables[table_name] = tables[table_name].drop(columns=[col_idx])
        return tables

@table_action_type
class ReplaceVals(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-exchange-alt", "fas fa-edit"]
        self.args.update({
            "replace_vals": {"type": "dict", 
                             "label": "Replace Domain:", 
                             "dict_options": {'create': True, 'remove': True, 'placeholder': {'key': 'To Replace', 'value': 'Replace By'}}
                            }
        })

    def get_name(self):
        return f"Replace values in column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, replace_vals, col_idx, col_dtype = await self._get(["table_name", "col_name", "replace_vals", "col_idx", "col_dtype"])
        
        if col_dtype.startswith('int') or col_dtype.startswith('float'):
            dtype_type = np.dtype(col_dtype).type
            replace_vals = {dtype_type(k): dtype_type(v) for k, v in replace_vals.items()}
        elif col_dtype.startswith('bool'):
            falses = ['False', 'false', '0']
            replace_vals = {False if k in falses else True: False if v in falses else True for k, v in replace_vals.items()}
        
        tables[table_name][col_idx] = tables[table_name][col_idx].replace(replace_vals)
        return tables

@table_action_type
class RemoveUnderOver(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-cut", "fas fa-arrows-alt-h"]
        self.args.update({
            "lower_bound": {"type": "number", "label": "Lower Bound"},
            "upper_bound": {"type": "number", "label": "Upper Bound"},
        })

    def get_name(self):
        return f"Keep values in [{self.form_data.get('lower_bound', '?')}, {self.form_data.get('upper_bound', '?')}] of column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, lower_bound, upper_bound, col_idx = await self._get(["table_name", "col_name", "lower_bound", "upper_bound", "col_idx"])
        lower_bound = float(lower_bound)
        upper_bound = float(upper_bound)
        tables[table_name] = tables[table_name][(tables[table_name][col_idx] >= lower_bound) & (tables[table_name][col_idx] <= upper_bound)]
        return tables

@table_action_type
class NLargest(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-arrow-up", "fas fa-sort-numeric-up"]
        self.args.update({
            "n": {"type": "number", "label": "N"},
            "keep": {"type": "select", "label": "Keep",
                     "select_options": [("first", "First"), ("last", "Last"), ("all", "All")],
                     "info": "If some lines have similar values:<br/> -'First' will keep the first one<br/> -'Last' will keep the last one<br/> -'All' will keep all of them (even if the number of elements is bigger than expected).", 
                    },
        })

    def get_name(self):
        return f"Keep {self.form_data.get('n', '?')} largest values of column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        tables[table_name] = tables[table_name].nlargest(int(n), [col_idx], keep=keep)
        return tables
    
@table_action_type
class NSmallest(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-arrow-down", "fas fa-sort-numeric-down"]
        self.args.update({
            "n": {"type": "number", "label": "N"},
            "keep": {"type": "select", "label": "Keep",
                     "select_options": [("first", "First"), ("last", "Last"), ("all", "All")],
                     "info": "If some lines have similar values:<br/> -'First' will keep the first one<br/> -'Last' will keep the last one<br/> -'All' will keep all of them (even if the number of elements is bigger than expected).", 
                    },
        })

    def get_name(self):
        return f"Keep {self.form_data.get('n', '?')} smallest values of column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        tables[table_name] = tables[table_name].nsmallest(int(n), [col_idx], keep=keep)
        return tables

@table_action_type
class RenameColumn(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-tag", "fas fa-edit"]
        self.args.update({
            "new_col_name": {"type": "text", "label": "New Col. Name"},
        })

    def get_name(self):
        return f"Rename column '{self.form_data.get('col_name', '?')}' to '{self.form_data.get('new_col_name', '?')}' in table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, new_col_name, col_idx = await self._get(["table_name", "col_name", "new_col_name", "col_idx"])
        if isinstance(col_idx, tuple):
            new_cols = [(val1, val2 if (val1, val2) != col_idx else new_col_name) for val1, val2 in tables[table_name].columns.tolist()]
            tables[table_name].columns = pd.MultiIndex.from_tuples(new_cols)
        else:
            tables[table_name].rename(columns={col_idx: new_col_name}, inplace=True)
        return tables

@table_action_type
class CutValues(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-cut", "fas fa-chart-pie"]
        self.args.update({
            "cut_values": {"type": "text", "label": "Cut Values", "info": "Comma separated. E.g. 0,10,20,30"},
            "cut_labels": {"type": "text", "label": "Cut Labels", "info": "Comma separated. E.g. low,middle,high'"},
        })

    def get_name(self):
        return f"Cut values in column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, cut_values, cut_labels, col_idx = await self._get(["table_name", "col_name", "cut_values", "cut_labels", "col_idx"])
        cut_values_list = [float(val) for val in cut_values.split(',')]
        cut_labels_list = cut_labels.split(',')
        tables[table_name][col_idx] = pd.cut(tables[table_name][col_idx], bins=cut_values_list, labels=cut_labels_list)
        return tables

@table_action_type
class SortColumn(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-sort", "fas fa-columns"]
        self.args.update({
            "sort_order": {"type": "select", "label": "Sort Order", 
                           "select_options": [("ascending", "Ascending"), ("descending", "Descending"), ("custom", "Custom")], 
                           "onchange": "onchangeFormValue('SortColumn_sort_order', event)",},
            "sort_key": {"type": "textarea", "label": "Sort Key", 
                         "info": "Key must be python code with x as the col values. E.g. x.str.len(), x**2, ... (in practice this will execute: key=lambda x: ...your_input...).", 
                         "required": True, "onchange_visibility": ["SortColumn_sort_order", "custom"]},
        })

    def get_name(self):
        return f"Sort column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, col_idx, sort_order, sort_key = await self._get(["table_name", "col_name", "col_idx", "sort_order", "sort_key"])
        
        if sort_order == "custom":
            key_func = eval(f"lambda x: {sort_key}")
            tables[table_name] = tables[table_name].sort_values(by=[col_idx], key=key_func)
        elif sort_order == "ascending":
            tables[table_name] = tables[table_name].sort_values(by=[col_idx], ascending=True)
        elif sort_order == "descending":
            tables[table_name] = tables[table_name].sort_values(by=[col_idx], ascending=False)
        else:
            raise ValueError("Invalid sort order")
        
        return tables

@table_action_type
class ChangeType(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-exchange-alt", "fas fa-database"]
        self.args.update({
            "new_type": {"type": "select", "label": "New Type", 
                         "select_options": [("int", "Integer"), ("float", "Float"), 
                                     ("string", "String"), ("bool", "Boolean"), ("category", "Category"), 
                                     ("datetime", "Datetime")]},
                })

    def get_name(self):
        return f"Change type of column '{self.form_data.get('col_name', '?')}' to '{self.form_data.get('new_type', '?')}' in table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, new_type, col_idx = await self._get(["table_name", "col_name", "new_type", "col_idx"])

        if new_type == "datetime":
            tables[table_name][col_idx] = pd.to_datetime(tables[table_name][col_idx])
        else:
            tables[table_name][col_idx] = tables[table_name][col_idx].astype(new_type)

        return tables

@table_action_type
class NormalizeColumn(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-balance-scale", "fas fa-chart-line"]
        self.args.update({
            "method": {"type": "select", "label": "Method", 
                       "select_options": [("min_max", "Min-Max"), ("z_score", "Z Score")]}
        })

    def get_name(self):
        return f"Normalize column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, method, col_idx = await self._get(["table_name", "col_name", "method", "col_idx"])
        
        if method == "min_max":
            col_data = tables[table_name][col_idx]
            tables[table_name][col_idx] = (col_data - col_data.min()) / (col_data.max() - col_data.min())
        elif method == "z_score":
            col_data = tables[table_name][col_idx]
            tables[table_name][col_idx] = (col_data - col_data.mean()) / col_data.std()
        else:
            raise ValueError("Invalid normalization method")
        return tables

@table_action_type
class HandleMissingValues(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-question-circle", "fas fa-tools"]
        self.args.update({
            "action": {"type": "select", "label": "Action", 
                       "select_options": [("delete", "Delete"), ("replace", "Replace"), ("interpolate", "Interpolate")],
                       "onchange": "onchangeFormValue('HandleMissingValues_action', event)",
                       "info": "Interpolate will only work for numeric columns."},
            "replace_value": {"type": "textarea", "label": "Replace Value", 
                              "required": True, "onchange_visibility": ["HandleMissingValues_action", "replace"]},
        })

    def get_name(self):
        return f"Handle missing values in column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, action, replace_value, col_idx = await self._get(["table_name", "col_name", "action", "replace_value", "col_idx"])
        
        if action == "delete":
            tables[table_name] = tables[table_name].dropna(subset=[col_idx])
        elif action == "replace":
            replace_val = eval(replace_value)
            tables[table_name][col_idx] = tables[table_name][col_idx].fillna(replace_val)
        elif action == "interpolate":
            tables[table_name][col_idx] = tables[table_name][col_idx].interpolate()
        else:
            raise ValueError("Invalid action for handling missing values")

        return tables

@table_action_type
class ApplyFunction(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-function", "fas fa-code"]
        self.args.update({
            "function": {"type": "textarea", "label": "Function", 
                         "info": "Function must be python code with 'row['Col_name']' as the col values. E.g. row['Col_name'].str.len(), row['Col_name'] * -1 if row['Col_name'] < 0 else row['Col_name'], ...",},
        })

    def get_name(self):
        return f"Apply custom function to column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, function, col_idx = await self._get(["table_name", "col_name", "function", "col_idx"])
        func = eval(f"lambda row: {function}")
        tables[table_name][col_idx] = tables[table_name].apply(func, axis=1)
        return tables

@table_action_type
class ColDiff(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-chart-line", "fas fa-minus"]
        self.args.update({
            "periods": {"type": "number", "label": "Periods"},
        })

    def get_name(self):
        return f"Calculate difference of column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, periods, col_idx = await self._get(["table_name", "col_name", "periods", "col_idx"])
        if isinstance(col_idx, tuple):
            new_col_idx = (col_idx[0], f"{col_idx[1]}-diff")
        else:
            new_col_idx = f"{col_idx}-diff"
        tables[table_name][new_col_idx] = tables[table_name][col_idx].diff(periods=int(periods))
        return tables

@table_action_type
class MathOperations(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-calculator", "fas fa-square-root-alt"]
        self.args.update({
            "operation": {"type": "select", "label": "Operation", 
                         "select_options": [("log", "Log"), ("sqrt", "Square Root"), ("abs", "Absolute"), ("round", "Round")],
                         "onchange": "onchangeFormValue('MathOperations_operation', event)",},
            "decimals": {"type": "number", "label": "Decimals", 
                        "required": False, "onchange_visibility": ["MathOperations_operation", "round"],
                        "info": "Number of decimal places to round to"},
        })

    def get_name(self):
        return f"Apply {self.form_data.get('operation', '?')} operation to column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"
  
    async def execute(self, tables):
        table_name, col_name, operation, decimals, col_idx = await self._get(["table_name", "col_name", "operation", "decimals", "col_idx"])
        
        if operation == "log":
            tables[table_name][col_idx] = tables[table_name][col_idx].apply(lambda x: np.log(x) if x > 0 else float('nan'))
        elif operation == "sqrt":
            tables[table_name][col_idx] = tables[table_name][col_idx].apply(lambda x: np.sqrt(x) if x >= 0 else float('nan'))
        elif operation == "abs":
            tables[table_name][col_idx] = tables[table_name][col_idx].abs()
        elif operation == "round":
            decimals_val = int(decimals) if decimals else 0
            tables[table_name][col_idx] = tables[table_name][col_idx].round(decimals_val)
        else:
            raise ValueError("Invalid math operation")
        return tables

@table_action_type
class ReplaceInCell(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-search", "fas fa-exchange-alt"]
        self.args.update({
            "action": {"type": "select", "label": "Action", 
                       "select_options": [("whitespace", "White spaces"), ("regex", "Regex")],
                       "onchange": "onchangeFormValue('ReplaceInCell_action', event)"},
            "regex": {"type": "textarea", "label": "Regex", 
                      "info": "Regex pattern to replace in every cell: E.g. '\\d+' matches digits; '\\x' matches all x; ...",
                      "required": True, "onchange_visibility": ["ReplaceInCell_action", "regex"]},
            "replacement": {"type": "text", "label": "Replacement"},
        })

    def get_name(self):
        return f"Replace values in cell in column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, col_idx, action, regex, replacement = await self._get(["table_name", "col_name", "col_idx", "action", "regex", "replacement"])
        
        if action == "whitespace":
            tables[table_name][col_idx] = tables[table_name][col_idx].str.replace(r'\s+', replacement, regex=True)
        elif action == "regex":
            tables[table_name][col_idx] = tables[table_name][col_idx].str.replace(regex, replacement, regex=True)
        else:
            raise ValueError("Invalid action for replacing in cell")
        return tables
    
@table_action_type
class FormatString(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-font", "fas fa-text-height"]
        self.args.update({
            "operation": {"type": "select", "label": "Operation", 
                         "select_options": [("upper", "Upper Case (HELLO WORLD)"), ("lower", "Lower Case (hello world)"), ("title", "Title Case (Hello World)"), ("capitalize", "Capitalize First Letter (Hello world)"),
                                            ("strip", "Remove start/end Whitespace (xxx)"), ("lstrip", "Remove start Whitespace (xxx )"), ("rstrip", "Remove end Whitespace ( xxx)")],},
        })

    def get_name(self):
        return f"Format string in column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

    async def execute(self, tables):
        table_name, col_name, operation, col_idx = await self._get(["table_name", "col_name", "operation", "col_idx"])
        
        str_methods = {
            "upper": lambda s: s.str.upper(),
            "lower": lambda s: s.str.lower(),
            "title": lambda s: s.str.title(),
            "capitalize": lambda s: s.str.capitalize(),
            "strip": lambda s: s.str.strip(),
            "lstrip": lambda s: s.str.lstrip(),
            "rstrip": lambda s: s.str.rstrip()
        }
        
        if operation not in str_methods:
            raise ValueError("Invalid string operation")
        
        tables[table_name][col_idx] = str_methods[operation](tables[table_name][col_idx])
        return tables
