from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait


class Widget:
    def _get_widget_wrapper(self, field_name: str, widget_type: str, widget_class: str):
        widget_xpath = f"{self.expected_visible}//*[@name='{field_name}'][@widget='{widget_type}']"
        widget = self.browser.find_element(By.XPATH, widget_xpath)
        return widget.find_element(By.XPATH, f"./preceding-sibling::div[@class='{widget_class}']")

class DictWidget(Widget):
    def _find_dict_row_by_key(self, wrapper, key: str):
        rows = wrapper.find_elements(By.XPATH, ".//tbody/tr")
        for row in rows:
            key_input = row.find_element(By.XPATH, "./td[1]/input")
            if key_input.get_attribute("value") == key:
                return row
        raise ValueError(f"Key '{key}' not found in dictionary widget")

    def add_to_dictionary(self, field_name: str, key: str, value: str) -> None:
        wrapper = self._get_widget_wrapper(field_name, 'squirrel-dictionary', 'squirrel-dict-widget squirrel-table-input-widget')
        
        wrapper.find_element(By.CSS_SELECTOR, ".btn-add-line").click()
        rows = wrapper.find_elements(By.XPATH, ".//tbody/tr")
        new_row = rows[-1]
        key_input = new_row.find_element(By.XPATH, "./td[1]/input")
        value_input = new_row.find_element(By.XPATH, "./td[2]/input")
        
        key_input.clear()
        key_input.send_keys(key)
        value_input.clear()
        value_input.send_keys(value)

    def edit_dictionary(self, field_name: str, key: str, new_value: str) -> None:
        wrapper = self._get_widget_wrapper(field_name, 'squirrel-dictionary', 'squirrel-dict-widget squirrel-table-input-widget')
        row = self._find_dict_row_by_key(wrapper, key)
        value_input = row.find_element(By.XPATH, "./td[2]/input")
        value_input.clear()
        value_input.send_keys(new_value)

    def remove_from_dictionary(self, field_name: str, key: str) -> None:
        wrapper = self._get_widget_wrapper(field_name, 'squirrel-dictionary', 'squirrel-dict-widget squirrel-table-input-widget')
        row = self._find_dict_row_by_key(wrapper, key)
        remove_btn = row.find_element(By.CSS_SELECTOR, ".btn-remove-line")
        remove_btn.click()


class ListWidget(Widget):
    def add_to_list(self, field_name: str, value: str) -> None:
        wrapper = self._get_widget_wrapper(field_name, 'squirrel-list', 'squirrel-list-widget squirrel-table-input-widget')

        wrapper.find_element(By.CSS_SELECTOR, ".btn-add-line").click()
        rows = wrapper.find_elements(By.XPATH, ".//tbody/tr")
        value_input = rows[-1].find_element(By.XPATH, "./td[1]/input")
        value_input.clear()
        value_input.send_keys(value)


class BaseElement(DictWidget, ListWidget):
    def __init__(self, browser: WebDriver):
        self.browser = browser

    def check_visibility(self, xpath: str = False, visible: bool = True, message: str = False) -> None:
        if visible:
            WebDriverWait(self.browser, 1, poll_frequency=0.1).until(
                expected_conditions.visibility_of_element_located((By.XPATH, xpath)),
                message=message or "Element should be visible.")
        else:
            WebDriverWait(self.browser, 0.2, poll_frequency=0.1).until(
                expected_conditions.invisibility_of_element_located((By.XPATH, xpath)),
                message=message or "Element should not be visible.")

    def check_elements(self, by_ids: list = False, by_css_selectors: list = False) -> None:
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
