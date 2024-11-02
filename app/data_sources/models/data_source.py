import os
import json


DATA_SOURCE_REGISTRY = {}
def data_source_type(cls):
    """
    Decorator to register all data source types
    """
    DATA_SOURCE_REGISTRY[cls.short_name] = cls
    return cls

class DataSource:
    def __init__(self, manifest, form_data=False):
        self.type = manifest['type']
        self.name = manifest['name']
        self.description = manifest.get('description')
        self.directory = manifest['directory']

    @staticmethod
    def check_available_infos(form_data):
        """
        Check if the required infos are available

        * form_data(dict): The form data
        """
        if not form_data.get("source_name"):
            raise ValueError("Source name is required")
        if not form_data.get("source_type"):
            raise ValueError("Source type is required")

    @staticmethod
    def _generate_manifest(form_data):
        """
        Generates the manifest of the source
        To be overriden by subclasses if manifest needs others infos

        * form_data(dict): The form data

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
        """
        Creates the base structure of a data source

        * manifest(dict): contains info about the source
        * form_data(dict): The form data
        """
        project_dir = form_data.get("project_dir")
        source_dir = form_data.get("source_name").replace(" ", "_")
        source_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", source_dir)

        os.makedirs(source_path)
        with open(os.path.join(source_path, "__manifest__.json"), 'w') as file:
            json.dump(manifest, file, indent=4)

    @classmethod
    async def _create_source(cls, form_data):
        """
        Creates the base structure of a data source

        * cls(class): The 'active' class
        * form_data(dict): contains:

        => Returns an object of the cls class
        """
        manifest = cls._generate_manifest(form_data)
        await cls._create_source_base(manifest, form_data)
        return cls(manifest, form_data)

    async def _create_data_file(self):
        """
        To be implemented by subclasses
        """
        pass
