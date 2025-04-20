import os

from app.pipelines.models.pipeline_utils import get_file_lines


class Pipeline:
    def __init__(self, project_dir: str):
        self.project_path = os.path.join(os.getcwd(), "_projects", project_dir)
        self.pipeline_path = os.path.join(self.project_path, "pipeline.py")

    async def get_actions(self):
        """
        Get the actions from the pipeline file.

        Returns a list of tuples containing the action ID, action name, and action line.
        """
        lines = await get_file_lines(self.pipeline_path)

        actions = []
        for line in lines:
            if isinstance(line, tuple):
                if "#sq_action:" in line[1]:
                    actions.append((line[0], line[1].split("#sq_action:")[1].strip(), line[1]))
                else:
                    actions.append(line)

        return actions
    
    async def confirm_new_order(self, order: str):
        """
        Reorder the actions in the pipeline, edit the python file.

        Args:
            order (str): The new order of the actions as a string.
        """
        lines = await get_file_lines(self.pipeline_path)

        new_order = [int(action_str.split('-')[0]) for action_str in order.split(",")] # the old ids in the new order
        old_actions = [line for line in lines if isinstance(line, tuple)]  # the actions in the old order
        new_lines = []
        action_id = 0
        for line in lines:
            if isinstance(line, tuple):
                id_of_old_order = new_order[action_id]  # Action that had id_of_old_order must now have action_id id
                new_line = old_actions[id_of_old_order][1]  # [1] because (action_id, line)
                new_lines.append(new_line)
                action_id += 1
            else:
                new_lines.append(line)

        with open(self.pipeline_path, 'w') as file:
            file.writelines(new_lines)

    async def edit_action(self, action_id: int, action_code: str):
        """
        Edit the code of an action in the pipeline.

        Args:
            action_id (int): The ID of the action to edit.
            action_code (str): The new code of the action.
        """
        lines = await get_file_lines(self.pipeline_path)

        new_lines = []
        for line in lines:
            if isinstance(line, tuple):
                if line[0] == action_id:
                    new_lines.append(action_code)
                else:
                    new_lines.append(line[1])
            else:
                new_lines.append(line)

        with open(self.pipeline_path, 'w') as file:
            file.writelines(new_lines)

    async def delete_action(self, delete_action_id: int):
        """
        Remove an action from the pipeline.

        Args:
            delete_action_id (int): The ID of the action to delete.
        """
        lines = await get_file_lines(self.pipeline_path)

        new_lines = []
        for line in lines:
            if not isinstance(line, tuple):
                new_lines.append(line)
            elif line[0] != delete_action_id:
                new_lines.append(line[1])

        with open(self.pipeline_path, 'w') as file:
            file.writelines(new_lines)
