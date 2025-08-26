import os
import json


class DataSource:
    short_name = "short_name"
    display_name = "Display name"
    icon = ""

    @classmethod
    def get_source_specific_args(cls, is_settings=False):
        return {}

    def __init__(self, manifest):
        self.type = manifest['type']
        self.name = manifest['name']
        self.description = manifest.get('description')
        self.directory = manifest['directory']
        self.project_dir = manifest.get('project_dir')
        self.path = os.path.join(os.getcwd(), "_projects", self.project_dir, "data_sources", self.directory)

    @staticmethod
    def _check_required_infos(form_data, additional_required_fields=False):
        if not form_data.get("source_name"):
            raise ValueError("Source name is required")
        if not form_data.get("source_type"):
            raise ValueError("Source type is required")
        if not form_data.get("project_dir"):
            raise ValueError("Project directory is required")

        if additional_required_fields:
            for field in additional_required_fields:
                if not form_data.get(field):
                    raise ValueError(f"{field} is required")

    def _read_manifest(self):
        manifest_path = os.path.join(self.path, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            return json.load(file)

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

    async def _create_source_directory(self, form_data):
        os.makedirs(self.path)

    async def _create_manifest_file(self, manifest_data):
        with open(os.path.join(self.path, "__manifest__.json"), 'w') as file:
            json.dump(manifest_data, file, indent=4)

    @classmethod
    async def create_source(cls, form_data):
        cls._check_required_infos(form_data)
        manifest = cls._generate_manifest_content(form_data)
        source = cls(manifest)
        await source._create_source_directory(form_data)
        await source._create_manifest_file(manifest)
        await source._create_data_file(form_data)
        return source

    async def _create_data_file(self, form_data=False):
        """To be implemented by subclasses (mandatory)"""
        pass

    def create_table(self, form_data=False):
        """To be implemented by subclasses (mandatory)"""
        pass

    async def sync(self, project_dir):
        """To be implemented by subclasses (optional)"""
        pass

    async def update_last_sync(self, project_dir):
        """To be implemented by subclasses (optional)"""
        pass

    def get_settings(self):
        return self._read_manifest()

    async def update_source_settings(self, updated_data):
        manifest_path = os.path.join(self.path, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            source = json.load(file)

        updated_source = await self.__class__._update_source_settings(source, updated_data)

        with open(manifest_path, 'w') as file:
            json.dump(updated_source, file, indent=4)

    @classmethod
    async def _update_source_settings(cls, source, updated_data):
        for key in updated_data.keys():
            if key in source.keys():
                source[key] = updated_data[key]

        return source
