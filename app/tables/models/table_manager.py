import json
import os
import pandas as pd
import pickle

from .table import Table
from app.pipelines.models.pipeline import Pipeline
from app.projects.models.project import Project

class TableManager:
    def __init__(self, tables: dict[str, pd.DataFrame], project_dir: str):
        self.project_dir = project_dir
        self.tables = self._create_table(tables)
        self.display_len = self._get_project_display_len()
        self.project = Project.instantiate_from_dir(project_dir)

    @classmethod
    async def init_from_project_dir(cls, project_dir: str, lazy: bool = False):
        if lazy:
            table_manager = cls.load_tables(project_dir)
            if table_manager:
                return table_manager
        pipeline = Pipeline(project_dir)
        table_manager = await pipeline.run_pipeline()
        table_manager.save_tables()
        return table_manager

    @staticmethod
    def load_tables(project_dir):
        datatables_path = os.path.join( os.getcwd(), "_projects", project_dir, "data_tables.pkl")
        if os.path.exists(datatables_path):
            with open(datatables_path, 'rb') as f:
                table_manager = pickle.load(f)
            return table_manager
        return False

    def _create_table(self, tables: dict):
        all_tables = {}
        for table_name, table_content in tables.items():
            all_tables[table_name] = Table(table_name, table_content)
        return all_tables

    def _get_project_display_len(self):
        manifest_path = os.path.join(os.getcwd(), "_projects", self.project_dir, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
        display_len = manifest_data.get('misc', {}).get("table_len", 10)
        return display_len

    def save_tables(self):
        datatables_path = os.path.join( os.getcwd(), "_projects", self.project_dir, "data_tables.pkl")
        with open(datatables_path, 'wb') as f:
            pickle.dump(self, f)

    def to_html(self, start=False, end=False):
        table_html = {}
        table_len_infos = {}
        for table_name, table in self.tables.items():
            table_html[table_name] = table.to_html(display_len=self.display_len, start=start, end=end)
            table_len_infos[table_name] = {
                'total_len': len(table.content.index),
                'display_len': self.display_len
            }
        return table_html, table_len_infos

    def get_col_info(self, table_name: str, column_idx: str):
        table = self.tables.get(table_name)
        if not table:
            return None
        return table.get_col_info(column_idx)
