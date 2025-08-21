import os
import json

from app.projects.models import project_type


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
        """Create the misc values of the manifest"""
        if "table_len" not in misc:
            misc["table_len"] = 10

        return misc

    async def create(self):
        """Creates a new project with the necessary files"""
        await self._create_project_directory()
        await self._create_manifest()
        await self._create_data_sources_directory()
        await self._create_pipeline_file()
       
    async def _create_project_directory(self):
        """Creates a new project directory in the ./_projects directory"""
        project_dir = self.path

        if os.path.exists(project_dir):
            raise FileExistsError(f"Project with name {self.name} or similar already exists")
        invalid_chars = '/\\.:?*'
        if any(char in self.name for char in invalid_chars):
            raise Exception(f"Project name cannot contain /, \\, ., :, ?, *")

        try:
            os.makedirs(project_dir)
        except Exception as e:
            raise Exception(f"Could not create a project with this name: {e}")

    async def _create_manifest(self):
        """Creates the manifest file"""
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
        """Creates the data_sources directory"""
        os.makedirs(os.path.join(self.path, "data_sources"))

    async def _create_pipeline_file(self):
        """Creates the pipeline file"""
        import pickle
        pipeline_path = os.path.join(self.path, "pipeline.pkl")
        # Create an empty pipeline with no actions
        actions = []
        with open(pipeline_path, 'wb') as file:
            pickle.dump(actions, file)

    async def update_settings(self, updated_data):
        """Update the project settings"""
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
