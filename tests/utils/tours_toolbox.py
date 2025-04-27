from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class BaseTool:
    """Base class for all toolbox components providing common functionality."""
    
    def __init__(self, browser: WebDriver):
        self.browser = browser


class App(BaseTool):
    """Represents the main application."""
    
    def check_page(self, title:str = False, url:str = False) -> None:
        """Check if the page title or URL matches the expected values."""
        if title:
            actual_title = self.browser.find_element(By.CSS_SELECTOR, "h1").text
            assert actual_title == title, f"Expected title: {title}, but got: {actual_title}"
        if url:
            actual_url = self.browser.current_url
            assert url in actual_url, f"Expected '{url}' in the url"

    def check_elements(self, by_ids: list = False, by_css_selectors: list = False) -> None:
        """
        Check if the elements with the given selector are visible on the page and have the expected values.
        
        :param by_ids: selector based on ids; [(id, expected_value)]
        :param by_css_selectors: selector based on css selectors; [(css_selector, expected_value)]
        """
        by_ids = by_ids or []
        by_css_selectors = by_css_selectors or []

        def check_element(element):
            assert element.is_displayed(), f"Element is not displayed."
            actual_value = element.get_attribute("value")
            assert actual_value == expected_value, f"Expected value: {expected_value}, but got: {actual_value}"

        for id, expected_value in by_ids:
            element = self.browser.find_element(By.ID, id)
            check_element(element)

        for css_selector, expected_value in by_css_selectors:
            element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
            check_element(element)

    def fill_element(self, by_id: str = False, by_css_selector: str = False, value: str = False) -> None:
        """Fill an element with the given value."""
        if by_id:
            element = self.browser.find_element(By.ID, by_id)
        elif by_css_selector:
            element = self.browser.find_element(By.CSS_SELECTOR, by_css_selector)
        else:
            raise ValueError("Either 'by_id' or 'by_css_selector' must be provided.")

        if element.tag_name.lower() == 'select':
            option = element.find_element(By.XPATH, f"//option[contains(text(), '{value}')]")
            option.click()
            return

        element.click()
        element.clear()
        element.send_keys(value)

    def assert_error_page(self) -> None:
        """Check if the error page is displayed."""
        assert self.browser.find_element(By.CSS_SELECTOR, "h3").text == "Error", "Error page not displayed as expected."


class Navbar(BaseTool):
    """Represents the navigation bar of the application."""
    
    def navbar_click(self, text: str) -> None:
        """Click on a navigation link by its text."""
        nav_element = self.browser.find_element(By.TAG_NAME, "nav")
        self.check_navbar_hover_effect(nav_element)
        link = nav_element.find_element(By.LINK_TEXT, text)
        link.click()

    def check_navbar_hover_effect(self, nav_element) -> None:
        """Check if hover effects works on navbar elements."""
        links = nav_element.find_elements(By.TAG_NAME, "a") 
        actions = ActionChains(self.browser)       
        for link in links:            
            original_color = link.value_of_css_property("background-color")
            actions.move_to_element(link).perform()
            hover_color = link.value_of_css_property("background-color")
            
            if hover_color == original_color:
                assert False, f"Hover effect not working on link with text: {link.text}"


class RightSidebar(BaseTool):
    def __init__(self, browser, expected_visible) -> None:
        super().__init__(browser)
        self.expected_visible = expected_visible
        self.assert_visibility(visible=True)

    def assert_visibility(self, visible=True) -> None:
        sidebar_style = self.browser.find_element(By.XPATH, self.expected_visible).get_attribute("style")
        if visible:
             WebDriverWait(self.browser, 2, poll_frequency=0.1).until(
                lambda driver: "width: 300px" in sidebar_style,
                message="Sidebar did not appear as expected.")
        else:
             WebDriverWait(self.browser, 2, poll_frequency=0.1).until(
                lambda driver: "width: 0" in sidebar_style or "width: 0px" in sidebar_style or not sidebar_style,
                message="Sidebar did not close as expected.")
            
    def fill(self, field_id: str, value: str) -> None:
        """Fill a field in the modal dialog."""
        field = self.browser.find_element(By.ID, field_id)

        # TODO: use from selenium.webdriver.support.ui import Select ?
        if field.tag_name.lower() == 'select':
            option = field.find_element(By.XPATH, f"//option[contains(text(), '{value}')]")
            option.click()
            return
        
        field.click()
        field.clear()
        field.send_keys(value)

    def submit(self, assert_closed=True) -> None:
        """Submit the modal dialog."""
        self.browser.find_element(By.XPATH, f"{self.expected_visible}//button[contains(@class, 'btn-primary')]").click()
        self.assert_visibility(visible=not assert_closed)

class Modal(BaseTool):
    """Represents a modal dialog in the application."""

    def __init__(self, browser, expected_visible) -> None:
        super().__init__(browser)
        self.expected_visible = expected_visible
        self.assert_visibility(visible=True)
        
    def assert_visibility(self, visible=True, redirect=False) -> None:
        if visible:
            WebDriverWait(self.browser, 2, poll_frequency=0.1).until(
                expected_conditions.visibility_of_element_located((By.XPATH, self.expected_visible)),
                message="Modal did not appear as expected.")
        else:
            if redirect:
                return
            WebDriverWait(self.browser, 2, poll_frequency=0.1).until(
                expected_conditions.invisibility_of_element_located((By.XPATH, self.expected_visible)),
                message="Modal did not close as expected.")
            
    def fill(self, field_id: str, value: str) -> None:
        """Fill a field in the modal dialog."""
        field = self.browser.find_element(By.ID, field_id)

        if field.tag_name.lower() == 'select':
            option = field.find_element(By.XPATH, f"//option[contains(text(), '{value}')]")
            option.click()
            return
        
        field.click()
        field.clear()
        field.send_keys(value)

    def click_button(self, by_button_text: str) -> None:
        """Click a button in the modal dialog."""
        button = self.browser.find_element(By.XPATH, f"{self.expected_visible}//button[contains(text(), '{by_button_text}')]")
        button.click()
        self.assert_visibility(visible=False)

    def click_action_button(self, by_button_text: str) -> None:
        """Click an action button in the modal dialog."""
        self.click_button(by_button_text)
        return RightSidebar(self.browser, expected_visible="//div[@id=\'ActionSidebar\']")

    def close(self, assert_closed=True) -> None:
        """Close the modal dialog."""
        self.browser.find_element(By.ID, "cancelButton").click()
        self.assert_visibility(visible=not assert_closed)
        
    def submit(self, assert_closed=True, redirect=False) -> None:
        """Submit the modal dialog."""
        self.browser.find_element(By.XPATH, f"{self.expected_visible}//button[contains(@class, 'btn-primary')]").click()
        self.assert_visibility(visible=not assert_closed, redirect=redirect)


class Grid(BaseTool):
    """Represents a grid view in the application."""

    def assert_card_visibility(self, visible=True, by_title=False) -> None:
        xpath = f"//div[@class=\'grid\']//h3[text()=\'{by_title}\']"
        if visible:
            WebDriverWait(self.browser, 2, poll_frequency=0.1).until(
                expected_conditions.visibility_of_element_located((By.XPATH, xpath)),
                message=f"Data source {by_title} should be displayed")
        else:
            WebDriverWait(self.browser, 2, poll_frequency=0.1).until(
                expected_conditions.invisibility_of_element_located((By.XPATH, xpath)),
                message="Data source {by_title} should not be displayed")

    def click_create_card(self, expected_visible=False) -> Modal:
        """Click on the create card button."""
        self.browser.find_element(By.CSS_SELECTOR, "p:nth-child(1)").click()
        return Modal(self.browser, expected_visible)
    
    def click_card(self, by_xpath:str = False, by_title:str = False, by_position: int = 0) -> None:
        """Click on a card in the grid."""
        if by_xpath:
            self.browser.find_element(By.XPATH, by_xpath).click()
        elif by_title:
            xpath = f"//div[@class=\'grid\']//h3[text()=\'{by_title}\']"
            self.browser.find_element(By.XPATH, xpath).click()
        elif by_position:
            self.browser.find_element(By.CSS_SELECTOR, f".card:nth-child({by_position})").click()
        else:
            raise ValueError("Either 'by_xpath', 'by_title', or 'by_position' must be provided.")


class Table(BaseTool):
    def __init__(self, browser: WebDriver, table_name: str) -> None:
        super().__init__(browser)
        self.table_name = table_name
        self.table_id = f"table-html-{table_name}"

    def click_header_button(self, by_col_number: int = 0) -> Modal:
        """Click on the header button of the table."""
        if by_col_number:
            self.browser.find_element(By.CSS_SELECTOR, f"#{self.table_id} th:nth-child({by_col_number}) > .table-header-btn").click()

        return Modal(self.browser, expected_visible=f"//div[@id='InfoColModal']")
    
    def get_cell(self, by_col_number: int, by_row_number: int) -> None:
        """Get the cell from the table at ColxLine."""
        return self.browser.find_element(
            By.CSS_SELECTOR, f"#table-html-ordered tr:nth-child({by_row_number}) > td:nth-child({by_col_number})")
        

class TablesScreen(BaseTool):
    """Represents the tables view in the application."""

    def click_create_new_table(self) -> None:
        """Click on the create new table button."""
        self.browser.find_element(By.CSS_SELECTOR, "img").click()
        return RightSidebar(self.browser, expected_visible="//div[@id=\'CreateTable\']")
    
    def check_table_exists(self, table_name: str) -> None:
        """Check if the table with the given name exists."""
        xpath = f"//button[contains(.,\'{table_name}\')]"
        WebDriverWait(self.browser, 2, poll_frequency=0.1).until(
            expected_conditions.visibility_of_element_located((By.XPATH, xpath)),
            message=f"Table {table_name} should be displayed")
        
    def select_table(self, by_name: str = False) -> None:
        """Select a table by its name."""
        if by_name:
            self.browser.find_element(By.CSS_SELECTOR, f"#table-html-{by_name}").click()
            return Table(self.browser, by_name)


class Tour(App, Navbar, Grid, TablesScreen):
    """Represents a tour."""

    def __init__(self, browser: WebDriver, tour_name: str = "Tour") -> None:
        super().__init__(browser)
        self.tour_name = tour_name

    def create_project(self, name, description=False):
        """Create a new project with the given name and description."""
        create_project_modal = self.click_create_card(expected_visible="//form[@id=\'projectForm\']")
        create_project_modal.fill("projectName", name)
        if description:
            create_project_modal.fill("projectDescription", description)
        create_project_modal.submit(assert_closed=True, redirect=True)
