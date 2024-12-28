import ast
import yfinance as yf
import pandas as pd

from app.data_sources.models.data_source import data_source_type
from app.data_sources.models.data_source_api import DataSourceAPI

@data_source_type
class DataSourceYahooFinance(DataSourceAPI):
    # Uses yfinance to get data from Yahoo Finance, if more infos are required use official yahoo finance API
    short_name = "yahoo_finance"
    display_name = "Yahoo Finance"
    icon = "yahoo_finance_icon.png"

    def __init__(self, manifest):
        super().__init__(manifest)
        self.tickers = manifest.get("tickers")
        self.start_date = manifest.get("start_date")
        self.end_date = manifest.get("end_date")
        self.interval = manifest.get("interval")
        # misc to select only columns such as close,...

    @staticmethod
    def check_available_infos(form_data):
        required_fields = ["tickers", "start_date", "end_date", "interval"]
        DataSourceAPI.check_available_infos(form_data, required_fields)

    @staticmethod
    def _generate_manifest(form_data):
        manifest = DataSourceAPI._generate_manifest(form_data)
        manifest["tickers"] = ast.literal_eval(form_data.get("tickers"))
        manifest["start_date"] = form_data.get("start_date")
        manifest["end_date"] = form_data.get("end_date")
        manifest["interval"] = form_data.get("interval")
        return manifest

    async def _get_data_from_api(self):
        tickers = self.tickers
        start_date = self.start_date
        end_date = self.end_date
        interval = self.interval

        data = yf.download(tickers, start=start_date, end=end_date, interval=interval)#returns a df
        data.reset_index(inplace=True) # keep the date
        data.columns = data.columns.set_names([None] * data.columns.nlevels) # removes the 'useless' lines name (created by multi-level, create an empty column)

        return data

    @classmethod
    async def _update_source_settings(cls, source, updated_data):
        """
        Update the source's values with the updated data, convert 'fields' and 'domain' to list
        """
        updated_source = await DataSourceAPI._update_source_settings(source, updated_data)

        updated_source["tickers"] = ast.literal_eval(updated_source["tickers"])

        return updated_source