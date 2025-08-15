# How pipeline is working 

The pipeline code is stored in a pipeline.py file inside a project. Everytime we have to run the pipeline, we load this file and run it.
We can see in C:\Users\sacha\Documents\projects\Squirrel\app\tables\routers\tables.py the following code multiple times:
```python
pipeline = load_pipeline_module(project_dir)
tables = pipeline.run_pipeline()
```
This code is responsible for loading and running the pipeline
Note: in the pipeline.py file, we define a function that executes the actions, and returns all the tables (dataframes) inside a dictionnary

To add new actions to the pipeline, each action (C:\Users\sacha\Documents\projects\Squirrel\app\data_sources\models) classes have an 'execute' function that returns the python code to add in the pipeline
Some actions also have an 'execute_advanced' function, and data sources have the 'create_table' function

In the pipeline tab (models and controllers) (C:\Users\sacha\Documents\projects\Squirrel\app\pipelines)
the application recognize the actions with the commentary '#sq_action:' after each actions (see how Pipeline class and pipeline_utils works)
When each actions are recognized, it display them and we can reorder them and change the action code


# How I want it to work

I do not want to pipeline to be store inside a python file anymore. Instead I want it to be stored inside a pickle file.
This file (pipeline.pkl) will only contain the actions and their parameters, not the code to execute them.
I guess, this should store the class of the action and the parameters 
(make sure each parameters can be added and nothing will break the logic (/\{},...), I guess a kind of sanitizer will be required, like in url?)
Instead of loading the pipeline.py file, we will load the pipeline.pkl file and execute the actions based on the class and parameters stored in it.

In the pipeline, the applications will recognize the action (because it will only contains the actions)
We will be, as before, able to reorder the actions and change the parameters of each action.
However, as the app can recognize which action we are using, instead of the code, it will display the parameters dynamically.
(when created the action from scratch, ActionSidebar display it dynamically, in the pipeline I want the EditActionModal to do the same (with the parameters of the action pre-filled))


# Guidelines
- Do only what is asked (or necessary to make it work); ie do not improve others things, add documentation files, correct or add unit tests
- Respect the code style an dstructure of the project
- make it the more modular, reusable, succint ans readable as possible
