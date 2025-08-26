import ast
import yfinance as yf

from app.data_sources.models.data_source_factory import data_source_type
from app.data_sources.models.data_source_api import DataSourceAPI

@data_source_type
class DataSourceYahooFinance(DataSourceAPI):
    # Uses yfinance to get data from Yahoo Finance, if more infos are required use official yahoo finance API
    short_name = "yahoo_finance"
    display_name = "Yahoo Finance"
    icon = "yahoo_finance_icon.png"

    @classmethod
    def get_source_specific_args(cls, is_settings=False):
        return {
            "tickers": {
                "type": "text",
                "label": "Tickers",
                "required": True,
                "info": "With format: ['ticker1', 'ticker2', ...]",
            },
            "start_date": {
                "type": "date",
                "label": "Start Date",
                "required": True,
            },
            "end_date": {
                "type": "date",
                "label": "End Date",
                "required": True,
            },
            "interval": {
                "type": "select",
                "label": "Interval",
                "required": True,
                "select_options": [("1d", "1 Day"), ("1wk", "1 Week"), ("1mo", "1 Month")],
            },
        }

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
        updated_source = await DataSourceAPI._update_source_settings(source, updated_data)

        updated_source["tickers"] = ast.literal_eval(updated_source["tickers"])

        return updated_source