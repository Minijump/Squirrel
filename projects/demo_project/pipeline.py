import pandas as pd


def run_pipeline():
    df = False
    # Squirrel Pipeline start
    df = pd.read_csv(r'C:\Users\sacha\Documents\projects\Squirrel\projects\demo_project\data_sources\demo_data_source\data.csv')
    df['test'] = 3
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    # No edit under
    return df
