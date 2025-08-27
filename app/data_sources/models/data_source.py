import json
import os

class DataSource:
    short_name = "short_name"
    display_name = "Display name"
    icon = ""

    def __init__(self, manifest):
        self.type = manifest['type']
        self.name = manifest['name']
        self.description = manifest.get('description')
        self.directory = manifest['directory']
        self.project_dir = manifest.get('project_dir')
        self.path = os.path.join(os.getcwd(), "_projects", self.project_dir, "data_sources", self.directory)

    @classmethod
    def get_source_specific_args(cls, is_settings=False):
        return {}
    
    @classmethod
    async def create_source(cls, form_data):
        """ Create the source in the project (!= object creation)"""
        cls._check_required_infos(form_data)
        manifest = cls._generate_manifest_content(form_data)
        source = cls(manifest)
        source._create_source_directory()
        source._create_manifest_file(manifest)
        await source._create_data_file(form_data)
        return source

    @staticmethod
    def _check_required_infos(form_data, additional_required_fields=False):
        required_fields = ["source_name", "source_type", "project_dir"] + (additional_required_fields or [])
        for field in required_fields:
            if not form_data.get(field):
                raise ValueError(f"{field} is required")

    @staticmethod
    def _generate_manifest_content(form_data):
        source_name = form_data.get("source_name")
        manifest = {
            "name": source_name,
            "type": form_data.get("source_type"),
            "description": form_data.get("source_description"),
            "directory": source_name.replace(" ", "_"),
            "project_dir": form_data.get("project_dir")
        }
        return manifest

    def _read_manifest(self):
        manifest_path = os.path.join(self.path, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            return json.load(file)
        
    def _write_manifest(self, manifest_data):
        manifest_path = os.path.join(self.path, "__manifest__.json")
        with open(manifest_path, 'w') as file:
            json.dump(manifest_data, file, indent=4)

    def _create_source_directory(self):
        os.makedirs(self.path)

    def _create_manifest_file(self, manifest_data):
        self._write_manifest(manifest_data)

    async def _create_data_file(self, form_data=False):
        """To be implemented by subclasses (mandatory)"""
        pass

    def create_table(self, form_data=False):
        """To be implemented by subclasses (mandatory)"""
        pass

    async def sync(self, project_dir):
        """To be implemented by subclasses (optional)"""
        pass

    def _update_last_sync(self, project_dir):
        """To be implemented by subclasses (optional)"""
        pass

    def get_settings(self):
        return self._read_manifest()

    async def update_source_settings(self, updated_data):
        manifest_data = self._read_manifest()
        updated_source = await self._update_source_settings(manifest_data, updated_data)
        self._write_manifest(updated_source)

    async def _update_source_settings(self, source, updated_data):
        for key in updated_data.keys():
            if key in source.keys():
                source[key] = updated_data[key]
        return source
