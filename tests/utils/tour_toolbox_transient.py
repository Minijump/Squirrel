from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from tests.utils.tour_toolbox_base import BaseElement


class TransientElement(BaseElement):
    def __init__(self, browser: WebDriver, expected_visible: str, transient_element_name: str = "Transient Element") -> None:
        super().__init__(browser)
        self.expected_visible = expected_visible
        self.transient_element_name = transient_element_name
        self.assert_visibility(visible=True)

    def assert_visibility(self, visible: bool = True) -> None:
        self.check_visibility(
            xpath="", 
            visible=visible, 
            message=f"{self.transient_element_name} did not {'appear' if visible else 'closed'} as expected.")
        
    def check_visibility(self, xpath: str, visible: bool = True, message: str = False) -> None:
        """ Check if the element is visible or not """
        xpath = f"{self.expected_visible}{xpath}"
        super().check_visibility(
            xpath=xpath, 
            visible=visible, 
            message=message or f"Element with xpath {xpath} of {self.transient_element_name} should {'be visible' if visible else 'not be visible'}.")

    def fill(self, values: list) -> None:
        """ Fill the form with the given values, where values is a list of tuples (by_id, value) """
        for value in values:
            xpath = f"{self.expected_visible}//*[@id='{value[0]}']"
            self.fill_element(by_xpath=xpath, value=value[1])

    def submit(self, assert_closed: bool = True) -> None:
        self.browser.find_element(By.XPATH, f"{self.expected_visible}//button[contains(@class, 'btn-primary')]").click()
        self.assert_visibility(visible=not assert_closed)

    def click_danger_button(self) -> None:
        self.browser.find_element(By.XPATH, f"{self.expected_visible}//button[contains(@class, 'btn-danger')]").click()


class RightSidebar(TransientElement):
    def __init__(self, browser: WebDriver, expected_visible: str) -> None:
        super().__init__(browser, expected_visible, transient_element_name="Right Sidebar")


class Modal(TransientElement):
    def click_button(self, by_button_text: str = False, by_id: str = False) -> None:
        if by_id:
            button = self.browser.find_element(By.ID, by_id)
        elif by_button_text:
            button = self.browser.find_element(By.XPATH, f"{self.expected_visible}//button[contains(text(), '{by_button_text}')]")
        else:
            raise ValueError("Either 'by_button_text' or 'by_id' must be provided.")
        button.click()
        self.assert_visibility(visible=False)

    def click_action_button(self, by_button_text: str) -> RightSidebar:
        self.click_button(by_button_text)
        return RightSidebar(self.browser, expected_visible="//div[starts-with(@id, 'ActionSidebar')]")

    def close(self, assert_closed: bool = True) -> None:
        modal = self.browser.find_element(By.XPATH, self.expected_visible)
        close_button = (modal.find_elements(By.CSS_SELECTOR, ".close-btn") or modal.find_elements(By.ID, "cancelButton"))[0]
        close_button.click()
        self.assert_visibility(visible=not assert_closed)
