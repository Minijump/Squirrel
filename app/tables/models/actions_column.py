import ast
import pandas as pd

from .actions_utils import table_action_type, _get_method_sig, convert_col_idx
from .actions import Action


class ActionColumn(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "col_name": {"type": "text", "invisible": True},
            "col_idx": {"type": "text", "invisible": True},
        })

    async def _get(self, args_list):
        form_data = await self.request.form()
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
    async def execute(self):
        table_name, col_name, col_idx = await self._get(["table_name", "col_name", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].drop(columns=[{col_idx}])  #sq_action:Delete column {col_name} on table {table_name}"""
        return new_code

@table_action_type
class ReplaceVals(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.kwargs = _get_method_sig(pd.Series.replace, remove=['inplace', 'limit', 'method'])
        self.args.update({
            "replace_vals": {"type": "dict", 
                             "label": "Replace Domain:", 
                             "info": "With format {'to_replace1': 'replacing1', 'to_replace2': 'replacing2', ...}",
                             "dict_options": {'create': True, 'remove': True}},
        })

    async def execute(self):
        table_name, col_name, replace_vals, col_idx = await self._get(["table_name", "col_name", "replace_vals", "col_idx"])
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].replace({replace_vals})  #sq_action:Replace values in column {col_name} of table {table_name}"""
        return new_code
    
    async def execute_advanced(self):
        table_name, col_name, col_idx, kwargs = await self._get(["table_name", "col_name", "col_idx", "kwargs"])
        kwrags_str = await self._get_kwargs_str(ast.literal_eval(kwargs))
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].replace({kwrags_str})  #sq_action:Replace values in column {col_name} of table {table_name}"""    
        return new_code

@table_action_type
class RemoveUnderOver(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "lower_bound": {"type": "number", "label": "Lower Bound"},
            "upper_bound": {"type": "number", "label": "Upper Bound"},
        })

    async def execute(self):
        table_name, col_name, lower_bound, upper_bound, col_idx = await self._get(["table_name", "col_name", "lower_bound", "upper_bound", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'][(tables['{table_name}'][{col_idx}] >= {lower_bound}) & (tables['{table_name}'][{col_idx}] <= {upper_bound})]  #sq_action:Remove vals out of [{lower_bound}, {upper_bound}] in column {col_name} of table {table_name}"""
        return new_code

@table_action_type
class NLargest(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "n": {"type": "number", "label": "N"},
            "keep": {"type": "select", "label": "Keep",
                     "select_options": [("first", "First"), ("last", "Last"), ("all", "All")],
                     "info": "If some lines have similar values:<br/> -'First' will keep the first one<br/> -'Last' will keep the last one<br/> -'All' will keep all of them (even if the number of elements is bigger than expected).", 
},
        })

    async def execute(self):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].nlargest({n}, [{col_idx}], keep='{keep}')  #sq_action:Get {n} largest values in column {col_name} of table {table_name}"""
        return new_code
    
@table_action_type
class NSmallest(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "n": {"type": "number", "label": "N"},
            "keep": {"type": "select", "label": "Keep",
                     "select_options": [("first", "First"), ("last", "Last"), ("all", "All")],
                     "info": "If some lines have similar values:<br/> -'First' will keep the first one<br/> -'Last' will keep the last one<br/> -'All' will keep all of them (even if the number of elements is bigger than expected).", 
},
        })

    async def execute(self):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].nsmallest({n}, [{col_idx}], keep='{keep}')  #sq_action:Get {n} smallest values in column {col_name} of table {table_name}"""
        return new_code

@table_action_type
class RenameColumn(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "new_col_name": {"type": "text", "label": "New Col. Name"},
        })

    async def execute(self):
        table_name, col_name, new_col_name, col_idx = await self._get(["table_name", "col_name", "new_col_name", "col_idx"])
        if col_idx.startswith('(') and col_idx.endswith(')'):
            new_code = f"""new_cols = [(val1, val2 if (val1, val2) != {col_idx} else '{new_col_name}') for val1, val2 in tables['{table_name}'].columns.tolist()]
tables['{table_name}'].columns = pd.MultiIndex.from_tuples(new_cols) #sq_action:Rename column {col_name} of {col_idx} to {new_col_name} in table {table_name}"""
        else:
            new_code = f"""tables['{table_name}'].rename(columns={{{col_idx}: '{new_col_name}'}}, inplace=True)  #sq_action:Rename column {col_name} to {new_col_name} in table {table_name}"""
        return new_code

@table_action_type
class CutValues(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.kwargs = _get_method_sig(pd.cut, remove=['x', 'retbins', 'duplicates'])
        self.args.update({
            "cut_values": {"type": "text", "label": "Cut Values", "info": "Comma separated. E.g. 0,10,20,30"},
            "cut_labels": {"type": "text", "label": "Cut Labels", "info": "Comma separated. E.g. low,middle,high'"},
        })

    async def execute(self):
        table_name, col_name, cut_values, cut_labels, col_idx = await self._get(["table_name", "col_name", "cut_values", "cut_labels", "col_idx"])
        cut_values = [float(val) for val in cut_values.split(',')]
        cut_labels = cut_labels.split(',')
        new_code = f"""tables['{table_name}'][{col_idx}] = pd.cut(tables['{table_name}'][{col_idx}], bins={cut_values}, labels={cut_labels})  #sq_action:Cut values in column {col_name} of table {table_name}"""
        return new_code
    
    async def execute_advanced(self):
        table_name, col_name, col_idx, kwargs = await self._get(["table_name", "col_name", "col_idx", "kwargs"])
        kwrags_str = await self._get_kwargs_str(ast.literal_eval(kwargs))
        new_code = f"""tables['{table_name}'][{col_idx}] = pd.cut(tables['{table_name}'][{col_idx}], {kwrags_str})  #sq_action:Cut values in column {col_name} of table {table_name}"""    
        return new_code

@table_action_type
class SortColumn(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.kwargs = _get_method_sig(pd.DataFrame.sort_values, remove=['by', 'inplace', 'ignore_index', 'axis'])
        self.args.update({
            "sort_order": {"type": "select", "label": "Sort Order", 
                           "select_options": [("ascending", "Ascending"), ("descending", "Descending"), ("custom", "Custom")], 
                           "onchange": "onchangeFormValue('SortColumn_sort_order', event)",},
            "sort_key": {"type": "textarea", "label": "Sort Key", 
                         "info": "Key must be python code with x as the col values. E.g. x.str.len(), x**2, ... (in practice this will execute: key=lambda x: ...your_input...).", 
                         "required": False, "onchange_visibility": ["SortColumn_sort_order", "custom"]},
        })

    async def execute(self):
        table_name, col_name, col_idx, sort_order, sort_key = await self._get(["table_name", "col_name", "col_idx", "sort_order", "sort_key"])
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].sort_values(by=[{col_idx}], """
        if sort_order == "custom":
            new_code += f"""key=lambda x: {sort_key})  #sq_action:Sort {col_name} of table {table_name} with custom key"""
        elif sort_order == "ascending":
            new_code += f"""ascending=True)  #sq_action:Sort(asc) {col_name} of table {table_name}"""
        elif sort_order == "descending":
            new_code += f"""ascending=False)  #sq_action:Sort(desc) {col_name} of table {table_name}"""
        else:
            raise ValueError("Invalid sort order")
    
        return new_code
    
    async def execute_advanced(self):
        table_name, col_name, col_idx, kwargs = await self._get(["table_name", "col_name", "col_idx", "kwargs"])
        kwrags_str = await self._get_kwargs_str(ast.literal_eval(kwargs))
        new_code = f"""tables['{table_name}'] = tables['{table_name}'].sort_values(by=[{col_idx}], {kwrags_str})  #sq_action:Sort {col_name} of table {table_name} with kwargs"""
        return new_code

@table_action_type
class ChangeType(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "new_type": {"type": "select", "label": "New Type", 
                         "select_options": [("int", "Integer"), ("float", "Float"), 
                                     ("string", "String"), ("bool", "Boolean"), ("category", "Category"), 
                                     ("datetime", "Datetime")]},
                })

    async def execute(self):
        table_name, col_name, new_type, col_idx = await self._get(["table_name", "col_name", "new_type", "col_idx"])

        if new_type == "datetime":
            new_code = f"""tables['{table_name}'][{col_idx}] = pd.to_datetime(tables['{table_name}'][{col_idx}])  #sq_action:Change type of column {col_name} to {new_type} in table {table_name}"""
        else:
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].astype('{new_type}')  #sq_action:Change type of column {col_name} to {new_type} in table {table_name}"""

        return new_code

@table_action_type
class NormalizeColumn(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "method": {"type": "select", "label": "Method", 
                       "select_options": [("min_max", "Min-Max"), ("z_score", "Z Score")]}
        })

    async def execute(self):
        table_name, col_name, method, col_idx = await self._get(["table_name", "col_name", "method", "col_idx"])
        if method == "min_max":
            new_code = f"""tables['{table_name}'][{col_idx}] = (tables['{table_name}'][{col_idx}] - tables['{table_name}'][{col_idx}].min()) / (tables['{table_name}'][{col_idx}].max() - tables['{table_name}'][{col_idx}].min())  #sq_action:Normalize column {col_name} in table {table_name} with Min-Max"""
        elif method == "z_score":
            new_code = f"""tables['{table_name}'][{col_idx}] = (tables['{table_name}'][{col_idx}] - tables['{table_name}'][{col_idx}].mean()) / tables['{table_name}'][{col_idx}].std()  #sq_action:Normalize column {col_name} in table {table_name} with Z Score"""
        else:
            raise ValueError("Invalid normalization method")
        return new_code

@table_action_type
class HandleMissingValues(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "action": {"type": "select", "label": "Action", 
                       "select_options": [("delete", "Delete"), ("replace", "Replace"), ("interpolate", "Interpolate")],
                       "onchange": "onchangeFormValue('HandleMissingValues_action', event)",
                       "info": "Interpolate will only work for numeric columns."},
            "replace_value": {"type": "textarea", "label": "Replace Value", 
                              "required": False, "onchange_visibility": ["HandleMissingValues_action", "replace"]},
        })

    async def execute(self):
        table_name, col_name, action, replace_value, col_idx = await self._get(["table_name", "col_name", "action", "replace_value", "col_idx"])
        if action == "delete":
            new_code = f"""tables['{table_name}'] = tables['{table_name}'].dropna(subset=[{col_idx}])  #sq_action:Delete rows with missing values in column {col_name} of table {table_name}"""
        elif action == "replace":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].fillna({replace_value})  #sq_action:Replace missing values with {replace_value} in column {col_name} of table {table_name}"""
        elif action == "interpolate":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].interpolate()  #sq_action:Interpolate missing values in column {col_name} of table {table_name}"""
        else:
            raise ValueError("Invalid action for handling missing values")

        return new_code

@table_action_type
class ApplyFunction(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "function": {"type": "textarea", "label": "Function", 
                         "info": "Function must be python code with 'row['Col_name']' as the col values. E.g. row['Col_name'].str.len(), row['Col_name'] * -1 if row['Col_name'] < 0 else row['Col_name'], ...",},
        })

    async def execute(self):
        table_name, col_name, function, col_idx = await self._get(["table_name", "col_name", "function", "col_idx"])
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'].apply(lambda row: {function}, axis=1)  #sq_action:Apply function to column {col_name} of table {table_name}"""
        return new_code

@table_action_type
class ColDiff(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.kwargs = _get_method_sig(pd.DataFrame.diff, remove=['axis'])
        self.args.update({
            "periods": {"type": "number", "label": "Periods"},
        })

    async def execute(self):
        table_name, col_name, periods, col_idx = await self._get(["table_name", "col_name", "periods", "col_idx"])
        new_col_idx = col_idx.replace(", ", "-").replace("'", "").replace("(", "").replace(")", "") + "-diff"
        new_code = f"""tables['{table_name}']['{new_col_idx}'] = tables['{table_name}'][{col_idx}].diff(periods={periods})  #sq_action:Calculate difference of {col_name} in table {table_name}"""
        return new_code
    
    async def execute_advanced(self):
        table_name, col_name, col_idx, kwargs = await self._get(["table_name", "col_name", "col_idx", "kwargs"])
        kwrags_str = await self._get_kwargs_str(ast.literal_eval(kwargs))
        new_col_idx = col_idx.replace(", ", "-").replace("'", "").replace("(", "").replace(")", "") + "-diff"
        new_code = f"""tables['{table_name}']['{new_col_idx}'] = tables['{table_name}'][{col_idx}].diff({kwrags_str})  #sq_action:Calculate difference of {col_name} in table {table_name}"""    
        return new_code

@table_action_type
class MathOperations(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "operation": {"type": "select", "label": "Operation", 
                         "select_options": [("log", "Log"), ("sqrt", "Square Root"), ("abs", "Absolute"), ("round", "Round")],
                         "onchange": "onchangeFormValue('MathOperations_operation', event)",},
            "decimals": {"type": "number", "label": "Decimals", 
                        "required": False, "onchange_visibility": ["MathOperations_operation", "round"],
                        "info": "Number of decimal places to round to"},
        })

    async def execute(self):
        table_name, col_name, operation, decimals, col_idx = await self._get(["table_name", "col_name", "operation", "decimals", "col_idx"])
        if operation == "log":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].apply(lambda x: __import__('math').log(x) if x > 0 else float('nan'))  #sq_action:Apply log to column {col_name} of table {table_name}"""
        elif operation == "sqrt":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].apply(lambda x: __import__('math').sqrt(x) if x >= 0 else float('nan'))  #sq_action:Apply sqrt to column {col_name} of table {table_name}"""
        elif operation == "abs":
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].abs()  #sq_action:Apply abs to column {col_name} of table {table_name}"""
        elif operation == "round":
            decimals = decimals or 0
            new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].round({decimals})  #sq_action:Round column {col_name} to {decimals} decimals in table {table_name}"""
        else:
            raise ValueError("Invalid math operation")
        return new_code

@table_action_type
class ReplaceInCell(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "action": {"type": "select", "label": "Action", 
                       "select_options": [("whitespace", "White spaces"), ("regex", "Regex")],
                       "onchange": "onchangeFormValue('ReplaceInCell_action', event)"},
            "regex": {"type": "textarea", "label": "Regex", 
                      "info": "Regex pattern to replace in every cell: E.g. '\\d+' matches digits; '\\x' matches all x; ...",
                      "required": False, "onchange_visibility": ["ReplaceInCell_action", "regex"]},
            "replacement": {"type": "text", "label": "Replacement"},
        })

    async def execute(self):
        table_name, col_name, col_idx, action, regex, replacement = await self._get(["table_name", "col_name", "col_idx", "action", "regex", "replacement"])
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].str.replace"""
        if action == "whitespace":
            new_code += f"""(r'\\s+', '{replacement}', regex=True)  #sq_action:Replace whitespace in column {col_name} of table {table_name}"""
        elif action == "regex":
            new_code += f"""(r'{regex}', '{replacement}', regex=True)  #sq_action:Replace regex in column {col_name} of table {table_name}"""
        else:
            raise ValueError("Invalid action for replacing in cell")
        return new_code
    
@table_action_type
class FormatString(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "operation": {"type": "select", "label": "Operation", 
                         "select_options": [("upper", "Upper Case (HELLO WORLD)"), ("lower", "Lower Case (hello world)"), ("title", "Title Case (Hello World)"), ("capitalize", "Capitalize First Letter (Hello world)"),
                                            ("strip", "Remove start/end Whitespace (xxx)"), ("lstrip", "Remove start Whitespace (xxx )"), ("rstrip", "Remove end Whitespace ( xxx)")],},
        })

    async def execute(self):
        table_name, col_name, operation, col_idx = await self._get(["table_name", "col_name", "operation", "col_idx"])
        new_code = f"""tables['{table_name}'][{col_idx}] = tables['{table_name}'][{col_idx}].str."""
        if operation == "upper":
            new_code += f"""upper()  #sq_action:Convert column {col_name} to uppercase in table {table_name}"""
        elif operation == "lower":
            new_code += f"""lower()  #sq_action:Convert column {col_name} to lowercase in table {table_name}"""
        elif operation == "title":
            new_code += f"""title()  #sq_action:Convert column {col_name} to title case in table {table_name}"""
        elif operation == "capitalize":
            new_code += f"""capitalize()  #sq_action:Capitalize column {col_name} in table {table_name}"""
        elif operation == "strip":
            new_code += f"""strip()  #sq_action:Strip whitespace from column {col_name} in table {table_name}"""
        elif operation == "lstrip":
            new_code += f"""lstrip()  #sq_action:Left strip whitespace from column {col_name} in table {table_name}"""
        elif operation == "rstrip":
            new_code += f"""rstrip()  #sq_action:Right strip whitespace from column {col_name} in table {table_name}"""
        else:
            raise ValueError("Invalid string operation")
        return new_code
