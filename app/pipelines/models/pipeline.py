import os
import pickle
import pandas as pd
import traceback
from typing import List

from app.pipelines.models.pipeline_action import PipelineAction
from app.tables.models.actions_utils import TABLE_ACTION_REGISTRY


class Pipeline:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.project_path = os.path.join(os.getcwd(), "_projects", project_dir)
        self.pipeline_path = os.path.join(self.project_path, "pipeline.pkl")
        self.actions: List[PipelineAction] = []
        self.load_actions()

    def load_actions(self) -> List[PipelineAction]:
        """Load actions from pickle file"""
        if os.path.exists(self.pipeline_path):
            with open(self.pipeline_path, 'rb') as f:
                self.actions = pickle.load(f)
        else:
            self.actions = []
        return self.actions

    async def get_actions(self):
        actions = self.load_actions()
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
        new_order = [int(action_str.split('-')[0]) for action_str in order.split(",")]
        if len(new_order) != len(self.actions):
            raise ValueError("New order must contain all action indices")
        
        reordered_actions = [self.actions[i] for i in new_order]
        self.actions = reordered_actions
        self.save_actions()

    async def edit_action(self, action_id: int, action_data):
        """Edit an action in the pipeline."""
        # TODO: not working, only edit description
        # action_data should contain the new parameters and optionally description
        if isinstance(action_data, str):
            # If it's a string (legacy code), we need to parse it
            # For now, we'll treat it as a description update
            actions = self.load_actions()
            if 0 <= action_id < len(actions):
                actions[action_id].description = action_data.strip()
                self.actions = actions
                self.save_actions()
        elif isinstance(action_data, dict):
            # If it's a dict, it contains the new parameters
            description = action_data.pop('description', None)
            if 0 <= action_id < len(self.actions):
                self.actions[action_id].parameters = action_data
                if description:
                    self.actions[action_id].description = description
                self.save_actions()
            else:
                raise IndexError("Action index out of range")

    async def delete_action(self, delete_action_id: int):
        if 0 <= delete_action_id < len(self.actions):
            del self.actions[delete_action_id]
            self.save_actions()
        else:
            raise IndexError("Action index out of range")
    
    def add_action(self, action: PipelineAction):
        self.actions.append(action)
        self.save_actions()

    async def _execute_action(self, action: PipelineAction, parameters):
        action_instance = TABLE_ACTION_REGISTRY.get(action.action_class)(parameters)
        code = await action_instance.execute()
        return code
    
    async def run_pipeline(self):
        tables = {}

        for i, action in enumerate(self.actions):            
            action_class = TABLE_ACTION_REGISTRY.get(action.action_class)
            if not action_class:
                continue
            
            try:
                code = await self._execute_action(action, action.parameters) 
                if not code:
                    print(f"No code generated for action {action.action_class}")
                    continue
                
                local_vars = {'tables': tables, 'pd': pd}
                exec(code, globals(), local_vars)
                tables.update(local_vars['tables'])
                
            except Exception as e:
                print(f"Error executing action {action.action_class}: {e}")
                traceback.print_exc()
                continue
        
        return tables
    
    def save_actions(self):
        with open(self.pipeline_path, 'wb') as f:
            pickle.dump(self.actions, f)
