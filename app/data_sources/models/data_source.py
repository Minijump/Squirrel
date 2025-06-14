import os
import json


DATA_SOURCE_REGISTRY = {}
def data_source_type(cls):
    """Decorator to register all data source types"""
    DATA_SOURCE_REGISTRY[cls.short_name] = cls
    return cls

class DataSource:
    short_name = "short_name"
    display_name = "Display name"
    icon = ""

    @classmethod
    def get_source_specific_creation_args(cls):
        return {}

    def __init__(self, manifest):
        self.type = manifest['type']
        self.name = manifest['name']
        self.description = manifest.get('description')
        self.directory = manifest['directory']

    @staticmethod
    def check_available_infos(form_data, additional_required_fields=False):
        """Check if the required infos are available"""
        if not form_data.get("source_name"):
            raise ValueError("Source name is required")
        if not form_data.get("source_type"):
            raise ValueError("Source type is required")
        
        if additional_required_fields:
            for field in additional_required_fields:
                if not form_data.get(field):
                    raise ValueError(f"{field} is required")

    @staticmethod
    def _generate_manifest(form_data):
        """
        Generates the manifest of the source
        To be overriden by subclasses if manifest needs others infos

        => Returns the manifest (dict)
        """
        source_name = form_data.get("source_name")
        manifest = {
            "name": source_name,
            "type": form_data.get("source_type"),
            "description": form_data.get("source_description"),
            "directory": source_name.replace(" ", "_")
        }
        return manifest

    @staticmethod
    async def _create_source_base(manifest, form_data):
        """Creates the base structure of a data source"""
        project_dir = form_data.get("project_dir")
        source_dir = form_data.get("source_name").replace(" ", "_")
        source_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", source_dir)

        os.makedirs(source_path)
        with open(os.path.join(source_path, "__manifest__.json"), 'w') as file:
            json.dump(manifest, file, indent=4)

    @classmethod
    async def _create_source(cls, form_data):
        """
        Creates the data source

        => Returns an object of the 'cls' class
        """
        manifest = cls._generate_manifest(form_data)
        await cls._create_source_base(manifest, form_data)
        return cls(manifest)

    async def _create_required_files(self, form_data=False):
        """Creates the required files for the source, can be directly a data file or a python file"""
        await self._create_python_file(form_data)
        await self._create_data_file(form_data)

    async def _create_python_file(self, form_data=False):
        """To be implemented by subclasses (optional)"""
        pass

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

    async def update_source_settings(self, updated_data):
        """Update the settings of a data source in the manifest"""
        manifest_path = os.path.join(os.getcwd(), "_projects", updated_data["project_dir"], "data_sources", self.directory, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            source = json.load(file)

        updated_source = await self.__class__._update_source_settings(source, updated_data)

        with open(manifest_path, 'w') as file:
            json.dump(updated_source, file, indent=4)

    @classmethod
    async def _update_source_settings(cls, source, updated_data):
        """
        Update the source's values with the updated data, method to be overriden by subclasses if needed

        => Returns the updated source (dict)
        """
        for key in updated_data.keys():
            if key in source.keys():
                source[key] = updated_data[key]

        return source
