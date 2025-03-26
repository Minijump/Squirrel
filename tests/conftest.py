import pytest
import multiprocessing
import time
import os
import uvicorn
import socket
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

@pytest.fixture(scope="function")
def server():
    """Start a server in a separate process and yield the URL"""
    # Find an available port
    port = find_free_port()
    
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
