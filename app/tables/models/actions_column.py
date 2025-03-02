from .actions import Action, table_action_type


def convert_col_idx(col_idx):
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    return col_idx

class ActionColumn(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "col_name": {"type": "str", "invisible": True},
            "col_idx": {"type": "str", "invisible": True},
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
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].drop(columns=[{col_idx}])  #sq_action:Delete column {col_name} on table {table_name}"""
        return new_code

@table_action_type
class ReplaceVals(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "replace_vals": {"type": "dict", 
                             "string": "Replace Domain:", 
                             "info": "With format {'to_replace1': 'replacing1', 'to_replace2': 'replacing2', ...}"},
        })

    async def execute(self):
        table_name, col_name, replace_vals, col_idx = await self._get(["table_name", "col_name", "replace_vals", "col_idx"])
        new_code = f"""dfs['{table_name}'][{col_idx}] = dfs['{table_name}'][{col_idx}].replace({replace_vals})  #sq_action:Replace values in column {col_name} of table {table_name}"""
        return new_code

@table_action_type
class RemoveUnderOver(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "lower_bound": {"type": "number", "string": "Lower Bound"},
            "upper_bound": {"type": "number", "string": "Upper Bound"},
        })

    async def execute(self):
        table_name, col_name, lower_bound, upper_bound, col_idx = await self._get(["table_name", "col_name", "lower_bound", "upper_bound", "col_idx"])
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'][(dfs['{table_name}'][{col_idx}] >= {lower_bound}) & (dfs['{table_name}'][{col_idx}] <= {upper_bound})]  #sq_action:Remove vals out of [{lower_bound}, {upper_bound}] in column {col_name} of table {table_name}"""
        return new_code

@table_action_type
class NLargest(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "n": {"type": "number", "string": "N"},
            "keep": {"type": "select", "string": "Keep",
                     "options": [("first", "First"), ("last", "Last"), ("all", "All")],
                     "info": "If some lines have similar values:<br/> -'First' will keep the first one<br/> -'Last' will keep the last one<br/> -'All' will keep all of them (even if the number of elements is bigger than expected).", 
},
        })

    async def execute(self):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].nlargest({n}, [{col_idx}], keep='{keep}')  #sq_action:Get {n} largest values in column {col_name} of table {table_name}"""
        return new_code
    
@table_action_type
class NSmallest(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "n": {"type": "number", "string": "N"},
            "keep": {"type": "select", "string": "Keep",
                     "options": [("first", "First"), ("last", "Last"), ("all", "All")],
                     "info": "If some lines have similar values:<br/> -'First' will keep the first one<br/> -'Last' will keep the last one<br/> -'All' will keep all of them (even if the number of elements is bigger than expected).", 
},
        })

    async def execute(self):
        table_name, col_name, n, keep, col_idx = await self._get(["table_name", "col_name", "n", "keep", "col_idx"])
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].nsmallest({n}, [{col_idx}], keep='{keep}')  #sq_action:Get {n} smallest values in column {col_name} of table {table_name}"""
        return new_code

@table_action_type
class RenameColumn(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "new_col_name": {"type": "str", "string": "New Col. Name"},
        })

    async def execute(self):
        table_name, col_name, new_col_name, col_idx = await self._get(["table_name", "col_name", "new_col_name", "col_idx"])
        new_code = f"""dfs['{table_name}'].rename(columns={{{col_idx}: '{new_col_name}'}}, inplace=True)  #sq_action:Rename column {col_name} to {new_col_name} in table {table_name}"""
        return new_code

@table_action_type
class CutValues(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "cut_values": {"type": "str", "string": "Cut Values", "info": "Comma separated. E.g. 0,10,20,30"},
            "cut_labels": {"type": "str", "string": "Cut Labels", "info": "Comma separated. E.g. low,middle,high'"},
        })

    async def execute(self):
        table_name, col_name, cut_values, cut_labels, col_idx = await self._get(["table_name", "col_name", "cut_values", "cut_labels", "col_idx"])
        cut_values = [float(val) for val in cut_values.split(',')]
        cut_labels = cut_labels.split(',')
        new_code = f"""dfs['{table_name}'][{col_idx}] = pd.cut(dfs['{table_name}'][{col_idx}], bins={cut_values}, labels={cut_labels})  #sq_action:Cut values in column {col_name} of table {table_name}"""
        return new_code

@table_action_type
class SortColumn(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "sort_order": {"type": "select", "string": "Sort Order", 
                           "options": [("ascending", "Ascending"), ("descending", "Descending"), ("custom", "Custom")], 
                           "onchange": "toggleSelect()"},
            "sort_key": {"type": "txt", "string": "Sort Key", 
                         "info": "Key must be python code with x as the col values. E.g. x.str.len(), x**2, ... (in practice this will execute: key=lambda x: ...your_input...).", 
                         "required": False, "select_onchange": "custom"}
        })

    async def execute(self):
        table_name, col_name, col_idx, sort_order, sort_key = await self._get(["table_name", "col_name", "col_idx", "sort_order", "sort_key"])
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].sort_values(by=[{col_idx}], """
        if sort_order == "custom":
            new_code += f"""key=lambda x: {sort_key})  #sq_action:Sort {col_name} of table {table_name} with custom key"""
        elif sort_order == "ascending":
            new_code += f"""ascending=True)  #sq_action:Sort(asc) {col_name} of table {table_name}"""
        elif sort_order == "descending":
            new_code += f"""ascending=False)  #sq_action:Sort(desc) {col_name} of table {table_name}"""
        else:
            raise ValueError("Invalid sort order")
    
        return new_code

@table_action_type
class ChangeType(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "new_type": {"type": "select", "string": "New Type", 
                         "options": [("int", "Integer"), ("float", "Float"), 
                                     ("string", "String"), ("bool", "Boolean"), ("category", "Category"), 
                                     ("datetime", "Datetime")]},
                })

    async def execute(self):
        table_name, col_name, new_type, col_idx = await self._get(["table_name", "col_name", "new_type", "col_idx"])

        if new_type == "datetime":
            new_code = f"""dfs['{table_name}'][{col_idx}] = pd.to_datetime(dfs['{table_name}'][{col_idx}])  #sq_action:Change type of column {col_name} to {new_type} in table {table_name}"""
        else:
            new_code = f"""dfs['{table_name}'][{col_idx}] = dfs['{table_name}'][{col_idx}].astype('{new_type}')  #sq_action:Change type of column {col_name} to {new_type} in table {table_name}"""

        return new_code

@table_action_type
class NormalizeColumn(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "method": {"type": "select", "string": "Method", 
                       "options": [("min_max", "Min-Max"), ("z_score", "Z Score")]}
        })

    async def execute(self):
        table_name, col_name, method, col_idx = await self._get(["table_name", "col_name", "method", "col_idx"])
        if method == "min_max":
            new_code = f"""dfs['{table_name}'][{col_idx}] = (dfs['{table_name}'][{col_idx}] - dfs['{table_name}'][{col_idx}].min()) / (dfs['{table_name}'][{col_idx}].max() - dfs['{table_name}'][{col_idx}].min())  #sq_action:Normalize column {col_name} in table {table_name} with Min-Max"""
        elif method == "z_score":
            new_code = f"""dfs['{table_name}'][{col_idx}] = (dfs['{table_name}'][{col_idx}] - dfs['{table_name}'][{col_idx}].mean()) / dfs['{table_name}'][{col_idx}].std()  #sq_action:Normalize column {col_name} in table {table_name} with Z Score"""
        else:
            raise ValueError("Invalid normalization method")
        return new_code

@table_action_type
class HandleMissingValues(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "action": {"type": "select", "string": "Action", 
                       "options": [("delete", "Delete"), ("replace", "Replace"), ("interpolate", "Interpolate")],
                       "onchange": "toggleSelect()",
                       "info": "Interpolate will only work for numeric columns."},
            "replace_value": {"type": "txt", "string": "Replace Value", 
                              "required": False, "select_onchange": "replace"},
        })

    async def execute(self):
        table_name, col_name, action, replace_value, col_idx = await self._get(["table_name", "col_name", "action", "replace_value", "col_idx"])
        if action == "delete":
            new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].dropna(subset=[{col_idx}])  #sq_action:Delete rows with missing values in column {col_name} of table {table_name}"""
        elif action == "replace":
            new_code = f"""dfs['{table_name}'][{col_idx}] = dfs['{table_name}'][{col_idx}].fillna({replace_value})  #sq_action:Replace missing values with {replace_value} in column {col_name} of table {table_name}"""
        elif action == "interpolate":
            new_code = f"""dfs['{table_name}'][{col_idx}] = dfs['{table_name}'][{col_idx}].interpolate()  #sq_action:Interpolate missing values in column {col_name} of table {table_name}"""
        else:
            raise ValueError("Invalid action for handling missing values")

        return new_code

@table_action_type
class ApplyFunction(ActionColumn):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "function": {"type": "txt", "string": "Function", 
                         "info": "Function must be python code with 'row['Col_name']' as the col values. E.g. row['Col_name'].str.len(), row['Col_name'] * -1 if row['Col_name'] < 0 else row['Col_name'], ...",},
        })

    async def execute(self):
        table_name, col_name, function, col_idx = await self._get(["table_name", "col_name", "function", "col_idx"])
        new_code = f"""dfs['{table_name}'][{col_idx}] = dfs['{table_name}'].apply(lambda row: {function}, axis=1)  #sq_action:Apply function to column {col_name} of table {table_name}"""
        return new_code
