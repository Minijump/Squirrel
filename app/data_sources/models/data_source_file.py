import os

from app.data_sources.models.data_source import DataSource, data_source_type

class DataSourceFile(DataSource):
    short_name = "file_extension (without dot)"
    display_name = "File name"

    def __init__(self, manifest):
        super().__init__(manifest)

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

    async def _create_data_file(self, form_data):
        """
        Creates (copy) the data file for the source

        * form_data(dict): The form data
        """
        source_path = os.path.join(os.getcwd(), "_projects", form_data["project_dir"], "data_sources", self.directory) 
        data_file_name = 'data.' + self.short_name
        source_file_path = os.path.join(source_path, data_file_name)
        source_file = form_data.get("source_file")
        with open(source_file_path, 'wb') as file:
            file.write(await source_file.read())

    async def update_data_file(self, content, updated_data):
        """
        Update the data file for the source

        * new_file: The new file
        * updated_data: The updated data
        """
        source_path = os.path.join(os.getcwd(), "_projects", updated_data["project_dir"], "data_sources", self.directory) 
        data_file_name = 'data.' + self.short_name
        source_file_path = os.path.join(source_path, data_file_name)
        with open(source_file_path, 'wb') as file:
            file.write(content)
    
    @classmethod
    async def _update_source_settings(cls, source, updated_data):
        """
        Update the source's values with the updated data, replace the file if it's not empty

        * source(dict): contains the current settings
        * updated_data(dict): contains the new settings

        => Returns the updated source
        """
        new_file = dict(updated_data).get("file")
        if new_file:
            content = await new_file.read()
            if content:
                await cls(source).update_data_file(content, updated_data)
        
        updated_source = await DataSource._update_source_settings(source, updated_data)
        return updated_source
