import json
import os


DATA_SOURCE_REGISTRY = {}
def data_source_type(cls):
    """Decorator to register all data source types"""
    DATA_SOURCE_REGISTRY[cls.short_name] = cls
    return cls


class DataSourceFactory:
    def init_source_from_dir(project_dir, source_dir):
        manifest_data = {}
        manifest_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", source_dir, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
        SourceClass = DATA_SOURCE_REGISTRY[manifest_data["type"]]
        manifest_data["project_dir"] = project_dir
        return SourceClass(manifest_data)

    async def create_source(form_data):
        SourceClass = DATA_SOURCE_REGISTRY[form_data.get("source_type")]
        await SourceClass.create_source(form_data)

    def get_available_type():
        return [(key, value.display_name) for key, value in DATA_SOURCE_REGISTRY.items()]

    def get_source_class(class_name):
        return DATA_SOURCE_REGISTRY[class_name]
