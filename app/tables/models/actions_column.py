from .actions import Action, table_action_type

def convert_col_idx(col_idx):
    if col_idx[0] != '(':
        col_idx = f"'{col_idx}'"
    return col_idx

@table_action_type
class AddColumn(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "col_name": {"type": "str", "string": "Col. Name"},
            "col_value": {"type": "txt", "string": "Col. Value"},
        }

    async def execute(self):
        table_name, col_name, col_value = await self._get(["table_name", "col_name", "col_value"])
        new_code = f"""dfs['{table_name}']['{col_name}'] = {col_value}  #sq_action:Add column {col_name} on table {table_name}"""
        return new_code

class ActionColumn(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args.update({
            "col_name": {"type": "str", "invisible": True},
            "col_identifier": {"type": "str", "invisible": True},
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
            "replace_vals": {"type": "txt", 
                             "string": "Replace Domain:", 
                             "info": "With format {'to_replace1': 'replacing1', 'to_replace2': 'replacing2', ...}"},
        })

    async def execute(self):
        table_name, col_name, replace_vals, col_identifier = await self._get(["table_name", "col_name", "replace_vals", "col_identifier"])
        new_code = f"""dfs['{table_name}']{col_identifier} = dfs['{table_name}']{col_identifier}.replace({replace_vals})  #sq_action:Replace values in column {col_name} of table {table_name}"""
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
        table_name, col_name, lower_bound, upper_bound, col_identifier = await self._get(["table_name", "col_name", "lower_bound", "upper_bound", "col_identifier"])
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'][(dfs['{table_name}']{col_identifier} >= {lower_bound}) & (dfs['{table_name}']{col_identifier} <= {upper_bound})]  #sq_action:Remove vals out of [{lower_bound}, {upper_bound}] in column {col_name} of table {table_name}"""
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
        table_name, col_name, cut_values, cut_labels, col_identifier = await self._get(["table_name", "col_name", "cut_values", "cut_labels", "col_identifier"])
        cut_values = [int(val) for val in cut_values.split(',')]
        cut_labels = cut_labels.split(',')
        new_code = f"""dfs['{table_name}']{col_identifier} = pd.cut(dfs['{table_name}']{col_identifier}, bins={cut_values}, labels={cut_labels})  #sq_action:Cut values in column {col_name} of table {table_name}"""
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
                         "options": [("int", "Integer"), ("float", "Float"), ("string", "String"), ("bool", "Boolean"), ("category", "Category")]}
        })

    async def execute(self):
        table_name, col_name, new_type, col_idx = await self._get(["table_name", "col_name", "new_type", "col_idx"])
        new_code = f"""dfs['{table_name}'][{col_idx}] = dfs['{table_name}'][{col_idx}].astype('{new_type}')  #sq_action:Change type of column {col_name} to {new_type} in table {table_name}"""
        return new_code
