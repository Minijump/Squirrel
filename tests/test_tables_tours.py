# Generated by Selenium IDE; edited
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select

class TestTablesTours:    
    @pytest.mark.slow
    def test_create_table(self, server, browser, reset_projects):
        """
        Check if the table is created correctly.
        """
        browser.get(f"{server}/projects/")

        # Open project
        browser.find_element(By.CSS_SELECTOR, ".card:nth-child(2)").click()

        # Click on "Create Table" button, complete inputs and confirm
        browser.find_element(By.CSS_SELECTOR, "img").click()
        browser.find_element(By.ID, "new_table_name").send_keys("test create new table")
        browser.find_element(By.ID, "data_source").click()
        browser.find_element(By.CSS_SELECTOR, ".btn-primary:nth-child(10)").click()

        # Check that the table is created
        WebDriverWait(browser, 2).until(
            expected_conditions.visibility_of_element_located((By.XPATH, "//button[contains(.,\'test create new table\')]")))
        
    @pytest.mark.slow
    def test_sort_column(self, server, browser, reset_projects):
        """
        Check if the column is sorted correctly.
        """
        browser.get(f"{server}/projects/")

        # Open project
        browser.find_element(By.CSS_SELECTOR, ".card:nth-child(2) .card-description").click()

        # Click on table header button
        browser.find_element(By.CSS_SELECTOR, "#table-html-ordered th:nth-child(2) > .table-header-btn").click()
        # Click on "Sort" button + select descending + confirm
        browser.find_element(By.XPATH, "//button[@onclick=\"\n                closeInfoColModal();\n                openSidebarActionForm(\'SortColumn\', getColumnInfo())\"]").click()
        
        select_element = browser.find_element(By.ID, "sort_order")
        select = Select(select_element)
        select.select_by_value("descending")
        browser.find_element(By.CSS_SELECTOR, "form:nth-child(1) > .btn-primary:nth-child(5)").click()
        element = browser.find_element(By.CSS_SELECTOR, "#table-html-ordered tr:nth-child(1) > td:nth-child(2)")
        assert element.text == "99"

        # Sort back to ascending
        browser.find_element(By.CSS_SELECTOR, "#table-html-ordered th:nth-child(2) > .table-header-btn").click()
        browser.find_element(By.XPATH, "//button[@onclick=\"\n                closeInfoColModal();\n                openSidebarActionForm(\'SortColumn\', getColumnInfo())\"]").click()
        browser.find_element(By.CSS_SELECTOR, "form:nth-child(1) > .btn-primary:nth-child(5)").click()
        element = browser.find_element(By.CSS_SELECTOR, "#table-html-ordered tr:nth-child(1) > td:nth-child(2)")
        assert element.text == "0"
