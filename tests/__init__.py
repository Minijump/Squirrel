import os
import pytest
import shutil


@pytest.fixture
def mock_project(tmpdir):
    """ 
    Create a mock project in a temp dir

    => Returns the path to the mock project directory
    """
    projects_dir = tmpdir.mkdir("_projects")

    project_dir = projects_dir.mkdir("mock_project")
    for item in os.listdir("tests/utils/mock_projects/ut_mock_project_1"):
        src_path = os.path.join("tests/utils/mock_projects/ut_mock_project_1", item)
        dst_path = os.path.join(project_dir, item)
        
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


    return str(project_dir)
