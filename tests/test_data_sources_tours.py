import pandas as pd
import pytest
from unittest.mock import patch

from tests.utils.tours_toolbox import Tour, MOCK_PROJECT1_NAME


MOCK_YFINANCE_DATA = pd.DataFrame({'Open': [100.0, 101.0, 102.0], 'High': [105.0, 106.0, 107.0], 'Low': [98.0, 99.0, 100.0]})


class TestDataSourcesTours:
    @pytest.mark.slow
    def test_create_data_source_modal(self, server, browser, reset_projects):
        """Test create project modal appears and disappears correctly"""
        tour = Tour(browser, server)

        tour.click_card(by_title=MOCK_PROJECT1_NAME)

        tour.navbar_click("Data sources")
        tour.check_grid_cards_over_effect()
        create_source_modal = tour.click_create_card(expected_visible="//div[@class=\'modal-content\']")
        create_source_modal.close()
        tour.check_grid_cards_over_effect()

    @pytest.mark.slow
    def test_form_input_depends_data_source_type(self, server, browser, reset_projects):
        """Test that form changes when changing source type"""
        tour = Tour(browser, server)

        tour.click_card(by_title=MOCK_PROJECT1_NAME)
        tour.navbar_click("Data sources")
        create_source_modal = tour.click_create_card(expected_visible="//div[@class=\'modal-content\']")
        tour.check_elements(by_ids=[("source_name", ""), ("source_description", ""), ("source_type", "csv"), ("source_file", "")])

        create_source_modal.fill([("source_type", "Odoo")])
        tour.check_elements(by_ids=[
            ("url", ""), ("db", ""),
            ("key", ""), ("username", ""),
            ("model", ""), ("fields", ""), ("domain", "")])

        create_source_modal.fill([("source_type", "Yahoo Finance")])
        tour.check_elements(by_ids=[("start_date", ""), ("end_date", ""), ("tickers", ""), ("interval", "1d")])

        create_source_modal.fill([("source_type", "Pickle")])
        tour.check_elements(by_ids=[("source_file", "")])

    @pytest.mark.slow
    def test_data_source_edit(self, server, browser, reset_projects):
        """Test edition of a data source's settings"""
        tour = Tour(browser, server)

        tour.click_card(by_title=MOCK_PROJECT1_NAME)
        tour.navbar_click("Data sources")

        tour.click_card(by_position=2)
        new_description = "Edition from test_data_source_edit"
        tour.fill_element(by_id="sourceDescription", value=new_description)
        tour.click_confirm_button()

        tour.click_card(by_position=2)
        tour.check_elements(by_ids=[("sourceDescription", new_description)])

    @pytest.mark.slow
    def test_create_yahoo_data_source(self, server, browser, reset_projects):
        """Test yahoo data source creation"""
        tour = Tour(browser, server)

        tour.click_card(by_title=MOCK_PROJECT1_NAME)
        tour.navbar_click("Data sources")

        create_source_modal = tour.click_create_card(expected_visible="//div[@class=\'modal-content\']")
        create_source_modal.fill([
            ("source_name", "test yahoo"),
            ("source_description", "a simple test for yahoo data source"),
            ("source_type", "Yahoo Finance"),
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
        tour = Tour(browser, server)

        tour.click_card(by_title=MOCK_PROJECT1_NAME)
        tour.navbar_click("Data sources")

        tour.assert_card_visibility(by_title="Csv ordered")
        tour.click_card(by_title="Csv ordered")
        tour.click_danger_button()
        tour.assert_card_visibility(visible=False, by_title="Csv ordered")
