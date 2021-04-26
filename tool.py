import pandas as pd
from pandas import Series, DataFrame
from pandas_datareader import DataReader
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns
import time
from datetime import datetime
import os

import poloniex

import config as cf

############################### LOAD DATA ###############################
# Load Coin Price from Poloniex
def loadChart(
    price='USDT_BTC',
    length=365
):
    polo = poloniex.Poloniex()
    period = polo.DAY # period of data
    end = time.time()
    start = end - period * length

    chart = polo.returnChartData(price, period=period, start=start, end=end)
    df = DataFrame.from_dict(chart, dtype=float)
    return df

# Load Stock Price from Yahoo
def loadStock(
    brand='AAPL',
    year=1
):
    end = datetime.now()
    start = datetime(end.year - year, end.month, end.day)
    return DataReader(brand, 'yahoo', start, end)

############################### EDIT TIME ###############################
# Timestamp to Date (year/month/day)
def timestamp2date(timestamp):
    return [datetime.fromtimestamp(timestamp[i]).date() for i in range(len(timestamp))]
# Date to String
def date2str(date):
    return [date[i].strftime('%Y-%m-%d') for i in range(len(date))]

############################### EDIT DATA FRAME ###############################
# Get Date from DataFrame
def getDate(df):
    timestamp = df['date'].values.tolist() # Series -> ndarray -> list
    date = timestamp2date(timestamp) # timestamp -> year/month/day
    return date

# Get price and date values
def getPrice(
    price='USDT_BTC',
    kind='open',
    length=365
    ):
    df = loadChart(price=price, length=length)
    date = getDate(df)
    price = df[kind].values.tolist()
    return (date, price)
# Get Stock price and date values
def getStockPrice(
    brand='AAPL',
    kind='Open',
    year=1
    ):
    df = loadStock(brand=brand, year=year)
    date = df.index.tolist()
    price = df[kind].values.tolist()
    return (date, price)

# Unify Coin DataFrame
def unifyCoinDF(df):
    date = getDate(df)
    df.drop(['date', 'quoteVolume', 'weightedAverage'], axis=1, inplace=True)
    df.index = pd.to_datetime(date)
    df.index.name = 'Date'
    df.columns = cf.unit_columns
    return df

# Unify Stock DataFrame
def unifyStockDF(df):
    return df.drop('Adj Close', axis=1)

# Concat DataFrame
def concatDF(list_df, list_name, column):
    newdf = pd.concat([df[column] for df in list_df], axis=1)
    newdf.columns = list_name
    newdf.dropna(inplace=True)
    return newdf

# Add Technical Index
def addTechnicalIndex(df, kind='Open', bw=20):
    df['Return'] = df[kind].pct_change() # Daily Return
    df['EMA20'] = df[kind].ewm(span=20).mean() # 20days EMA
    df['SMA50'] = df[kind].rolling(window=50).mean() # 50days SMA
    # Bollinger Band
    r = df[kind].rolling(bw)
    df['Upper'] = r.mean() + 2 * r.std()
    df['Lower'] = r.mean() - 2 * r.std()
    return df

############################### PLOT CHART ###############################
# Save Figure by some formats
def savefig(name):
    for fmt in cf.save_formats:
        plt.savefig(cf.save_dir + name + fmt)

# Plot graph
def plotGraph(
    price='USDT_BTC',
    kind='open',
    length=365,
    name='chart-BTC'
    ):
    date, price = getPrice(
        price=price,
        kind=kind,
        length=length)
    plt.plot(date, price)
    savefig(name)

# Plot CandleStick Chart
def plotCandlestickChart(
    price='USDT_BTC',
    kind='Open',
    length=100,
    name='candlestick_BTC'
    ):
    df = loadChart(price=price, length=length)
    df = unifyCoinDF(df)
    df = addTechnicalIndex(df, kind=kind)

    fig, axes = mpf.plot(df, type='candle', returnfig=True, figratio=(12,4))
    savefig(name)

# Plot Technical Chart
def plotTechnicalChart(
    price='USDT_BTC',
    kind='Open',
    length=100,
    name='technical_BTC'
    ):
    # length+50 to calcurate SMA50
    df = loadChart(price=price, length=length+50)

    # Prepare data
    df = unifyCoinDF(df)
    df = addTechnicalIndex(df, kind=kind)
    df = df.tail(length)

    # Plot
    addplot = mpf.make_addplot(df[['EMA20', 'SMA50']])
    fig, axes = mpf.plot(
        df, type='candle', addplot=addplot, volume=True,
        fill_between=dict(y1=df['Lower'].values, y2=df['Upper'].values, color='lightblue', alpha=.3),
        style='charles', returnfig=True, figratio=(12,8))
    axes[0].legend(['EMA20', 'SMA50'], loc=2)
    savefig(name)

############################### PLOT GRAPH ###############################
# JointPlot
def plotJoint(df1, df2, kind='Open', scatter='hex', name='jointplot', color=None):
    plt.figure()
    sns.jointplot(x=df1[kind], y=df2[kind], kind=scatter, color=color)
    savefig(name)

def plotPair(df, name='pairplot'):
    plt.figure()
    fig = sns.PairGrid(df)
    fig.map_upper(plt.scatter)
    fig.map_lower(sns.kdeplot, cmap='cool_d')
    fig.map_diag(plt.hist, color='purple')
    savefig(name)

def plotHeatmap(df, name='heatmap', annot=True):
    plt.figure()
    sns.heatmap(df.corr(), annot=annot)
    savefig(name)