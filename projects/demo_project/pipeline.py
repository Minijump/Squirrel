import pandas as pd


def run_pipeline():
    dfs = {}

    # Squirrel Pipeline start
    dfs['table1'] = pd.read_csv(r'projects\demo_project\data_sources\demo_data_source\data.csv')  #sq_action:Create table table1 from demo_data_source
    dfs['table2'] = pd.read_csv(r'projects\demo_project\data_sources\demo_data_source\data.csv')  #sq_action:Create table table2 from demo_data_source
    dfs['table1']['col1'] = 9  #sq_action:Add column col1 on table table1
    dfs['table2'] = dfs['table2'].drop(columns=['price'])  #sq_action:Delete column price on table table2
    dfs['table2']['col2'] = 88  #sq_action:Add column col2 on table table2
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    return dfs
