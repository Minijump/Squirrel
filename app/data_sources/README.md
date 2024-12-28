# Data Sources

This module provides various classes and functions to handle different types of data sources in the Squirrel application. 

## Main Classes
### DataSource
The base class for all data sources. It provides common methods and attributes that all data sources share.

### DataSourceFile
A subclass of `DataSource` for handling file-based data sources. It provides methods to create and manage data files. 
Some available subclasses are DataSourceCSV, DataSourcePickle, DataSourceXLSX 

### DataSourceAPI
A subclass of `DataSource` for handling API-based data sources. It provides methods to fetch data from APIs and manage the data.
Some available subclasses ar DataSourceOdoo, DataSourceYahooFinance

## Structure
If you want an DataSource type to be available for the users, you need to add the `@data_source_type` decorator on the top of your class (it also requires to give an unique short_name to your class). 

Every sublass can use the methods of their parents one but some must be implemented. Consider reading the code of the parent classes to know which ones.
