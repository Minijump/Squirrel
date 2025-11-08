from selenium.webdriver.remote.webdriver import WebDriver

from tests.utils.tour_toolbox_app import App, TablesScreen, PipelineScreen


MOCK_PROJECT1_NAME = "UT Mock Project 1"


class Tour(App, TablesScreen, PipelineScreen):
    def __init__(self, browser: WebDriver, server: str) -> None:
        super().__init__(browser)
        browser.get(f"{server}/projects/")

    def create_project(self, name: str, description: str = False) -> None:
        create_project_modal = self.click_create_card(
            expected_visible="//div[contains(@class,'modal-content')]//form[@id='createProjectModalForm']")
        values = [("name", name)]
        if description:
            values.append(("description", description))
        create_project_modal.fill(values)
        create_project_modal.submit(assert_closed=True)
