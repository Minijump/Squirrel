import pytest
import json

@pytest.fixture
def mock_project(tmpdir):
    """ 
    Create a mock project used in unit tests

    => Returns the path to the mock project directory
    """
    working_dir = tmpdir.mkdir("_projects")
    project_dir = working_dir.mkdir("mock_project")
    
    # Create necessary files and directories within the mock project
    # Manifest file
    manifest_file = project_dir.join("__manifest__.json")
    manifest_content = {
        "name": "Mock project",
        "description": "A mock project use in unit tests",
        "directory": "mock_project",
        "project_type": "std",
        "misc": {}
    }
    manifest_file.write(json.dumps(manifest_content, indent=4))

    # Data sources directory
    project_dir.mkdir("data_sources")
    # Create mock data source
    # csv
    csv_source_dir = project_dir.join("data_sources").mkdir("mock_source_csv")
    csv_source_dir.join("__manifest__.json").write(json.dumps({
        "name": "Mock source csv",
        "type": "csv",
        "description": "a mock csv source",
        "directory": "mock_source_csv"
    }, indent=4))
    csv_source_dir.join("data.csv").write("mock_name,mock_price"+"".join([f"\nmock{i},{i}" for i in range(100)]))
    #create a dataframe and add it in a data.pkl file
    import pandas as pd
    data = []
    for i in range(100):
        name = 'name'
        list_price = i
        data.append([name, list_price])
    pd.DataFrame(data, columns=['mock_name', 'mock_price']).to_pickle(csv_source_dir.join("data.pkl"))

    # Pipeline file
    pipeline_file = project_dir.join("pipeline.py")
    pipeline_file.write("""
import pandas as pd

def run_pipeline():
    data = []
    for _ in range(100):
        name = 'test'
        list_price = 10
        data.append([name, list_price])
    dfs = {}
    dfs['df'] = pd.DataFrame(data, columns=['name', 'price'])

    # Squirrel Pipeline start
    dfs['df']['action1'] = 1  #sq_action: action1
    #Useless comment, must have no effect (comment + 2 next python line should be 1 action)
    dfs['df']['action2'] = 1
    dfs['df']['action2'] = 2  #sq_action: action2
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    # No edit under
    return dfs""")

    # Return the path to the mock project directory
    # Path to the project, not the directory as it should be: to change
    return str(project_dir)
