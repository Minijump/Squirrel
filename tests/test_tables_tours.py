import pytest

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

        sidebar.fill([("source_creation_type", "Data Source")])
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
    def test_replace_vals_int(self, server, browser, reset_projects):
        """Check if the vals are replaced correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "0"
        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Replace vals.")
        sidebar.add_to_dictionary("replace_vals", 0, 1)
        sidebar.submit()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "1"

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

    @pytest.mark.slow
    def test_normalize(self, server, browser, reset_projects):
        """Check if the normalize function works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Normalize")
        sidebar.fill([("method", "Min-Max")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert float(cell.text) == 0.0, "smallest element should be 0.0"

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.fill([("sort_order", "Descending")])
        sidebar.submit()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert float(cell.text) == 1.0, "Biggest element should be 1.0"

    @pytest.mark.slow
    def test_remove_under_over(self, server, browser, reset_projects):
        """Check if the remove under/overflow function works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Remove under/over")
        sidebar.fill([("lower_bound", "10")])
        sidebar.fill([("upper_bound", "90")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert float(cell.text) == 10, "smallest element should be 10"

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.fill([("sort_order", "Descending")])
        sidebar.submit()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert float(cell.text) == 90, "Biggest element should be 90"

    @pytest.mark.slow
    def test_cut(self, server, browser, reset_projects):
        """Check if the cut function works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Cut")
        sidebar.fill([("cut_values", "-1,50,100")])
        sidebar.fill([("cut_labels", "failed,success")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "failed", "smallest element should be 'failed'"

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.fill([("sort_order", "Descending")])
        sidebar.submit()
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "success", "Biggest element should be 'success'"

    @pytest.mark.slow  
    def test_keep_n_largest(self, server, browser, reset_projects):
        """Check if the keep n largest function works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Keep N largest")
        sidebar.fill([("n", "5")])
        sidebar.submit()

        cell_1 = table.get_cell(by_col_number=2, by_row_number=1)
        assert float(cell_1.text) == 99, "1st largest element should be 99"
        cell_5 = table.get_cell(by_col_number=2, by_row_number=5)
        assert float(cell_5.text) == 95, "5th largest element should be 95"

    @pytest.mark.slow  
    def test_keep_n_smallest(self, server, browser, reset_projects):
        """Check if the keep n smallest function works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Keep N smallest")
        sidebar.fill([("n", "5")])
        sidebar.submit()

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.fill([("sort_order", "Descending")]) # sort else test would pass even if keep n smallest does not work
        sidebar.submit()
        cell_1 = table.get_cell(by_col_number=2, by_row_number=1)
        assert float(cell_1.text) == 4, "1st element should be 4"
        cell_5 = table.get_cell(by_col_number=2, by_row_number=5)
        assert float(cell_5.text) == 0, "5th element should be 0"

    @pytest.mark.slow  
    def test_diff(self, server, browser, reset_projects):
        """Check if the diff function works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Diff")
        sidebar.fill([("periods", "1")])
        sidebar.submit()

        # creates a new column ('col2-diff')
        cell_1 = table.get_cell(by_col_number=3, by_row_number=1)
        assert cell_1.text == "NaN", "First element should be NaN"
        cell_2 = table.get_cell(by_col_number=3, by_row_number=2)
        assert float(cell_2.text) == 1, "Second element should be 1"

    @pytest.mark.slow 
    def test_math_operations(self, server, browser, reset_projects):
        """Check if the math operation works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Math operations")
        sidebar.fill([("operation", "Square Root")])
        sidebar.submit()

        cell_1 = table.get_cell(by_col_number=2, by_row_number=1)
        assert float(cell_1.text) == 0, "First element should be 0"
        cell_2 = table.get_cell(by_col_number=2, by_row_number=2)
        assert float(cell_2.text) == 1, "Second element should be 1"
        cell_5 = table.get_cell(by_col_number=2, by_row_number=5)
        assert float(cell_5.text) == 2, "Fifth element should be 2"

    @pytest.mark.slow 
    def test_replace_in_cells(self, server, browser, reset_projects):
        """Check if the replace in cells works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0"

        col_modal = table.click_header_button(by_col_number=1)
        sidebar = col_modal.click_action_button("Replace in cell")
        sidebar.fill([("action", "Regex")])
        sidebar.fill([("regex", "mock")])
        sidebar.fill([("replacement", "test")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "test0", "Cell should be replaced with 'test0'"

    @pytest.mark.slow 
    def test_string_formats(self, server, browser, reset_projects):
        """Check if the string formats work correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        col_modal = table.click_header_button(by_col_number=1)
        sidebar = col_modal.click_action_button("String formats")
        sidebar.fill([("operation", "Upper Case (HELLO WORLD)")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "MOCK0", "Cell should be in uppercase"

    @pytest.mark.slow 
    def test_delete_column(self, server, browser, reset_projects):
        """Check if the delete column works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0", "Cell should be mock0"

        col_modal = table.click_header_button(by_col_number=1)
        col_modal.click_danger_button()

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "0", "Cell should be 0, first column should be deleted"




    # TABLE ACTIONS TOURS -----------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------------
    @pytest.mark.slow
    def test_add_column(self, server, browser, reset_projects):
        """Check if the add column works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        sidebar = table.click_action_button("Add Column")
        sidebar.fill([("col_name", "new_col")])
        sidebar.fill([("col_value", "3")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=3, by_row_number=1)
        assert cell.text == "3", "New column should have the value '3'"

    @pytest.mark.slow
    def test_group_by(self, server, browser, reset_projects):
        """Check if the group by works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        # create bins to be able to group by on something
        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Cut")
        sidebar.fill([("cut_values", "-1,50,100")])
        sidebar.fill([("cut_labels", "failed,success")])
        sidebar.submit()
        # ------------------------------------------------

        sidebar = table.click_action_button("Group By")
        sidebar.fill([("groupby", "mock_price")])
        sidebar.add_to_dictionary("agg", "mock_name", "nunique")
        sidebar.submit()

        grouped_cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert grouped_cell.text == "failed", "group of failed values"
        grouped_cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert grouped_cell.text == "51", "Should have 51 values in the group"

        grouped_cell = table.get_cell(by_col_number=1, by_row_number=2)
        assert grouped_cell.text == "success", "group of success values"
        grouped_cell = table.get_cell(by_col_number=2, by_row_number=2)
        assert grouped_cell.text == "49", "Should have 49 values in the group"

    @pytest.mark.slow
    def test_merge_tables(self, server, browser, reset_projects):
        """Check if the merge tables works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)

        # Create a new table to merge with
        sidebar = tour.click_create_new_table()
        table_name = "ordered_2"
        sidebar.fill([("table_name", table_name), ("data_source_dir", "Csv ordered")])
        sidebar.submit()
        # ---------------------------------------------------------------------------

        table = tour.select_table(by_name="ordered")

        sidebar = table.click_action_button("Merge Tables")
        sidebar.fill([("table2", "ordered_2")])
        sidebar.fill([("on", "mock_name")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0", "First cell should be 'mock0' after merge"
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "0", "Second cell should be '0' after merge"
        cell = table.get_cell(by_col_number=3, by_row_number=1)
        assert cell.text == "0", "Third cell should be '0' after merge"

    @pytest.mark.slow
    def test_concatenate_tables(self, server, browser, reset_projects):
        """Check if the concatenate tables works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)

        # Create a new table to concatenate with
        sidebar = tour.click_create_new_table()
        table_name = "ordered_2"
        sidebar.fill([("table_name", table_name), ("data_source_dir", "Csv ordered")])
        sidebar.submit()
        # ---------------------------------------------------------------------------

        table = tour.select_table(by_name="ordered")

        sidebar = table.click_action_button("Concatenate Tables")
        sidebar.fill([("table", "ordered_2")])
        sidebar.submit()

        # Sort ascending to make sure there is twice the same value
        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.fill([("sort_order", "Ascending")])
        sidebar.submit()
        # ---------------------------------------------------------

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0", "First cell should be 'mock0' after concatenate"
        cell = table.get_cell(by_col_number=1, by_row_number=2)
        assert cell.text == "mock0", "Second cell should be 'mock0' after concatenate"
    
    @pytest.mark.slow
    def test_add_custom_action(self, server, browser, reset_projects):
        """Check if the custom action is added correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        modal = table.click_custom_action_button()
        modal.fill([("custom_action_code", "tables['ordered']['mock_name'] = 'Custom Test'")])
        modal.fill([("custom_action_name", "Custom Test")])
        modal.submit()

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "Custom Test", "First cell should be 'Custom Test' after concatenate"

    @pytest.mark.slow
    def test_keep_rows(self, server, browser, reset_projects):
        """Check if the keep rows works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        sidebar = table.click_dropdown_action_button("Rows", "Keep Rows")
        sidebar.fill([("keep_domain", "mock_price >= 10")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "10", "First cell should be 10 after keeping rows"

    @pytest.mark.slow
    def test_delete_rows(self, server, browser, reset_projects):
        """Check if the delete rows works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        sidebar = table.click_dropdown_action_button("Rows", "Delete Rows")
        sidebar.fill([("delete_domain", "mock_price < 10")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "10", "First cell should be 10 after deleting rows"

    @pytest.mark.slow
    def test_add_rows(self, server, browser, reset_projects):
        """Check if the add rows works correctly."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        sidebar = table.click_dropdown_action_button("Rows", "Add Rows")
        sidebar.fill([("new_rows", "[{'mock_name': 'new_mock_1', 'mock_price': -2}, {'mock_name': 'new_mock_2', 'mock_price': -1}]")])
        sidebar.submit()

        # Sort ascending to test if the new values were added correctly
        col_modal = table.click_header_button(by_col_number=2)
        sidebar = col_modal.click_action_button("Sort")
        sidebar.fill([("sort_order", "Ascending")])
        sidebar.submit()
        # ---------------------------------------------------------

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "new_mock_1", "Last cell should be 'new_mock_1' after adding rows"
        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "-2", "Last cell should be -2 after adding rows"
        cell = table.get_cell(by_col_number=1, by_row_number=2)
        assert cell.text == "new_mock_2", "Second last cell should be 'new_mock_2' after adding rows"
        cell = table.get_cell(by_col_number=2, by_row_number=2)
        assert cell.text == "-1", "Second last cell should be -1 after adding rows"
