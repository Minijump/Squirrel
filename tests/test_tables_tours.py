import pytest

from tests.utils.tour_toolbox_tour import Tour


class TestTablesTours:
    @pytest.mark.slow
    def test_create_table_onchange(self, server, browser, reset_projects):
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
        tour = Tour(browser, server)

        tour.click_card(by_position=2)

        sidebar = tour.click_create_new_table()
        table_name = "test create new table"
        sidebar.fill([("table_name", table_name), ("data_source_dir", "Csv ordered")])
        sidebar.submit()

        tour.check_table_select_button_visibility(table_name)

    @pytest.mark.slow
    def test_create_table_from_other_table_copy(self, server, browser, reset_projects):
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
    def test_replace_vals(self, server, browser, reset_projects):
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
    def test_delete_column(self, server, browser, reset_projects):
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "mock0", "Cell should be mock0"

        col_modal = table.click_header_button(by_col_number=1)
        col_modal.click_danger_button()

        cell = table.get_cell(by_col_number=1, by_row_number=1)
        assert cell.text == "0", "Cell should be 0, first column should be deleted"

    @pytest.mark.slow
    def test_add_column(self, server, browser, reset_projects):
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
    def test_keep_rows(self, server, browser, reset_projects):
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        table = tour.select_table(by_name="ordered")

        sidebar = table.click_dropdown_action_button("Rows", "Keep Rows")
        sidebar.fill([("keep_domain", "mock_price >= 10")])
        sidebar.submit()

        cell = table.get_cell(by_col_number=2, by_row_number=1)
        assert cell.text == "10", "First cell should be 10 after keeping rows"

    @pytest.mark.slow
    def test_add_rows(self, server, browser, reset_projects):
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
