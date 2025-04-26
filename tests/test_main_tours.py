import pytest

from tests.utils.tours_toolbox import Tour


class TestAppTours:
    @pytest.mark.slow
    def test_navigate_in_app_menus(self, server, browser, reset_projects):
        """
        Test the navigation in the app menus
        """
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test navbar")

        # Navigate to app settings
        tour.navbar_click("Settings")
        tour.check_page(title="App settings", url="/app/settings/")

        # Navigate back to projects
        tour.navbar_click("Projects")
        tour.check_page(title="ProjectHub", url="/projects/")
