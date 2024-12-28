import os
import ast
import pandas as pd

from app.data_sources.models.data_source import DataSource, data_source_type

class DataSourceFile(DataSource):
    short_name = "file_extension (without dot)"
    display_name = "File Type name"
    icon = ""

    def __init__(self, manifest):
        super().__init__(manifest)
        self.kwargs = manifest.get("kwargs") or {}

    @classmethod
    def check_available_infos(cls, form_data):
        """
        Check if the required infos are available
        """
        source_file = form_data.get("source_file")

        if not source_file:
            raise ValueError("Source file is required")
        if not source_file.filename.endswith('.' + cls.short_name):
            raise ValueError(f"File must be a {cls.short_name} file")
        
        DataSource.check_available_infos(form_data)

    @staticmethod
    def _generate_manifest(form_data):
        """
        Generates the manifest of the source

        * form_data(dict): The form data

        => Returns the manifest (dict)
        """
        manifest = DataSource._generate_manifest(form_data)
        manifest["kwargs"] = ast.literal_eval(form_data.get("kwargs")) if form_data.get("kwargs") else {}
        return manifest

    async def _create_pickle_file(self, source_file_path):
        """
        To be implemented by the child class
        """
        pass

    async def _create_data_file(self, form_data, content=False):
        """
        Creates (copy) the data file for the source

        * form_data(dict): The form data
        """
        source_path = os.path.join(os.getcwd(), "_projects", form_data["project_dir"], "data_sources", self.directory)
        source_file_path = os.path.join(source_path, 'data.' + self.short_name)
        form_data_content = await form_data.get("source_file").read() if form_data.get("source_file") else False
        content = content or form_data_content
        if content:
            with open(source_file_path, 'wb') as file:
                file.write(content)

        # All sources are converted to pickle files, this increase the speed of reading the data
        # However, the drawback is that if the user change the file (csv,...) manually, the changes will not be reflected 
        # (must use the settings page) => Is there something to do about this?
        await self._create_pickle_file(source_file_path)
    
    @classmethod
    async def _update_source_settings(cls, source, updated_data):
        """
        Update the source's values with the updated data, replace the file if it's not empty

        * source(dict): contains the current settings
        * updated_data(dict): contains the new settings

        => Returns the updated source
        """
        old_kwargs = source.get("kwargs") or {}

        updated_source = await DataSource._update_source_settings(source, updated_data)
        updated_source["kwargs"] = ast.literal_eval(updated_source["kwargs"]) if updated_source.get("kwargs") else {}

        new_file = dict(updated_data).get("file")
        new_kwargs = old_kwargs != source.get("kwargs")
        content = False
        if new_file:
            content = await new_file.read()

        if content:
            await cls(source)._create_data_file(updated_data, content)
        elif new_kwargs:
            await cls(source)._create_data_file(updated_data)

        return updated_source
    
    def create_table(self, form_data):
        """
        Return the code to read data file
        """
        project_dir = form_data.get("project_dir")
        data_file_path = os.path.join(os.getcwd(), '_projects', project_dir, 'data_sources', self.directory, 'data.pkl')
        data_file_path = os.path.relpath(data_file_path, os.getcwd())
        table_name = form_data.get("table_name")
        return f"dfs['{table_name}'] = pd.read_pickle(r'{data_file_path}')  #sq_action:Create table {table_name} from {self.name}"

@data_source_type
class DataSourceCSV(DataSourceFile):
    short_name = "csv"
    display_name = "CSV"
    icon = "csv_icon.png"

    async def _create_pickle_file(self, source_file_path):
        """
        Create a pickle file from the source file

        * source_file_path(str): The source file path
        """
        data = pd.read_csv(source_file_path, **self.kwargs)
        pickle_file_path = source_file_path.replace(f'.{self.short_name}', '.pkl')
        data.to_pickle(pickle_file_path)

@data_source_type
class DataSourcePickle(DataSourceFile):
    short_name = "pkl"
    display_name = "Pickle"
    icon = "pickle_icon.png"

    async def _create_pickle_file(self, source_file_path):
        """
        Already pickle file: kwargs does not work here
        """
        pass
    
@data_source_type
class DataSourceXLSX(DataSourceFile):
    short_name = "xlsx"
    display_name = "Excel"
    icon = "xlsx_icon.png"

    async def _create_pickle_file(self, source_file_path):
        """
        Create a pickle file from the source file

        * source_file_path(str): The source file path
        """
        data = pd.read_excel(source_file_path, **self.kwargs)
        pickle_file_path = source_file_path.replace(f'.{self.short_name}', '.pkl')
        data.to_pickle(pickle_file_path)

@data_source_type
class DataSourceJSON(DataSourceFile):
    short_name = "json"
    display_name = "JSON"
    icon = "json_icon.png"

    async def _create_pickle_file(self, source_file_path):
        """
        Create a pickle file from the source file

        * source_file_path(str): The source file path
        """
        data = pd.read_json(source_file_path, **self.kwargs)
        pickle_file_path = source_file_path.replace(f'.{self.short_name}', '.pkl')
        data.to_pickle(pickle_file_path)
