import os
import datetime
import json

from app.data_sources.models.data_source import DataSource

class DataSourceAPI(DataSource):
    short_name = "short_name"
    display_name = "Display name"
    icon = ""

    def __init__(self, manifest):
        super().__init__(manifest)
        self.last_sync = manifest.get("last_sync")

    @staticmethod
    def _generate_manifest(form_data):
        manifest = DataSource._generate_manifest(form_data)
        manifest["last_sync"] = ""

        return manifest
    
    def create_table(self, form_data):
        """Return the code to create the table from the API connection data"""
        project_dir = form_data.get("project_dir")
        data_file_path = os.path.join(os.getcwd(), '_projects', project_dir, 'data_sources', self.directory, 'data.pkl')
        data_file_path = os.path.relpath(data_file_path, os.getcwd())
        table_name = form_data.get("table_name")
        return f"""dfs['{table_name}'] = pd.read_pickle(r'{data_file_path}')  #sq_action:Create table {table_name} from {self.name}"""
    
    async def _get_data_from_api(self):
        """To be overriden by subclasses"""
        pass

    async def _create_data_file(self, form_data):
        data = await self._get_data_from_api()

        data_file_path = os.path.join(os.getcwd(), "_projects", form_data["project_dir"], "data_sources", self.directory, 'data.pkl')
        data.to_pickle(data_file_path)

        await self.update_last_sync(form_data["project_dir"])

    async def update_last_sync(self, project_dir):
        """Update the last sync date"""
        last_sync = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_sync = last_sync

        manifest_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", self.directory, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest = json.load(file)

        manifest["last_sync"] = last_sync

        with open(manifest_path, 'w') as file:
            json.dump(manifest, file, indent=4)

    async def sync(self, project_dir):
        """Sync the data"""
        await self._create_data_file({"project_dir": project_dir})