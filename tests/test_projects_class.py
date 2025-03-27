import json
import os
import pytest
import tempfile
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.projects.models.project import Project, BASIC_PIPELINE, PROJECT_TYPE_REGISTRY

client = TestClient(app)

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
