import pytest

from tests.utils.tour_toolbox_tour import Tour


class TestPipelineTours:
    @pytest.mark.slow
    def test_change_action_order(self, server, browser, reset_projects):
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        tour.navbar_click("Pipeline")
        
        tour.check_visibility(xpath="//button[@id='save-order']", visible=False)
        
        action_elements = tour.get_pipeline_actions()
        original_first_action = action_elements[0]
        original_first_action_text = original_first_action.text
        original_second_action = action_elements[1]
        original_second_action_text = original_second_action.text

        tour.move_action(original_second_action, original_first_action)

        tour.check_visibility(xpath="//button[@id='save-order']", visible=True)
        tour.click_confirm_button()
        tour.check_visibility(xpath="//button[@id='save-order']", visible=False)

        tour.navbar_click("Table")
        tour.navbar_click("Pipeline")
        action_elements_after_leaving_page = tour.get_pipeline_actions()
        assert action_elements_after_leaving_page[0].text == original_second_action_text, "New action order is not saved; first action is not correct"
        assert action_elements_after_leaving_page[1].text == original_first_action_text, "New action order is not saved; second action is not correct"

    @pytest.mark.slow
    def test_delete_action(self, server, browser, reset_projects):
        """Test the delete action in the pipeline."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        tour.navbar_click("Pipeline")

        original_action_elements = tour.get_pipeline_actions()
        original_number_of_actions = len(original_action_elements)
        
        edit_action_modal = tour.click_edit_action(1)
        edit_action_modal.click_danger_button()
        tour.confirm_modal(confirm=False) # First, cancel
        edit_action_modal.click_danger_button()
        tour.confirm_modal(confirm=True) # Then, confirm
        
        new_action_elements = tour.get_pipeline_actions(wait_a_minute=True)
        new_number_of_actions = len(new_action_elements)
        assert new_number_of_actions == original_number_of_actions - 1, "Action was not deleted"

    @pytest.mark.slow
    def test_edit_action(self, server, browser, reset_projects):
        """Test the edit action in the pipeline."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        tour.navbar_click("Pipeline")

        edit_action_modal = tour.click_edit_action(1)
        edit_action_modal.fill([("table_name", "New Table Name")])
        edit_action_modal.submit()
        
        edit_action_modal = tour.click_edit_action(1)
        tour.check_elements(by_ids=[("table_name", "New Table Name")])
