import os
import json
import datetime
import ast
import yfinance as yf
import pandas as pd

from app.data_sources.models.data_source import DataSource, data_source_type

@data_source_type
class DataSourceYahooFinance(DataSource):
    short_name = "yahoo_finance"
    display_name = "Yahoo Finance"
    icon = "yahoo_finance_icon.png"

    def __init__(self, manifest):
        super().__init__(manifest)
        self.tickers = manifest.get("tickers")
        self.start_date = manifest.get("start_date")
        self.end_date = manifest.get("end_date")
        self.interval = manifest.get("interval")
        self.last_sync = manifest.get("last_sync")
        # misc to select only columns such as close,...

    @staticmethod
    def check_available_infos(form_data):
        required_fields = ["tickers", "start_date", "end_date", "interval"]
        for field in required_fields:
            if not form_data.get(field):
                raise ValueError(f"{field} is required")
        
        DataSource.check_available_infos(form_data)

    @staticmethod
    def _generate_manifest(form_data):
        manifest = DataSource._generate_manifest(form_data)
        manifest["tickers"] = ast.literal_eval(form_data.get("tickers"))
        manifest["start_date"] = form_data.get("start_date")
        manifest["end_date"] = form_data.get("end_date")
        manifest["interval"] = form_data.get("interval")
        manifest["last_sync"] = ""
        return manifest

    async def _create_data_file(self, form_data):
        tickers = self.tickers
        start_date = self.start_date
        end_date = self.end_date
        interval = self.interval

        data = yf.download(tickers, start=start_date, end=end_date, interval=interval)
        data.reset_index(inplace=True) # keep the date
        data.columns = data.columns.set_names([None] * data.columns.nlevels) # remove the 'useless' lines name (created by multi-level, create an empty column)

        data_file_path = os.path.join(os.getcwd(), "_projects", form_data["project_dir"], "data_sources", self.directory, 'data.pkl')
        data.to_pickle(data_file_path)

        await self.update_last_sync(form_data["project_dir"])

    def create_table(self, form_data):
        project_dir = form_data.get("project_dir")
        data_file_path = os.path.join(os.getcwd(), '_projects', project_dir, 'data_sources', self.directory, 'data.pkl')
        data_file_path = os.path.relpath(data_file_path, os.getcwd())
        table_name = form_data.get("table_name")
        return f"dfs['{table_name}'] = pd.read_pickle(r'{data_file_path}')  #sq_action:Create table {table_name} from {self.name}"

    async def update_last_sync(self, project_dir):
        last_sync = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_sync = last_sync

        manifest_path = os.path.join(os.getcwd(), "_projects", project_dir, "data_sources", self.directory, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest = json.load(file)

        manifest["last_sync"] = last_sync

        with open(manifest_path, 'w') as file:
            json.dump(manifest, file, indent=4)

    async def sync(self, project_dir):
        await self._create_data_file({"project_dir": project_dir})

    @classmethod
    async def _update_source_settings(cls, source, updated_data):
        """
        Update the source's values with the updated data, convert 'fields' and 'domain' to list

        * source(dict): contains the current settings
        * updated_data(dict): contains the new settings

        => Returns the updated source
        """
        updated_source = await DataSource._update_source_settings(source, updated_data)

        updated_source["tickers"] = ast.literal_eval(updated_source["tickers"])

        return updated_source