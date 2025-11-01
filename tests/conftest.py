import multiprocessing
import os
import pickle
import pytest
import shutil
import socket
import tempfile
import time
import uvicorn
import requests

from unittest.mock import patch

from selenium.webdriver.firefox.options import Options as FirefoxOptions  
from selenium.webdriver import Firefox

from app.main import app


def _copy_dir(src, dst, ignore=None):
    """Recursively copy a directory to a new location."""
    if ignore:
        ignore_func = shutil.ignore_patterns(ignore)
    else:
        ignore_func = None
    
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        
        if ignore and item == ignore:
            continue
        elif os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, ignore=ignore_func, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)

def _create_fake_pipeline():
    from app.pipelines.models.actions import CreateTable, AddColumn
    from app.pipelines.models.pipeline_action import PipelineAction
    action_1 = CreateTable({
            "project_dir": "ut_mock_project_1",
            "table_name": "ordered",
            "source_creation_type": "data_source",
            "data_source_dir": "Csv_ordered"
        }
    )
    pipeline_action_1 = PipelineAction(False, action_1)
    action_2 = CreateTable(
        {
            "project_dir": "ut_mock_project_1",
            "table_name": "random",
            "source_creation_type": "data_source",
            "data_source_dir": "Csv_random"
        }
    )
    pipeline_action_2 = PipelineAction(False, action_2)
    action_3 = AddColumn(
        {
            "project_dir": "ut_mock_project_1",
            "col_name": "ref + price",
            "value_type": "python",
            "table_name": "random",
            "col_value": "'reference' + 'price'"
        }
    )
    pipeline_action_3 = PipelineAction(False, action_3)
    pipeline = [pipeline_action_1, pipeline_action_2, pipeline_action_3]
    return pipeline

@pytest.fixture
def temp_project_dir_fixture():
    """Fixture that creates a temporary directory and patches os.getcwd to return it."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            projects_dir = os.path.join(temp_dir, "_projects")
            os.makedirs(projects_dir, exist_ok=True)
            
            project_dir = os.path.join(projects_dir, "ut_mock_project_1")
            os.makedirs(project_dir, exist_ok=True)
            _copy_dir("tests/utils/mock_projects/ut_mock_project_1", project_dir)
            pipeline = _create_fake_pipeline()
            with open(os.path.join(project_dir, "pipeline.pkl"), "wb") as f:
                pickle.dump(pipeline, f)

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
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def wait_for_server(url, timeout=10):
    """Wait for server to be ready"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(url, timeout=1)
            return True
        except:
            time.sleep(0.1)
    return False

_SERVER_TEMP_DIR = None

@pytest.fixture(scope="session")
def server(tmpdir_factory):
    """Start a server once for all tests"""
    global _SERVER_TEMP_DIR
    port = find_free_port()
    
    temp_dir = tmpdir_factory.mktemp("squirrel_test")
    _SERVER_TEMP_DIR = str(temp_dir)
    original_cwd = os.getcwd()
    _copy_dir(original_cwd, temp_dir, ignore="_projects")
    projects_dir = os.path.join(temp_dir, "_projects")
    os.makedirs(projects_dir)
    os.chdir(temp_dir)
    
    proc = multiprocessing.Process(target=run_server, args=(port,))
    proc.start()
    
    server_url = f"http://127.0.0.1:{port}"
    if not wait_for_server(server_url):
        proc.terminate()
        proc.join()
        os.chdir(original_cwd)
        raise RuntimeError("Server failed to start")

    yield server_url
    
    proc.terminate()
    proc.join()
    os.chdir(original_cwd)

_MOCK_PROJECT_CACHE = None

def _get_or_create_mock_project():
    """Cache the mock project structure to avoid repeated file operations"""
    global _MOCK_PROJECT_CACHE
    if _MOCK_PROJECT_CACHE is None:
        _MOCK_PROJECT_CACHE = {
            'pipeline': _create_fake_pipeline(),
            'files': {}
        }
        
        source_dir = "tests/utils/mock_projects/ut_mock_project_1"
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, source_dir)
                with open(src_path, 'rb') as f:
                    _MOCK_PROJECT_CACHE['files'][rel_path] = f.read()
    
    return _MOCK_PROJECT_CACHE

@pytest.fixture
def reset_projects(server):
    """Reset projects to initial state before each test"""
    global _SERVER_TEMP_DIR
    
    projects_dir = os.path.join(_SERVER_TEMP_DIR, "_projects")
    if os.path.exists(projects_dir):
        shutil.rmtree(projects_dir)
    os.makedirs(projects_dir)
    
    project_dir = os.path.join(projects_dir, "ut_mock_project_1") 
    os.makedirs(project_dir)
    
    cache = _get_or_create_mock_project()
    for rel_path, content in cache['files'].items():
        dst_path = os.path.join(project_dir, rel_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(dst_path, 'wb') as f:
            f.write(content)
    
    with open(os.path.join(project_dir, "pipeline.pkl"), "wb") as f:
        pickle.dump(cache['pipeline'], f)
    
    yield

@pytest.fixture(scope="session")
def browser():
    options = FirefoxOptions()
    if os.environ.get("BROWSER_HEADLESS", "1") == "1":
        options.add_argument('--headless')
    
    driver = Firefox(options=options)
    
    driver.set_window_size(1524, 716)
    yield driver
    driver.quit()

# Running Server for Tours: END -----------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------
