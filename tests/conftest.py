import multiprocessing
import os
import pandas as pd
import pytest
import shutil
import socket
import tempfile
import time
from unittest.mock import patch
import uvicorn

from app.main import app

@pytest.fixture
def temp_project_dir_fixture():
    """Fixture that creates a temporary directory and patches os.getcwd to return it."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            yield temp_dir


# Running Server for Tours: START ---------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------
def find_free_port():
    """Find a free port on localhost"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def run_server(port):
    """Run the FastAPI app with uvicorn"""
    uvicorn.run(app, host="127.0.0.1", port=port)

@pytest.fixture(scope="function")
def server(tmpdir):
    """Start a server in a separate process using a temporary directory and yield the URL"""
    port = find_free_port()
    
    original_cwd = os.getcwd()
    temp_dir = tmpdir.mkdir("squirrel_test")
    
    # Copy everything from the original working directory to the temp directory
    for item in os.listdir(original_cwd):
        src_path = os.path.join(original_cwd, item)
        dst_path = os.path.join(temp_dir, item)
        
        if item == "_projects":
            continue
        elif os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
    os.makedirs(os.path.join(temp_dir, "_projects"), exist_ok=True)

    mock_project_dir = temp_dir.join("_projects").mkdir("mock_project")
    mock_project_dir.join("__manifest__.json").write('{"name": "Mock project", "description": "A mock project use in unit tests", "directory": "mock_project", "project_type": "std", "misc": {}}')
    mock_project_dir.mkdir("data_sources").mkdir("mock_source_csv")
    mock_project_dir.join("data_sources/mock_source_csv/__manifest__.json").write('{"name": "Mock source csv", "type": "csv", "description": "a mock csv source", "directory": "mock_source_csv"}')
    with open("tests/mock_datas/demo_ordered_data.csv", "r") as f:
        mock_project_dir.join("data_sources/mock_source_csv/data.csv").write(f.read())
    pd.read_csv(mock_project_dir.join("data_sources/mock_source_csv/data.csv")).to_pickle(mock_project_dir.join("data_sources/mock_source_csv/data.pkl"))
    mock_project_dir.join("data_sources").mkdir("mock_source_csv_2")
    mock_project_dir.join("data_sources/mock_source_csv_2/__manifest__.json").write('{"name": "Mock source csv 2", "type": "csv", "description": "a 2nd mock csv source", "directory": "mock_source_csv_2"}')
    with open("tests/mock_datas/demo_ordered_data.csv", "r") as f:
        mock_project_dir.join("data_sources/mock_source_csv_2/data.csv").write(f.read())
    pd.read_csv(mock_project_dir.join("data_sources/mock_source_csv_2/data.csv")).to_pickle(mock_project_dir.join("data_sources/mock_source_csv_2/data.pkl"))
    with open("tests/mock_datas/mock_pipeline.py", "r") as f:
        mock_project_dir.join("pipeline.py").write(f.read())
    
    os.chdir(temp_dir)
    
    proc = multiprocessing.Process(target=run_server, args=(port,))
    proc.start()
    
    time.sleep(1)
    server_url = f"http://127.0.0.1:{port}"
    yield server_url
    
    proc.terminate()
    proc.join()
    os.chdir(original_cwd)

# Running Server for Tours: END -----------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------
