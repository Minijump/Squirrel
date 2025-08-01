
import pandas as pd

def run_pipeline():
    tables = {}
    
    # Squirrel Pipeline start
    tables['Tech_stocks'] = pd.read_pickle(r'_projects\demo_project\data_sources\Stock_tech\data.pkl')  #sq_action:Create table Tech_stocks from Stock_tech
    tables['AU_stock'] = pd.read_pickle(r'_projects\demo_project\data_sources\Stock_AU\data.pkl')  #sq_action:Create table AU_stock from Stock_AU
    tables['Mosck_csv'] = pd.read_csv(r'_projects\demo_project\data_sources\Mock_CSV\data.csv')  #sq_action:Create table Mosck_csv from Mock CSV
    tables['pickle_file'] = pd.read_pickle(r'_projects\demo_project\data_sources\Mock_Pickle\data.pkl')  #sq_action:Create table pickle_file from Mock Pickle
    tables['pickle_file']['test'] = "test"  #sq_action:Add column test on table pickle_file
    tables['pickle_file']['test'] = tables['pickle_file']['test'].astype('string')  #sq_action:Change type of column test to string in table pickle_file
    tables['pickle_file'] = tables['pickle_file'].sort_values(by=['id'], ascending=True)  #sq_action:Sort(asc) id of table pickle_file
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    return tables
