from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from tests.utils.tour_toolbox_base import BaseElement
from tests.utils.tour_toolbox_transient import Modal, RightSidebar


class TableElement(BaseElement):
    def __init__(self, browser: WebDriver, table_name: str) -> None:
        super().__init__(browser)
        self.table_name = table_name
        self.table_id = f"table-html-{table_name}"

    def click_header_button(self, by_col_number: int = 0) -> Modal:
        if by_col_number:
            self.browser.find_element(By.CSS_SELECTOR, f"#{self.table_id} th:nth-child({by_col_number}) > .table-header-btn").click()

        return Modal(self.browser, expected_visible=f"//div[@id='InfoColModal']//div[@class='modal-content']")
    
    def get_cell(self, by_col_number: int, by_row_number: int):
        return self.browser.find_element(
            By.CSS_SELECTOR, f"#{self.table_id} tr:nth-child({by_row_number}) > td:nth-child({by_col_number})")
    
    def check_displayed(self) -> None:
        self.check_visibility(
            xpath=f"//div[@id=\'{self.table_id}\']", 
            visible=True, 
            message=f"Table {self.table_name} should be displayed")

    def next_page(self) -> None:
        self.browser.find_element(By.XPATH, f"//div[@id=\'table-{self.table_name}\']//div[@id= \'next\']").click()
    
    def previous_page(self) -> None:
        self.browser.find_element(By.XPATH, f"//div[@id=\'table-{self.table_name}\']//div[@id= \'prev\']").click()

    def click_button(self, by_button_text: str = False, by_id: str = False) -> None:
        if by_id:
            button = self.browser.find_element(By.ID, by_id)
        elif by_button_text:
            button = self.browser.find_element(By.XPATH, f"//button[contains(text(), '{by_button_text}')]")
        else:
            raise ValueError("Either 'by_button_text' or 'by_id' must be provided.")
        button.click()

    def click_action_button(self, by_button_text: str) -> RightSidebar:
        self.click_button(by_button_text)
        return RightSidebar(self.browser, expected_visible="//div[starts-with(@id, 'ActionSidebar')]")

    def click_custom_action_button(self) -> Modal:
        button_text = "Add Action"
        self.click_button(button_text)
        return Modal(self.browser, expected_visible="//form[@id='customActionModalForm']")
    
    def click_dropdown_action_button(self, first_button_text: str, second_button_text: str) -> RightSidebar:
        self.click_button(by_button_text=first_button_text)
        button = self.browser.find_element(By.XPATH, f"//a[contains(text(), '{second_button_text}')]")
        button.click()
        return RightSidebar(self.browser, expected_visible="//div[starts-with(@id, 'ActionSidebar')]")
