class PipelineAction:
    """Represents a single action in the pipeline"""
    def __init__(self, pipeline, action_instance):
        self.pipeline = pipeline
        self.action = action_instance
        self.description = self.action.name or self.action.__class__.__name__

    async def add_to_pipeline(self):
        self.pipeline.add_action(self)
