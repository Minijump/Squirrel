from .actions import TABLE_ACTION_REGISTRY

class ActionFactory:
    @staticmethod
    def init_action(form_data):
        action_name = form_data.get("action_name")
        ActionClass = TABLE_ACTION_REGISTRY.get(action_name)
        if not ActionClass:
            raise ValueError(f"Action {action_name} not found")
        action_instance = ActionClass(form_data)
        return action_instance
