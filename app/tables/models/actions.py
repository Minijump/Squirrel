TABLE_ACTION_REGISTRY = {}
def table_action_type(cls):
    TABLE_ACTION_REGISTRY[cls.__name__] = cls
    return cls

from fastapi import Request
from fastapi.responses import RedirectResponse

import os
import json
from functools import wraps

from app.projects.models.project import NEW_CODE_TAG
from app.data_sources.models.data_source import DATA_SOURCE_REGISTRY
from app.utils.error_handling import squirrel_error

def add(func):
    @squirrel_error
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        """
        Adds code returned by func to the pipeline (with the correct indentation)

        * request contains the project_dir
        * func provides the new code line(s) (str)
          (func MUST return lines splitted with '\n'
           expl: 'line1\nline2\nline3'
           else indentation will be wrong)

        => Returns a RedirectResponse to the project page
        """        
        form_data = await request.form()
        project_dir = form_data.get("project_dir")
        pipeline_path = os.path.join(os.getcwd(), "_projects", project_dir, "pipeline.py")

        # Find the line with the NEW_CODE_TAG, and get the indentation
        with open(pipeline_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if NEW_CODE_TAG in line:
                    current_indentation = len(line) - len(line.lstrip())
                    break
            
        # Edit pipeline code
        with open(pipeline_path, 'r') as file:
          pipeline_code = file.read()
          new_code = await func(request)
          new_code += """\n""" + NEW_CODE_TAG 
          new_code_list = new_code.split('\n')
          new_code = str(new_code_list[0]) + '\n' + '\n'.join((' ' * current_indentation) + l for l in new_code_list[1:])
          new_pipeline_code = pipeline_code.replace(NEW_CODE_TAG, new_code)

        # Write the new content to the file
        with open(pipeline_path, 'w') as file:
            file.write(new_pipeline_code)
        
        return RedirectResponse(url=f"/tables/?project_dir={project_dir}", status_code=303)                                                    
    return wrapper

action = type('action', (object,), {'add': add})

class Action:
    def __init__(self, request):
        self.request = request
        self.args = {}

    async def _get(self, args_list):
        form_data = await self.request.form()
        return (form_data.get(arg) for arg in args_list)
    
    async def execute(self):
        raise NotImplementedError("Subclasses must implement this method")

@table_action_type
class AddColumn(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "col_name": {"type": "str", "string": "Col. Name"},
            "col_value": {"type": "txt", "string": "Col. Value"},
        }

    async def execute(self):
        table_name, col_name, col_value = await self._get(["table_name", "col_name", "col_value"])
        new_code = f"""dfs['{table_name}']['{col_name}'] = {col_value}  #sq_action:Add column {col_name} on table {table_name}"""
        return new_code

@table_action_type
class AddRow(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "new_rows": {"type": "txt", "string": "New rows", "info": """With format<br/> [<br/>{'Col1': Value1, 'Col2': Value2, ...},<br/> {'Col1': Value3 ...<br/>]"""},
        }

    async def execute(self):
        table_name, new_rows = await self._get(["table_name", "new_rows"])
        new_rows = f"pd.DataFrame({new_rows})" if new_rows else "pd.DataFrame()"
        new_code = f"""dfs['{table_name}'] = pd.concat([dfs['{table_name}'], {new_rows}], ignore_index=True)  #sq_action:Add rows in table {table_name}"""
        return new_code

@table_action_type
class DeleteRow(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "delete_domain": {"type": "txt", "string": "Domain", "info": "With format Col1 &lt; Col2, Colx == 'Value',...."},
        }

    async def execute(self):
        table_name, delete_domain = await self._get(["table_name", "delete_domain"])
        new_code = f"""dfs['{table_name}'] = dfs['{table_name}'].query("not ({delete_domain})")  #sq_action:Delete rows in table {table_name}"""
        return new_code

@table_action_type
class CreateTable(Action):
    async def execute(self):
        project_dir, data_source_dir = await self._get(["project_dir", "data_source_dir"])
        data_source_path = os.path.relpath(
            os.path.join(os.getcwd(), '_projects', project_dir, 'data_sources', data_source_dir), 
            os.getcwd())

        manifest_path = os.path.join(data_source_path, "__manifest__.json")
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)

        SourceClass = DATA_SOURCE_REGISTRY[manifest_data["type"]]
        source = SourceClass(manifest_data)
        new_code = source.create_table(await self.request.form())
        
        return new_code
    
@table_action_type
class CustomPythonAction(Action):
    def __init__(self, request):
        super().__init__(request)
        self.args = {
            "python_action_code": {"type": "txt", "string": "Python"},
            "python_action_name": {"type": "str", "string": "Action Name"},
        }

    async def execute(self):
        python_action_code, python_action_name = await self._get(["python_action_code", "python_action_name"])
        new_code = f"""{python_action_code}  #sq_action: {python_action_name}"""
        return new_code