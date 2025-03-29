import pandas as pd
import random

def run_pipeline():
    data = []
    for _ in range(100):
        name = 'test'
        list_price = random.randint(1, 1000)
        data.append([name, list_price])
    dfs = {}
    dfs['df'] = pd.DataFrame(data, columns=['name', 'price'])

    # Squirrel Pipeline start
    dfs['df']['action1'] = 1  #sq_action: action1
    #Useless comment, must have no effect (comment + 2 next python line should be 1 action)
    dfs['df']['action2'] = 1
    dfs['df']['action2'] = 2  #sq_action: action2
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    # No edit under
    return dfs
