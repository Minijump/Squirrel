class PipelineAction:
    """Represents a single action in the pipeline"""
    def __init__(self, pipeline, action_instance):
        self.pipeline = pipeline
        self.action = action_instance # can be all subclasses of Action
        self.description = False
        self.update_description()

    def update_description(self):
        self.description = self.action.get_name() or self.action.__class__.__name__
