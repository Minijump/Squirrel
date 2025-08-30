class PipelineAction:
    """Represents a single action in the pipeline"""
    def __init__(self, pipeline, action_instance):
        self.pipeline = pipeline
        self.action = action_instance # can be all subclasses of Action
        self.description = self.action.name or self.action.__class__.__name__
