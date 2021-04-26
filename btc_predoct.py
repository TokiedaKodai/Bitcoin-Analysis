import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt

import tool
import predict_tool as ptl

# coin_name_list = ['BTC', 'ETH']
coin_name_list = ['BTC']
coin_list = []

#### Get Data
# Coin
for coin in coin_name_list:
    df = tool.loadChart(price='USDT_%s'%coin)
    globals()[coin] = tool.unifyCoinDF(df)
    coin_list.append(globals()[coin])

#### Predict BTC by Monte Carlo
start = 200
split = 315
train = BTC.iloc[start:split]
test = BTC['Open'].iloc[split-1:]
pred = ptl.predictMonteCarlo(train, 50, 50, runs=100)
plt.figure(figsize=(15, 5))
plt.plot(pred['Open'])
plt.plot(test)
plt.plot(pred['Best'])
plt.legend(['Train','Test', 'Predict'])
tool.savefig('monte_carlo_btc')

# plt.plot(pred)
# plt.plot(test)
# plt.legend(pred.columns)
# tool.savefig('monte_carlo_btc_10simu')