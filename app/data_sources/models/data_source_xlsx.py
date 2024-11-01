import os

from app.data_sources.models.data_source import DataSource, data_source_type

@data_source_type
class DataSourceXLSX(DataSource):
    short_name = "xlsx"
    display_name = "Excel"

    def __init__(self, manifest, form_data):
        super().__init__(manifest)
        self.source_file = form_data['source_file']

    @staticmethod
    def check_available_infos(form_data):
        """
        Check if the required infos are available

        * - source_file: ends with '.xlsx'
          - DataSource()'s ones
        """
        source_file = form_data.get("source_file")

        if not source_file:
            raise ValueError("Source file is required")
        if not source_file.filename.endswith('.xlsx'):
            raise ValueError("File must be an xlsx file")
        
        DataSource.check_available_infos(form_data)

    async def _create_data_file(self, form_data):
        """
        Creates (copy) the data file for the source

        * form_data(dict): The form data
        """
        source_path = os.path.join(os.getcwd(), "_projects", form_data["project_dir"], "data_sources", self.directory) 
        data_file_name = 'data.' + 'xlsx'
        source_file_path = os.path.join(source_path, data_file_name)
        with open(source_file_path, 'wb') as file:
            file.write(await self.source_file.read())