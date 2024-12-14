import os
import json

NEW_CODE_TAG = "# Add new code here (keep this comment line)"
PIPELINE_START_TAG = "# Squirrel Pipeline start"
PIPELINE_END_TAG = "# Squirrel Pipeline end"

BASIC_PIPELINE = """
import pandas as pd

def run_pipeline():
    dfs = {}
    
    %s
    %s
    %s

    return dfs
""" % (PIPELINE_START_TAG, NEW_CODE_TAG, PIPELINE_END_TAG)

PROJECT_TYPE_REGISTRY = {}
def project_type(cls):
    """
    Decorator to register all data source types
    """
    PROJECT_TYPE_REGISTRY[cls.short_name] = cls
    return cls
@project_type
class Project:
    short_name = "std"
    display_name = "Standard"

    def __init__(self, manifest):
        self.name = manifest['name']
        self.description = manifest['description']
        self.directory = manifest.get('directory', self.name.lower().replace(" ", "_"))
        self.path = os.path.join(os.getcwd(), "_projects", self.directory)
        self.project_type = self.short_name,
        self.misc = self.create_misc(manifest.get('misc', {}))

    def create_misc(self, misc):
        """
        Create the misc values for manifest
        """
        if "table_len" not in misc:
            misc["table_len"] = 10

        return misc

    async def create(self):
        """
        Creates a new project directory in the ./_projects directory, with the necessary files
        """
        await self._create_project_directory()
        await self._create_manifest()
        await self._create_data_sources_directory()
        await self._create_pipeline_file()
       
    async def _create_project_directory(self):
        """
        Creates a new project directory in the ./_projects directory
        """
        os.makedirs(self.path)

    async def _create_manifest(self):
        """
        Creates the manifest file
        """
        manifest_path = os.path.join(self.path, "__manifest__.json")
        manifest_content = {
            "name": self.name,
            "description": self.description,
            "directory": self.directory,
            "project_type": self.project_type[0],
            "misc": self.misc
        }
        with open(manifest_path, 'w') as file:
            json.dump(manifest_content, file, indent=4)

    async def _create_data_sources_directory(self):
        """
        Creates the data_sources directory
        """
        os.makedirs(os.path.join(self.path, "data_sources"))

    async def _create_pipeline_file(self):
        """
        Creates the pipeline.py file
        """
        pipeline_path = os.path.join(self.path, "pipeline.py")
        with open(pipeline_path, 'w') as file:
            file.write(BASIC_PIPELINE)

    async def update_settings(self, updated_data):
        """
        Update the project settings
        """
        manifest_path = os.path.join(self.path, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)

        for key, value in updated_data.items():
            if key in ('misc'):
                try:
                    value = json.loads(value)
                except:
                    value = self.create_misc({})
            if key in manifest_data:
                manifest_data[key] = value

        with open(manifest_path, 'w') as file:
            json.dump(manifest_data, file, indent=4)
