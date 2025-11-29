import os
import datetime

from app.data_sources.models.data_source import DataSource

class DataSourceAPI(DataSource):
    short_name = "short_name"
    display_name = "Display name"
    icon = ""

    def __init__(self, manifest):
        super().__init__(manifest)
        self.last_sync = manifest.get("last_sync")

    @staticmethod
    def _generate_manifest_content(form_data):
        manifest = DataSource._generate_manifest_content(form_data)
        manifest["last_sync"] = ""
        return manifest
    
    async def _get_data_from_api(self):
        """To be overriden by subclasses"""
        pass

    async def _create_data_file(self, form_data):
        data = await self._get_data_from_api()
        data_file_path = os.path.join(self.path, 'data.pkl')
        data.to_pickle(data_file_path)
        self._update_last_sync()

    def _update_last_sync(self):
        last_sync = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_sync = last_sync

        manifest = self._read_manifest()
        manifest["last_sync"] = last_sync
        self._write_manifest(manifest)

    async def sync(self):
        await self._create_data_file(False)
