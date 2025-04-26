from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains


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

class Tour(App, Navbar):
    """Represents a tour."""

    def __init__(self, browser: WebDriver, tour_name: str = "Tour") -> None:
        super().__init__(browser)
        self.tour_name = tour_name
