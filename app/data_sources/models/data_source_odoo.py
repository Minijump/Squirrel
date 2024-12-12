import json
import ast
import xmlrpc.client

import pandas as pd

from app.data_sources.models.data_source import data_source_type
from app.data_sources.models.data_source_api import DataSourceAPI


@data_source_type
class DataSourceOdoo(DataSourceAPI):
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
        self.domain = manifest.get("domain") or []

    @staticmethod
    def check_available_infos(form_data):
        """
        Check if the required infos are available

        * - odoo_url: The URL of the Odoo instance
          - db: The database name
          - username: The username to connect to Odoo
          - password: The password to connect to Odoo
          - DataSourceAPI()'s ones
        """
        required_fields = ["url", "db", "username", "key", "model", "fields"]
        DataSourceAPI.check_available_infos(form_data, required_fields)

    @staticmethod
    def _generate_manifest(form_data):
        """
        Generates the manifest of the source

        * form_data(dict): The form data

        => Returns the manifest (dict)
        """
        manifest = DataSourceAPI._generate_manifest(form_data)
        manifest["url"] = form_data.get("url")
        manifest["db"] = form_data.get("db")
        manifest["username"] = form_data.get("username")
        manifest["key"] = form_data.get("key")
        manifest["model"] = form_data.get("model")
        manifest["fields"] = ast.literal_eval(form_data.get("fields"))
        manifest["domain"] = ast.literal_eval(form_data.get("domain")) if form_data.get("domain") else []

        return manifest
    
    async def _get_data_from_api(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.key, {})

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        table = models.execute_kw(self.db, uid, self.key, self.model, 'search_read', [self.domain], {'fields': self.fields})

        data = pd.read_json(json.dumps(table))

        return data

    @classmethod
    async def _update_source_settings(cls, source, updated_data):
        """
        Update the source's values with the updated data, convert 'fields' and 'domain' to list
        """
        updated_source = await DataSourceAPI._update_source_settings(source, updated_data)

        updated_source["fields"] = ast.literal_eval(updated_source["fields"])
        updated_source["domain"] = ast.literal_eval(updated_source["domain"]) if updated_source["domain"] else ""

        return updated_source
