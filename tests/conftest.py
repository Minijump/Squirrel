import pytest
import multiprocessing
import time
import os
import uvicorn
import socket
import shutil
from fastapi.testclient import TestClient
from app.main import app

def find_free_port():
    """Find a free port on localhost"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def run_server(port):
    """Run the FastAPI app with uvicorn"""
    uvicorn.run(app, host="127.0.0.1", port=port)

# @pytest.fixture(scope="function")
# def server():
#     """Start a server in a separate process and yield the URL"""
#     # Find an available port
#     port = find_free_port()
    
#     # Start the server in a separate process
#     proc = multiprocessing.Process(target=run_server, args=(port,))
#     proc.start()
    
#     # Wait for server to start
#     time.sleep(1)
    
#     server_url = f"http://127.0.0.1:{port}"
    
#     # Yield the server URL to the test
#     yield server_url
    
#     # Teardown - stop the server
#     proc.terminate()
#     proc.join()

@pytest.fixture(scope="function")
def server(tmpdir):
    """Start a server in a separate process using a temporary directory and yield the URL"""
    # Find an available port
    port = find_free_port()
    
    # Original working directory
    original_cwd = os.getcwd()
    
    # Create a temporary directory for the test
    temp_dir = tmpdir.mkdir("squirrel_test")
    
       # Copy all files from the original directory to the temp directory
    # excluding the _projects directory
    def ignore_projects(src, names):
        return ["_projects"] if "_projects" in names else []
    
    # Copy everything from the original working directory to the temp directory
    for item in os.listdir(original_cwd):
        src_path = os.path.join(original_cwd, item)
        dst_path = os.path.join(temp_dir, item)
        
        if item == "_projects":
            # Skip _projects directory
            continue
        elif os.path.isdir(src_path):
            # Copy directory recursively
            shutil.copytree(src_path, dst_path, ignore=ignore_projects)
        else:
            # Copy file
            shutil.copy2(src_path, dst_path)
    
    # Create empty _projects directory in the temp directory
    os.makedirs(os.path.join(temp_dir, "_projects"), exist_ok=True)
    
    # Change working directory to the temp directory
    os.chdir(temp_dir)
    
    # Start the server in a separate process
    proc = multiprocessing.Process(target=run_server, args=(port,))
    proc.start()
    
    # Wait for server to start
    time.sleep(1)
    
    server_url = f"http://127.0.0.1:{port}"
    
    # Yield the server URL to the test
    yield server_url
    
    # Teardown - stop the server
    proc.terminate()
    proc.join()
    
    # Restore original working directory
    os.chdir(original_cwd)
