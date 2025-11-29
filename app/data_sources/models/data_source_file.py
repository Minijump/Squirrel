import ast
import os
import pandas as pd

from app.data_sources.models.data_source import DataSource
from app.data_sources.models.data_source_factory import data_source_type


class DataSourceFile(DataSource):
    short_name = "file_extension (without dot)"
    display_name = "File Type name"
    icon = ""

    def __init__(self, manifest):
        super().__init__(manifest)
        self.kwargs = manifest.get("kwargs") or {}

    @classmethod
    def get_source_specific_args(cls, is_settings=False):
        return {
            "source_file" : {
                "type": "file",
                "label": "Source file",
                "required": False if is_settings else True,
                "accept": f".{cls.short_name}",
            },
            "kwargs": {
                "type": "dict",
                "dict_options": {'create': True, 'remove': True},
                "label": "Kwargs",
                "required": False,
            }
        }

    @classmethod
    def _check_required_infos(cls, form_data):
        source_file = form_data.get("source_file")

        if not source_file:
            raise ValueError("Source file is required")
        if not source_file.filename.endswith('.' + cls.short_name):
            raise ValueError(f"File must be a {cls.short_name} file")
        
        DataSource._check_required_infos(form_data)

    @staticmethod
    def _generate_manifest_content(form_data):
        manifest = DataSource._generate_manifest_content(form_data)
        try:
            manifest["kwargs"] = ast.literal_eval(form_data["kwargs"])
        except:
            manifest["kwargs"] = {}
        return manifest

    def _create_pickle_file(self, source_file_path):
        """To be implemented by the subclasses"""
        pass

    async def _create_data_file(self, form_data):
        source_file_path = os.path.join(self.path, 'data.' + self.short_name)
        source_file = form_data.get("source_file")
        if source_file and source_file.size > 0:
            source_file_content = await source_file.read()
            with open(source_file_path, 'wb') as file:
                file.write(source_file_content)
        self._create_pickle_file(source_file_path)

    async def _update_source_settings(self, source, updated_data):
        """Update the source's values with the updated data, replace the file if it's not empty"""
        updated_source = await super()._update_source_settings(source, updated_data)
        try: 
            updated_source["kwargs"] = ast.literal_eval(updated_source["kwargs"])
        except:
            updated_source["kwargs"] = {}
        await self._create_data_file(updated_data)
        return updated_source

@data_source_type
class DataSourceCSV(DataSourceFile):
    short_name = "csv"
    display_name = "CSV"
    icon = "csv_icon.png"

    def _create_pickle_file(self, source_file_path):
        data = pd.read_csv(source_file_path, **self.kwargs)
        pickle_file_path = source_file_path.replace(f'.{self.short_name}', '.pkl')
        data.to_pickle(pickle_file_path)

@data_source_type
class DataSourcePickle(DataSourceFile):
    short_name = "pkl"
    display_name = "Pickle"
    icon = "pickle_icon.png"

    def _create_pickle_file(self, source_file_path):
        """Already pickle file: kwargs does not work here"""
        pass
    
@data_source_type
class DataSourceXLSX(DataSourceFile):
    short_name = "xlsx"
    display_name = "Excel"
    icon = "xlsx_icon.png"

    def _create_pickle_file(self, source_file_path):
        data = pd.read_excel(source_file_path, **self.kwargs)
        pickle_file_path = source_file_path.replace(f'.{self.short_name}', '.pkl')
        data.to_pickle(pickle_file_path)

@data_source_type
class DataSourceJSON(DataSourceFile):
    short_name = "json"
    display_name = "JSON"
    icon = "json_icon.png"

    def _create_pickle_file(self, source_file_path):
        data = pd.read_json(source_file_path, **self.kwargs)
        pickle_file_path = source_file_path.replace(f'.{self.short_name}', '.pkl')
        data.to_pickle(pickle_file_path)
