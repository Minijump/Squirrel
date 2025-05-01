import pytest

from selenium.webdriver.common.by import By

from tests.utils.tours_toolbox import Tour

class TestProjectsTours:
    @pytest.mark.slow
    def test_create_project_modal(self, server, browser, reset_projects):
        """Check we can open/close the create project modal"""
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test create project modal")

        create_project_modal = tour.click_create_card(expected_visible="//form[@id=\'projectForm\']")
        create_project_modal.close()

    @pytest.mark.slow
    def test_mandatory_input_create_project_modal(self, server, browser, reset_projects):
        """Check the mandatory inputs in the create project modal"""
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test mandatory input create project modal")

        # Try to confirm with no name, pop up does not disappear
        create_project_modal = tour.click_create_card(expected_visible="//form[@id=\'projectForm\']")
        create_project_modal.submit(assert_closed=False)
        # Add a name and confirm, pop up disappears
        create_project_modal.fill([("projectName", "dumb project name")])
        create_project_modal.submit(assert_closed=True)

    @pytest.mark.slow
    def test_project_creation(self, server, browser, reset_projects):
        """
        Check project creation
        """
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test project creation")

        project_name = "tour_project_creation"
        project_description = "Project creation test tour"
        tour.create_project(project_name, description=project_description)

        # Check in project settings that the project has been created with the correct values
        tour.check_page(title="Tables", url=f"/tables/")
        tour.navbar_click("Settings", check_over_effect=True)
        tour.check_page(title="Project Settings", url=f"/settings/")
        expected_settings_byids = [('projectName', project_name), ('projectDescription', project_description)]
        tour.check_elements(by_ids=expected_settings_byids)

    @pytest.mark.slow
    def test_invalid_or_existing_project_name(self, server, browser, reset_projects):
        """
        Check invalid/existing project name
        """
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test invalid or existing project name")

        # Case invalid name: try to create a project with an invalid name
        tour.create_project('"..\\invalid name"')
        tour.assert_error_page()

        # Case existing project name: create a project, then try to create it again
        project_name = "existing"
        tour.navbar_click("Projects")
        tour.create_project(project_name)

        tour.click_home_button()
        tour.create_project(project_name)
        tour.assert_error_page()

    @pytest.mark.slow
    def test_openexistingproject(self, server, browser, reset_projects):
        """Check we can open an existing project (we just created)"""
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test open existing project")

        project_name = "Open Existing"
        tour.create_project(project_name)

        # Check that the new project is displayed, open it and check its name in settings
        tour.click_home_button()
        tour.click_card(by_title=project_name)
        tour.navbar_click("Settings")
        tour.check_elements(by_ids=[('projectName', project_name)])

    @pytest.mark.slow
    def test_project_edit_settings(self, server, browser, reset_projects):
        """Check project settings edition"""
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test project edit settings")

        tour.create_project("Test updates settings")

        # Edit Project Settings
        descr_update = "settings description updated"
        table_len_update = "20"
        tour.navbar_click("Settings")
        tour.fill_element(by_id="projectDescription", value=descr_update)
        tour.fill_element(by_css_selector="td:nth-child(2) > input", value=table_len_update)
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Check settings were edited
        tour.navbar_click("Settings")
        tour.check_elements(
            by_ids=[('projectDescription', descr_update)],
            by_css_selectors=[("td:nth-child(2) > input", table_len_update)]
        )
