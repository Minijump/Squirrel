# Generated by Selenium IDE; edited
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


class TestAppTours():
  def setup_method(self, method):
    options = Options()
    options.add_argument('--headless')

    self.driver = webdriver.Firefox(options=options) #TODO: is too slow
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()

  @pytest.mark.slow
  def test_navigate_in_app_menus(self, server):
      """
      Test the navigation in the app menus
      """
      self.driver.get(f"{server}/projects/")
      self.driver.set_window_size(1524, 717)

      # Navigate to app settings
      self.driver.find_element(By.LINK_TEXT, "Settings").click()
      assert self.driver.find_element(By.CSS_SELECTOR, "h1").text == "App settings"

      # Navigate back to projects
      self.driver.find_element(By.LINK_TEXT, "Projects").click()
      assert self.driver.find_element(By.CSS_SELECTOR, "h1").text == "ProjectHub"
