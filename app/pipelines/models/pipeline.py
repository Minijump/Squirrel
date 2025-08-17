import os
import pickle
import pandas as pd
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

    async def get_actions(self):
        self.load_actions()
        result = []
        
        for idx, pipeline_action in enumerate(self.actions):
            result.append((idx, pipeline_action.description, pipeline_action.action))

        return result
    
    async def confirm_new_order(self, order: str):
        new_order = [int(action_str.split('-')[0]) for action_str in order.split(",")]
        reordered_actions = [self.actions[i] for i in new_order]
        self.actions = reordered_actions
        self.save_actions()

    async def edit_action(self, action_id: int, action_data):
        self.load_actions()
        # TODO: not working
        # edit pipeline_action.action object instead
        actions = self.actions
        actions[action_id].parameters = action_data
        self.actions = actions
        self.save_actions()

    async def delete_action(self, delete_action_id: int):
        if 0 <= delete_action_id < len(self.actions):
            del self.actions[delete_action_id]
            self.save_actions()
        else:
            raise IndexError("Action index out of range")
    
    def add_action(self, action: PipelineAction):
        self.actions.append(action)
        self.save_actions()
    
    async def run_pipeline(self):
        tables = {}
        for i, pipeline_action in enumerate(self.actions):              
            code = await pipeline_action.action.execute() 
            local_vars = {'tables': tables, 'pd': pd}
            exec(code, globals(), local_vars)
            tables.update(local_vars['tables'])
        
        return tables
    
    def save_actions(self):
        with open(self.pipeline_path, 'wb') as f:
            pickle.dump(self.actions, f)
