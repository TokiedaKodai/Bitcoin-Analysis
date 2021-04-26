import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt

import tool
import predict_tool as pt

# coin_name_list = ['BTC', 'ETH']
coin_name_list = ['BTC']
coin_list = []

#### Get Data
# Coin
for coin in coin_name_list:
    df = tool.loadChart(price='USDT_%s'%coin)
    globals()[coin] = tool.unifyCoinDF(df)
    coin_list.append(globals()[coin])

#### Predict BTC
pred = pt.predictMonteCarlo(BTC.tail(100), 50, 50, runs=10, eval_end=False)
plt.figure(figsize=(15, 5))
plt.plot(pred)
plt.legend(pred.columns)
tool.savefig('monte_carlo_btc')