import ast
import numpy as np

from .action_factory import table_action_type
from app.data_sources.models.data_source_factory import DataSourceFactory
from app.tables.models.table_manager import TableManager
from app.projects.models.project import Project

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

    async def get_code(self):
        table_name, subset, keep = await self._get(["table_name", "subset", "keep"])
        subset = ast.literal_eval(subset)
        keep_val = f"""'{keep}'""" if keep != 'false' else False
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].drop_duplicates(subset={subset or None}, keep={keep_val})"""
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

# ACTION FOR COLUMNS --------------------------------------------------------------------------------------------------------

class ActionColumn(Action):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.args.update({
            "col_name": {"type": "text", "invisible": True},
            "col_idx": {"type": "text", "invisible": True},
            "col_dtype": {"type": "text", "invisible": True},
        })

    async def _get(self, args_list):
        form_data = self.form_data
        data = []
        for arg in args_list:
            arg_data = form_data.get(arg)
            if arg == 'col_idx':
                arg_data = convert_col_idx(arg_data)
            data.append(arg_data)
        return tuple(data)
    
@table_action_type
class DropColumn(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.icons = ["fas fa-trash", "fas fa-columns"]

    def get_name(self):
        return f"Drop column '{self.form_data.get('col_name', '?')}' in table '{self.form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, col_name, col_idx = await self._get(["table_name", "col_name", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].drop(columns=[{col_idx}])"""
        return new_code

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

    async def get_code(self):
        table_name, col_name, replace_vals, col_idx, col_dtype = await self._get(["table_name", "col_name", "replace_vals", "col_idx", "col_dtype"])
        if col_dtype.startswith('int') or col_dtype.startswith('float'):
            dtype_type = np.dtype(col_dtype).type
            replace_vals = {dtype_type(k): dtype_type(v) for k, v in ast.literal_eval(replace_vals).items()}
        elif col_dtype.startswith('bool'):
            falses = ['False', 'false', '0']
            replace_vals = {False if k in falses else True: False if v in falses else True for k, v in ast.literal_eval(replace_vals).items()}
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].replace({replace_vals})"""
        return new_code

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

    async def get_code(self):
        table_name, col_name, lower_bound, upper_bound, col_idx = await self._get(["table_name", "col_name", "lower_bound", "upper_bound", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'][(tables['{table_name}'][{col_idx}] >= {lower_bound}) & (tables['{table_name}'][{col_idx}] <= {upper_bound})]"""
        return new_code

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

    async def get_code(self):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].nlargest({n}, [{col_idx}], keep='{keep}')"""
        return new_code
    
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

    async def get_code(self):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].nsmallest({n}, [{col_idx}], keep='{keep}')"""
        return new_code

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

    async def get_code(self):
        table_name, col_name, new_col_name, col_idx = await self._get(["table_name", "col_name", "new_col_name", "col_idx"])
        if col_idx.startswith('(') and col_idx.endswith(')'):
            new_code = f"""new_cols = [(val1, val2 if (val1, val2) != {col_idx} else '{new_col_name}') for val1, val2 in tables['{table_name}'].columns.tolist()]
tables['{table_name}'].columns = pd.MultiIndex.from_tuples(new_cols)"""
        else:
            new_code = f"""tables['{table_name}'].rename(columns={{{col_idx}: '{new_col_name}'}}, inplace=True)"""
        return new_code

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

    async def get_code(self):
        table_name, col_name, cut_values, cut_labels, col_idx = await self._get(["table_name", "col_name", "cut_values", "cut_labels", "col_idx"])
        cut_values = [float(val) for val in cut_values.split(',')]
        cut_labels = cut_labels.split(',')
        new_code = f"""tables['{table_name}'][{col_idx}] = pd.cut(tables['{table_name}'][{col_idx}], bins={cut_values}, labels={cut_labels})"""
        return new_code

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

    async def get_code(self):
        table_name, col_name, col_idx, sort_order, sort_key = await self._get(["table_name", "col_name", "col_idx", "sort_order", "sort_key"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].sort_values(by=[{col_idx}], """
        if sort_order == "custom":
            new_code += f"""key=lambda x: {sort_key})"""
        elif sort_order == "ascending":
            new_code += f"""ascending=True)"""
        elif sort_order == "descending":
            new_code += f"""ascending=False)"""
        else:
            raise ValueError("Invalid sort order")
    
        return new_code

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

    async def get_code(self):
        table_name, col_name, new_type, col_idx = await self._get(["table_name", "col_name", "new_type", "col_idx"])

        if new_type == "datetime":
            new_code = f"""tables['{table_name}'][{col_idx}] = pd.to_datetime(tables['{table_name}'][{col_idx}])"""
        else:
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].astype('{new_type}')"""

        return new_code

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

    async def get_code(self):
        table_name, col_name, method, col_idx = await self._get(["table_name", "col_name", "method", "col_idx"])
        if method == "min_max":
            new_code = f"""tables['{table_name}'][{col_idx}] = (tables['{table_name}'][{col_idx}] - tables['{table_name}'][{col_idx}].min()) / (tables['{table_name}'][{col_idx}].max() - tables['{table_name}'][{col_idx}].min())"""
        elif method == "z_score":
            new_code = f"""tables['{table_name}'][{col_idx}] = (tables['{table_name}'][{col_idx}] - tables['{table_name}'][{col_idx}].mean()) / tables['{table_name}'][{col_idx}].std()"""
        else:
            raise ValueError("Invalid normalization method")
        return new_code

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

    async def get_code(self):
        table_name, col_name, action, replace_value, col_idx = await self._get(["table_name", "col_name", "action", "replace_value", "col_idx"])
        if action == "delete":
            new_code = f"""tables['{table_name}'] = tables['{table_name}'].dropna(subset=[{col_idx}])"""
        elif action == "replace":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].fillna({replace_value})"""
        elif action == "interpolate":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].interpolate()"""
        else:
            raise ValueError("Invalid action for handling missing values")

        return new_code

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

    async def get_code(self):
        table_name, col_name, function, col_idx = await self._get(["table_name", "col_name", "function", "col_idx"])
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'].apply(lambda row: {function}, axis=1)"""
        return new_code

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

    async def get_code(self):
        table_name, col_name, periods, col_idx = await self._get(["table_name", "col_name", "periods", "col_idx"])
        new_col_idx = col_idx.replace(", ", "-").replace("'", "").replace("(", "").replace(")", "") + "-diff"
        new_code = f"""tables['{table_name}']['{new_col_idx}'] = tables['{table_name}'][{col_idx}].diff(periods={periods})"""
        return new_code
# DEMO NEW STRCT
# @table_action_type
# class ColDiff(ActionColumn):
#     def __init__(self, form_data):
#         super().__init__(form_data)
#         self.icons = ["fas fa-chart-line", "fas fa-minus"]
#         self.args.update({
#             "periods": {"type": "number", "label": "Periods"},
#         })

#     def get_name(self):
#         return f"Calculate difference of column '{self.form_data.get('col_name', '?')}' of table '{self.form_data.get('table_name', '?')}'"

#     async def execute(self, tables):
#         import pandas as pd
#         fct = pd.DataFrame.diff
#         table_name, col_name, periods, col_idx = await self._get(["table_name", "col_name", "periods", "col_idx"])
#         new_col_idx = col_idx.replace(", ", "-").replace("'", "").replace("(", "").replace(")", "") + "-diff"
#         tables[table_name][new_col_idx] = fct(tables[table_name][col_idx], periods=periods)
#         return tables

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
  
    async def get_code(self):
        table_name, col_name, operation, decimals, col_idx = await self._get(["table_name", "col_name", "operation", "decimals", "col_idx"])
        if operation == "log":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].apply(lambda x: __import__('math').log(x) if x > 0 else float('nan'))"""
        elif operation == "sqrt":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].apply(lambda x: __import__('math').sqrt(x) if x >= 0 else float('nan'))"""
        elif operation == "abs":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].abs()"""
        elif operation == "round":
            decimals = decimals or 0
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].round({decimals})"""
        else:
            raise ValueError("Invalid math operation")
        return new_code

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

    async def get_code(self):
        table_name, col_name, col_idx, action, regex, replacement = await self._get(["table_name", "col_name", "col_idx", "action", "regex", "replacement"])
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].str.replace"""
        if action == "whitespace":
            new_code += f"""(r'\\s+', '{replacement}', regex=True)"""
        elif action == "regex":
            new_code += f"""(r'{regex}', '{replacement}', regex=True)"""
        else:
            raise ValueError("Invalid action for replacing in cell")
        return new_code
    
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

    async def get_code(self):
        table_name, col_name, operation, col_idx = await self._get(["table_name", "col_name", "operation", "col_idx"])
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].str."""
        if operation == "upper":
            new_code += f"""upper()"""
        elif operation == "lower":
            new_code += f"""lower()"""
        elif operation == "title":
            new_code += f"""title()"""
        elif operation == "capitalize":
            new_code += f"""capitalize()"""
        elif operation == "strip":
            new_code += f"""strip()"""
        elif operation == "lstrip":
            new_code += f"""lstrip()"""
        elif operation == "rstrip":
            new_code += f"""rstrip()"""
        else:
            raise ValueError("Invalid string operation")
        return new_code
