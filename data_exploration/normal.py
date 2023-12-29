import pandas as pd
import numpy as np

FRACTION_DEMAND = 0.02  

def normal_data(df):
    df = df.dropna(subset=['city', 'lat', 'lng', 'population','admin_name']).reset_index(drop=True)
    df = df.drop(df[df['population'] < 10000].index).reset_index(drop=True)
    df['Demand'] = np.floor(
    FRACTION_DEMAND * df.population + np.random.uniform(-10, 10, size=(df.shape[0],)))
    return df
