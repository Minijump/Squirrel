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
    
@table_action_type
class DropColumn(Action):
    async def execute(self):
        table_name, col_name, col_idx = await self._get(["table_name", "col_name", "col_idx"])
        col_idx = convert_col_idx(col_idx)
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].drop(columns=[{col_idx}])  #sq_action:Delete column {col_name} on table {table_name}"""
        return new_code

@table_action_type
class ReplaceVals(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "replace_vals": {"type": "txt", "string": "Replace Domain:", "info": "With format {'to_replace1': 'replacing1', 'to_replace2': 'replacing2', ...}"},
            "col_name": {"type": "str", "invisible": True},
            "col_identifier": {"type": "str", "invisible": True},
            "col_idx": {"type": "str", "invisible": True},
        }

    async def execute(self):
        table_name, col_name, replace_vals, col_identifier = await self._get(["table_name", "col_name", "replace_vals", "col_identifier"])
        new_code = f"""dfs['{table_name}']{col_identifier} = dfs['{table_name}']{col_identifier}.replace({replace_vals})  #sq_action:Replace values in column {col_name} of table {table_name}"""
        return new_code
