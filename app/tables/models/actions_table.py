import os
import json

from .actions import Action, table_action_type
from app.data_sources.models.data_source import DATA_SOURCE_REGISTRY


@table_action_type
class CreateTable(Action):
    def __init__(self, request):
        super().__init__(request)

    async def execute(self):
        project_dir, data_source_dir = await self._get(["project_dir", "data_source_dir"])
        data_source_path = os.path.relpath(
            os.path.join(os.getcwd(), '_projects', project_dir, 'data_sources', data_source_dir), 
            os.getcwd())

        manifest_path = os.path.join(data_source_path, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)

        SourceClass = DATA_SOURCE_REGISTRY[manifest_data["type"]]
        source = SourceClass(manifest_data)
        new_code = source.create_table(await self.request.form())
        
        return new_code
