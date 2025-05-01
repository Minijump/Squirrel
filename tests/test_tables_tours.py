import pytest

from tests.utils.tours_toolbox import Tour


class TestTablesTours:
    @pytest.mark.slow
    def test_create_table(self, server, browser, reset_projects):
        """
        Check if the table is created correctly.
        """
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test create table")

        tour.click_card(by_position=2)

        sidebar = tour.click_create_new_table()
        table_name = "test create new table"
        sidebar.fill([("new_table_name", table_name), ("data_source", "Csv ordered")])
        sidebar.submit()

        tour.check_table_exists(table_name)

    @pytest.mark.slow
    def test_sort_column(self, server, browser, reset_projects):
        """
        Check if the column is sorted correctly.
        """
        browser.get(f"{server}/projects/")
        tour = Tour(browser, "Test sort column")

        tour.click_card(by_position=2)

        table = tour.select_table(by_name="ordered")

        # Sort descending
        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.fill([("sort_order", "Descending")])
        sidebar.submit()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "99"

        # Sort back to ascending
        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.fill([("sort_order", "Ascending")])
        sidebar.submit()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "0"
