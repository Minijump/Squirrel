import json
import os
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.projects.models import Project, PROJECT_TYPE_REGISTRY


client = TestClient(app)


def test_project_utils_registry():
    """
    Test if the project registry is correctly initialized
    """
    assert PROJECT_TYPE_REGISTRY != {}, "Empty project type registry"
    assert "std" in PROJECT_TYPE_REGISTRY, "Failed to register standard project type"

@pytest.mark.asyncio
async def test_create(temp_project_dir_fixture):
    project_infos = {
        "name": "Test Create",
        "description": "This is a test for project creation"
    }
    project = Project(project_infos)

    await project.create()

    assert os.path.exists(project.path), "Failed to create project directory"
    assert os.path.exists(os.path.join(project.path, "__manifest__.json")), "Failed to create project manifest"
    assert os.path.exists(os.path.join(project.path, "pipeline.pkl")), "Failed to create project pipeline"
    assert os.path.exists(os.path.join(project.path, "data_sources")), "Failed to create project data_sources directory"

@pytest.mark.asyncio
async def test_get_available_projects(temp_project_dir_fixture):
    project_dir = os.path.join(temp_project_dir_fixture, "_projects")
    available_projects = Project.get_available_projects(project_dir)

    assert len(available_projects) > 0, "No available projects found"
    assert type(available_projects[0]) == Project, "Failed to retrieve correct project type"

@pytest.mark.asyncio
async def test_instantiate_project_from_path(temp_project_dir_fixture):
    project_path = os.path.join(temp_project_dir_fixture, "_projects", "ut_mock_project_1")

    project = Project.instantiate_project_from_path(project_path)

    assert type(project) is Project, "Failed to instantiate project from path"
    assert project.name == "UT Mock Project 1", "Failed to initialize project name from path"

@pytest.mark.asyncio
async def test_get_settings(temp_project_dir_fixture):
    project_infos = {
        "name": "Test Get Settings",
        "description": "This is a test for project settings retrieval"
    }
    project = Project(project_infos)
    await project.create()

    settings = project.get_settings()

    assert settings['name'] == project_infos['name'], "Failed to retrieve project name"
    assert settings['description'] == project_infos['description'], "Failed to retrieve project description"

@pytest.mark.asyncio
async def test_update_settings(temp_project_dir_fixture):
    project_infos = {
        "name": "Test Update Settings",
        "description": "This is a test for project settings update"
    }
    project = Project(project_infos)
    await project.create()

    new_settings = {
        "name": "Test Update Settings; Updated",
        "description": "This is a test for project settings update; Updated",
        "misc": '{"table_len": 20}'
    }
    project.update_settings(new_settings)

    updated_settings = project.get_settings()
    assert updated_settings['name'] == new_settings['name'], "Failed to update project name"
    assert updated_settings['description'] == new_settings['description'], "Failed to update project description"
    assert updated_settings['misc'] == json.loads(new_settings['misc']), "Failed to update project misc"

def test_get_sources(temp_project_dir_fixture):
    project_path = os.path.join(temp_project_dir_fixture, "_projects", "ut_mock_project_1")
    project = Project.instantiate_project_from_path(project_path)

    sources = project.get_sources()

    assert len(sources) == 2, "Expected 2 sources in the project"
    assert sources[0]["name"] == "Csv ordered", "Expected first source to be 'Csv ordered'"
    assert sources[1]["name"] == "Csv random", "Expected second source to be 'Csv random'"
