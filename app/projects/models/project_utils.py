NEW_CODE_TAG = "# Add new code here (keep this comment line)"
PIPELINE_START_TAG = "# Squirrel Pipeline start"
PIPELINE_END_TAG = "# Squirrel Pipeline end"

BASIC_PIPELINE = """
import pandas as pd

def run_pipeline():
    tables = {}
    
    %s
    %s
    %s

    return tables
""" % (PIPELINE_START_TAG, NEW_CODE_TAG, PIPELINE_END_TAG)

PROJECT_TYPE_REGISTRY = {}
def project_type(cls):
    """
    Decorator to register all data source types
    """
    PROJECT_TYPE_REGISTRY[cls.short_name] = cls
    return cls
