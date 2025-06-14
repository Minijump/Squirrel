import ast
import aiohttp
import pandas as pd

from app.data_sources.models.data_source import data_source_type
from app.data_sources.models.data_source_api import DataSourceAPI


@data_source_type
class DataSourceOdoo(DataSourceAPI):
    short_name = "odoo"
    display_name = "Odoo"
    icon = "odoo_icon.png"

    @classmethod
    def get_source_specific_creation_args(cls):
        return {
            "url": {
                "type": "text",
                "label": "URL",
                "required": True,
            },
            "db": {
                "type": "text",
                "label": "Database",
                "required": True,
            },
            "username": {
                "type": "text",
                "label": "User",
                "required": True,
            },
            "key": {
                "type": "text",
                "label": "Key",
                "required": True,
            },
            "model": {
                "type": "text",
                "label": "Model",
                "required": True,
                "info": "E.g. res.partner",
            },
            "fields": {
                "type": "text",
                "label": "Fields",
                "required": True,
                "info": "With format: ['field_name1', 'field_name2', ...]",
            },
            "domain": {
                "type": "text",
                "label": "Domain",
                "required": False,
                "info": "With format: [('field1', '=', x), ('field2', '!=', y), ...] No domain=[]",
            },
            'kwargs': {
                'type': 'dict',
                'options': {'create': True, 'remove': True},
                'label': 'Kwargs',
                'required': False,
            }
        }

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
        """ Uses the jsonrpc protocol, because it is easier to use with aiohttp. Standard XML-RPC is not working async """
        async with aiohttp.ClientSession() as session:
            auth_url = f"{self.url}/jsonrpc"
            auth_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "authenticate",
                    "args": [self.db, self.username, self.key, {}]
                },
                "id": 1
            }
            async with session.post(auth_url, json=auth_payload) as auth_response:
                auth_data = await auth_response.json()
                uid = auth_data.get("result")
                if not uid:
                    raise ValueError("Authentication failed. Check your credentials.")

            object_url = f"{self.url}/jsonrpc"
            data_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.db, uid, self.key, self.model, "search_read", [],
                        {
                            "domain": self.domain,
                            "fields": self.fields,
                            **self.kwargs
                        }
                    ]
                },
                "id": 2
            }
            async with session.post(object_url, json=data_payload) as data_response:
                data = await data_response.json()
                table = data.get("result", [])

        data = pd.DataFrame(table)
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
