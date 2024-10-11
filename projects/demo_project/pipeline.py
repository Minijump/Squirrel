import pandas as pd


def run_pipeline():
    dfs = {}

    # Squirrel Pipeline start
    dfs['table1'] = pd.read_csv(r'C:\Users\sacha\Documents\projects\Squirrel\projects\demo_project\data_sources\demo_data_source\data.csv')  #sq_action:Create table table1 from demo_data_source
    dfs['table1']['col_test'] = 1  #sq_action:Add column col_test on table table1
    dfs['table1']['col_test2'] = 9  #sq_action:Add column col_test2 on table table1
    dfs['table2'] = pd.read_csv(r'C:\Users\sacha\Documents\projects\Squirrel\projects\demo_project\data_sources\demo_data_source\data.csv')  #sq_action:Create table table2 from demo_data_source
    dfs['table2']['heloooo'] = 88  #sq_action:Add column heloooo on table table2
    dfs['table2'] = dfs['table2'].drop(columns=['price'])  #sq_action:Delete column price on table table2
    dfs['table3'] = pd.read_csv(r'C:\Users\sacha\Documents\projects\Squirrel\projects\demo_project\data_sources\demo_data_source\data.csv')  #sq_action:Create table table3 from demo_data_source
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    return dfs
