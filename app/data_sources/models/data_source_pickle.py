import os
import pandas as pd

from app.data_sources.models.data_source import DataSource, data_source_type

@data_source_type
class DataSourcePickle(DataSource):
    short_name = "pkl"
    display_name = "Pickle"
    icon = "pickle_icon.png"

    def __init__(self, manifest):
        super().__init__(manifest)

    @staticmethod
    def check_available_infos(form_data):
        """
        Check if the required infos are available

        * - source_file: ends with '.pkl'
          - DataSource()'s ones
        """
        source_file = form_data.get("source_file")

        if not source_file:
            raise ValueError("Source file is required")
        if not source_file.filename.endswith('.pkl'):
            raise ValueError("File must be a pickle file")
        
        DataSource.check_available_infos(form_data)

    @staticmethod
    def _generate_manifest(form_data):
        """
        Generates the manifest of the source

        * form_data(dict): The form data

        => Returns the manifest (dict)
        """
        manifest = DataSource._generate_manifest(form_data)
        return manifest

    async def _create_data_file(self, form_data):
        """
        Creates (copy) the data file for the source

        * form_data(dict): The form data
        """
        source_path = os.path.join(os.getcwd(), "_projects", form_data["project_dir"], "data_sources", self.directory) 
        data_file_name = 'data.' + 'pkl'
        source_file_path = os.path.join(source_path, data_file_name)
        source_file = form_data.get("source_file")
        with open(source_file_path, 'wb') as file:
            file.write(await source_file.read())

    def create_table(self, form_data):
        """
        Return the code to read data file
        """
        project_dir = form_data.get("project_dir")
        data_file_path = os.path.join(os.getcwd(), '_projects', project_dir, 'data_sources', self.directory, 'data.pkl')
        data_file_path = os.path.relpath(data_file_path, os.getcwd())
        table_name = form_data.get("table_name")
        return f"dfs['{table_name}'] = pd.read_pickle(r'{data_file_path}')  #sq_action:Create table {table_name} from {self.name}"
    