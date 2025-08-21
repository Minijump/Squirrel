from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_squirrel_error():
    """Test that in case of error on the root enpoint, the error page is displayed."""
    with patch("app.main.RedirectResponse", side_effect=Exception("Mock error")):        
        response = client.get("/")
        assert response.status_code == 200, "Error page not displayed"
        assert response.context.get("exception"), "Response does not contain an exception"
