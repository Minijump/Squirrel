import pytest

from tests.utils.tours_toolbox import Tour


class TestPipelineTours:
    @pytest.mark.slow
    def test_change_action_order(self, server, browser, reset_projects):
        """Test the change action order in the pipeline."""
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

        new_action_elements = tour.get_pipeline_actions()
        assert new_action_elements[0].text == original_second_action_text, "First action should now be the previous second action"
        assert new_action_elements[1].text == original_first_action_text, "Second action should now be the previous first action"

        tour.navbar_click("Table")
        tour.navbar_click("Pipeline")
        action_elements_after_leaving_page = tour.get_pipeline_actions()
        assert action_elements_after_leaving_page[0].text == original_second_action_text, "New action order is not saved; first action is not correct"
        assert action_elements_after_leaving_page[1].text == original_first_action_text, "New action order is not saved; second action is not correct"

    @pytest.mark.slow
    def test_modal_edit_action_modal(self, server, browser, reset_projects):
        """Test the edit action modal in the pipeline + test the hover effect"""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        tour.navbar_click("Pipeline")

        tour.check_pipeline_actions_hover_effect()
        
        edit_action_modal = tour.click_edit_action(1)
        edit_action_modal.close()

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
        # Handle the alert
        alert = browser.switch_to.alert
        assert alert.text == "Are you sure you want to delete this action?", "Unexpected alert text"
        alert.accept()
        
        new_action_elements = tour.get_pipeline_actions(wait_a_minute=True)
        new_number_of_actions = len(new_action_elements)
        assert new_number_of_actions == original_number_of_actions - 1, "Action was not deleted"
    
    @pytest.mark.slow
    def test_cancel_delete_action(self, server, browser, reset_projects):
        """Test canceling delete action in the pipeline."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        tour.navbar_click("Pipeline")

        original_action_elements = tour.get_pipeline_actions()
        original_number_of_actions = len(original_action_elements)
        
        edit_action_modal = tour.click_edit_action(1)
        edit_action_modal.click_danger_button()
        # Handle the alert but cancel
        alert = browser.switch_to.alert
        alert.dismiss()
        
        edit_action_modal.close()
        new_action_elements = tour.get_pipeline_actions(wait_a_minute=True)
        assert len(new_action_elements) == original_number_of_actions, "Action shouldn't have been deleted"

    @pytest.mark.slow
    def test_edit_action(self, server, browser, reset_projects):
        """Test the edit action in the pipeline."""
        tour = Tour(browser, server)

        tour.click_card(by_position=2)
        tour.navbar_click("Pipeline")
        
        # TODO: with actual code, a white line must end the input (else next action will be on same line), fix that
        new_action_code = "print('Hello world')  #sq_action:a simple print"
        new_action_code_input = f"""
{new_action_code}
"""

        edit_action_modal = tour.click_edit_action(1)
        edit_action_modal.fill([("action_code", new_action_code_input)])
        edit_action_modal.submit()
        
        new_action_elements = tour.get_pipeline_actions(wait_a_minute=True)
        assert "a simple print" in new_action_elements[0].text, f"Action name was not updated; expected 'a simple print'to be in name"
