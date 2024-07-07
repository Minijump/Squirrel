import sys
import os
import pandas as pd
import random


def run_pipeline():
    data = []
    for _ in range(100):
        name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))
        reference = random.randint(1000, 9999)
        list_price = round(random.uniform(10, 100), 2)
        data.append([name, reference, list_price])

    df = pd.DataFrame(data, columns=['name', 'reference', 'price'])

    # Squirrel Pipeline start
    df['test'] = 3

    df['test 2'] = 6
    
    df = df.drop(columns=['test 2'])
    
    df['ttt'] = 9
    # Add new code here (keep this comment line)
    # Squirrel Pipeline end

    # No edit under
    return df
