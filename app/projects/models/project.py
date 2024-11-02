import os
import json
from utils import PIPELINE_START_TAG, PIPELINE_END_TAG, NEW_CODE_TAG

BASIC_PIPELINE = """
import pandas as pd

def run_pipeline():
    dfs = {}
    
    %s
    %s
    %s

    return dfs
""" % (PIPELINE_START_TAG, NEW_CODE_TAG, PIPELINE_END_TAG)

# TODO: add decorator; project type (here it would be "standard"?)
class Project:
    def __init__(self, name, description, form_data=False):
        self.name = name
        self.description = description
        self.directory = name.lower().replace(" ", "_")
        self.path = os.path.join(os.getcwd(), "_projects", self.directory)

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
            "directory": self.directory
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
