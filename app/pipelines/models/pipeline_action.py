from typing import Dict, Any

from app.utils.form_utils import squirrel_action_error


class PipelineAction:
    """Represents a single action in the pipeline"""
    def __init__(self, action_class: str, parameters: Dict[str, Any], description: str = ""):
        self.action_class = action_class
        self.parameters = parameters
        self.description = description

    @squirrel_action_error
    async def add_to_pipeline(self, pipeline):
        pipeline.add_action(self)
