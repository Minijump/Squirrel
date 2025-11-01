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
from app.pipelines.models.actions import CreateTable, AddColumn
from app.pipelines.models.pipeline_action import PipelineAction


class MockProjectBuilder:
    PROJECT_NAME = "ut_mock_project_1"
    SOURCE_DIR = "tests/utils/mock_projects/ut_mock_project_1"
    
    _cache = None
    
    @classmethod
    def build_pipeline(cls):
        actions = [
            PipelineAction(False, CreateTable({
                "project_dir": cls.PROJECT_NAME,
                "table_name": "ordered",
                "source_creation_type": "data_source",
                "data_source_dir": "Csv_ordered"
            })),
            PipelineAction(False, CreateTable({
                "project_dir": cls.PROJECT_NAME,
                "table_name": "random",
                "source_creation_type": "data_source",
                "data_source_dir": "Csv_random"
            })),
            PipelineAction(False, AddColumn({
                "project_dir": cls.PROJECT_NAME,
                "col_name": "ref + price",
                "value_type": "python",
                "table_name": "random",
                "col_value": "'reference' + 'price'"
            }))
        ]
        return actions
    
    @classmethod
    def get_cached_project(cls):
        if cls._cache is None:
            cls._cache = {
                'pipeline': cls.build_pipeline(),
                'files': {}
            }
            
            for root, _, files in os.walk(cls.SOURCE_DIR):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, cls.SOURCE_DIR)
                    with open(src_path, 'rb') as f:
                        cls._cache['files'][rel_path] = f.read()
        
        return cls._cache
    
    @classmethod
    def copy_to(cls, dst):
        for item in os.listdir(cls.SOURCE_DIR):
            src_path = os.path.join(cls.SOURCE_DIR, item)
            dst_path = os.path.join(dst, item)
            
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)
    
    @classmethod
    def create_from_cache(cls, project_dir):
        cache = cls.get_cached_project()
        
        for rel_path, content in cache['files'].items():
            dst_path = os.path.join(project_dir, rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            with open(dst_path, 'wb') as f:
                f.write(content)
        
        with open(os.path.join(project_dir, "pipeline.pkl"), "wb") as f:
            pickle.dump(cache['pipeline'], f)


class TestServer:
    _temp_dir = None
    
    @staticmethod
    def _copy_dir(src, dst, ignore=None):
        ignore_func = shutil.ignore_patterns(ignore) if ignore else None
        
        for item in os.listdir(src):
            if ignore and item == ignore:
                continue
            
            src_path = os.path.join(src, item)
            dst_path = os.path.join(dst, item)
            
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, ignore=ignore_func, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)
    
    @classmethod
    def find_free_port(cls):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    @classmethod
    def run(cls, port):
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")
    
    @classmethod
    def wait_until_ready(cls, url, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            try:
                requests.get(url, timeout=1)
                return True
            except:
                time.sleep(0.1)
        return False
    
    @classmethod
    def setup(cls, tmpdir_factory):
        port = cls.find_free_port()
        temp_dir = tmpdir_factory.mktemp("squirrel_test")
        cls._temp_dir = str(temp_dir)
        
        original_cwd = os.getcwd()
        cls._copy_dir(original_cwd, temp_dir, ignore="_projects")
        os.makedirs(os.path.join(temp_dir, "_projects"))
        os.chdir(temp_dir)
        
        proc = multiprocessing.Process(target=cls.run, args=(port,))
        proc.start()
        
        server_url = f"http://127.0.0.1:{port}"
        if not cls.wait_until_ready(server_url):
            proc.terminate()
            proc.join()
            os.chdir(original_cwd)
            raise RuntimeError("Server failed to start")
        
        return proc, server_url, original_cwd
    
    @classmethod
    def teardown(cls, proc, original_cwd):
        proc.terminate()
        proc.join()
        os.chdir(original_cwd)
    
    @classmethod
    def reset_projects(cls):
        projects_dir = os.path.join(cls._temp_dir, "_projects")
        if os.path.exists(projects_dir):
            shutil.rmtree(projects_dir)
        os.makedirs(projects_dir)
        
        project_dir = os.path.join(projects_dir, MockProjectBuilder.PROJECT_NAME)
        os.makedirs(project_dir)
        MockProjectBuilder.create_from_cache(project_dir)


@pytest.fixture
def temp_project_dir_fixture():
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            projects_dir = os.path.join(temp_dir, "_projects")
            os.makedirs(projects_dir, exist_ok=True)
            
            project_dir = os.path.join(projects_dir, MockProjectBuilder.PROJECT_NAME)
            os.makedirs(project_dir, exist_ok=True)
            MockProjectBuilder.copy_to(project_dir)
            
            pipeline = MockProjectBuilder.build_pipeline()
            with open(os.path.join(project_dir, "pipeline.pkl"), "wb") as f:
                pickle.dump(pipeline, f)
            
            yield temp_dir


@pytest.fixture(scope="session")
def server(tmpdir_factory):
    proc, server_url, original_cwd = TestServer.setup(tmpdir_factory)
    yield server_url
    TestServer.teardown(proc, original_cwd)


@pytest.fixture
def reset_projects(server):
    TestServer.reset_projects()
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
