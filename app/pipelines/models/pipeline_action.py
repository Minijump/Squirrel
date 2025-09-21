class PipelineAction:
    """Represents a single action in the pipeline"""
    def __init__(self, pipeline, action_instance):
        self.pipeline = pipeline
        self.action = action_instance
        self.custom_description = None
        self.description = False
        self.update_description()

    def _set_field(self, field_name, value):
        if not hasattr(self, field_name):
            setattr(self, field_name, value)

    def __setstate__(self, state):
        """
        __setstate__ is called during unpickling
          * Ensure backward compatibility by settings creating missing fields
        """
        self.__dict__.update(state)
        self._set_field('custom_description', None)

    def update_description(self):
        if self.custom_description and self.custom_description.strip():
            self.description = self.custom_description
        else:
            self.description = self.action.get_name() or self.action.__class__.__name__

    def set_custom_description(self, description):
        self.custom_description = description
        self.update_description()
