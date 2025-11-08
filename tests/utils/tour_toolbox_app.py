import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from tests.utils.tour_toolbox_base import BaseElement
from tests.utils.tour_toolbox_transient import Modal, RightSidebar
from tests.utils.tour_toolbox_table import TableElement


class App(BaseElement):    
    def check_page(self, title: str = False, url: str = False) -> None:
        if title:
            actual_title = self.browser.find_element(By.CSS_SELECTOR, "h1, h3").text
            assert actual_title == title, f"Expected title: {title}, but got: {actual_title}"
        if url:
            actual_url = self.browser.current_url
            assert url in actual_url, f"Expected '{url}' in the url"

    def assert_error_page(self) -> None:
        assert self.browser.find_element(By.CSS_SELECTOR, "h3").text == "Error", "Error page not displayed as expected."

    def click_home_button(self) -> None:
        self.browser.find_element(By.CSS_SELECTOR, ".fa-home").click()

    def navbar_click(self, text: str) -> None:
        nav_element = self.browser.find_element(By.TAG_NAME, "nav")
        link = nav_element.find_element(By.LINK_TEXT, text)
        link.click()

    def assert_card_visibility(self, visible: bool = True, by_title: str = False) -> None:
        self.check_visibility(
            xpath=f"//div[@class=\'grid\']//h3[text()=\'{by_title}\']", 
            visible=visible, 
            message=f"Card {by_title} should {'' if visible else 'not'} be displayed")

    def click_create_card(self, expected_visible: bool = False) -> Modal:
        self.browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        return Modal(self.browser, expected_visible)
    
    def click_card(self, by_xpath: str = False, by_title: str = False, by_position: int = 0) -> None:
        if by_xpath:
            self.browser.find_element(By.XPATH, by_xpath).click()
        elif by_title:
            xpath = f"//div[@class=\'grid\']//h3[text()=\'{by_title}\']"
            self.browser.find_element(By.XPATH, xpath).click()
        elif by_position:
            self.browser.find_element(By.CSS_SELECTOR, f".card:nth-child({by_position})").click()
        else:
            raise ValueError("Either 'by_xpath', 'by_title', or 'by_position' must be provided.")

    def confirm_modal(self, confirm: bool = True) -> Modal:
        """ Handle the confirmation modal """
        modal = Modal(self.browser, expected_visible="//div[starts-with(@id,'confirmation-modal')]")
        button_id = "confirm-btn" if confirm else "cancel-btn"
        modal.click_button(by_id=button_id)
        return modal


class TablesScreen(BaseElement):
    def click_create_new_table(self) -> RightSidebar:
        self.browser.find_element(By.CSS_SELECTOR, "img").click()
        return RightSidebar(self.browser, expected_visible="//div[starts-with(@id, 'ActionSidebar-CreateTable')]")

    def check_table_select_button_visibility(self, table_name: str, visible: bool = True) -> None:
        self.check_visibility(
            xpath=f"//button[contains(.,\'{table_name}\')]",
            visible=visible,
            message=f"Table {table_name} should {'' if visible else 'not'} be displayed")
        
    def select_table(self, by_name: str = False) -> TableElement:
        if by_name:
            self.browser.find_element(By.XPATH, f"//button[contains(.,\'{by_name}\')]").click()
            return TableElement(self.browser, by_name)


class PipelineScreen(BaseElement):
    def get_pipeline_actions(self, wait_a_minute: bool = False) -> list:
        if wait_a_minute:
            time.sleep(0.5)
        return self.browser.find_elements(By.CSS_SELECTOR, ".action")
    
    def move_action(self, action: WebElement, target: WebElement) -> None:
        actions = ActionChains(self.browser)
        actions.drag_and_drop(action, target)
        actions.perform()

    def click_edit_action(self, by_position: int) -> Modal:
        self.browser.find_element(
            By.XPATH,
            f"//div[@id=\'pipeline\']//div[@class=\'action\'][{by_position}]//button[contains(@class, \'list-edit-btn\') and @name='edit-action-btn']"
        ).click()
        return Modal(self.browser, expected_visible="//div[@id=\'editActionModal\']")
    
    def click_edit_pipeline_action(self, by_position: int) -> Modal:
        self.browser.find_element(
            By.XPATH,
            f"//div[@id=\'pipeline\']//div[@class=\'action\'][{by_position}]//button[contains(@class, \'list-edit-btn\') and @name='edit-pipeline-action-btn']"
        ).click()
        return Modal(self.browser, expected_visible="//div[@id=\'editPipelineActionModal\']")
