import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import time
from datetime import datetime, timedelta

#### Monte Carlo
def monte_carlo(start_price, days, dt, mu, sigma):
    prices = np.zeros(days)
    prices[0] = start_price
    
    shocks = np.zeros(days)
    drifts = np.zeros(days)
    
    for i in range(1, days):
        shocks[i] = np.random.normal(loc=0, scale=sigma*np.sqrt(dt))
        drifts[i] = mu * dt
        prices[i] = prices[i-1] + (prices[i-1] * (drifts[i] + shocks[i]))
        
    return prices
# Only Simulation
def simulateMonteCarlo(df, days, runs=5, kind='Open'):
    length = len(df) - days
    dt = 1 / days
    returns = df[kind].head(length).pct_change()
    mu = returns.mean()
    sigma = returns.std()
    
    simudf = DataFrame(df[kind])
    
    for run in range(runs):
        simu = np.full(len(df), None)
        simu[length:] = monte_carlo(df.iloc[length][kind], days, dt, mu, sigma)

        simudf['Simulate {}'.format(run+1)] = simu
    
    return simudf
# Predict by Monte Carlo
def predictMonteCarlo(df, days, val_days, runs=5, kind='Open', eval_end=False):
    length = len(df) - val_days
    dt = 1 / days
    returns = df[kind].head(length).pct_change()
    mu = returns.mean()
    sigma = returns.std()
    
    simudf = DataFrame(df[kind])
    preddf = DataFrame(np.full(days, None), columns=[kind])
    preddf.index = pd.date_range(df.tail(1).index.values[0], periods=days+1, freq='D')[1:]
    simudf = pd.concat([simudf, preddf])
    
    # Simulate
    for run in range(1, runs+1):
        simu = np.full(len(df)+days, None)
        simu[length:] = monte_carlo(df.iloc[length][kind], val_days+days, dt, mu, sigma)

        simudf['Simulate {}'.format(run)] = simu
        
    # Evaluate
    score = []
    val = len(df) - 1
    goal = df[kind][val]
    for run in range(1, runs+1):
        if eval_end:
            score.append(abs(simudf['Simulate {}'.format(run)].iloc[val] - goal))
        else:
            score.append(np.mean(np.abs(simudf['Simulate {}'.format(run)].iloc[length:len(df)] - goal)))
    for run in range(1, runs+1):
        if run != np.argmin(score) + 1:
            simudf['Simulate {}'.format(run)].iloc[len(df):] = None
    print(score)
    return simudf

