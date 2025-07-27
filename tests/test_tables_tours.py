import pytest
from tomlkit import table

from tests.utils.tours_toolbox import Tour


class TestTablesTours:
    @pytest.mark.slow
    def test_create_table_onchange(self, server, browser, reset_projects):
        """Check the onchange of right sidebar table creation."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)

        sidebar = tour.click_create_new_table()

        sidebar.fill([("source_creation_type", "Other Tables")])
        sidebar.check_visibility("//select[@id='table_df']", visible=True)
        sidebar.check_visibility("//select[@id='data_source_dir']", visible=False)

        sidebar.fill([("source_creation_type", "Data Sources")])
        sidebar.check_visibility("//select[@id='table_df']", visible=False)
        sidebar.check_visibility("//select[@id='data_source_dir']", visible=True)

    @pytest.mark.slow
    def test_create_table_from_data_source(self, server, browser, reset_projects):
        """Check if the table is created correctly (from a data source)."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)

        sidebar = tour.click_create_new_table()
        table_name = "test create new table"
        sidebar.fill([("table_name", table_name), ("data_source_dir", "Csv ordered")])
        sidebar.submit()

        tour.check_table_select_button_visibility(table_name)

    @pytest.mark.slow
    def test_create_table_from_other_table_copy(self, server, browser, reset_projects):
        """Check if the table is created correctly (from another table)."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)

        sidebar = tour.click_create_new_table()
        table_name = "test create new table"
        sidebar.fill([("table_name", table_name), ("source_creation_type", "Other Tables")])
        sidebar.fill([("table_df", "random")])
        sidebar.submit()

        tour.check_table_select_button_visibility(table_name)

    @pytest.mark.slow
    def test_swap_table_displayed(self, server, browser, reset_projects):
        """Check if the selected table is displayed correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)

        table = tour.select_table(by_name="ordered")
        table.check_displayed()

        table = tour.select_table(by_name="random")
        table.check_displayed()

        table = tour.select_table(by_name="ordered")
        table.check_displayed()

    @pytest.mark.slow
    def test_table_pager(self, server, browser, reset_projects):
        """Check if the table pager is displayed correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)

        table = tour.select_table(by_name="ordered")

        table.next_page()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "10", "First cell on second column should be '10' on the second page."

        table.previous_page()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "0", "First cell on second column should be '0' on the second page."

    @pytest.mark.slow
    def test_info_col_modal(self, server, browser, reset_projects):
        """Check if the info column modal is displayed correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)

        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=1)
        col_modal.check_visibility(xpath="//div[@class='infos-div']")
        col_modal.check_visibility(xpath="//div[@class='btn-div']")
        col_modal.check_visibility(xpath="//div[@class='infos-div numeric-only']", visible=False)
        col_modal.check_visibility(xpath="//div[@class='btn-div numeric-only']", visible=False)
        col_modal.close()

        col_modal = table.click_header_button(by_col_number=2)
        col_modal.check_visibility(xpath="//div[@class='infos-div']")
        col_modal.check_visibility(xpath="//div[@class='btn-div']")
        col_modal.check_visibility(xpath="//div[@class='infos-div numeric-only']")
        col_modal.check_visibility(xpath="//div[@class='btn-div numeric-only']")
        col_modal.close()

    @pytest.mark.slow
    def test_sort_column(self, server, browser, reset_projects):
        """Check if the column is sorted correctly."""
        tour = Tour(browser, server)

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

    @pytest.mark.slow
    def test_sort_column_advanced(self, server, browser, reset_projects):
        """Test sorting a column using the advanced tab with dictionary widget."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        # Sort descending
        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.switch_to_advanced_tab()
        sidebar.edit_dictionary("kwargs", "ascending", "False")     
        sidebar.submit()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "99"

        # Sort back to ascending (by removing and adding back the key)
        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.switch_to_advanced_tab()
        sidebar.remove_from_dictionary("kwargs", "ascending")
        sidebar.add_to_dictionary("kwargs", "ascending", "True")
        sidebar.submit()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "0"

    @pytest.mark.slow
    def test_replace_vals(self, server, browser, reset_projects):
        """Check if the vals are replaced correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0"
        col_modal = table.click_header_button(by_col_number=1)
        sidebar = col_modal.click_action_button("Replace vals.")
        sidebar.add_to_dictionary("replace_vals", "mock0", "mock0_edited")
        sidebar.submit()
        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0_edited"

    @pytest.mark.slow
    def test_replace_vals_advanced(self, server, browser, reset_projects):
        """Test replacing values using the advanced tab with dictionary widget."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0"
        col_modal = table.click_header_button(by_col_number=1)
        sidebar = col_modal.click_action_button("Replace vals.")
        sidebar.switch_to_advanced_tab()
        sidebar.edit_dictionary("kwargs", "to_replace", '["mock0"]')
        sidebar.edit_dictionary("kwargs", "value", '["mock0_edited"]')
        sidebar.submit()
        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0_edited"

    @pytest.mark.slow
    def test_missing_vals(self, server, browser, reset_projects):
        """Check if the missing vals are replaced correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="random")

        cell = table.get_cell(by_col_number=1, by_row_number=2)
        assert cell.text == "NaN"
        col_modal = table.click_header_button(by_col_number=1)
        sidebar = col_modal.click_action_button("Missing vals.")
        sidebar.fill([("action", "Replace")])
        sidebar.fill([("replace_value", "1000")])
        sidebar.submit()
        cell = table.get_cell(by_col_number=1, by_row_number=2)
        assert cell.text == "1000"

    @pytest.mark.slow
    def test_change_type(self, server, browser, reset_projects):
        """Check if the column changes of type correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=2)
        col_modal.check_visibility(xpath="//div[@class='infos-div numeric-only']")
        col_modal.check_visibility(xpath="//div[@class='infos-div string-only']", visible=False)
        sidebar = col_modal.click_action_button("Change type")
        sidebar.fill([("new_type", "String")])
        sidebar.submit()

        col_modal = table.click_header_button(by_col_number=2)  
        col_modal.check_visibility(xpath="//div[@class='infos-div numeric-only']", visible=False)
        col_modal.check_visibility(xpath="//div[@class='infos-div string-only']")

    @pytest.mark.slow
    def test_apply_function(self, server, browser, reset_projects):
        """Check if the apply function works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0"
        col_modal = table.click_header_button(by_col_number=1)
        sidebar = col_modal.click_action_button("Apply Function")
        sidebar.fill([("function", "len(row['mock_name'])")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "5"
