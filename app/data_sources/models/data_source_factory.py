from .data_source import DataSource


DATA_SOURCE_REGISTRY = {}
def data_source_type(cls):
    """Decorator to register all data source types"""
    DATA_SOURCE_REGISTRY[cls.short_name] = cls
    return cls


class DataSourceFactory:
    def init_source_from_dir(project_dir, source_dir):
        manifest_data = DataSource.get_manifest(project_dir, source_dir)
        SourceClass = DATA_SOURCE_REGISTRY[manifest_data["type"]]
        return SourceClass(manifest_data)

    async def create_source(form_data):
        SourceClass = DATA_SOURCE_REGISTRY[form_data.get("source_type")]
        SourceClass.check_available_infos(form_data)
        source = await SourceClass._create_source(form_data)
        await source._create_required_files(form_data)

    def get_available_type():
        return [(key, value.display_name) for key, value in DATA_SOURCE_REGISTRY.items()]

    def get_source_class(class_name):
        return DATA_SOURCE_REGISTRY[class_name]
