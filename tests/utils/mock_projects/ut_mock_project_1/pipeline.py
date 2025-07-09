import pandas as pd

def run_pipeline():
    tables = {}
    
    # Squirrel Pipeline start
    tables['ordered'] = pd.read_pickle(r'_projects\ut_mock_project_1\data_sources\Csv_ordered\data.pkl')  #sq_action:Create table ordered from Csv ordered
    tables['random'] = pd.read_pickle(r'_projects\ut_mock_project_1\data_sources\Csv_random\data.pkl')  #sq_action:Create table random from Csv random
    tables['random']['ref + price'] = tables['random']['reference'] + tables['random']['price']  #sq_action:Add column ref + price on table random
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    return tables
