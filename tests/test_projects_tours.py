# Generated by Selenium IDE; edited
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

class TestProjectsTours:    
    @pytest.mark.slow
    def test_create_project_modal(self, server, browser, reset_projects):
        """
        Check we can open/close the create project modal
        """
        browser.get(f"{server}/projects/")

        # Click on "Create Project Card and check name input is visible"
        browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        WebDriverWait(browser, 2, poll_frequency=0.1).until(
          expected_conditions.visibility_of_element_located((By.XPATH, "//form[@id=\'projectForm\']/input[@name=\'name\']")))
        
        # Click on "Cancel" button and check that the modal is closed
        browser.find_element(By.ID, "cancelButton").click()
        WebDriverWait(browser, 2, poll_frequency=0.1).until(
          expected_conditions.invisibility_of_element_located((By.XPATH, "//form[@id=\'projectForm\']")))

    @pytest.mark.slow
    def test_mandatory_input_create_project_modal(self, server, browser, reset_projects):
        """
        Check the mandatory input in the create project modal
        """
        browser.get(f"{server}/projects/")

        # Try to confirm with no name, pop up does not disappear
        browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        WebDriverWait(browser, 2, poll_frequency=0.1).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".modal-content")))

        # Add a name and confirm, pop up disappears
        browser.find_element(By.ID, "projectName").click()
        browser.find_element(By.ID, "projectName").send_keys("dumb project name")
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        WebDriverWait(browser, 2, poll_frequency=0.1).until(
          expected_conditions.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-content")))
      
    @pytest.mark.slow
    def test_project_creation(self, server, browser, reset_projects):
        """
        Check project creation
        """
        browser.get(f"{server}/projects/")

        # Create Project
        project_name = "Yolo"
        project_description = "Project creation test tour"
        browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        browser.find_element(By.ID, "projectName").click()
        browser.find_element(By.ID, "projectName").send_keys(project_name)
        browser.find_element(By.ID, "projectDescription").click()
        browser.find_element(By.ID, "projectDescription").send_keys(project_description)
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Check in project settings that the project has been created with the correct values
        browser.find_element(By.LINK_TEXT, "Settings").click()
        value = browser.find_element(By.ID, "projectName").get_attribute("value")
        assert value == project_name
        value = browser.find_element(By.ID, "projectDescription").get_attribute("value")
        assert value == project_description

    @pytest.mark.slow
    def test_invalid_or_existing_project_name(self, server, browser, reset_projects):
        """
        Check invalid/existing project name
        """
        browser.get(f"{server}/projects/")

        # Try to create a project with an invalid name (containing "..\\")
        browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        browser.find_element(By.ID, "projectName").click()
        browser.find_element(By.ID, "projectName").send_keys("..\\")
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        # Check that an error message is well displayed
        assert browser.find_element(By.CSS_SELECTOR, "h3").text == "Error"

        # Return on projects page and create one
        project_name = "existing"
        browser.find_element(By.LINK_TEXT, "Projects").click()
        browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        browser.find_element(By.ID, "projectName").click()
        browser.find_element(By.ID, "projectName").send_keys(project_name)
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Return on projects page and try to create a project with the same name
        browser.find_element(By.CSS_SELECTOR, ".fa-home").click()
        browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        browser.find_element(By.ID, "projectName").click()
        browser.find_element(By.ID, "projectName").send_keys(project_name)
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        # Check that an error message is well displayed
        assert browser.find_element(By.CSS_SELECTOR, "h3").text == "Error"

    @pytest.mark.slow
    def test_openexistingproject(self, server, browser, reset_projects):
        """
        Check we can open an existing project
        """
        browser.get(f"{server}/projects/")

        # Create Project
        project_name = "open existing"
        browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        browser.find_element(By.ID, "projectName").click()
        browser.find_element(By.ID, "projectName").send_keys(project_name)
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Come back to project's page, check the new project is displayed, open it and check its name in settings
        browser.find_element(By.CSS_SELECTOR, ".fa-home").click()
        WebDriverWait(browser, 2, poll_frequency=0.1).until(
          expected_conditions.visibility_of_element_located((By.XPATH, f"//div[@id=\'projectGrid\']//h3[text()=\'{project_name}\']")))
        browser.find_element(By.XPATH, f"//div[@id=\'projectGrid\']//h3[text()=\'{project_name}\']").click()
        browser.find_element(By.LINK_TEXT, "Settings").click()
        value = browser.find_element(By.ID, "projectName").get_attribute("value")
        assert value == project_name

    @pytest.mark.slow
    def test_project_edit_settings(self, server, browser, reset_projects):
        """
        Check project settings edition
        """
        browser.get(f"{server}/projects/")

        # Create Project
        project_name = "update settings project"
        project_description = "test update settings"
        browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        browser.find_element(By.ID, "projectName").click()
        browser.find_element(By.ID, "projectName").send_keys(project_name)
        browser.find_element(By.ID, "projectDescription").click()
        browser.find_element(By.ID, "projectDescription").send_keys(project_description)
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Edit Project Settings
        description_update = ", settings updated"
        updated_project_description = "test update settings, settings updated"
        table_len_update = "0"
        updated_project_table_len = "100"
        browser.find_element(By.LINK_TEXT, "Settings").click()
        browser.find_element(By.ID, "projectDescription").click()
        browser.find_element(By.ID, "projectDescription").send_keys(description_update)
        browser.find_element(By.CSS_SELECTOR, "td:nth-child(2) > input").click()
        browser.find_element(By.CSS_SELECTOR, "td:nth-child(2) > input").send_keys(table_len_update)
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Check settings were edited
        browser.find_element(By.LINK_TEXT, "Settings").click()
        value = browser.find_element(By.ID, "projectDescription").get_attribute("value")
        assert value == updated_project_description
        value = browser.find_element(By.CSS_SELECTOR, "td:nth-child(2) > input").get_attribute("value")
        assert value == updated_project_table_len