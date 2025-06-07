import pytest

from tests.utils.tours_toolbox import Tour, MOCK_PROJECT1_NAME

class TestProjectsTours:
    @pytest.mark.slow
    def test_create_project_modal(self, server, browser, reset_projects):
        """Check we can open/close the create project modal"""
        tour = Tour(browser, server)

        tour.check_grid_cards_over_effect()
        create_project_modal = tour.click_create_card(
            expected_visible="//div[@id='createProjectModal']")
        create_project_modal.close()
        tour.check_grid_cards_over_effect()

    @pytest.mark.slow
    def test_mandatory_input_create_project_modal(self, server, browser, reset_projects):
        """Check the mandatory inputs in the create project modal"""
        tour = Tour(browser, server)

        # Try to confirm with no name, pop up does not disappear
        create_project_modal = tour.click_create_card(
            expected_visible="//div[contains(@class,'modal-content')]//form[@id='createProjectModalForm']")
        create_project_modal.submit(assert_closed=False)
        # Add a name and confirm, pop up disappears
        create_project_modal.fill([("name", "dumb project name")])
        create_project_modal.submit(assert_closed=True)

    @pytest.mark.slow
    def test_openexistingproject(self, server, browser, reset_projects):
        """Check we can open an existing project"""
        tour = Tour(browser, server)

        tour.click_card(by_title=MOCK_PROJECT1_NAME)
        tour.check_page(title="Tables", url=f"/tables/")
        tour.navbar_click("Data sources")
        tour.check_page(title="Data Sources", url=f"/data_sources/")
        tour.navbar_click("Pipeline")
        tour.check_page(title="Pipeline", url=f"/pipeline/")
        tour.navbar_click("Table")
        tour.check_page(title="Tables", url=f"/tables/")
        tour.navbar_click("Settings", check_over_effect=True)
        tour.check_page(title="Project Settings", url=f"/settings/")
        tour.check_elements(by_ids=[('projectName', MOCK_PROJECT1_NAME)])

    @pytest.mark.slow
    def test_project_creation(self, server, browser, reset_projects):
        """Check project creation"""
        tour = Tour(browser, server)

        project_name = "tour_project_creation"
        project_descr = "Project creation test tour"
        tour.create_project(project_name, description=project_descr)

        # Check we can open the project from main menu + check its name in settings
        tour.click_home_button()
        tour.click_card(by_title=project_name)
        tour.navbar_click("Settings")
        tour.check_elements(by_ids=[('projectName', project_name), ('projectDescription', project_descr)])

    @pytest.mark.slow
    def test_invalid_or_existing_project_name(self, server, browser, reset_projects):
        """Check invalid/existing project name"""
        tour = Tour(browser, server)

        tour.create_project('"..\\invalid name"') # Invalid name
        tour.assert_error_page()

        tour.navbar_click("Projects")

        tour.create_project("UT Mock Project 1") # Existing name
        tour.assert_error_page()

    @pytest.mark.slow
    def test_project_edit_settings(self, server, browser, reset_projects):
        """Check project settings edition"""
        tour = Tour(browser, server)

        tour.click_card(by_title=MOCK_PROJECT1_NAME)

        descr, table_len = "settings description updated", "20"
        tour.navbar_click("Settings")
        tour.fill_element(by_id="projectDescription", value=descr)
        tour.fill_element(by_css_selector="td:nth-child(2) > input", value=table_len)
        tour.click_confirm_button()

        tour.navbar_click("Settings")
        tour.check_elements(
            by_ids=[('projectDescription', descr)],
            by_css_selectors=[("td:nth-child(2) > input", table_len)]
        )

    @pytest.mark.slow
    def test_change_project_name(self, server, browser, reset_projects):
        """Check project name change"""
        tour = Tour(browser, server)

        new_name = "new_project_name"
        tour.click_card(by_title=MOCK_PROJECT1_NAME)
        tour.navbar_click("Settings")
        tour.fill_element(by_id="projectName", value=new_name)
        tour.click_confirm_button()

        tour.click_home_button()
        tour.click_card(by_title=new_name)
        tour.navbar_click("Settings")
        tour.check_elements(by_ids=[('projectName', new_name)])
