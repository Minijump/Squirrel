import json
import pandas as pd
import pytest

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

    # Data sources directory + mock source
    project_dir.mkdir("data_sources")
    # (csv)
    csv_source_dir = project_dir.join("data_sources").mkdir("mock_source_csv")
    csv_source_dir.join("__manifest__.json").write(json.dumps({
        "name": "Mock source csv",
        "type": "csv",
        "description": "a mock csv source",
        "directory": "mock_source_csv"
    }, indent=4))
    with open("tests/mock_datas/demo_ordered_data.csv", "r") as f:
        csv_source_dir.join("data.csv").write(f.read())
    pd.read_csv(csv_source_dir.join("data.csv")).to_pickle(csv_source_dir.join("data.pkl"))
    
    # Pipeline file
    pipeline_file = project_dir.join("pipeline.py")
    with open("tests/mock_datas/mock_pipeline.py", "r") as f:
        pipeline_file.write(f.read())

    return str(project_dir)
