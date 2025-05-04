import pytest

from tests.utils.tours_toolbox import Tour


class TestAppTours:
    @pytest.mark.slow
    def test_navigate_in_app_menus(self, server, browser, reset_projects):
        """Test the navigation in the app menus"""
        tour = Tour(browser, server)

        tour.navbar_click("Settings", check_over_effect=True)
        tour.check_page(title="App settings", url="/app/settings/")

        tour.navbar_click("Projects")
        tour.check_page(title="ProjectHub", url="/projects/")
