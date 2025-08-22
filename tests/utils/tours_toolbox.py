import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

import warnings

MOCK_PROJECT1_NAME = "UT Mock Project 1"

class BaseElement:    
    def __init__(self, browser: WebDriver):
        self.browser = browser

    def check_visibility(self, xpath: str = False, visible: bool = True, message: str= False) -> None:
        if visible:
            WebDriverWait(self.browser, 1, poll_frequency=0.1).until(
                expected_conditions.visibility_of_element_located((By.XPATH, xpath)),
                message=message or "Element should be visible.")
        else:
            WebDriverWait(self.browser, 0.2, poll_frequency=0.1).until(
                expected_conditions.invisibility_of_element_located((By.XPATH, xpath)),
                message=message or "Element should not be visible.")

    def check_elements(self, by_ids: list = False, by_css_selectors: list = False) -> None:
        """
        Check if the elements with the given selector are visible on the page and have the expected values.
        
        :param by_ids: selector based on ids; [(id, expected_value)]
        :param by_css_selectors: selector based on css selectors; [(css_selector, expected_value)]
        """
        by_ids = by_ids or []
        by_css_selectors = by_css_selectors or []

        def check_element(element, expected_value):
            assert element.is_displayed(), f"Element is not displayed."
            actual_value = element.get_attribute("value")
            assert actual_value == expected_value, f"Expected value: {expected_value}, but got: {actual_value}"

        for id, expected_value in by_ids:
            element = self.browser.find_element(By.ID, id)
            check_element(element, expected_value)

        for css_selector, expected_value in by_css_selectors:
            element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
            check_element(element, expected_value)

    def fill_element(self, by_id: str = False, by_css_selector: str = False, by_xpath: str = False, value: str = False) -> None:
        if by_id:
            element = self.browser.find_element(By.ID, by_id)
        elif by_css_selector:
            element = self.browser.find_element(By.CSS_SELECTOR, by_css_selector)
        elif by_xpath:
            element = self.browser.find_element(By.XPATH, by_xpath)
        else:
            raise ValueError("Either 'by_id', 'by_css_selector' or 'by_xpath' must be provided.")

        if element.tag_name.lower() == 'select':
            select = Select(element)
            select.select_by_visible_text(value)
            return

        element.click()
        element.clear()
        element.send_keys(value)

    def click_confirm_button(self) -> None:
        self.browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()

    def click_danger_button(self) -> None:
        self.browser.find_element(By.CSS_SELECTOR, ".btn-danger").click()

    def add_to_dictionary(self, field_name: str, key: str, value: str) -> None:
        """ Add a key-value pair to a dictionary widget """
        dict_widget_xpath = f"{self.expected_visible}//*[@name='{field_name}'][@widget='squirrel-dictionary']"
        dict_widget = self.browser.find_element(By.XPATH, dict_widget_xpath)
        wrapper = dict_widget.find_element(By.XPATH, "./preceding-sibling::div[@class='squirrel-dict-widget']")
        
        # Click add button
        add_btn = wrapper.find_element(By.CSS_SELECTOR, ".btn-add-line")
        add_btn.click()
        # Fill the new row
        rows = wrapper.find_elements(By.XPATH, ".//tbody/tr")
        new_row = rows[-1]
        key_input = new_row.find_element(By.XPATH, "./td[1]/input")
        value_input = new_row.find_element(By.XPATH, "./td[2]/input")
        
        key_input.clear()
        key_input.send_keys(key)
        value_input.clear()
        value_input.send_keys(value)

    def edit_dictionary(self, field_name: str, key: str, new_value: str) -> None:
        """ Edit an existing key in a dictionary widget """
        dict_widget_xpath = f"{self.expected_visible}//*[@name='{field_name}'][@widget='squirrel-dictionary']"
        dict_widget = self.browser.find_element(By.XPATH, dict_widget_xpath)
        wrapper = dict_widget.find_element(By.XPATH, "./preceding-sibling::div[@class='squirrel-dict-widget']")
        
        rows = wrapper.find_elements(By.XPATH, ".//tbody/tr")
        for row in rows:
            key_input = row.find_element(By.XPATH, "./td[1]/input")
            if key_input.get_attribute("value") == key:
                value_input = row.find_element(By.XPATH, "./td[2]/input")
                value_input.clear()
                value_input.send_keys(new_value)
                break
        else:
            raise ValueError(f"Key '{key}' not found in dictionary widget")

    def remove_from_dictionary(self, field_name: str, key: str) -> None:
        """ Remove a key from a dictionary widget """
        dict_widget_xpath = f"{self.expected_visible}//*[@name='{field_name}'][@widget='squirrel-dictionary']"
        dict_widget = self.browser.find_element(By.XPATH, dict_widget_xpath)
        wrapper = dict_widget.find_element(By.XPATH, "./preceding-sibling::div[@class='squirrel-dict-widget']")
        
        rows = wrapper.find_elements(By.XPATH, ".//tbody/tr")
        for row in rows:
            key_input = row.find_element(By.XPATH, "./td[1]/input")
            if key_input.get_attribute("value") == key:
                remove_btn = row.find_element(By.CSS_SELECTOR, ".btn-remove-line")
                remove_btn.click()
                break
        else:
            raise ValueError(f"Key '{key}' not found in dictionary widget")


class App(BaseElement):    
    def check_page(self, title:str = False, url:str = False) -> None:
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


class Navbar(BaseElement):    
    def navbar_click(self, text: str) -> None:
        nav_element = self.browser.find_element(By.TAG_NAME, "nav")
        link = nav_element.find_element(By.LINK_TEXT, text)
        link.click()

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
        self.right_sidebar_expected_visible = expected_visible # Used to deal with the sidebar tabs (for action sidebars)

class Modal(TransientElement):
    def click_button(self, by_button_text: str = False, by_id:str = False) -> None:
        if by_id:
            button = self.browser.find_element(By.ID, by_id)
        elif by_button_text:
            button = self.browser.find_element(By.XPATH, f"{self.expected_visible}//button[contains(text(), '{by_button_text}')]")
        else:
            raise ValueError("Either 'by_button_text' or 'by_id' must be provided.")
        button.click()
        self.assert_visibility(visible=False)

    def click_action_button(self, by_button_text: str) -> None:
        self.click_button(by_button_text)
        return RightSidebar(self.browser, expected_visible="//div[starts-with(@id, 'ActionSidebar')]")

    def close(self, assert_closed: bool = True) -> None:
        try:
            modal = self.browser.find_element(By.XPATH, self.expected_visible)
            close_button = modal.find_element(By.CSS_SELECTOR, ".close-btn")
        except:
            modal = self.browser.find_element(By.XPATH, self.expected_visible)
            close_button = modal.find_element(By.ID, "cancelButton")

        close_button.click()
        self.assert_visibility(visible=not assert_closed)


class Grid(BaseElement):
    def assert_card_visibility(self, visible: bool = True, by_title: str = False) -> None:
        self.check_visibility(
            xpath=f"//div[@class=\'grid\']//h3[text()=\'{by_title}\']", 
            visible=visible, 
            message=f"Card {by_title} should {'' if visible else 'not'} be displayed")

    def click_create_card(self, expected_visible:bool = False) -> Modal:
        self.browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        return Modal(self.browser, expected_visible)
    
    def click_card(self, by_xpath:str = False, by_title:str = False, by_position: int = 0) -> None:
        if by_xpath:
            self.browser.find_element(By.XPATH, by_xpath).click()
        elif by_title:
            xpath = f"//div[@class=\'grid\']//h3[text()=\'{by_title}\']"
            self.browser.find_element(By.XPATH, xpath).click()
        elif by_position:
            self.browser.find_element(By.CSS_SELECTOR, f".card:nth-child({by_position})").click()
        else:
            raise ValueError("Either 'by_xpath', 'by_title', or 'by_position' must be provided.")


class Table(BaseElement):
    def __init__(self, browser: WebDriver, table_name: str) -> None:
        super().__init__(browser)
        self.table_name = table_name
        self.table_id = f"table-html-{table_name}"

    def click_header_button(self, by_col_number: int = 0) -> Modal:
        if by_col_number:
            self.browser.find_element(By.CSS_SELECTOR, f"#{self.table_id} th:nth-child({by_col_number}) > .table-header-btn").click()

        return Modal(self.browser, expected_visible=f"//div[@id='InfoColModal']//div[@class='modal-content']")
    
    def get_cell(self, by_col_number: int, by_row_number: int) -> None:
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

    def click_button(self, by_button_text: str = False, by_id:str = False) -> None:
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

class TablesScreen(BaseElement):
    def click_create_new_table(self) -> None:
        self.browser.find_element(By.CSS_SELECTOR, "img").click()
        return RightSidebar(self.browser, expected_visible="//div[@id=\'CreateTableSidebar\']")
    
    def check_table_select_button_visibility(self, table_name: str, visible: bool = True) -> None:
        self.check_visibility(
            xpath=f"//button[contains(.,\'{table_name}\')]",
            visible=visible,
            message=f"Table {table_name} should {'' if visible else 'not'} be displayed")
        
    def select_table(self, by_name: str = False) -> None:
        if by_name:
            self.browser.find_element(By.XPATH, f"//button[contains(.,\'{by_name}\')]").click()
            return Table(self.browser, by_name)


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
            f"//div[@id=\'pipeline\']//div[@class=\'action\'][{by_position}]//button[contains(@class, \'list-edit-btn\')]"
        ).click()
        return Modal(self.browser, expected_visible="//div[@id=\'editActionModal\']")

class Tour(App, Navbar, Grid, TablesScreen, PipelineScreen):
    def __init__(self, browser: WebDriver, server: str) -> None:
        super().__init__(browser)
        browser.get(f"{server}/projects/")

    def create_project(self, name: str, description: str = False):
        create_project_modal = self.click_create_card(
            expected_visible="//div[contains(@class,'modal-content')]//form[@id='createProjectModalForm']")
        create_project_modal.fill([("name", name)])
        if description:
            create_project_modal.fill([("description", description)])
        create_project_modal.submit(assert_closed=True)

    def confirmation_modal(self, confirm: bool = True) -> Modal:
        """ Handle the confirmation modal """
        modal = Modal(self.browser, expected_visible="//div[starts-with(@id,'confirmation-modal')]")
        button_id = "confirm-btn" if confirm else "cancel-btn"
        modal.click_button(by_id=button_id)
