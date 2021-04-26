import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import tool

###################################### Plot BTC Chart
tool.plotGraph()
tool.plotCandlestickChart()
tool.plotTechnicalChart()

###################################### Plot Graphs
coin_name_list = ['BTC', 'ETH']
coin_list = []
tech_name_list = ['AAPL', 'GOOG']
tech_list = []

#### Get Data
# Coin
for coin in coin_name_list:
    df = tool.loadChart(price='USDT_%s'%coin)
    globals()[coin] = tool.unifyCoinDF(df)
    coin_list.append(globals()[coin])
# Stock
for brand in tech_name_list:
    df = tool.loadStock(brand=brand)
    globals()[brand] = tool.unifyStockDF(df)
    tech_list.append(globals()[brand])

# Joint List
brand_list = coin_list
brand_list.extend(tech_list)
brand_name_list = coin_name_list
brand_name_list.extend(tech_name_list)

# Add Technical Index
for brand in brand_list:
    brand = tool.addTechnicalIndex(brand)

# New DataFrame
df_opens = tool.concatDF(brand_list, brand_name_list, 'Open')
df_returns = tool.concatDF(brand_list, brand_name_list, 'Return')

#### Plot
tool.plotJoint(BTC, ETH, name='joint_coin_open')
tool.plotJoint(AAPL, GOOG, kind='Return', name='joint_stock_return', color='seagreen')
tool.plotJoint(BTC, GOOG, kind='Return', name='joint_coin-stock_return', color='indianred')
tool.plotPair(df_returns, name='pair_return')
tool.plotHeatmap(df_opens, name='heatmap_open')