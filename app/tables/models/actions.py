TABLE_ACTION_REGISTRY = {}
def table_action_type(cls):
    TABLE_ACTION_REGISTRY[cls.__name__] = cls
    return cls

class Action:
    def __init__(self, request):
        self.request = request
        self.args = {}

    async def _get(self, args_list):
        form_data = await self.request.form()
        return (form_data.get(arg) for arg in args_list)
    
    async def execute(self):
        raise NotImplementedError("Subclasses must implement this method")
