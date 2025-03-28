from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_home_page():
    """
    Test if the homepage is accessible
    Test if response url finish with /projects/
    """
    response = client.get("/")
    assert response.status_code == 200, "Failed to access the homepage"
    assert str(response.url).endswith("/projects/"), "Failed to redirect to /projects/"

def test_access_app_settings():
    """
    Test if the application settings endpoint is accessible
    """
    response = client.get("/app/settings/")
    assert response.status_code == 200, "Failed to access the application settings endpoint"
