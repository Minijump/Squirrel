from .actions import Action, table_action_type

@table_action_type
class DeleteRow(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "delete_domain": {"type": "txt", "string": "Domain", "info": "With format Col1 &lt; Col2, Colx == 'Value',...."},
        }

    async def execute(self):
        table_name, delete_domain = await self._get(["table_name", "delete_domain"])
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].query("not ({delete_domain})")  #sq_action:Delete rows where {delete_domain} in table {table_name}"""
        return new_code
