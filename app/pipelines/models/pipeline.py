import os

from app.pipelines.models.pipeline_storage import PipelineStorage, PipelineAction


class Pipeline:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.project_path = os.path.join(os.getcwd(), "_projects", project_dir)
        self.storage = PipelineStorage(project_dir)

    async def get_actions(self):
        """
        Get the actions from the pipeline storage.

        Returns a list of tuples containing the action ID, action description, and action code.
        Format: (action_id, action_description, action_parameters_summary)
        """
        actions = self.storage.load_actions()
        result = []
        
        for idx, action in enumerate(actions):
            # Format: (action_id, action_description, action_summary)
            # Create a summary for display and editing
            key_params = {}
            for key, value in action.parameters.items():
                if key not in ['project_dir', 'csrfmiddlewaretoken'] and value:
                    key_params[key] = value
            
            # Create a readable summary
            params_summary = f"Action: {action.action_class}"
            if key_params:
                params_summary += f"\nKey parameters: {key_params}"
            
            result.append((idx, action.description, params_summary))
        
        return result
    
    async def confirm_new_order(self, order: str):
        """Reorder the actions in the pipeline."""
        new_order = [int(action_str.split('-')[0]) for action_str in order.split(",")]
        self.storage.reorder_actions(new_order)

    async def edit_action(self, action_id: int, action_data):
        """Edit an action in the pipeline."""
        # TODO: not working, only edit description
        # action_data should contain the new parameters and optionally description
        if isinstance(action_data, str):
            # If it's a string (legacy code), we need to parse it
            # For now, we'll treat it as a description update
            actions = self.storage.load_actions()
            if 0 <= action_id < len(actions):
                actions[action_id].description = action_data.strip()
                self.storage.actions = actions
                self.storage.save_actions()
        elif isinstance(action_data, dict):
            # If it's a dict, it contains the new parameters
            description = action_data.pop('description', None)
            self.storage.edit_action(action_id, action_data, description)

    async def delete_action(self, delete_action_id: int):
        """Remove an action from the pipeline."""
        self.storage.delete_action(delete_action_id)
    
    def add_action(self, action: PipelineAction):
        """Add a new action to the pipeline."""
        self.storage.add_action(action)
    
    async def run_pipeline(self):
        """Execute the pipeline and return the resulting tables."""
        return await self.storage.execute_pipeline()
