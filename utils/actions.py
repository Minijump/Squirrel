from fastapi import Request
from fastapi.responses import RedirectResponse

import os
from functools import wraps

NEW_CODE_TAG = "# Add new code here (keep this comment line)"
PIPELINE_START_TAG = "# Squirrel Pipeline start"
PIPELINE_END_TAG = "# Squirrel Pipeline end"

def add(func):
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
