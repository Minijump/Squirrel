import os
import json
import ast
import datetime
import pickle
import xmlrpc.client

import pandas as pd

from app.data_sources.models.data_source import DataSource, data_source_type


@data_source_type
class DataSourceOdoo(DataSource):
    short_name = "odoo"
    display_name = "Odoo"
    icon = "odoo_icon.png"

    def __init__(self, manifest):
        super().__init__(manifest)
        self.username = manifest.get("username")
        self.url = manifest.get("url")
        self.db = manifest.get("db")
        self.key = manifest.get("key")
        self.model = manifest.get("model")
        self.fields = manifest.get("fields")
        self.domain = manifest.get("domain")
        self.last_sync = manifest.get("last_sync")

    @staticmethod
    def check_available_infos(form_data):
        """
        Check if the required infos are available

        * - odoo_url: The URL of the Odoo instance
          - db: The database name
          - username: The username to connect to Odoo
          - password: The password to connect to Odoo
          - DataSource()'s ones
        """
        required_fields = ["url", "db", "username", "key", "model", "fields"]
        for field in required_fields:
            if not form_data.get(field):
                raise ValueError(f"{field} is required")
        
        DataSource.check_available_infos(form_data)

    @staticmethod
    def _generate_manifest(form_data):
        """
        Generates the manifest of the source

        * form_data(dict): The form data

        => Returns the manifest (dict)
        """
        manifest = DataSource._generate_manifest(form_data)
        manifest["url"] = form_data.get("url")
        manifest["db"] = form_data.get("db")
        manifest["username"] = form_data.get("username")
        manifest["key"] = form_data.get("key")
        manifest["model"] = form_data.get("model")
        manifest["fields"] = ast.literal_eval(form_data.get("fields")) or ['id']
        manifest["domain"] = ast.literal_eval(form_data.get("domain")) or []
        manifest["last_sync"] = ""

        return manifest
    
    async def _create_data_file(self, form_data):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.key, {})

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        table = models.execute_kw(self.db, uid, self.key, self.model, 'search_read', [self.domain], {'fields': self.fields})

        table_df = pd.read_json(json.dumps(table))
        data_file_path = os.path.join(os.getcwd(), "_projects", form_data["project_dir"], "data_sources", self.directory, 'data.pkl')
        table_df.to_pickle(data_file_path)

        await self.update_last_sync(form_data["project_dir"])

    def create_table(self, form_data):
        """
        Return the code to create the table from the odoo API
        """
        project_dir = form_data.get("project_dir")
        data_file_path = os.path.join(os.getcwd(), '_projects', project_dir, 'data_sources', self.directory, 'data.pkl')
        data_file_path = os.path.relpath(data_file_path, os.getcwd())
        table_name = form_data.get("table_name")
        return f"""dfs['{table_name}'] = pd.read_pickle(r'{data_file_path}')  #sq_action:Create table {table_name} from {self.name}"""

    async def update_last_sync(self, project_dir):
        """
        Update the last sync date
        """
        last_sync = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_sync = last_sync
        print(last_sync)

        manifest_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", self.directory, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest = json.load(file)

        manifest["last_sync"] = last_sync

        with open(manifest_path, 'w') as file:
            json.dump(manifest, file, indent=4)


    async def sync(self, project_dir):
        """
        Sync the data from the Odoo instance
        """
        await self._create_data_file({"project_dir": project_dir})
