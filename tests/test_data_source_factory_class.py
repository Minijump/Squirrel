from app.data_sources.models.data_source_factory import DataSourceFactory

# Test to init_source_from_dir and create_source are in subclasses tests

def test_get_available_type(temp_project_dir_fixture):
    available_types = DataSourceFactory.get_available_type()

    assert ('csv', 'CSV') in available_types
    assert ('odoo', 'Odoo') in available_types
    assert ('yahoo_finance', 'Yahoo Finance') in available_types
    assert ('xlsx', 'Excel') in available_types
    assert ('json', 'JSON') in available_types
    assert ('pkl', 'Pickle') in available_types

def test_get_source_class(temp_project_dir_fixture):
    source_classes = {
        'csv': 'DataSourceCSV',
        'odoo': 'DataSourceOdoo',
        'yahoo_finance': 'DataSourceYahooFinance',
        'xlsx': 'DataSourceXLSX',
        'json': 'DataSourceJSON',
        'pkl': 'DataSourcePickle',
    }
    for key, expected_class_name in source_classes.items():
        source_class = DataSourceFactory.get_source_class(key)
        assert source_class.__name__ == expected_class_name
