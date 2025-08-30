from app.pipelines.models.action_factory import ActionFactory
from app.pipelines.models.actions import CreateTable

def test_init_action():
    form_data = {
        "action_name": "CreateTable",
        "table_name": "test_table",
        "source_creation_type": "data_source",
        "data_source_dir": "test_source"
    }
    
    action_instance = ActionFactory.init_action(form_data)
    
    assert isinstance(action_instance, CreateTable)
    assert action_instance.form_data == form_data
