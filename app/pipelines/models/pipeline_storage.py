import os
import pickle
import pandas as pd
import traceback
from typing import Dict, Any, List

from app.tables.models.actions_utils import TABLE_ACTION_REGISTRY
from app.utils.form_utils import squirrel_action_error


class PipelineAction:
    """Represents a single action in the pipeline"""
    def __init__(self, action_class: str, parameters: Dict[str, Any], description: str = ""):
        self.action_class = action_class
        self.parameters = parameters
        self.description = description

    @squirrel_action_error
    async def add_to_pipeline(self, pipeline):
        pipeline.add_action(self)

class PipelineStorage:
    """Handles storage of pipelines using pickle files"""
    
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
    
    def save_actions(self):
        """Save actions to pickle file"""
        with open(self.pipeline_path, 'wb') as f:
            pickle.dump(self.actions, f)
    
    def add_action(self, action: PipelineAction):
        """Add an action to the pipeline"""
        self.actions.append(action)
        self.save_actions()
    
    def reorder_actions(self, new_order: List[int]):
        """Reorder actions based on provided indices"""
        if len(new_order) != len(self.actions):
            raise ValueError("New order must contain all action indices")
        
        reordered_actions = [self.actions[i] for i in new_order]
        self.actions = reordered_actions
        self.save_actions()
    
    def edit_action(self, action_index: int, new_parameters: Dict[str, Any], new_description: str = None):
        """Edit an action's parameters"""
        # Not working, does not go through this function, only edit_action of Pipeline class
        if 0 <= action_index < len(self.actions):
            self.actions[action_index].parameters = new_parameters
            if new_description:
                self.actions[action_index].description = new_description
            self.save_actions()
        else:
            raise IndexError("Action index out of range")
    
    def delete_action(self, action_index: int):
        """Delete an action from the pipeline"""
        if 0 <= action_index < len(self.actions):
            del self.actions[action_index]
            self.save_actions()
        else:
            raise IndexError("Action index out of range")

    async def execute_pipeline(self) -> Dict[str, pd.DataFrame]:
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
    
    async def _execute_action(self, action: PipelineAction, parameters):
        action_instance = TABLE_ACTION_REGISTRY.get(action.action_class)(parameters)
        code = await action_instance.execute()
        return code
