# __init__ file is required to fill data of data_source_type
# TODO: goal of data_source_type was to make the addition of a new datasource easy, 
# if we need to add an import, there is no reason to keep it. => change that (see how actions are done?)
from .data_source_factory import data_source_type
from .data_source_api_odoo import DataSourceOdoo
from .data_source_api_yahoo_finance import DataSourceYahooFinance
from .data_source_file import DataSourceCSV, DataSourceXLSX, DataSourcePickle, DataSourceJSON
