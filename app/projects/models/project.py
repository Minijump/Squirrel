import json
import os
import pickle


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

    def get_available_projects(all_projects_path: str) -> list['Project']:
        projects = []
        for project in os.listdir(all_projects_path):
            projects.append(Project.instantiate_from_dir(project))
        return projects

    def _instantiate_from_path(project_path: str) -> 'Project':
        manifest_path = os.path.join(project_path, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
        return Project(manifest_data)
    
    def instantiate_from_dir(project_dir: str) -> 'Project':
        project_path = os.path.join(os.getcwd(), "_projects", project_dir)
        return Project._instantiate_from_path(project_path)

    def __init__(self, manifest):
        self.name = manifest['name']
        self.description = manifest['description']
        self.directory = manifest.get('directory', self.name.lower().replace(" ", "_"))
        self.path = os.path.join(os.getcwd(), "_projects", self.directory)
        self.project_type = self.short_name,
        self.misc = self._create_misc(manifest.get('misc', {}))
    
    def _read_manifest(self) -> dict:
        manifest_path = os.path.join(self.path, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
        return manifest_data

    def _write_manifest(self, data: dict):
        manifest_path = os.path.join(self.path, "__manifest__.json")
        with open(manifest_path, 'w') as file:
            json.dump(data, file, indent=4)

    def _create_misc(self, misc: dict) -> dict:
        if "table_len" not in misc:
            misc["table_len"] = 10
        return misc

    async def create(self):
        self._create_project_directory()
        self._create_manifest()
        self._create_data_sources_directory()
        self._create_pipeline_file()

    def _create_project_directory(self):
        if os.path.exists(self.path):
            raise FileExistsError(f"Project with name {self.name} or similar already exists")
        invalid_chars = '/\\.:?*'
        if any(char in self.name for char in invalid_chars):
            raise Exception(f"Project name cannot contain /, \\, ., :, ?, *")

        try:
            os.makedirs(self.path)
        except Exception as e:
            raise Exception(f"Could not create a project with this name: {e}")

    def _create_manifest(self):
        manifest_content = {
            "name": self.name,
            "description": self.description,
            "directory": self.directory,
            "project_type": self.project_type[0],
            "misc": self.misc
        }
        self._write_manifest(manifest_content)

    def _create_data_sources_directory(self):
        os.makedirs(os.path.join(self.path, "data_sources"))

    def _create_pipeline_file(self):
        """Create a dummy, useless, file for the pipeline"""
        pipeline_path = os.path.join(self.path, "pipeline.pkl")
        with open(pipeline_path, 'wb') as file:
            pickle.dump([], file)

    def get_settings(self) -> dict:
        manifest_data = self._read_manifest()
        return manifest_data

    def update_settings(self, updated_data: dict):
        manifest_data = self._read_manifest()

        for key, value in updated_data.items():
            if key in ('misc'):
                try:
                    value = json.loads(value)
                except:
                    value = self._create_misc({})
            if key in manifest_data:
                manifest_data[key] = value

        self._write_manifest(manifest_data)

    def get_sources(self):
        # TODO: return DATASOURCES objects? change inheritance stuct first?
        sources = []
        project_data_sources_path = os.path.join(self.path, "data_sources")
        for source in os.listdir(project_data_sources_path):
            manifest_path = os.path.join(project_data_sources_path, source, "__manifest__.json")
            if os.path.isfile(manifest_path):
                with open(manifest_path, 'r') as file:
                    manifest_data = json.load(file)
                    sources.append(manifest_data)
        return sources
