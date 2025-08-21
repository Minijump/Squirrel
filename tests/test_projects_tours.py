import pytest

from tests.utils.tours_toolbox import Tour, MOCK_PROJECT1_NAME

class TestProjectsTours:
    @pytest.mark.slow
    def test_project_creation(self, server, browser, reset_projects):
        """Check project creation"""
        tour = Tour(browser, server)

        # Try to confirm with no name, pop up does not disappear
        create_project_modal = tour.click_create_card(
            expected_visible="//div[@id='createProjectModal']")
        create_project_modal.submit(assert_closed=False)
        create_project_modal.close()

        # Create the project
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

        # Test invalid name
        tour.create_project('"..\\invalid name"')
        tour.assert_error_page()

        tour.navbar_click("Projects")

        # Test existing name
        tour.create_project("UT Mock Project 1")
        tour.assert_error_page()

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

    @pytest.mark.slow
    def test_delete_project(self, server, browser, reset_projects):
        """Test project deletion"""
        tour = Tour(browser, server)

        project_name = "test_project_to_delete"
        tour.create_project(project_name)
        
        tour.navbar_click("Settings")
        tour.click_danger_button()
        
        tour.check_page(title="ProjectHub", url="/projects/")
        tour.assert_card_visibility(visible=False, by_title=project_name)
