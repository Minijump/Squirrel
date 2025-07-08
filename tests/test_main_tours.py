import pytest
from selenium.webdriver.common.by import By

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

    @pytest.mark.slow
    def test_theme_toggle(self, server, browser, reset_projects):
        """Test the theme toggle in the app"""
        tour = Tour(browser, server)

        tour.navbar_click("Settings")
        tour.check_page(title="App settings", url="/app/settings/")
        
        # Switch to light theme
        tour.fill_element(by_id="themeSelect", value="Light Mode")
        html_element = browser.find_element(By.TAG_NAME, "html")
        assert html_element.get_attribute("data-theme") == "light"
        
        # Switch back to dark theme
        tour.fill_element(by_id="themeSelect", value="Dark Mode")
        html_element = browser.find_element(By.TAG_NAME, "html")
        assert html_element.get_attribute("data-theme") is None

        # Switch to light theme and change page
        tour.fill_element(by_id="themeSelect", value="Light Mode")
        tour.navbar_click("Projects")
        html_element = browser.find_element(By.TAG_NAME, "html")
        assert html_element.get_attribute("data-theme") == "light"
