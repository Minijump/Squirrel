import pytest
import json

@pytest.fixture
def mock_project(tmpdir):
    """ 
    Create a mock project used in unit tests

    => Returns the path to the mock project directory
    """
    project_dir = tmpdir.mkdir("mock_project")
    
    # Create necessary files and directories within the mock project
    # Manifest file
    manifest_file = project_dir.join("__manifest__.json")
    manifest_content = {
        "name": "Mock project",
        "description": "A mock project use in unit tests",
        "directory": "mock_project"
    }
    manifest_file.write(json.dumps(manifest_content, indent=4))

    # Data sources directory
    project_dir.mkdir("data_sources")

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

    df = pd.DataFrame(data, columns=['name', 'price'])

    # Squirrel Pipeline start
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    # No edit under
    return df""")

    # Return the path to the mock project directory
    return str(project_dir)
