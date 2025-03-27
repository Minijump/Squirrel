import pytest
import multiprocessing
import time
import os
import uvicorn
import socket
import shutil
from app.main import app

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
    
    os.chdir(temp_dir)
    
    proc = multiprocessing.Process(target=run_server, args=(port,))
    proc.start()
    
    time.sleep(1)
    server_url = f"http://127.0.0.1:{port}"
    yield server_url
    
    proc.terminate()
    proc.join()
    os.chdir(original_cwd)
