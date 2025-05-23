import ast
import json
import pandas as pd
import xmlrpc.client

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
        self.kwargs = manifest.get("kwargs") or {}

    @staticmethod
    def check_available_infos(form_data):
        required_fields = ["url", "db", "username", "key", "model", "fields"]
        DataSourceAPI.check_available_infos(form_data, required_fields)

    @staticmethod
    def _generate_manifest(form_data):
        manifest = DataSourceAPI._generate_manifest(form_data)
        manifest["url"] = form_data.get("url")
        manifest["db"] = form_data.get("db")
        manifest["username"] = form_data.get("username")
        manifest["key"] = form_data.get("key")
        manifest["model"] = form_data.get("model")
        manifest["fields"] = ast.literal_eval(form_data.get("fields"))
        manifest["domain"] = ast.literal_eval(form_data.get("domain")) if form_data.get("domain") else []
        manifest["kwargs"] = ast.literal_eval(form_data.get("kwargs")) if form_data.get("kwargs") else {}

        return manifest
    
    async def _get_data_from_api(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.key, {})

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        table = models.execute_kw(self.db, uid, self.key, self.model, 'search_read', [], 
            {
                **{'domain': self.domain, 'fields': self.fields}, 
                **self.kwargs
            })

        data = pd.read_json(json.dumps(table))

        return data

    @classmethod
    async def _update_source_settings(cls, source, updated_data):
        updated_source = await DataSourceAPI._update_source_settings(source, updated_data)

        updated_source["fields"] = ast.literal_eval(updated_source["fields"])
        updated_source["domain"] = ast.literal_eval(updated_source["domain"]) if updated_source["domain"] else ""
        try: 
            updated_source["kwargs"] = ast.literal_eval(updated_source["kwargs"])
        except:
            updated_source["kwargs"] = {}

        return updated_source
