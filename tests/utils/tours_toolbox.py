from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

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

    def fill_element(self, by_id: str = False, by_css_selector: str = False, value: str = False) -> None:
        if by_id:
            element = self.browser.find_element(By.ID, by_id)
        elif by_css_selector:
            element = self.browser.find_element(By.CSS_SELECTOR, by_css_selector)
        else:
            raise ValueError("Either 'by_id' or 'by_css_selector' must be provided.")

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


class App(BaseElement):    
    def check_page(self, title:str = False, url:str = False) -> None:
        if title:
            actual_title = self.browser.find_element(By.CSS_SELECTOR, "h1").text
            assert actual_title == title, f"Expected title: {title}, but got: {actual_title}"
        if url:
            actual_url = self.browser.current_url
            assert url in actual_url, f"Expected '{url}' in the url"

    def assert_error_page(self) -> None:
        assert self.browser.find_element(By.CSS_SELECTOR, "h3").text == "Error", "Error page not displayed as expected."

    def click_home_button(self) -> None:
        self.browser.find_element(By.CSS_SELECTOR, ".fa-home").click()


class Navbar(BaseElement):    
    def navbar_click(self, text: str, check_over_effect: bool = False) -> None:
        nav_element = self.browser.find_element(By.TAG_NAME, "nav")
        if check_over_effect:
            self.check_navbar_hover_effect(nav_element)
        link = nav_element.find_element(By.LINK_TEXT, text)
        link.click()

    def check_navbar_hover_effect(self, nav_element: WebElement) -> None:
        links = nav_element.find_elements(By.TAG_NAME, "a") 
        actions = ActionChains(self.browser)       
        for link in links:            
            original_color = link.value_of_css_property("background-color")
            actions.move_to_element(link).perform()
            hover_color = link.value_of_css_property("background-color")
            
            if hover_color == original_color:
                assert False, f"Hover effect not working on link with text: {link.text}"


class TransientElement(BaseElement):
    def __init__(self, browser: WebDriver, expected_visible: str) -> None:
        super().__init__(browser)
        self.expected_visible = expected_visible
        self.assert_visibility(visible=True)

    def assert_visibility(self, visible: bool = True) -> None:
        self.check_visibility(
            xpath=self.expected_visible, 
            visible=visible, 
            message=f"Transient element did not {'appear' if visible else 'closed'} as expected.")

    def fill(self, values: list) -> None:
        """ Fill the form with the given values, where values is a list of tuples (by_id, value) """
        for value in values:
            self.fill_element(by_id=value[0], value=value[1])

    def submit(self, assert_closed: bool = True) -> None:
        self.browser.find_element(By.XPATH, f"{self.expected_visible}//button[contains(@class, 'btn-primary')]").click()
        self.assert_visibility(visible=not assert_closed)


class RightSidebar(TransientElement):
    def assert_visibility(self, visible: bool = True) -> None:
        sidebar_style = self.browser.find_element(By.XPATH, self.expected_visible).get_attribute("style")
        if visible:
             WebDriverWait(self.browser, 1, poll_frequency=0.1).until(
                lambda driver: "width: 300px" in sidebar_style,
                message="Sidebar did not appear as expected.")
        else:
             WebDriverWait(self.browser, 0.2, poll_frequency=0.1).until(
                lambda driver: "width: 0" in sidebar_style or "width: 0px" in sidebar_style or not sidebar_style,
                message="Sidebar did not close as expected.")


class Modal(TransientElement):
    def click_button(self, by_button_text: str) -> None:
        button = self.browser.find_element(By.XPATH, f"{self.expected_visible}//button[contains(text(), '{by_button_text}')]")
        button.click()
        self.assert_visibility(visible=False)

    def click_action_button(self, by_button_text: str) -> None:
        self.click_button(by_button_text)
        return RightSidebar(self.browser, expected_visible="//div[@id=\'ActionSidebar\']")

    def close(self, assert_closed: bool = True) -> None:
        self.browser.find_element(By.ID, "cancelButton").click()
        self.assert_visibility(visible=not assert_closed)


class Grid(BaseElement):
    def assert_card_visibility(self, visible: bool = True, by_title: str = False) -> None:
        self.check_visibility(
            xpath=f"//div[@class=\'grid\']//h3[text()=\'{by_title}\']", 
            visible=visible, 
            message=f"Data source {by_title} should {'' if visible else 'not'} be displayed")
        
    def check_grid_cards_over_effect(self) -> None:
        grid = self.browser.find_element(By.CSS_SELECTOR, ".grid")
        cards = grid.find_elements(By.CSS_SELECTOR, ".card")
        actions = ActionChains(self.browser)
        
        for card in cards:
            original_transform = card.value_of_css_property("transform")
            actions.move_to_element(card).perform()
            hover_transform = card.value_of_css_property("transform")
            
            if hover_transform == original_transform:
                assert False, f"Hover effect not working on card with title: {card.text}"

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

        return Modal(self.browser, expected_visible=f"//div[@id='InfoColModal']")
    
    def get_cell(self, by_col_number: int, by_row_number: int) -> None:
        return self.browser.find_element(
            By.CSS_SELECTOR, f"#table-html-ordered tr:nth-child({by_row_number}) > td:nth-child({by_col_number})")
        

class TablesScreen(BaseElement):
    def click_create_new_table(self) -> None:
        self.browser.find_element(By.CSS_SELECTOR, "img").click()
        return RightSidebar(self.browser, expected_visible="//div[@id=\'CreateTable\']")
    
    def check_table_visibility(self, table_name: str, visible: bool = True) -> None:
        self.check_visibility(
            xpath=f"//button[contains(.,\'{table_name}\')]",
            visible=visible,
            message=f"Table {table_name} should {'' if visible else 'not'} be displayed")
        
    def select_table(self, by_name: str = False) -> None:
        if by_name:
            self.browser.find_element(By.CSS_SELECTOR, f"#table-html-{by_name}").click()
            return Table(self.browser, by_name)


class Tour(App, Navbar, Grid, TablesScreen):
    def __init__(self, browser: WebDriver, server: str) -> None:
        super().__init__(browser)
        browser.get(f"{server}/projects/")

    def create_project(self, name: str, description: str = False):
        create_project_modal = self.click_create_card(expected_visible="//form[@id=\'projectForm\']")
        create_project_modal.fill([("projectName", name)])
        if description:
            create_project_modal.fill([("projectDescription", description)])
        create_project_modal.submit(assert_closed=True)
