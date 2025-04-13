import multiprocessing
import os
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

    # Copy everything except projects (app codes, ...) to the temp directory
    for item in os.listdir(original_cwd):
        src_path = os.path.join(original_cwd, item)
        dst_path = os.path.join(temp_dir, item)
        
        if item == "_projects":
            continue
        elif os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
    
    # Create _projects directory in the temp directory
    projects_dir = temp_dir.mkdir("_projects")
    project_dir = projects_dir.mkdir("mock_project")
    for item in os.listdir("tests/utils/mock_projects/ut_mock_project_1"):
        src_path = os.path.join("tests/utils/mock_projects/ut_mock_project_1", item)
        dst_path = os.path.join(project_dir, item)
        
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
    
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
