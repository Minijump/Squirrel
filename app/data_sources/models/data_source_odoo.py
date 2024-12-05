import os
import requests
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
        required_fields = ["url", "db", "username", "key"]
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
        return manifest

    async def _create_python_file(self, form_data):
        """
        Creates the python file to connect to Odoo
        """
        source_path = os.path.join(os.getcwd(), "_projects", form_data["project_dir"], "data_sources", self.directory) 

        python_file_path = os.path.join(source_path, 'odoo_api_request.py')
        request = f"""
import xmlrpc.client
import time

def get_odoo_table(model, domain=[], fields=False, sleep_time=False, url="{self.url}", db="{self.db}", username="{self.username}", key="{self.key}"):
    if not fields:
        fields = ['id']
    if sleep_time:
        # Odoo can block the connection if too many requests are made in a short period of time
        time.sleep(sleep_time)
    
    common = xmlrpc.client.ServerProxy('{{}}/xmlrpc/2/common'.format(url))
    common.version()
    uid = common.authenticate(db, username, key, {{}})

    models = xmlrpc.client.ServerProxy('{{}}/xmlrpc/2/object'.format(url))
    table = models.execute_kw(db, uid, key, model, 'search_read', [domain], {{'fields': fields}})

    return table
"""
        with open(python_file_path, 'wb') as file:
            file.write(request.encode())

    def create_table(self, form_data):
        """
        Return the code to create the table from the odoo API
        """
        project_dir = form_data.get("project_dir")
        table_name = form_data.get("table_name")

        python_file_path = os.path.join(os.getcwd(), '_projects', project_dir, 'data_sources', self.directory, 'odoo_api_request.py')
        python_file_path = os.path.relpath(python_file_path, os.getcwd())

        model = form_data.get("model")
        fields = form_data.get("fields")
        #domain = form_data.get("domain")

        code = f"""list_json_table = load_python_file(r'{python_file_path}').get_odoo_table("{model}", fields={fields})"""
        code += f"""\ndfs['{table_name}'] = pd.read_json(json.dumps(list_json_table))  #sq_action:Create table {table_name} from {model} of {self.name}"""

        return code
