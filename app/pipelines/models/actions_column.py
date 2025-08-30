import ast
import numpy as np

from .actions_utils import convert_col_idx
from .action_factory import table_action_type

from .actions import Action


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
            if arg == 'col_idx':
                col_idx = convert_col_idx(form_data.get('col_idx'))
                data.append(col_idx)
                continue
            data.append(form_data.get(arg))
        return tuple(data)
    
@table_action_type
class DropColumn(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.name = f"Drop column '{form_data.get('col_name', '?')}' in table '{form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, col_name, col_idx = await self._get(["table_name", "col_name", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].drop(columns=[{col_idx}])"""
        return new_code

@table_action_type
class ReplaceVals(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.args.update({
            "replace_vals": {"type": "dict", 
                             "label": "Replace Domain:", 
                             "dict_options": {'create': True, 'remove': True, 'placeholder': {'key': 'To Replace', 'value': 'Replace By'}}
                            }
        })
        self.name = f"Replace values in column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

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
        self.args.update({
            "lower_bound": {"type": "number", "label": "Lower Bound"},
            "upper_bound": {"type": "number", "label": "Upper Bound"},
        })
        self.name = f"Remove values outside [{form_data.get('lower_bound', '?')}, {form_data.get('upper_bound', '?')}] of column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, col_name, lower_bound, upper_bound, col_idx = await self._get(["table_name", "col_name", "lower_bound", "upper_bound", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'][(tables['{table_name}'][{col_idx}] >= {lower_bound}) & (tables['{table_name}'][{col_idx}] <= {upper_bound})]"""
        return new_code

@table_action_type
class NLargest(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.args.update({
            "n": {"type": "number", "label": "N"},
            "keep": {"type": "select", "label": "Keep",
                     "select_options": [("first", "First"), ("last", "Last"), ("all", "All")],
                     "info": "If some lines have similar values:<br/> -'First' will keep the first one<br/> -'Last' will keep the last one<br/> -'All' will keep all of them (even if the number of elements is bigger than expected).", 
                    },
        })
        self.name = f"Keep {form_data.get('n', '?')} largest values of column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].nlargest({n}, [{col_idx}], keep='{keep}')"""
        return new_code
    
@table_action_type
class NSmallest(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.args.update({
            "n": {"type": "number", "label": "N"},
            "keep": {"type": "select", "label": "Keep",
                     "select_options": [("first", "First"), ("last", "Last"), ("all", "All")],
                     "info": "If some lines have similar values:<br/> -'First' will keep the first one<br/> -'Last' will keep the last one<br/> -'All' will keep all of them (even if the number of elements is bigger than expected).", 
                    },
        })
        self.name = f"Keep {form_data.get('n', '?')} smallest values of column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].nsmallest({n}, [{col_idx}], keep='{keep}')"""
        return new_code

@table_action_type
class RenameColumn(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.args.update({
            "new_col_name": {"type": "text", "label": "New Col. Name"},
        })
        self.name = f"Rename column '{form_data.get('col_name', '?')}' to '{form_data.get('new_col_name', '?')}' in table '{form_data.get('table_name', '?')}'"

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
        self.args.update({
            "cut_values": {"type": "text", "label": "Cut Values", "info": "Comma separated. E.g. 0,10,20,30"},
            "cut_labels": {"type": "text", "label": "Cut Labels", "info": "Comma separated. E.g. low,middle,high'"},
        })
        self.name = f"Cut values in column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

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
        self.args.update({
            "sort_order": {"type": "select", "label": "Sort Order", 
                           "select_options": [("ascending", "Ascending"), ("descending", "Descending"), ("custom", "Custom")], 
                           "onchange": "onchangeFormValue('SortColumn_sort_order', event)",},
            "sort_key": {"type": "textarea", "label": "Sort Key", 
                         "info": "Key must be python code with x as the col values. E.g. x.str.len(), x**2, ... (in practice this will execute: key=lambda x: ...your_input...).", 
                         "required": True, "onchange_visibility": ["SortColumn_sort_order", "custom"]},
        })
        self.name = f"Sort column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

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
        self.args.update({
            "new_type": {"type": "select", "label": "New Type", 
                         "select_options": [("int", "Integer"), ("float", "Float"), 
                                     ("string", "String"), ("bool", "Boolean"), ("category", "Category"), 
                                     ("datetime", "Datetime")]},
                })
        self.name = f"Change type of column '{form_data.get('col_name', '?')}' to '{form_data.get('new_type', '?')}' in table '{form_data.get('table_name', '?')}'"

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
        self.args.update({
            "method": {"type": "select", "label": "Method", 
                       "select_options": [("min_max", "Min-Max"), ("z_score", "Z Score")]}
        })
        self.name = f"Normalize column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

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
        self.args.update({
            "action": {"type": "select", "label": "Action", 
                       "select_options": [("delete", "Delete"), ("replace", "Replace"), ("interpolate", "Interpolate")],
                       "onchange": "onchangeFormValue('HandleMissingValues_action', event)",
                       "info": "Interpolate will only work for numeric columns."},
            "replace_value": {"type": "textarea", "label": "Replace Value", 
                              "required": True, "onchange_visibility": ["HandleMissingValues_action", "replace"]},
        })
        self.name = f"Handle missing values in column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

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
        self.args.update({
            "function": {"type": "textarea", "label": "Function", 
                         "info": "Function must be python code with 'row['Col_name']' as the col values. E.g. row['Col_name'].str.len(), row['Col_name'] * -1 if row['Col_name'] < 0 else row['Col_name'], ...",},
        })
        self.name = f"Apply custom function to column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, col_name, function, col_idx = await self._get(["table_name", "col_name", "function", "col_idx"])
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'].apply(lambda row: {function}, axis=1)"""
        return new_code

@table_action_type
class ColDiff(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.args.update({
            "periods": {"type": "number", "label": "Periods"},
        })
        self.name = f"Calculate difference of column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

    async def get_code(self):
        table_name, col_name, periods, col_idx = await self._get(["table_name", "col_name", "periods", "col_idx"])
        new_col_idx = col_idx.replace(", ", "-").replace("'", "").replace("(", "").replace(")", "") + "-diff"
        new_code = f"""tables['{table_name}']['{new_col_idx}'] = tables['{table_name}'][{col_idx}].diff(periods={periods})"""
        return new_code

@table_action_type
class MathOperations(ActionColumn):
    def __init__(self, form_data):
        super().__init__(form_data)
        self.args.update({
            "operation": {"type": "select", "label": "Operation", 
                         "select_options": [("log", "Log"), ("sqrt", "Square Root"), ("abs", "Absolute"), ("round", "Round")],
                         "onchange": "onchangeFormValue('MathOperations_operation', event)",},
            "decimals": {"type": "number", "label": "Decimals", 
                        "required": False, "onchange_visibility": ["MathOperations_operation", "round"],
                        "info": "Number of decimal places to round to"},
        })
        self.name = f"Apply {form_data.get('operation', '?')} operation to column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

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
        self.args.update({
            "action": {"type": "select", "label": "Action", 
                       "select_options": [("whitespace", "White spaces"), ("regex", "Regex")],
                       "onchange": "onchangeFormValue('ReplaceInCell_action', event)"},
            "regex": {"type": "textarea", "label": "Regex", 
                      "info": "Regex pattern to replace in every cell: E.g. '\\d+' matches digits; '\\x' matches all x; ...",
                      "required": True, "onchange_visibility": ["ReplaceInCell_action", "regex"]},
            "replacement": {"type": "text", "label": "Replacement"},
        })
        self.name = f"Replace values in cell in column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

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
        self.args.update({
            "operation": {"type": "select", "label": "Operation", 
                         "select_options": [("upper", "Upper Case (HELLO WORLD)"), ("lower", "Lower Case (hello world)"), ("title", "Title Case (Hello World)"), ("capitalize", "Capitalize First Letter (Hello world)"),
                                            ("strip", "Remove start/end Whitespace (xxx)"), ("lstrip", "Remove start Whitespace (xxx )"), ("rstrip", "Remove end Whitespace ( xxx)")],},
        })
        self.name = f"Format string in column '{form_data.get('col_name', '?')}' of table '{form_data.get('table_name', '?')}'"

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
