PROJECT_TYPE_REGISTRY = {}
def project_type(cls):
    """
    Decorator to register all data source types
    """
    PROJECT_TYPE_REGISTRY[cls.short_name] = cls
    return cls
