import os
import pickle
import pandas as pd
from typing import List

from app.pipelines.models.pipeline_action import PipelineAction


class Pipeline:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.pipeline_path = os.path.join(os.getcwd(), "_projects", project_dir, "pipeline.pkl")
        self.actions: List[PipelineAction] = []
        self._load_actions()

    def _load_actions(self) -> List[PipelineAction]:
        with open(self.pipeline_path, 'rb') as f:
            self.actions = pickle.load(f)

        for action in self.actions:
            action.update_description()

    def _save_actions(self):
        with open(self.pipeline_path, 'wb') as f:
            pickle.dump(self.actions, f)

    def get_actions(self):
        self._load_actions()
        return self.actions
    
    def confirm_new_order(self, order: str):
        self._load_actions()
        new_order = [int(action_str.split('-')[0]) for action_str in order.split(",")]
        reordered_actions = [self.actions[i] for i in new_order]
        self.actions = reordered_actions
        self._save_actions()
    
    def get_action_data(self, action_id: int):
        self._load_actions()
        return self.actions[action_id].action.form_data

    def edit_action(self, action_id: int, edit_action_data: dict):
        self._load_actions()
        pipeline_action = self.actions[action_id]
        current_action_data = pipeline_action.action.form_data
        new_action_data = {
            key: value 
            for key, value in edit_action_data.items() 
            if key in current_action_data
        }  # Update keys already existing in current_action_data
        current_action_data.update(new_action_data)
        pipeline_action.action.form_data = current_action_data
        
        self._save_actions()

    def get_pipeline_action_data(self, action_id: int):
        self._load_actions()
        pipeline_action = self.actions[action_id]
        return {
            'custom_description': pipeline_action.custom_description or "",
        }

    def edit_pipeline_action(self, action_id: int, info_data: dict):
        self._load_actions()
        pipeline_action = self.actions[action_id]
        
        if 'custom_description' in info_data:
            custom_desc = info_data['custom_description']
            pipeline_action.set_custom_description(custom_desc if custom_desc.strip() else None)
        
        self._save_actions()

    def delete_action(self, delete_action_id: int):
        self._load_actions()
        del self.actions[delete_action_id]
        self._save_actions()
    
    def add_action(self, action):
        self._load_actions()
        self.actions.append(PipelineAction(self, action))
        self._save_actions()
    
    async def run_pipeline(self):
        self._load_actions()
        tables = {}
        for i, pipeline_action in enumerate(self.actions):              
            code = await pipeline_action.action.get_code() 
            local_vars = {'tables': tables, 'pd': pd}
            exec(code, globals(), local_vars)
            tables.update(local_vars['tables'])

        return tables
