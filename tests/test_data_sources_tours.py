import pandas as pd
import pytest
from unittest.mock import patch

from selenium.webdriver.common.by import By

from tests.utils.tours_toolbox import Tour


MOCK_YFINANCE_DATA = pd.DataFrame({'Open': [100.0, 101.0, 102.0], 'High': [105.0, 106.0, 107.0], 'Low': [98.0, 99.0, 100.0]})


class TestDataSourcesTours:
    @pytest.mark.slow
    def test_create_data_source_modal(self, server, browser, reset_projects):
        """Test create project modal appears and disappears correctly"""
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test create data source modal")

        tour.create_project("test create data source modal")

        tour.navbar_click("Data sources")
        create_source_modal = tour.click_create_card(expected_visible="//div[@class=\'modal-content\']")
        create_source_modal.close()

    @pytest.mark.slow
    def test_form_input_depends_data_source_type(self, server, browser, reset_projects):
        """Test that form changes when changing source type"""
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test create data source modal")

        tour.create_project("test data source type")

        tour.navbar_click("Data sources")
        create_source_modal = tour.click_create_card(expected_visible="//div[@class=\'modal-content\']")
        # Check visible inputs are correct while changing source type (default type is CSV)
        tour.check_elements(by_ids=[("sourceName", ""), ("sourceDescription", ""), ("sourceType", "csv"), ("sourceFile", "")])

        create_source_modal.fill([("sourceType", "Odoo")])
        tour.check_elements(by_ids=[("odooUrl", ""), ("odooDb", ""), ("odooModel", "")])

        create_source_modal.fill([("sourceType", "Yahoo Finance")])
        tour.check_elements(by_ids=[("start_date", ""), ("interval", "1d")])

        create_source_modal.fill([("sourceType", "Pickle")])
        tour.check_elements(by_ids=[("sourceFile", "")])

    @pytest.mark.slow
    def test_data_source_edit(self, server, browser, reset_projects):
        """Test edition of a data source's settings"""
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test data source edit")

        tour.click_card(by_position=2)
        tour.navbar_click("Data sources")

        tour.click_card(by_position=2)
        new_description = "Edition from test_data_source_edit"
        tour.fill_element(by_id="sourceDescription", value=new_description)
        browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        tour.click_card(by_position=2)
        tour.check_elements(by_ids=[("sourceDescription", new_description)])

    @pytest.mark.slow
    def test_create_yahoo_data_source(self, server, browser, reset_projects):
        """Test yahoo data source creation"""
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test create yahoo data source")

        tour.create_project("test create yahoo data source")
        tour.navbar_click("Data sources")

        create_source_modal = tour.click_create_card(expected_visible="//div[@class=\'modal-content\']")
        create_source_modal.fill([
            ("sourceName", "test yahoo"),
            ("sourceDescription", "a simple test for yahoo data source"),
            ("sourceType", "Yahoo Finance"),
            ("tickers", "[\'AU\']"),
            ("start_date", "2025-03-03"),
            ("end_date", "2025-03-21")
        ])
        with patch('yfinance.download', return_value=MOCK_YFINANCE_DATA):
            create_source_modal.submit()

        tour.assert_card_visibility(by_title="test yahoo")

    @pytest.mark.slow
    def test_delete_data_source(self, server, browser, reset_projects):
        """Test data source deletion"""
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test delete data source")

        tour.click_card(by_position=2)
        tour.navbar_click("Data sources")

        tour.assert_card_visibility(by_title="Csv ordered")
        tour.click_card(by_title="Csv ordered")
        browser.find_element(By.CSS_SELECTOR, ".btn-danger").click()
        tour.assert_card_visibility(visible=False, by_title="Csv ordered")
