from fastapi.testclient import TestClient

import os
import tempfile
from unittest.mock import patch
import json
import pytest

from app.main import app
from tests import mock_project

from app.projects.models.project import Project, BASIC_PIPELINE, PROJECT_TYPE_REGISTRY

client = TestClient(app)

# Test models
#----------------------------------------------------------------------------------
@pytest.mark.asyncio()
async def test_project_registry():
    """
    Test if the project registry is correctly initialized
    """
    assert PROJECT_TYPE_REGISTRY != {}, "Empty project type registry"
    assert "std" in PROJECT_TYPE_REGISTRY, "Failed to register standard project type"

@pytest.mark.asyncio()
async def test_create_project_directory():
    """
    Test if the project directory is created
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project_infos = {
                "name": "Test Create Project Directory",
                "description": "This is a test for project directory creation"
            }
            project = Project(project_infos)
            await project._create_project_directory()
            assert os.path.exists(project.path), "Failed to create project directory"

@pytest.mark.asyncio()
async def test_create_pipeline_file():
    """
    Test if the pipeline file is created
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project_infos = {
                "name": "Test Create Pipeline File",
                "description": "This is a test for pipeline creation"
            }
            project = Project(project_infos)
            await project._create_project_directory()
            await project._create_pipeline_file()
            assert os.path.exists(os.path.join(project.path, "pipeline.py")), "Failed to create project pipeline"
            assert BASIC_PIPELINE in open(os.path.join(project.path, "pipeline.py")).read(), "Failed to create project pipeline with the correct content"

@pytest.mark.asyncio()
async def test_create_data_sources_directory():
    """
    Test if the data_sources directory is created
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project_infos = {
                "name": "Test Create Data Sources Dir",
                "description": "This is a test for data_sources creation"
            }
            project = Project(project_infos)
            await project._create_project_directory()
            await project._create_data_sources_directory()
            assert os.path.exists(os.path.join(project.path, "data_sources")), "Failed to create project data_sources directory"

@pytest.mark.asyncio()
async def test_create_manifest():
    """
    Test if the manifest file is correctly created
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project_infos = {
                "name": "Test Create Manifest File",
                "description": "This is a test for manifest creation"
            }
            project = Project(project_infos)
            await project._create_project_directory()
            await project._create_manifest()
            assert os.path.exists(os.path.join(project.path, "__manifest__.json")), "Failed to create project manifest"
            assert {
                "name": project.name,
                "description": project.description,
                "directory": project.directory,
                "project_type": project.project_type[0],
                "misc": project.misc
            } == json.load(open(os.path.join(project.path, "__manifest__.json"))), "Failed to create project manifest with the correct content"

@pytest.mark.asyncio()
async def test_init_from_manifest():
    """
    Test if the project is correctly initialized from a manifest
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project_infos = {
                "name": "Test Init From Manifest",
                "description": "This is a test for project initialization from manifest"
            }
            project = Project(project_infos)
            await project._create_project_directory()
            await project._create_manifest()
            assert os.path.exists(os.path.join(project.path, "__manifest__.json")), "Failed to create project manifest"

            manifest_data = json.load(open(os.path.join(project.path, "__manifest__.json")))    
            project = Project(manifest_data)
            assert project.name == project_infos['name'], "Failed to initialize project name from manifest"
            assert project.description == project_infos['description'], "Failed to initialize project description from manifest"
            assert project.directory == project_infos['name'].lower().replace(" ", "_"), "Failed to initialize project directory from manifest"
            assert project.path == os.path.join(os.getcwd(), "_projects", project_infos['name'].lower().replace(" ", "_")), "Failed to initialize project path from manifest"
            assert project.project_type[0] == project.short_name, "Failed to initialize project project_type from manifest"
            assert project.misc == project.create_misc({}), "Failed to initialize project misc from manifest"

@pytest.mark.asyncio()
async def test_create_misc():
    """
    Test if the misc values are correctly created
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project_infos = {
                "name": "Test Create Misc",
                "description": "This is a test for misc creation"
            }
            project = Project(project_infos)
            assert project.create_misc({"other_misc_field": 8})["table_len"] == 10, "Failed set default misc values"
            assert project.create_misc({"table_len": 20})["table_len"] == 20, "Failed to set custom misc values"

@pytest.mark.asyncio()
async def test_update_settings():
    """
    Test if the project settings are correctly updated
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            project_infos = {
                "name": "Test Update Settings",
                "description": "This is a test for project settings update"
            }
            project = Project(project_infos)
            await project._create_project_directory()
            await project._create_manifest()
            assert os.path.exists(os.path.join(project.path, "__manifest__.json")), "Failed to create project manifest"

            new_settings = {
                "name": "Test Update Settings; Updated",
                "description": "This is a test for project settings update; Updated",
                "misc": '{"table_len": 20}'
            }
            await project.update_settings(new_settings)

            manifest_data = json.load(open(os.path.join(project.path, "__manifest__.json")))
            updated_project = Project(manifest_data)
            assert updated_project.name == new_settings['name'], "Failed to update project name"
            assert updated_project.description == new_settings['description'], "Failed to update project description"
            assert updated_project.misc == json.loads(new_settings['misc']), "Failed to update project misc"

# Test routers
#----------------------------------------------------------------------------------
def test_projects():
    """
    Test if the projects endpoint is accessible and contains projects
    """
    response = client.get("/projects/")
    assert response.status_code == 200, "Failed to access the projects endpoint"
    assert response.context.get("projects"), "Response does not contain projects"
    assert response.context.get("PROJECT_TYPE_REGISTRY"), "Response does not contain the project type registry"

def test_fail_access_projects():
    """
    Test the case when we fail to open a project; 
    We must me redirected to projects' page, with a error message (exception)
    
    Error triggers: if os.getcwd = /../.., system won't find _projects folder
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value="/../.."):
            response = client.get("/projects/")
            assert response.status_code == 200, "Failed to access the projects endpoint"
            assert response.context.get("exception"), "Response does not contain an exception"

def test_open_project(mock_project):
    """
    Test if the open_project endpoint is accessible 
    Contains a table, the project_dir and is redirected to table endpoint
    """
    response = client.get(f"/projects/open/?project_dir={mock_project}")
    assert response.status_code == 200, "Failed to access the open_project endpoint"
    assert response.context.get("table"), "Response does not contain a table"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"
    assert "/tables/?project_dir=" in str(response.url), "Failed to redirect to table's page"

def test_create_project():
    """
    Test if project's directory, manifest and pipeline were created
    Test we are redirected to /tables/?project_dir={project_dir} enpoint
    """
    form_data = {
        "name": "Test Create Project", 
        "description": "This is a test for project creation",
        }
    project_name_dir = form_data['name'].lower().replace(" ", "_")
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/projects/create/", data=form_data)
            project_dir = os.path.join(temp_dir, "_projects", project_name_dir)

            assert os.path.exists(project_dir), "Failed to create project directory"
            assert os.path.exists(os.path.join(project_dir, "__manifest__.json")), "Failed to create project manifest"
            assert os.path.exists(os.path.join(project_dir, "pipeline.py")), "Failed to create project pipeline"

            assert str(response.url).endswith(f"/tables/?project_dir={project_name_dir}"), "Failed to redirect to project's page"

            response = client.get("/projects/")
            assert response.context.get("projects"), "Response does not contain projects"
            assert any(project['directory'] == project_name_dir for project in response.context.get("projects")), "New project does not appear in root page"

def test_fail_create_project():
    """
    Test if the error page is displayed when the project creation fails due to invalid project name
    """
    form_data = {
        "project_name": "''./\"''", 
        "project_description": "This is a test for project creation",
        }
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/projects/create/", data=form_data)
            assert response.status_code == 200, "Unexpected error while failing to create project"
            assert response.context.get("exception"), "Response does not contain an exception"

def test_project_settings(mock_project):
    """
    Test if the project settings endpoint is accessible
    Contains the project's manifest and project_dir
    """
    response = client.get(f"/project/settings/?project_dir={mock_project}")
    assert response.status_code == 200, "Failed to access the project settings endpoint"
    assert response.context.get("project"), "Response does not contain the project infos (manifest data)"
    assert response.context.get("project")['directory'] == 'mock_project', "Response does not contain the correct project"
    assert response.context.get("project_dir") == mock_project, "Response does not contain the correct project_dir"

def test_fail_access_project_settings():
    """
    Test the case when we fail to open a project; 
    We must me redirected to project's page, with a error message (exception)
    
    Error triggers: if os.getcwd = /../.., system won't find _projects folder
    """
    response = client.get(f"/project/settings/?project_dir=wrong_dir")
    assert response.status_code == 200, "Failed to access the project settings endpoint"
    assert response.context.get("exception"), "Response does not contain an exception"

def test_update_project_settings():
    """
    Test if the project settings are correctly updated
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/projects/create/", data={"name": "Test Update Project Settings", "description": "This is a test for project settings update"})

            form_data = {
                "project_dir": "test_update_project_settings",
                "name": "Test Update Project Settings; Updated",
            }
            response = client.post("/project/update_settings/", data=form_data)
            assert response.status_code == 200, "Failed to update project settings"

            manifest_data = json.load(open(os.path.join(temp_dir, "_projects", "test_update_project_settings", "__manifest__.json")))
            assert manifest_data['name'] == form_data['name'], "Failed to update project name"

def test_fail_update_project_settings():
    """
    Test if the error page is displayed when the project settings update fails due to invalid project name
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir):
            response = client.post("/projects/create/", data={"name": "Test Fail Update Project Settings", "description": "This is a test for project settings update"})

            form_data = {
                "project_dir": "test_fail_update_project_settings_wrong_dir",
            }
            response = client.post("/project/update_settings/", data=form_data)
            assert response.status_code == 200, "Failed to update project settings"
            assert response.context.get("exception"), "Response does not contain an exception"
