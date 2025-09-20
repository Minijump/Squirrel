class PipelineAction:
    """Represents a single action in the pipeline"""
    def __init__(self, pipeline, action_instance):
        self.pipeline = pipeline
        self.action = action_instance # can be all subclasses of Action
        self.custom_description = None
        self.description = False
        self.update_description()

    def update_description(self):
        if self.custom_description and self.custom_description.strip():
            self.description = self.custom_description
        else:
            self.description = self.action.get_name() or self.action.__class__.__name__

    def set_custom_description(self, description):
        self.custom_description = description
        self.update_description()
